"""Shared configuration constants for ALZ Recall."""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

AGENT_OUTPUT_DIR = "agent-output"
DB_PATH = Path("tmp/.alz-recall.db")

# ---------------------------------------------------------------------------
# Workflow steps (0-9, with 3_5 as governance gate)
# ---------------------------------------------------------------------------

VALID_STEPS: list[str] = [
    "0", "1", "2", "3", "3_5", "4", "5", "6", "7", "8", "9",
]

STEP_KEY_TO_INT: dict[str, int] = {
    "0": 0,
    "1": 1,
    "2": 2,
    "3": 3,
    "3_5": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
}

STEP_META: dict[str, dict[str, str]] = {
    "0":   {"name": "Assessment",    "agent": "assessment"},
    "1":   {"name": "Requirements",  "agent": "requirements"},
    "2":   {"name": "Architecture",  "agent": "architect"},
    "3":   {"name": "Design",        "agent": "design"},
    "3_5": {"name": "Governance",    "agent": "governance"},
    "4":   {"name": "IaC Plan",      "agent": "iac-planner"},
    "5":   {"name": "IaC Code",      "agent": "bicep-code"},
    "6":   {"name": "Deploy",        "agent": "deploy"},
    "7":   {"name": "Documentation", "agent": "documentation"},
    "8":   {"name": "Monitor",       "agent": "monitor"},
    "9":   {"name": "Remediate",     "agent": "remediate"},
}

# Review audit gates (subset of steps that require Challenger review)
REVIEW_GATES: list[str] = ["1", "2", "3_5", "4", "5", "6"]

# ---------------------------------------------------------------------------
# Artifact classification patterns  (fnmatch-style)
# ---------------------------------------------------------------------------

ARTIFACT_PATTERNS: list[tuple[str, str]] = [
    ("00-estate-state.json",           "estate-state"),
    ("00-session-state.json",          "session-state"),
    ("00-assessment-*.md",             "assessment"),
    ("00-assessment-*.json",           "assessment-json"),
    ("00-handoff.md",                  "handoff"),
    ("01-requirements.md",             "requirements"),
    ("02-architecture-assessment.md",  "architecture"),
    ("03-design-*.md",                 "design"),
    ("04-governance-constraints.json", "governance-json"),
    ("04-governance-constraints.md",   "governance"),
    ("04-implementation-plan.md",      "implementation-plan"),
    ("06-deployment-summary.md",       "deployment-summary"),
    ("07-*.md",                        "as-built"),
    ("08-compliance-report.md",        "compliance"),
    ("09-remediation-log.md",          "remediation"),
]

# ---------------------------------------------------------------------------
# Session state template (v3.0)
# ---------------------------------------------------------------------------

DEFAULT_REGION = "southcentralus"

SESSION_STATE_VERSION = "3.0"


def build_session_template(
    project: str,
    landing_zone: str = "",
    iac_tool: str = "",
    region: str = DEFAULT_REGION,
) -> dict:
    """Return a fresh v3.0 session-state dict."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    steps: dict[str, dict] = {}
    for key in VALID_STEPS:
        meta = STEP_META[key]
        steps[key] = {
            "name": meta["name"],
            "agent": meta["agent"],
            "status": "pending",
            "started": None,
            "completed": None,
            "artifacts": [],
        }
    return {
        "schema_version": SESSION_STATE_VERSION,
        "project": project,
        "landing_zone": landing_zone,
        "iac_tool": iac_tool,
        "region": region,
        "branch": "",
        "updated": now,
        "current_step": 0,
        "decisions": {
            "region": region,
            "compliance": "",
            "budget": "",
            "architecture_pattern": "",
            "deployment_strategy": "",
            "complexity": "",
        },
        "decision_log": [],
        "open_findings": [],
        "review_audit": {},
        "steps": steps,
    }
