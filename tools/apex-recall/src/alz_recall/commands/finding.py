"""finding — Manage open_findings."""

from __future__ import annotations

import argparse
import json

from ..indexer import ensure_fresh
from ..state_writer import load_session, save_session


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("finding", help="Manage open findings")
    p.add_argument("project", help="Project name")
    p.add_argument("--add", default=None, help="Finding text to add")
    p.add_argument("--remove", default=None, help="Finding text to remove (exact match)")
    p.add_argument("--json", dest="as_json", action="store_true", help="JSON output")


def run(args: argparse.Namespace) -> int:
    conn = ensure_fresh()
    data = load_session(args.project)
    if data is None:
        msg = f"No session state for {args.project!r}. Run 'init' first."
        if args.as_json:
            print(json.dumps({"error": msg}))
        else:
            print(msg)
        return 1

    findings: list[str] = data.setdefault("open_findings", [])

    if args.add:
        if args.add not in findings:
            findings.append(args.add)
        action = "added"
        detail = args.add
    elif args.remove:
        if args.remove in findings:
            findings.remove(args.remove)
            action = "removed"
        else:
            action = "not_found"
        detail = args.remove
    else:
        # List mode
        if args.as_json:
            print(json.dumps({"project": args.project, "open_findings": findings}))
        else:
            if findings:
                print(f"Open findings for {args.project!r}:")
                for f in findings:
                    print(f"  - {f}")
            else:
                print(f"No open findings for {args.project!r}.")
        return 0

    save_session(args.project, data, conn)

    result = {
        "project": args.project,
        "action": action,
        "finding": detail,
        "open_findings": findings,
    }

    if args.as_json:
        print(json.dumps(result))
    else:
        if action == "not_found":
            print(f"Finding not found: {detail!r}")
        else:
            print(f"Finding {action}: {detail!r}")
    return 0
