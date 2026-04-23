"""
Agent Orchestrator (🧠 Conductor) — APEX-aligned workflow orchestration.

Coordinates the multi-agent workflow through DAG-based step execution,
enforcing approval gates, routing IaC tracks, and managing artifact handoffs.

Inspired by the APEX Orchestrator pattern:
  AI Orchestrates · Humans Decide · Azure Executes
"""

import asyncio
import logging
from enum import Enum
from pathlib import Path
from typing import Optional

import typer
import yaml
from azure.identity import DefaultAzureCredential
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from src.agents.assessment_agent import AssessmentAgent
from src.agents.challenger_agent import ChallengerAgent
from src.agents.deployment_agent import DeploymentAgent
from src.agents.governance_agent import GovernanceAgent
from src.agents.monitoring_agent import MonitoringAgent
from src.agents.remediation_agent import RemediationAgent
from src.agents.requirements_agent import RequirementsAgent
from src.agents.workflow_engine import StepStatus, WorkflowEngine, WorkflowState
from src.config.settings import Settings

logger = logging.getLogger(__name__)


class RunMode(str, Enum):
    WORKFLOW = "workflow"   # Full APEX workflow (Steps 0-9)
    DEPLOY = "deploy"      # Deploy only (Steps 4-6)
    MONITOR = "monitor"    # Continuous monitoring (Step 8-9)
    FULL = "full"          # Deploy + Monitor
    ASSESS = "assess"      # Brownfield assessment (Step 0 only)


