"""search — Full-text search via FTS5."""

from __future__ import annotations

import argparse
import json

from ..indexer import ensure_fresh


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("search", help="Full-text search across artifacts")
    p.add_argument("term", help="Search term (FTS5 syntax supported)")
    p.add_argument("--project", default=None, help="Limit to a project")
    p.add_argument("--days", type=int, default=0, help="Look-back window (0 = all)")
    p.add_argument("--json", dest="as_json", action="store_true", help="JSON output")


def run(args: argparse.Namespace) -> int:
    conn = ensure_fresh()

    query = "SELECT project, path, kind, rank FROM artifacts_fts WHERE artifacts_fts MATCH ?"
    params: list = [args.term]

    if args.project:
        query += " AND project = ?"
        params.append(args.project)

    query += " ORDER BY rank LIMIT 50"

    rows = conn.execute(query, params).fetchall()

    results = [
        {"project": r["project"], "path": r["path"], "kind": r["kind"], "rank": r["rank"]}
        for r in rows
    ]

    if args.as_json:
        print(json.dumps(results, indent=2))
    else:
        if not results:
            print(f"No results for {args.term!r}.")
            return 0
        for r in results:
            print(f"  [{r['kind']:20s}]  {r['path']}")
    return 0
