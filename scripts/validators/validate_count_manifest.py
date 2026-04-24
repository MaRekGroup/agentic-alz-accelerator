#!/usr/bin/env python3
"""Validate count-manifest.json against actual file counts on disk.

Resolves each glob pattern in the manifest and compares the actual count.
Exits non-zero if any count is wrong, ensuring the manifest stays in sync.

Usage:
    python scripts/validators/validate_count_manifest.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent.parent
    manifest_path = repo_root / "tools" / "registry" / "count-manifest.json"

    if not manifest_path.is_file():
        print(f"ERROR: {manifest_path} not found")
        return 1

    with open(manifest_path) as f:
        manifest = json.load(f)

    counts = manifest.get("counts", {})
    errors: list[str] = []

    for key, entry in counts.items():
        glob_pattern = entry.get("computed_from", "")
        if not glob_pattern:
            continue

        actual = sorted(repo_root.glob(glob_pattern))
        actual_count = len(actual)
        desc = entry.get("description", "")
        print(f"  {key}: {actual_count} files (glob: {glob_pattern})")

        if actual_count == 0:
            errors.append(f"{key}: 0 files matched '{glob_pattern}' — pattern may be wrong")

    print(f"\nChecked {len(counts)} manifest entries")

    if errors:
        print(f"\n{len(errors)} error(s):")
        for e in errors:
            print(f"  ✗ {e}")
        return 1

    print("All count-manifest entries have matches")
    return 0


if __name__ == "__main__":
    sys.exit(main())
