"""start-step — Mark a step as in_progress."""

from __future__ import annotations

import argparse
import json

from ..config import VALID_STEPS
from ..indexer import ensure_fresh
from ..state_writer import load_session, save_session, set_step_status


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("start-step", help="Mark a step as in_progress")
    p.add_argument("project", help="Project name")
    p.add_argument("step", choices=VALID_STEPS, help="Step key")
    p.add_argument("--force", action="store_true", help="Override status guards")
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

    try:
        set_step_status(data, args.step, "in_progress", force=args.force)
    except ValueError as exc:
        if args.as_json:
            print(json.dumps({"error": str(exc)}))
        else:
            print(f"Error: {exc}")
        return 1

    save_session(args.project, data, conn)

    if args.as_json:
        print(json.dumps({"project": args.project, "step": args.step, "status": "in_progress"}))
    else:
        print(f"Step {args.step} → in_progress for {args.project!r}.")
    return 0
