#!/usr/bin/env python3
"""Run all project validators in sequence.

A single entry point for CI and local use. Runs each validator and reports
pass/fail. Exits non-zero if any validator fails.

Usage:
    python tools/scripts/validate-all.py
    python tools/scripts/validate-all.py --quick   # skip slow validators
"""

from __future__ import annotations

import importlib.util
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

VALIDATORS: list[dict[str, str]] = [
    {
        "name": "JSON Schemas",
        "path": "scripts/validators/validate_json_schemas.py",
        "tier": "quick",
    },
    {
        "name": "Agents",
        "path": "scripts/validators/validate_agents.py",
        "tier": "quick",
    },
    {
        "name": "Skills",
        "path": "scripts/validators/validate_skills.py",
        "tier": "quick",
    },
    {
        "name": "Count Manifest",
        "path": "scripts/validators/validate_count_manifest.py",
        "tier": "quick",
    },
    {
        "name": "Security Baseline",
        "path": "scripts/validators/validate_security_baseline.py",
        "tier": "full",
    },
    {
        "name": "Cost Governance",
        "path": "scripts/validators/validate_cost_governance.py",
        "tier": "full",
    },
]


def _load_and_run(validator_path: str) -> int:
    """Dynamically import a validator module and run its main()."""
    full_path = REPO_ROOT / validator_path
    if not full_path.exists():
        print(f"    SKIP — {full_path} not found")
        return 0

    spec = importlib.util.spec_from_file_location(
        full_path.stem, full_path,
    )
    if spec is None or spec.loader is None:
        print(f"    SKIP — cannot load {full_path}")
        return 0

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    main_fn = getattr(mod, "main", None)
    if main_fn is None:
        print(f"    SKIP — no main() in {full_path}")
        return 0

    # Security/cost validators take a path argument
    if validator_path.endswith(("validate_security_baseline.py", "validate_cost_governance.py")):
        sys.argv = [str(full_path), str(REPO_ROOT / "infra")]
    else:
        sys.argv = [str(full_path)]

    return main_fn()


def main() -> int:
    quick_only = "--quick" in sys.argv

    print(f"{'=' * 60}")
    print("  ALZ Accelerator — Validate All")
    print(f"  Mode: {'quick' if quick_only else 'full'}")
    print(f"{'=' * 60}\n")

    results: list[tuple[str, str, float]] = []

    for v in VALIDATORS:
        if quick_only and v["tier"] != "quick":
            continue

        print(f"▸ {v['name']}")
        t0 = time.time()
        try:
            rc = _load_and_run(v["path"])
        except SystemExit as e:
            rc = e.code or 0
        except Exception as e:
            print(f"    ERROR: {e}")
            rc = 1
        elapsed = time.time() - t0
        status = "PASS" if rc == 0 else "FAIL"
        results.append((v["name"], status, elapsed))
        print(f"  → {status} ({elapsed:.1f}s)\n")

    # Summary
    print(f"{'=' * 60}")
    print("  Results")
    print(f"{'=' * 60}")
    for name, status, elapsed in results:
        marker = "✓" if status == "PASS" else "✗"
        print(f"  {marker} {name:<25} {status:>4}  ({elapsed:.1f}s)")

    failures = sum(1 for _, s, _ in results if s == "FAIL")
    total = len(results)
    print(f"\n  {total - failures}/{total} passed", end="")
    if failures:
        print(f", {failures} failed")
    else:
        print()

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
