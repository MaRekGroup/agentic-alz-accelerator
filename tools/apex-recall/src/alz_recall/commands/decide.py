"""decide — Record a decision (Mode A: decisions object, Mode B: decision_log)."""

from __future__ import annotations

import argparse
import json

from ..indexer import ensure_fresh
from ..state_writer import load_session, save_session
from ..types import now_iso


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("decide", help="Record a decision")
    p.add_argument("project", help="Project name")
    # Mode A: key/value into decisions object
    p.add_argument("--key", default=None, help="Decision key (Mode A)")
    p.add_argument("--value", default=None, help="Decision value (Mode A)")
    # Mode B: append to decision_log
    p.add_argument("--decision", default=None, help="Decision text (Mode B)")
    p.add_argument("--rationale", default=None, help="Rationale text (Mode B)")
    p.add_argument("--step", default=None, help="Step context (Mode B)")
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

    mode_a = args.key is not None and args.value is not None
    mode_b = args.decision is not None

    if not mode_a and not mode_b:
        msg = "Provide --key + --value (Mode A) or --decision + --rationale + --step (Mode B)."
        if args.as_json:
            print(json.dumps({"error": msg}))
        else:
            print(f"Error: {msg}")
        return 1

    if mode_a:
        data.setdefault("decisions", {})[args.key] = args.value
        result = {"mode": "A", "key": args.key, "value": args.value}
    else:
        entry = {
            "decision": args.decision,
            "rationale": args.rationale or "",
            "step": args.step or "",
            "timestamp": now_iso(),
        }
        data.setdefault("decision_log", []).append(entry)
        result = {"mode": "B", "entry": entry}

    save_session(args.project, data, conn)

    if args.as_json:
        print(json.dumps({"project": args.project, **result}))
    else:
        if mode_a:
            print(f"Decision {args.key}={args.value} recorded for {args.project!r}.")
        else:
            print(f"Decision logged for {args.project!r}: {args.decision}")
    return 0
