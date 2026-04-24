"""show — Full context dump for one project."""

from __future__ import annotations

import argparse
import json

from ..indexer import ensure_fresh
from ..state_writer import load_estate, load_session
from ..types import fmt_json


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("show", help="Full context dump for a project")
    p.add_argument("project", help="Project name (directory under agent-output/)")
    p.add_argument("--json", dest="as_json", action="store_true", help="JSON output")


def run(args: argparse.Namespace) -> int:
    conn = ensure_fresh()

    session = load_session(args.project)
    estate = load_estate(args.project)

    rows = conn.execute(
        "SELECT path, kind, mtime, size FROM artifacts WHERE project = ? ORDER BY mtime DESC",
        (args.project,),
    ).fetchall()

    artifacts = [
        {"path": r["path"], "kind": r["kind"], "mtime": r["mtime"], "size": r["size"]}
        for r in rows
    ]

    result: dict = {
        "project": args.project,
        "session_state": session,
        "estate_state": estate,
        "artifacts": artifacts,
    }

    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n=== Project: {args.project} ===\n")

        if estate:
            print("--- Estate State ---")
            prefix = estate.get("estate", {}).get("prefix", "?")
            region = estate.get("estate", {}).get("primary_region", "?")
            print(f"  prefix={prefix}  region={region}")
            plzs = estate.get("platform_landing_zones", {})
            for name, lz in plzs.items():
                print(f"    {name}: {lz.get('status', '?')}")
            print()

        if session:
            print("--- Session State ---")
            print(f"  version={session.get('schema_version', '?')}"
                  f"  step={session.get('current_step', '?')}"
                  f"  updated={session.get('updated', '?')}")
            steps = session.get("steps", {})
            for key, entry in steps.items():
                status = entry.get("status", "?")
                name = entry.get("name", "?")
                marker = "✓" if status == "complete" else ("▸" if status == "in_progress" else "○")
                print(f"    {marker} [{key:>3s}] {name:20s}  {status}")

            findings = session.get("open_findings", [])
            if findings:
                print(f"\n  Open findings ({len(findings)}):")
                for f in findings:
                    print(f"    - {f}")

            decisions = session.get("decisions", {})
            if decisions:
                print("\n  Decisions:")
                for k, v in decisions.items():
                    if v:
                        print(f"    {k}: {v}")
            print()
        else:
            print("  (no session state found)\n")

        if artifacts:
            print(f"--- Artifacts ({len(artifacts)}) ---")
            for a in artifacts[:30]:
                print(f"  {a['kind']:20s}  {a['path']}")
            if len(artifacts) > 30:
                print(f"  ... and {len(artifacts) - 30} more")
        else:
            print("  (no indexed artifacts)")
        print()

    return 0
