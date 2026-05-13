"""SQLite + FTS5 indexer for agent-output artifacts."""

from __future__ import annotations

import fnmatch
import os
import sqlite3
import time
from pathlib import Path
from typing import Any

from .config import AGENT_OUTPUT_DIR, ARTIFACT_PATTERNS, DB_PATH

# ---------------------------------------------------------------------------
# Canonical Step 7 artifact names
# Resolved before the broad "07-*.md" wildcard in ARTIFACT_PATTERNS so that
# each canonical file gets a precise, queryable kind.  Legacy names (e.g.
# 07-design-document.md) continue to fall through to the wildcard and are
# returned as "as-built" — no existing artifact becomes invisible.
# ---------------------------------------------------------------------------

_STEP7_CANONICAL: list[tuple[str, str]] = [
    ("07-technical-design-document.md", "tdd"),
    ("07-operational-runbook.md",       "runbook"),
    ("07-resource-inventory.md",        "resource-inventory"),
    ("07-compliance-summary.md",        "compliance-summary"),
    ("07-cost-baseline.md",             "cost-baseline"),
]

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS artifacts (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    project  TEXT    NOT NULL,
    path     TEXT    NOT NULL UNIQUE,
    kind     TEXT    NOT NULL DEFAULT 'unknown',
    mtime    REAL    NOT NULL,
    size     INTEGER NOT NULL DEFAULT 0,
    indexed  REAL    NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS artifacts_fts USING fts5(
    project, path, kind, body
);

CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);
"""

_INSERT_ARTIFACT = """
INSERT OR REPLACE INTO artifacts (project, path, kind, mtime, size, indexed)
VALUES (?, ?, ?, ?, ?, ?)
"""

_INSERT_FTS = """
INSERT INTO artifacts_fts (project, path, kind, body)
VALUES (?, ?, ?, ?)
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _classify(filename: str) -> str:
    """Classify an artifact filename into a recall kind.

    Canonical Step 7 names are resolved first so each file gets a precise
    kind.  All other patterns fall through to ARTIFACT_PATTERNS, which keeps
    legacy Step 7 names (e.g. 07-design-document.md) visible as "as-built".
    """
    for pattern, kind in _STEP7_CANONICAL:
        if fnmatch.fnmatch(filename, pattern):
            return kind
    for pattern, kind in ARTIFACT_PATTERNS:
        if fnmatch.fnmatch(filename, pattern):
            return kind
    return "unknown"


def _read_body(path: Path, max_bytes: int = 64_000) -> str:
    """Read the first *max_bytes* of a text file, ignoring errors."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read(max_bytes)
    except OSError:
        return ""


def _project_from_path(rel: str) -> str:
    """Extract project name from a relative path under agent-output/."""
    parts = Path(rel).parts
    # agent-output/<project>/...
    if len(parts) >= 2:
        return parts[1]
    return "unknown"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def ensure_db() -> sqlite3.Connection:
    """Open (or create) the index database and return a connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA_SQL)
    return conn


def ensure_fresh(conn: sqlite3.Connection | None = None) -> sqlite3.Connection:
    """Return a connection whose index is up-to-date.

    If any artifact file on disk is newer than the last index run we
    trigger a full reindex.
    """
    own = conn is None
    if own:
        conn = ensure_db()

    row = conn.execute(
        "SELECT value FROM meta WHERE key = 'last_index'",
    ).fetchone()
    last_ts = float(row["value"]) if row else 0.0

    needs_reindex = False
    ao = Path(AGENT_OUTPUT_DIR)
    if ao.is_dir():
        for root, _dirs, files in os.walk(ao):
            for f in files:
                fp = Path(root) / f
                try:
                    if fp.stat().st_mtime > last_ts:
                        needs_reindex = True
                        break
                except OSError:
                    continue
            if needs_reindex:
                break
    else:
        needs_reindex = True

    if needs_reindex:
        reindex(conn)

    return conn


def reindex(conn: sqlite3.Connection | None = None) -> dict[str, Any]:
    """Full reindex of agent-output/ into the database."""
    own = conn is None
    if own:
        conn = ensure_db()

    conn.execute("DELETE FROM artifacts")
    conn.execute("DELETE FROM artifacts_fts")

    count = 0
    ao = Path(AGENT_OUTPUT_DIR)
    if ao.is_dir():
        for root, _dirs, files in os.walk(ao):
            for fname in files:
                fp = Path(root) / fname
                rel = str(fp)
                project = _project_from_path(rel)
                kind = _classify(fname)
                try:
                    st = fp.stat()
                except OSError:
                    continue
                now = time.time()
                conn.execute(
                    _INSERT_ARTIFACT,
                    (project, rel, kind, st.st_mtime, st.st_size, now),
                )
                body = _read_body(fp) if fp.suffix in (".md", ".json", ".txt", ".yaml", ".yml") else ""
                conn.execute(
                    _INSERT_FTS,
                    (project, rel, kind, body),
                )
                count += 1

    now = time.time()
    conn.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES ('last_index', ?)",
        (str(now),),
    )
    conn.commit()
    return {"indexed": count, "timestamp": now}


def reindex_file(conn: sqlite3.Connection, path: Path) -> None:
    """Re-index a single file (after a write command mutates it)."""
    rel = str(path)
    project = _project_from_path(rel)
    kind = _classify(path.name)
    try:
        st = path.stat()
    except OSError:
        return
    now = time.time()

    # Remove old FTS row first
    conn.execute("DELETE FROM artifacts_fts WHERE path = ?", (rel,))

    conn.execute(_INSERT_ARTIFACT, (project, rel, kind, st.st_mtime, st.st_size, now))
    body = _read_body(path) if path.suffix in (".md", ".json", ".txt", ".yaml", ".yml") else ""
    conn.execute(_INSERT_FTS, (project, rel, kind, body))
    conn.commit()