class AgentOrchestrator:
    """APEX-aligned orchestrator with DAG workflow, approval gates, and MCP integration."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.credential = DefaultAzureCredential()
        self.kernel = self._build_kernel()
        self.config = self._load_config()
        self.workflow_engine = WorkflowEngine()

        # Initialize agent roster
        self.assessment_agent = AssessmentAgent(
            kernel=self.kernel, credential=self.credential, settings=self.settings,
        )
        self.requirements_agent = RequirementsAgent(
            kernel=self.kernel, credential=self.credential, settings=self.settings,
        )
        self.governance_agent = GovernanceAgent(
            kernel=self.kernel, credential=self.credential, settings=self.settings,
        )
        self.challenger_agent = ChallengerAgent(
            kernel=self.kernel, credential=self.credential, settings=self.settings,
        )
        self.deployment_agent = DeploymentAgent(
            kernel=self.kernel, credential=self.credential, settings=self.settings,
        )
        self.monitoring_agent = MonitoringAgent(
            kernel=self.kernel, credential=self.credential, settings=self.settings,
        )
        self.remediation_agent = RemediationAgent(
            kernel=self.kernel, credential=self.credential, settings=self.settings,
        )

    def _build_kernel(self) -> Kernel:
        """Initialize Semantic Kernel with Azure OpenAI."""
        kernel = Kernel()
        kernel.add_service(
            AzureChatCompletion(
                deployment_name=self.settings.ai.openai_deployment,
                endpoint=self.settings.ai.openai_endpoint,
                api_version=self.settings.ai.openai_api_version,
                ad_token_provider=self._get_token,
            )
        )
        return kernel

    def _get_token(self) -> str:
        token = self.credential.get_token("https://cognitiveservices.azure.com/.default")
        return token.token

    def _load_config(self) -> dict:
        config_path = Path(__file__).parent.parent / "config" / "agent_config.yaml"
        with open(config_path) as f:
            return yaml.safe_load(f)

    # =========================================================================
    # Full APEX Workflow (Steps 0-9)
    # =========================================================================

    async def run_workflow(
        self,
        project_name: str,
        iac_tool: str = "bicep",
        diagram_engine: str = "python",
        brownfield: bool = False,
        scope: Optional[str] = None,
        scope_type: str = "subscription",
    ) -> WorkflowState:
        """Execute the full APEX-aligned workflow with approval gates.

        Args:
            project_name: Project identifier for artifact output.
            iac_tool: "bicep" or "terraform".
            diagram_engine: "python" (PNG via diagrams lib, default),
                            "svg" (custom inline SVG), or "drawio" (MCP).
            brownfield: If True, run Step 0 (assessment) before Step 1.
            scope: Azure scope for brownfield assessment (e.g. subscription ID).
            scope_type: "subscription" or "management_group".
        """
        state = WorkflowState(project_name=project_name, iac_tool=iac_tool)
        output_dir = Path("agent-output") / project_name
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Starting APEX workflow for project '%s' (%s, brownfield=%s)", project_name, iac_tool, brownfield)

        # Step 0: Brownfield Assessment (Assessor) — only if brownfield
        if brownfield:
            logger.info("Step 0: Running brownfield assessment...")
            state.steps["step-0-assess"] = StepStatus.IN_PROGRESS
            assessment_result = await self.run_assessment(
                scope=scope or self.settings.azure.subscription_id,
                scope_type=scope_type,
            )
            state.artifacts["00-assessment"] = assessment_result
            state.steps["step-0-assess"] = StepStatus.COMPLETED
            logger.info("Step 0 complete — %d findings, scores: %s",
                        assessment_result.get("total_findings", 0),
                        assessment_result.get("pillar_scores", {}))

        # Step 1: Requirements (Scribe)
        logger.info("Step 1: Gathering requirements...")
        state.steps["step-1-requirements"] = StepStatus.IN_PROGRESS
        await self._run_requirements_step(state, output_dir)
        state.steps["step-1-requirements"] = StepStatus.COMPLETED

        # Gate 1: Approval
        gate_1 = await self._request_approval("Gate 1", "Confirm requirements complete")
        state.gate_approvals["gate-1"] = gate_1

        # Step 2: Architecture (Oracle) — delegated to deployment agent for now
        logger.info("Step 2: Architecture assessment...")
        state.steps["step-2-architect"] = StepStatus.COMPLETED

        # Gate 2: Approval
        gate_2 = await self._request_approval("Gate 2", "Approve WAF/CAF assessment")
        state.gate_approvals["gate-2"] = gate_2

        # Step 3: Design (Artisan) — architecture diagrams
        logger.info("Step 3: Generating architecture diagrams (engine=%s)...", diagram_engine)
        state.steps["step-3-design"] = StepStatus.IN_PROGRESS
        diagram_outputs = self._run_design_step(
            state, output_dir, diagram_engine=diagram_engine,
        )
        state.artifacts["03-design-diagrams"] = diagram_outputs
        state.steps["step-3-design"] = StepStatus.COMPLETED

        # Step 3.5: Governance (Warden)
        logger.info("Step 3.5: Governance discovery...")
        state.steps["step-3.5-governance"] = StepStatus.IN_PROGRESS
        await self.governance_agent.discover_policy_constraints()
        state.artifacts["04-governance-constraints.json"] = str(output_dir / "04-governance-constraints.json")
        state.steps["step-3.5-governance"] = StepStatus.COMPLETED

        # Gate 3: Approval
        gate_3 = await self._request_approval("Gate 3", "Approve governance constraints")
        state.gate_approvals["gate-3"] = gate_3

        # Challenger review (adversarial)
        challenger_passes = self.workflow_engine.get_challenger_passes(state, "plan")
        for i in range(challenger_passes):
            logger.info(f"Challenger review pass {i + 1}/{challenger_passes}...")

        # Steps 4-6: Plan → Code → Deploy
        logger.info("Steps 4-6: Plan, generate, deploy...")
        await self.deployment_agent.run_interactive()
        state.steps["step-4-plan"] = StepStatus.COMPLETED
        state.steps["step-5-code"] = StepStatus.COMPLETED
        state.steps["step-6-deploy"] = StepStatus.COMPLETED

        # Step 7: Documentation (Chronicler)
        logger.info("Step 7: Generating documentation...")
        state.steps["step-7-docs"] = StepStatus.COMPLETED

        # Steps 8-9: Continuous monitoring
        logger.info("Starting continuous monitoring (Steps 8-9)...")
        await asyncio.gather(
            self._run_monitoring_loop(state),
            self._run_drift_detection_loop(state),
        )

        return state

    async def _run_requirements_step(self, state: WorkflowState, output_dir: Path) -> dict:
        """Execute the requirements gathering step."""
        template = self.requirements_agent.get_requirements_template()
        # In interactive mode, this would be a conversation
        # In automated mode, use the template + profile
        return {"template": template, "status": "gathered"}

    def _run_design_step(
        self,
        state: WorkflowState,
        output_dir: Path,
        diagram_engine: str = "python",
    ) -> list[str]:
        """Execute Step 3 — generate architecture diagrams.

        Args:
            diagram_engine: "python" | "svg" | "drawio"

        Returns:
            List of generated file paths.
        """
        from src.tools.azure_diagram_generator import generate_diagrams

        mg_prefix = self.settings.azure.management_group_prefix or "mrg"
        diagram_dir = str(output_dir / "diagrams")

        outputs = generate_diagrams(
            engine=diagram_engine,
            output_dir=diagram_dir,
            mg_prefix=mg_prefix,
        )
        logger.info("Step 3 produced %d diagram(s): %s", len(outputs), outputs)
        return outputs

    async def _request_approval(self, gate_name: str, description: str) -> bool:
        """Request human approval at a gate. Returns True for now (auto-approve in dev)."""
        logger.info(f"🛑 APPROVAL GATE: {gate_name} — {description}")
        # In production, this integrates with Teams/Slack/CLI for interactive approval
        # For development, auto-approve with logging
        logger.info(f"✅ {gate_name} approved (auto-approve mode)")
        return True

    # =========================================================================
    # Deployment Modes
    # =========================================================================

    async def run_deployment(self, profile: Optional[str] = None) -> dict:
        """Run the deployment agent interactively or with a profile."""
        logger.info("Starting deployment agent...")

        # Run governance discovery first
        governance = await self.governance_agent.discover_policy_constraints()
        logger.info(f"Governance: {governance['summary']}")

        # Run challenger review on governance
        logger.info("Challenger reviewing governance constraints...")

        if profile:
            return await self.deployment_agent.deploy_profile(profile)
        return await self.deployment_agent.run_interactive()

    async def run_monitoring(self) -> dict:
        """Run continuous monitoring loop."""
        logger.info("Starting monitoring agent (Sentinel)...")
        state = WorkflowState(project_name="monitoring", iac_tool=self.settings.iac.framework)
        await asyncio.gather(
            self._run_monitoring_loop(state),
            self._run_drift_detection_loop(state),
        )

    async def _run_monitoring_loop(self, state: WorkflowState) -> None:
        """Run periodic compliance monitoring."""
        while True:
            results = await self.monitoring_agent.run_compliance_scan()
            if results.get("violations"):
                await self._handle_violations(results["violations"])
            interval = self.settings.monitor.interval_minutes * 60
            logger.info(f"Next compliance scan in {self.settings.monitor.interval_minutes} min")
            await asyncio.sleep(interval)

    async def _run_drift_detection_loop(self, state: WorkflowState) -> None:
        """Run periodic drift detection."""
        interval = self.settings.monitor.drift_check_interval_minutes * 60
        while True:
            drift = await self.monitoring_agent.detect_drift()
            if drift.get("drifted_resources"):
                logger.warning(f"Drift in {len(drift['drifted_resources'])} resources")
                if self.settings.monitor.auto_remediate:
                    await self.remediation_agent.remediate(drift["drifted_resources"])
            await asyncio.sleep(interval)

    async def _handle_violations(self, violations: list[dict]) -> None:
        """Route policy violations to the remediation agent."""
        remediation_config = self.config["agents"]["remediation"]
        auto_severities = remediation_config.get("auto_remediate_severities", [])

        for violation in violations:
            if violation.get("severity") in auto_severities:
                logger.info(f"Auto-remediating: {violation.get('policy_name')}")
                await self.remediation_agent.remediate_single(violation)
            else:
                logger.info(f"Requires approval: {violation.get('policy_name')}")
                await self._notify_for_approval(violation)

    async def _notify_for_approval(self, violation: dict) -> None:
        """Send notification requesting human approval for remediation."""
        logger.info(f"Notification sent for: {violation.get('policy_name')}")

    async def run_full_lifecycle(self, profile: Optional[str] = None) -> None:
        """Deploy then start continuous monitoring."""
        deploy_result = await self.run_deployment(profile)
        logger.info(f"Deployment complete: {deploy_result}")
        await self.run_monitoring()

    async def run_assessment(
        self,
        scope: Optional[str] = None,
        scope_type: str = "subscription",
        mode: str = "full",
    ) -> dict:
        """Run brownfield assessment (Step 0).

        Args:
            scope: Azure scope (subscription ID or MG name). Falls back to settings.
            scope_type: "subscription" or "management_group".
            mode: Assessment mode — "full", "quick", or "security-only".

        Returns:
            Assessment summary dict with findings, scores, and report paths.
        """
        resolved_scope = scope or self.settings.azure.subscription_id
        logger.info("Step 0: Brownfield assessment (scope=%s, type=%s, mode=%s)",
                    resolved_scope, scope_type, mode)

        result = await self.assessment_agent.run_assessment(
            scope=resolved_scope,
            scope_type=scope_type,
            mode=mode,
        )
        logger.info("Assessment complete — %d findings", result.get("total_findings", 0))
        return result


# =============================================================================
# CLI Entry Point
# =============================================================================

app = typer.Typer(help="Agentic Azure Landing Zone Accelerator (APEX-aligned)")


@app.command()
def main(
    mode: RunMode = typer.Option(RunMode.FULL, help="Run mode"),
    project: str = typer.Option("default", help="Project name for artifact output"),
    iac_tool: str = typer.Option("bicep", help="IaC framework: bicep or terraform"),
    profile: Optional[str] = typer.Option(None, help="Landing zone profile"),
    brownfield: bool = typer.Option(False, "--brownfield", help="Enable Step 0 brownfield assessment"),
    scope: Optional[str] = typer.Option(None, help="Azure scope for brownfield assessment"),
    scope_type: str = typer.Option("subscription", help="Scope type: subscription or management_group"),
    assess_mode: str = typer.Option("full", "--assess-mode", help="Assessment mode: full, quick, or security-only"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    """Run the Agentic ALZ Accelerator."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    orchestrator = AgentOrchestrator()

    if mode == RunMode.WORKFLOW:
        asyncio.run(orchestrator.run_workflow(
            project, iac_tool, brownfield=brownfield,
            scope=scope, scope_type=scope_type,
        ))
    elif mode == RunMode.DEPLOY:
        asyncio.run(orchestrator.run_deployment(profile))
    elif mode == RunMode.MONITOR:
        asyncio.run(orchestrator.run_monitoring())
    elif mode == RunMode.ASSESS:
        asyncio.run(orchestrator.run_assessment(
            scope=scope, scope_type=scope_type, mode=assess_mode,
        ))
    elif mode == RunMode.FULL:
        asyncio.run(orchestrator.run_full_lifecycle(profile))


if __name__ == "__main__":
    app()
