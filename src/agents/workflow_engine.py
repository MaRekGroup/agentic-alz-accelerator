"""
Workflow Engine — DAG-based orchestration for the multi-agent ALZ workflow.

Reads the workflow graph definition and executes steps in order, enforcing
approval gates, routing IaC tracks, and managing artifact handoffs.

Inspired by the APEX workflow engine pattern.
"""

import json
import logging
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class StepStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


class ComplexityTier(str, Enum):
    SIMPLE = "simple"      # ≤3 resource types, single region, no custom policy
    STANDARD = "standard"  # 4-8 types, multi-region OR multi-env
    COMPLEX = "complex"    # >8 types, multi-region + multi-env, hub-spoke


class WorkflowState:
    """Tracks the state of a workflow execution."""

    def __init__(self, project_name: str, iac_tool: str = "bicep"):
        self.project_name = project_name
        self.iac_tool = iac_tool
        self.complexity = ComplexityTier.STANDARD
        self.steps: dict[str, StepStatus] = {}
        self.artifacts: dict[str, str] = {}
        self.current_step: Optional[str] = None
        self.gate_approvals: dict[str, bool] = {}

    def to_dict(self) -> dict:
        return {
            "project_name": self.project_name,
            "iac_tool": self.iac_tool,
            "complexity": self.complexity.value,
            "steps": {k: v.value for k, v in self.steps.items()},
            "artifacts": self.artifacts,
            "current_step": self.current_step,
            "gate_approvals": self.gate_approvals,
        }


class WorkflowEngine:
    """DAG-based workflow engine that orchestrates agent steps and approval gates."""

    def __init__(self, graph_path: Optional[str] = None):
        self.graph = self._load_graph(graph_path)
        self.nodes = {n["id"]: n for n in self.graph["nodes"]}
        self.edges = self.graph["edges"]

    def _load_graph(self, graph_path: Optional[str]) -> dict:
        """Load the workflow DAG from JSON."""
        if graph_path:
            path = Path(graph_path)
        else:
            path = (
                Path(__file__).parent.parent.parent
                / ".github"
                / "skills"
                / "workflow-engine"
                / "templates"
                / "workflow-graph.json"
            )

        with open(path) as f:
            return json.load(f)

    def get_next_steps(self, state: WorkflowState) -> list[dict]:
        """Determine the next executable steps based on current state and DAG edges."""
        ready = []

        for edge in self.edges:
            target_id = edge["to"]
            source_id = edge["from"]

            # Skip if target already completed or in progress
            if state.steps.get(target_id) in (
                StepStatus.COMPLETED,
                StepStatus.IN_PROGRESS,
                StepStatus.AWAITING_APPROVAL,
            ):
                continue

            # Check if source is satisfied
            source_status = state.steps.get(source_id)
            condition = edge.get("condition", "on_complete")

            satisfied = False
            if condition == "on_complete" and source_status == StepStatus.COMPLETED:
                satisfied = True
            elif condition == "on_approve" and state.gate_approvals.get(source_id):
                satisfied = True
            elif condition == "on_violation":
                # Triggered by monitoring findings
                satisfied = source_status == StepStatus.COMPLETED

            if satisfied:
                node = self.nodes.get(target_id, {})
                # Apply IaC routing for divergent steps
                if self._is_iac_divergent(target_id) and node.get("iac_variants"):
                    node = self._resolve_iac_variant(node, state.iac_tool)
                ready.append(node)

        return ready

    def get_challenger_passes(self, state: WorkflowState, step_type: str) -> int:
        """Get the number of adversarial review passes for a step."""
        matrix = self.graph.get("challenger_review", {}).get("complexity_matrix", {})
        tier_config = matrix.get(state.complexity.value, {})
        return tier_config.get(step_type, 1)

    def classify_complexity(self, requirements: dict) -> ComplexityTier:
        """Classify project complexity based on requirements."""
        resource_count = len(requirements.get("resource_types", []))
        regions = len(requirements.get("regions", []))
        environments = len(requirements.get("environments", []))
        custom_policies = len(requirements.get("custom_policies", []))
        networking = requirements.get("networking_type", "standalone")

        if (
            resource_count <= 3
            and regions <= 1
            and custom_policies == 0
            and environments <= 1
        ):
            return ComplexityTier.SIMPLE

        if (
            resource_count > 8
            or (regions > 1 and environments > 1)
            or custom_policies > 3
            or networking == "hub_spoke"
        ):
            return ComplexityTier.COMPLEX

        return ComplexityTier.STANDARD

    def validate_gate(self, gate_id: str, state: WorkflowState) -> dict:
        """Validate that prerequisites are met before approving a gate."""
        node = self.nodes.get(gate_id)
        if not node or node.get("type") != "gate":
            return {"valid": False, "error": f"'{gate_id}' is not a gate node"}

        # Find the step that feeds into this gate
        feeding_steps = [
            e["from"] for e in self.edges if e["to"] == gate_id
        ]

        incomplete = [
            step_id
            for step_id in feeding_steps
            if state.steps.get(step_id) != StepStatus.COMPLETED
        ]

        if incomplete:
            return {
                "valid": False,
                "error": f"Prerequisite steps not complete: {incomplete}",
            }

        return {"valid": True, "gate": gate_id, "description": node.get("description")}

    def get_artifact_path(self, step_id: str, project_name: str) -> str:
        """Get the output artifact path for a step."""
        node = self.nodes.get(step_id, {})
        artifact = node.get("artifact", "")
        return f"agent-output/{project_name}/{artifact}"

    def _is_iac_divergent(self, step_id: str) -> bool:
        """Check if a step diverges by IaC track."""
        routing = self.graph.get("iac_routing", {})
        return step_id in routing.get("divergent_steps", [])

    def _resolve_iac_variant(self, node: dict, iac_tool: str) -> dict:
        """Resolve the IaC-specific variant of a step."""
        variants = node.get("iac_variants", {})
        variant = variants.get(iac_tool, node)
        if isinstance(variant, str):
            return {**node, "agent": variant}
        if isinstance(variant, dict):
            return {**node, **variant}
        return node

    def get_full_workflow_summary(self) -> list[dict]:
        """Return a human-readable summary of all workflow steps."""
        summary = []
        for node in self.graph["nodes"]:
            summary.append({
                "id": node["id"],
                "type": node.get("type"),
                "agent": node.get("agent", node.get("codename", "")),
                "description": node.get("description", ""),
                "artifact": node.get("artifact", ""),
                "approval_required": node.get("approval_required", False),
            })
        return summary
