#!/usr/bin/env python3
"""Check documentation freshness against source file timestamps.

Flags documentation files that are significantly older than the source
files they describe. Useful for catching stale docs after code changes.

Usage:
    python tools/scripts/check-docs-freshness.py
    python tools/scripts/check-docs-freshness.py --max-age-days 14
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Mapping: doc file → source files/dirs it documents
DOC_SOURCE_MAP: list[tuple[str, list[str]]] = [
    ("docs/security-baseline.md", [
        "scripts/validators/validate_security_baseline.py",
        ".github/skills/security-baseline/SKILL.md",
    ]),
    ("docs/cost-governance.md", [
        "scripts/validators/validate_cost_governance.py",
        ".github/skills/cost-governance/SKILL.md",
    ]),
    ("docs/platform-landing-zones.md", [
        "pipelines/github-actions/2-platform-deploy.yml",
        "pipelines/github-actions/reusable-deploy.yml",
    ]),
    ("docs/workflow.md", [
        ".github/skills/workflow-engine/templates/workflow-graph.json",
        ".github/agent-registry.json",
    ]),
    ("docs/session-state.md", [
        "tools/apex-recall/src/alz_recall/state_writer.py",
        "tools/apex-recall/src/alz_recall/config.py",
    ]),
]


def _mtime(path: Path) -> float:
    """Return mtime or 0 if file doesn't exist."""
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def main() -> int:
    max_age_days = 30
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--max-age-days" and i < len(sys.argv) - 1:
            max_age_days = int(sys.argv[i + 1])

    warnings: list[str] = []
    checked = 0

    for doc_rel, source_rels in DOC_SOURCE_MAP:
        doc_path = REPO_ROOT / doc_rel
        if not doc_path.exists():
            continue

        doc_mtime = _mtime(doc_path)
        checked += 1

        for src_rel in source_rels:
            src_path = REPO_ROOT / src_rel
            src_mtime = _mtime(src_path)
            if src_mtime == 0:
                continue

            age_days = (src_mtime - doc_mtime) / 86400
            if age_days > max_age_days:
                warnings.append(
                    f"  {doc_rel} is {age_days:.0f}d older than {src_rel}"
                )

    print(f"Checked {checked} doc→source mappings (max age: {max_age_days}d)")

    if warnings:
        print(f"\n{len(warnings)} stale doc(s):")
        for w in warnings:
            print(w)
        return 1

    print("All docs are fresh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
