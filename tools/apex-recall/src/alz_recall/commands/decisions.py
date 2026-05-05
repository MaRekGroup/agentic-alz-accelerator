"""decisions — Query decision logs across projects."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..config import AGENT_OUTPUT_DIR
from ..state_writer import load_session


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("decisions", help="Query decision logs across projects")
    p.add_argument("--project", default=None, help="Limit to a project")
    p.add_argument("--json", dest="as_json", action="store_true", help="JSON output")


def run(args: argparse.Namespace) -> int:
    ao = Path(AGENT_OUTPUT_DIR)
    if not ao.is_dir():
        if args.as_json:
            print(json.dumps([]))
        else:
            print("No agent-output/ directory found.")
        return 0

    results: list[dict] = []

    projects: list[str] = []
    if args.project:
        projects = [args.project]
    else:
        for d in sorted(ao.iterdir()):
            if d.is_dir():
                projects.append(d.name)
                # Also check sub-dirs for per-LZ sessions
                for sub in d.iterdir():
                    if sub.is_dir():
                        projects.append(f"{d.name}/{sub.name}")

    for proj in projects:
        data = load_session(proj)
        if data is None:
            continue

        decisions_obj = data.get("decisions", {})
        decision_log = data.get("decision_log", [])

        entry: dict = {
            "project": proj,
            "decisions": decisions_obj,
            "decision_log": decision_log,
        }
        results.append(entry)

    if args.as_json:
        print(json.dumps(results, indent=2))
    else:
        if not results:
            print("No decisions found.")
            return 0
        for entry in results:
            print(f"\n--- {entry['project']} ---")
            decs = entry["decisions"]
            for k, v in decs.items():
                if v:
                    print(f"  {k}: {v}")
            log = entry["decision_log"]
            if log:
                print(f"  Decision log ({len(log)} entries):")
                for item in log:
                    step = item.get("step", "?")
                    decision = item.get("decision", "?")
                    print(f"    [{step}] {decision}")
        print()

    return 0
