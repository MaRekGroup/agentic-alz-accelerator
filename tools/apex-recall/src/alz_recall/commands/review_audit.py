"""review-audit — Manage review_audit entries (Challenger gate tracking)."""

from __future__ import annotations

import argparse
import json

from ..config import REVIEW_GATES
from ..indexer import ensure_fresh
from ..state_writer import load_session, save_session
from ..types import now_iso


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("review-audit", help="Manage review audit entries")
    p.add_argument("project", help="Project name")
    p.add_argument("step", choices=REVIEW_GATES, help="Gate step key")
    p.add_argument("--complexity", default=None, help="Complexity tier (simple/standard/complex)")
    p.add_argument("--passes-planned", type=int, default=None, help="Planned review passes")
    p.add_argument("--passes-executed", type=int, default=None, help="Executed review passes")
    p.add_argument("--model", default=None, help="Model used for review")
    p.add_argument("--skip", action="store_true", help="Mark gate as skipped")
    p.add_argument("--skip-reason", default=None, help="Reason for skipping")
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

    audit: dict = data.setdefault("review_audit", {})
    entry: dict = audit.setdefault(args.step, {
        "gate": args.step,
        "status": "pending",
        "complexity": "",
        "passes_planned": 0,
        "passes_executed": 0,
        "model": "",
        "reviews": [],
    })

    if args.skip:
        entry["status"] = "skipped"
        entry["skip_reason"] = args.skip_reason or ""
        entry["skipped_at"] = now_iso()
    else:
        if args.complexity is not None:
            entry["complexity"] = args.complexity
        if args.passes_planned is not None:
            entry["passes_planned"] = args.passes_planned
        if args.passes_executed is not None:
            entry["passes_executed"] = args.passes_executed
            if entry["passes_executed"] >= entry.get("passes_planned", 0) and entry["passes_planned"] > 0:
                entry["status"] = "complete"
            else:
                entry["status"] = "in_progress"
        if args.model is not None:
            entry["model"] = args.model

    entry["updated"] = now_iso()
    save_session(args.project, data, conn)

    result = {"project": args.project, "step": args.step, "audit": entry}

    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Review audit for gate {args.step} on {args.project!r}:")
        print(f"  status:          {entry.get('status', '?')}")
        print(f"  complexity:      {entry.get('complexity', '?')}")
        print(f"  passes planned:  {entry.get('passes_planned', 0)}")
        print(f"  passes executed: {entry.get('passes_executed', 0)}")
        if entry.get("model"):
            print(f"  model:           {entry['model']}")
    return 0
