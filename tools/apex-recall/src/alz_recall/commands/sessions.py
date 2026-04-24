"""sessions — List session states across projects."""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from ..config import AGENT_OUTPUT_DIR
from ..state_writer import load_session


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("sessions", help="List session states across projects")
    p.add_argument("--limit", type=int, default=20, help="Max results")
    p.add_argument("--days", type=int, default=30, help="Look-back window in days")
    p.add_argument("--json", dest="as_json", action="store_true", help="JSON output")


def run(args: argparse.Namespace) -> int:
    ao = Path(AGENT_OUTPUT_DIR)
    if not ao.is_dir():
        if args.as_json:
            print(json.dumps([]))
        else:
            print("No agent-output/ directory found.")
        return 0

    cutoff = time.time() - args.days * 86400
    sessions: list[dict] = []

    for project_dir in sorted(ao.iterdir()):
        if not project_dir.is_dir():
            continue
        # Check top-level and sub-directories for session states
        for root, _dirs, files in os.walk(project_dir):
            if "00-session-state.json" in files:
                fp = Path(root) / "00-session-state.json"
                try:
                    if fp.stat().st_mtime < cutoff:
                        continue
                except OSError:
                    continue
                # Derive project from the relative path
                rel = fp.relative_to(ao)
                proj_name = str(rel.parent)
                data = load_session(proj_name)
                if data is None:
                    continue
                sessions.append({
                    "project": proj_name,
                    "path": str(fp),
                    "schema_version": data.get("schema_version", "?"),
                    "current_step": data.get("current_step", -1),
                    "updated": data.get("updated", ""),
                    "landing_zone": data.get("landing_zone", ""),
                })
        if len(sessions) >= args.limit:
            break

    sessions = sessions[: args.limit]

    if args.as_json:
        print(json.dumps(sessions, indent=2))
    else:
        if not sessions:
            print("No session states found in the last {} day(s).".format(args.days))
            return 0
        for s in sessions:
            step = s["current_step"]
            print(f"  step={step:<4}  v{s['schema_version']}  {s['project']:40s}  {s['updated']}")
    return 0
