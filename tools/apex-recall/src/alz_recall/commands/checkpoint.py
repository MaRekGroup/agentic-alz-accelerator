"""checkpoint — Record a sub-step checkpoint."""

from __future__ import annotations

import argparse
import json

from ..config import VALID_STEPS
from ..indexer import ensure_fresh
from ..state_writer import add_checkpoint, load_session, save_session


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("checkpoint", help="Record a sub-step checkpoint")
    p.add_argument("project", help="Project name")
    p.add_argument("step", choices=VALID_STEPS, help="Step key")
    p.add_argument("sub_step", help="Sub-step label")
    p.add_argument("--artifact", default=None, help="Artifact path to attach")
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
        add_checkpoint(data, args.step, args.sub_step, args.artifact)
    except ValueError as exc:
        if args.as_json:
            print(json.dumps({"error": str(exc)}))
        else:
            print(f"Error: {exc}")
        return 1

    save_session(args.project, data, conn)

    result = {
        "project": args.project,
        "step": args.step,
        "sub_step": args.sub_step,
        "artifact": args.artifact,
    }

    if args.as_json:
        print(json.dumps(result))
    else:
        art = f" (artifact: {args.artifact})" if args.artifact else ""
        print(f"Checkpoint {args.sub_step!r} on step {args.step} for {args.project!r}{art}.")
    return 0
