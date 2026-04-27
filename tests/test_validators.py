"""Tests for scripts/validators/ — validate against the real repo structure."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


def _load_validator(name: str):
    """Import a validator module from scripts/validators/."""
    path = Path(__file__).resolve().parent.parent / "scripts" / "validators" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


# ---------------------------------------------------------------------------
# TestJsonSchemaValidator
# ---------------------------------------------------------------------------


class TestJsonSchemaValidator:
    def test_passes(self):
        mod = _load_validator("validate_json_schemas")
        assert mod.main() == 0


# ---------------------------------------------------------------------------
# TestAgentValidator
# ---------------------------------------------------------------------------


class TestAgentValidator:
    def test_passes(self):
        mod = _load_validator("validate_agents")
        assert mod.main() == 0


# ---------------------------------------------------------------------------
# TestSkillValidator
# ---------------------------------------------------------------------------


class TestSkillValidator:
    def test_passes(self):
        mod = _load_validator("validate_skills")
        assert mod.main() == 0


# ---------------------------------------------------------------------------
# TestCountManifestValidator
# ---------------------------------------------------------------------------


class TestCountManifestValidator:
    def test_passes(self):
        mod = _load_validator("validate_count_manifest")
        assert mod.main() == 0
