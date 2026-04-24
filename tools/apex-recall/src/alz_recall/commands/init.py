"""init — Create fresh session-state for a project."""

from __future__ import annotations

import argparse
import json

from ..indexer import ensure_fresh
from ..state_writer import init_session


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("init", help="Create fresh session-state for a project")
    p.add_argument("project", help="Project name")
    p.add_argument("--force", action="store_true", help="Overwrite existing state")
    p.add_argument("--json", dest="as_json", action="store_true", help="JSON output")


def run(args: argparse.Namespace) -> int:
    conn = ensure_fresh()
    data, created = init_session(args.project, force=args.force, conn=conn)

    result = {"project": args.project, "created": created, "state": data}

    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        if created:
            print(f"Created session state for {args.project!r}.")
        else:
            print(f"Session state for {args.project!r} already exists (use --force to overwrite).")
    return 0
