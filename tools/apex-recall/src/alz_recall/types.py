"""Shared type aliases and small helpers (stdlib only)."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Atomic JSON write with .tmp → rename → .bak
# ---------------------------------------------------------------------------

def atomic_write_json(path: Path, data: Any, *, indent: int = 2) -> None:
    """Write *data* as JSON to *path* atomically.

    Steps:
        1. Write to a temporary file in the same directory.
        2. If *path* exists, rename it to ``path.with_suffix('.bak')``.
        3. Rename the temporary file to *path*.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(
        dir=path.parent, prefix=path.stem, suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=indent, ensure_ascii=False)
            fh.write("\n")
        # Backup existing file
        bak = path.with_suffix(path.suffix + ".bak")
        if path.exists():
            shutil.copy2(path, bak)
        os.replace(tmp_path, path)
    except BaseException:
        # Clean up temp file on any failure
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def read_json(path: Path) -> Any:
    """Read and return parsed JSON from *path*."""
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def fmt_json(data: Any) -> str:
    """Return compact pretty-printed JSON."""
    return json.dumps(data, indent=2, ensure_ascii=False)
