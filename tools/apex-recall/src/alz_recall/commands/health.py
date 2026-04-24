"""health — Health dashboard for the index database."""

from __future__ import annotations

import argparse
import json
import time

from ..config import DB_PATH
from ..indexer import ensure_db


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("health", help="Health dashboard")
    p.add_argument("--json", dest="as_json", action="store_true", help="JSON output")


def run(args: argparse.Namespace) -> int:
    exists = DB_PATH.exists()
    result: dict = {
        "db_exists": exists,
        "db_path": str(DB_PATH),
        "db_size_bytes": 0,
        "total_artifacts": 0,
        "last_index": None,
        "staleness_seconds": None,
    }

    if exists:
        result["db_size_bytes"] = DB_PATH.stat().st_size
        conn = ensure_db()
        row = conn.execute("SELECT COUNT(*) AS cnt FROM artifacts").fetchone()
        result["total_artifacts"] = row["cnt"]

        meta = conn.execute(
            "SELECT value FROM meta WHERE key = 'last_index'",
        ).fetchone()
        if meta:
            last = float(meta["value"])
            result["last_index"] = last
            result["staleness_seconds"] = round(time.time() - last, 1)

    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        print(f"  DB exists:    {result['db_exists']}")
        print(f"  DB path:      {result['db_path']}")
        print(f"  DB size:      {result['db_size_bytes']} bytes")
        print(f"  Artifacts:    {result['total_artifacts']}")
        staleness = result["staleness_seconds"]
        if staleness is not None:
            print(f"  Staleness:    {staleness}s")
        else:
            print("  Staleness:    (never indexed)")
    return 0
