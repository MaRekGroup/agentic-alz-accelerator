#!/usr/bin/env python3
"""Validate JSON files against their $schema references.

Scans for JSON files with a $schema property pointing to a local schema file
and validates them using jsonschema. Exits non-zero if any file fails.

Usage:
    python scripts/validators/validate_json_schemas.py [paths...]
    python scripts/validators/validate_json_schemas.py  # scans default locations
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def find_schema_path(json_file: Path, schema_ref: str) -> Path | None:
    """Resolve a $schema reference to a local file path."""
    if schema_ref.startswith(("http://", "https://")):
        return None  # skip remote schemas

    candidate = json_file.parent / schema_ref
    if candidate.is_file():
        return candidate.resolve()

    # Try from repo root
    repo_root = Path(__file__).resolve().parent.parent.parent
    candidate = repo_root / schema_ref
    if candidate.is_file():
        return candidate.resolve()

    return None


def validate_file(json_file: Path, *, verbose: bool = False) -> list[str]:
    """Validate a single JSON file against its $schema. Returns list of errors."""
    errors: list[str] = []

    try:
        with open(json_file) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"{json_file}: invalid JSON — {e}"]

    if not isinstance(data, dict):
        return []  # arrays and primitives have no $schema

    schema_ref = data.get("$schema")
    if not schema_ref:
        return []  # no schema reference — skip

    schema_path = find_schema_path(json_file, schema_ref)
    if schema_path is None:
        if verbose:
            print(f"  skip {json_file} (remote or missing schema: {schema_ref})")
        return []

    try:
        with open(schema_path) as f:
            schema = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        return [f"{json_file}: cannot load schema {schema_path} — {e}"]

    try:
        import jsonschema
        jsonschema.validate(instance=data, schema=schema)
    except ImportError:
        # Fallback: structural checks only (required keys)
        required = schema.get("required", [])
        missing = [k for k in required if k not in data]
        if missing:
            errors.append(f"{json_file}: missing required keys: {missing}")
    except jsonschema.ValidationError as e:
        errors.append(f"{json_file}: schema violation — {e.message}")
        if e.absolute_path:
            errors[-1] += f" (at $.{'.'.join(str(p) for p in e.absolute_path)})"

    return errors


def find_json_files(paths: list[Path]) -> list[Path]:
    """Find all JSON files in the given paths."""
    files: list[Path] = []
    for p in paths:
        if p.is_file() and p.suffix == ".json":
            files.append(p)
        elif p.is_dir():
            files.extend(sorted(p.rglob("*.json")))
    return files


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent.parent

    if len(sys.argv) > 1:
        search_paths = [Path(a) for a in sys.argv[1:]]
    else:
        search_paths = [
            repo_root / ".github",
            repo_root / "tools",
            repo_root / "agent-output",
        ]

    json_files = find_json_files(search_paths)
    if not json_files:
        print("No JSON files found")
        return 0

    all_errors: list[str] = []
    validated = 0

    for jf in json_files:
        try:
            with open(jf) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            all_errors.append(f"{jf}: cannot parse")
            continue

        if not isinstance(data, dict) or "$schema" not in data:
            continue

        schema_ref = data["$schema"]
        schema_path = find_schema_path(jf, schema_ref)
        if schema_path is None:
            continue

        errors = validate_file(jf, verbose=True)
        all_errors.extend(errors)
        validated += 1
        status = "FAIL" if errors else "OK"
        print(f"  {status}  {jf.relative_to(repo_root)}")

    print(f"\nValidated {validated} files against schemas")

    if all_errors:
        print(f"\n{len(all_errors)} error(s):")
        for e in all_errors:
            print(f"  ✗ {e}")
        return 1

    print("All schema validations passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
