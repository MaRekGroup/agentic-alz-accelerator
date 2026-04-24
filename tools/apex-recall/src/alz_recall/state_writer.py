"""Session-state reader/writer with atomic persistence and auto-migration."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from .config import (
    AGENT_OUTPUT_DIR,
    SESSION_STATE_VERSION,
    VALID_STEPS,
    build_session_template,
)
from .indexer import reindex_file
from .types import atomic_write_json, now_iso, read_json


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def session_path(project: str) -> Path:
    """Return the canonical session-state path for a project."""
    return Path(AGENT_OUTPUT_DIR) / project / "00-session-state.json"


def estate_path(project: str) -> Path:
    """Return the canonical estate-state path for a project."""
    return Path(AGENT_OUTPUT_DIR) / project / "00-estate-state.json"


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def load_session(project: str) -> dict | None:
    """Load and auto-migrate a session-state file. Returns None if missing."""
    p = session_path(project)
    if not p.exists():
        return None
    data = read_json(p)
    return _migrate(data, project)


def load_estate(project: str) -> dict | None:
    """Load estate-state if it exists."""
    p = estate_path(project)
    if not p.exists():
        return None
    return read_json(p)


# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------

def save_session(
    project: str,
    data: dict,
    conn: sqlite3.Connection | None = None,
) -> Path:
    """Atomically persist *data* as the session state and reindex."""
    data["updated"] = now_iso()
    p = session_path(project)
    atomic_write_json(p, data)
    if conn is not None:
        reindex_file(conn, p)
    return p


def init_session(
    project: str,
    *,
    force: bool = False,
    conn: sqlite3.Connection | None = None,
) -> tuple[dict, bool]:
    """Create a fresh session-state.  Returns (data, created).

    If *force* is False and a file already exists, returns the existing data
    with ``created=False``.
    """
    p = session_path(project)
    if p.exists() and not force:
        return load_session(project) or {}, False  # type: ignore[return-value]
    data = build_session_template(project)
    save_session(project, data, conn)
    return data, True


# ---------------------------------------------------------------------------
# Migration v1/v2 → v3
# ---------------------------------------------------------------------------

def _migrate(data: dict, project: str) -> dict:
    """Upgrade v1 / v2 session-state to v3 in-place."""
    ver = str(data.get("schema_version", "1.0"))
    if ver.startswith("3"):
        return data

    # Ensure all step keys exist
    steps = data.setdefault("steps", {})
    from .config import STEP_META

    for key in VALID_STEPS:
        if key not in steps:
            meta = STEP_META[key]
            steps[key] = {
                "name": meta["name"],
                "agent": meta["agent"],
                "status": "pending",
                "started": None,
                "completed": None,
                "artifacts": [],
            }

    # Promote missing top-level fields
    data.setdefault("decision_log", [])
    data.setdefault("open_findings", [])
    data.setdefault("review_audit", {})
    data.setdefault("decisions", {
        "region": data.get("region", ""),
        "compliance": "",
        "budget": "",
        "architecture_pattern": "",
        "deployment_strategy": "",
        "complexity": "",
    })
    data["schema_version"] = SESSION_STATE_VERSION
    return data


# ---------------------------------------------------------------------------
# Step helpers
# ---------------------------------------------------------------------------

def set_step_status(
    data: dict,
    step: str,
    status: str,
    *,
    force: bool = False,
) -> dict:
    """Transition a step to *status*.

    Raises ValueError on invalid step or illegal transition (unless *force*).
    """
    if step not in VALID_STEPS:
        raise ValueError(f"Invalid step: {step!r}. Valid: {VALID_STEPS}")

    entry: dict[str, Any] = data["steps"][step]
    current = entry["status"]

    # Transition guards
    if status == "in_progress":
        if current == "in_progress" and not force:
            raise ValueError(
                f"Step {step!r} is already in_progress (use --force to override)"
            )
        if current == "complete" and not force:
            raise ValueError(
                f"Step {step!r} is already complete (use --force to override)"
            )
        entry["status"] = "in_progress"
        entry["started"] = now_iso()
        from .config import STEP_KEY_TO_INT
        data["current_step"] = STEP_KEY_TO_INT[step]

    elif status == "complete":
        entry["status"] = "complete"
        entry["completed"] = now_iso()

    elif status == "skipped":
        entry["status"] = "skipped"
        entry["completed"] = now_iso()

    else:
        entry["status"] = status

    return data


def add_checkpoint(
    data: dict,
    step: str,
    sub_step: str,
    artifact: str | None = None,
) -> dict:
    """Record a sub-step checkpoint under a step."""
    if step not in VALID_STEPS:
        raise ValueError(f"Invalid step: {step!r}")

    entry = data["steps"][step]
    checkpoints: list[dict] = entry.setdefault("checkpoints", [])
    cp: dict[str, Any] = {"sub_step": sub_step, "timestamp": now_iso()}
    if artifact:
        cp["artifact"] = artifact
        arts: list[str] = entry.setdefault("artifacts", [])
        if artifact not in arts:
            arts.append(artifact)
    checkpoints.append(cp)
    return data
