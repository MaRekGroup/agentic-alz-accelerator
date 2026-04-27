"""Pytest shared setup for repository tests."""

from __future__ import annotations

import sys
from pathlib import Path


# Make alz_recall package importable in CI without editable install.
_ALZ_RECALL_SRC = Path(__file__).resolve().parent.parent / "tools" / "apex-recall" / "src"
if _ALZ_RECALL_SRC.exists():
    sys.path.insert(0, str(_ALZ_RECALL_SRC))
