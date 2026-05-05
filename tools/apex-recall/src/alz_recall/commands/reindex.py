"""reindex — Force rebuild of the index."""

from __future__ import annotations

import argparse
import json

from ..indexer import ensure_db
from ..indexer import reindex as do_reindex


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("reindex", help="Force rebuild of the index")
    p.add_argument("--json", dest="as_json", action="store_true", help="JSON output")


def run(args: argparse.Namespace) -> int:
    conn = ensure_db()
    result = do_reindex(conn)

    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Reindexed {result['indexed']} artifacts.")
    return 0
