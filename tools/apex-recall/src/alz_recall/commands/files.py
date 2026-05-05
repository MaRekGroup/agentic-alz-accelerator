"""files — List recently modified artifact files from the index."""

from __future__ import annotations

import argparse
import json
import time

from ..indexer import ensure_fresh


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("files", help="List recently modified artifact files")
    p.add_argument("--limit", type=int, default=20, help="Max results")
    p.add_argument("--days", type=int, default=7, help="Look-back window in days")
    p.add_argument("--json", dest="as_json", action="store_true", help="JSON output")


def run(args: argparse.Namespace) -> int:
    conn = ensure_fresh()
    cutoff = time.time() - args.days * 86400
    rows = conn.execute(
        "SELECT project, path, kind, mtime, size FROM artifacts "
        "WHERE mtime >= ? ORDER BY mtime DESC LIMIT ?",
        (cutoff, args.limit),
    ).fetchall()

    results = [
        {
            "project": r["project"],
            "path": r["path"],
            "kind": r["kind"],
            "mtime": r["mtime"],
            "size": r["size"],
        }
        for r in rows
    ]

    if args.as_json:
        print(json.dumps(results, indent=2))
    else:
        if not results:
            print(f"No artifacts found in the last {args.days} day(s).")
            return 0
        for r in results:
            ts = time.strftime("%Y-%m-%d %H:%M", time.localtime(r["mtime"]))
            print(f"  {ts}  {r['kind']:20s}  {r['path']}")
    return 0
