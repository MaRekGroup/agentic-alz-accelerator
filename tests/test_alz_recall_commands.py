"""Tests for alz-recall read commands (files, sessions, search, show, decisions, reindex, health, version)."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from alz_recall.__main__ import main


def _run(argv: list[str], capsys: pytest.CaptureFixture[str]) -> tuple[int, str]:
    rc = main(argv)
    out = capsys.readouterr().out
    return rc, out


@pytest.fixture(autouse=True)
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    ao = tmp_path / "agent-output"
    ao.mkdir()
    db = tmp_path / "tmp" / ".alz-recall.db"

    # Monkeypatch in all modules that import these
    monkeypatch.setattr("alz_recall.indexer.AGENT_OUTPUT_DIR", str(ao))
    monkeypatch.setattr("alz_recall.indexer.DB_PATH", db)
    monkeypatch.setattr("alz_recall.config.AGENT_OUTPUT_DIR", str(ao))
    monkeypatch.setattr("alz_recall.config.DB_PATH", db)
    monkeypatch.setattr("alz_recall.state_writer.AGENT_OUTPUT_DIR", str(ao))
    monkeypatch.setattr("alz_recall.commands.sessions.AGENT_OUTPUT_DIR", str(ao))
    monkeypatch.setattr("alz_recall.commands.decisions.AGENT_OUTPUT_DIR", str(ao))
    monkeypatch.setattr("alz_recall.commands.health.DB_PATH", db)

    proj = ao / "demo"
    proj.mkdir()

    session = {
        "schema_version": "3.0",
        "project": "demo",
        "landing_zone": "",
        "iac_tool": "Bicep",
        "region": "southcentralus",
        "branch": "main",
        "updated": "2026-04-20T15:00:00Z",
        "current_step": 2,
        "decisions": {
            "region": "southcentralus",
            "compliance": "NIST",
            "budget": "medium",
            "architecture_pattern": "hub-spoke",
            "deployment_strategy": "phased",
            "complexity": "standard",
        },
        "decision_log": [
            {
                "step": "1",
                "decision": "Use hub-spoke",
                "rationale": "Isolation",
                "timestamp": "2026-04-20T10:00:00Z",
            }
        ],
        "open_findings": [],
        "review_audit": {},
        "steps": {
            k: {
                "name": "s",
                "agent": "a",
                "status": "pending",
                "started": None,
                "completed": None,
                "artifacts": [],
            }
            for k in ["0", "1", "2", "3", "3_5", "4", "5", "6", "7", "8", "9"]
        },
    }
    session["steps"]["1"]["status"] = "complete"
    session["steps"]["2"]["status"] = "in_progress"
    (proj / "00-session-state.json").write_text(json.dumps(session))
    (proj / "01-requirements.md").write_text("# Requirements\nHub-spoke network.\n")
    (proj / "02-architecture-assessment.md").write_text("# Architecture\nWAF pillars.\n")
    (proj / "04-implementation-plan.md").write_text("# Implementation\nPhase 1.\n")

    from alz_recall.indexer import ensure_db, reindex

    conn = ensure_db()
    reindex(conn)
    conn.close()

    monkeypatch.chdir(tmp_path)
    return tmp_path


# ---------------------------------------------------------------------------
# TestFiles
# ---------------------------------------------------------------------------


class TestFiles:
    def test_json_output(self, capsys: pytest.CaptureFixture[str]):
        rc, out = _run(["files", "--json", "--days", "9999"], capsys)
        assert rc == 0
        data = json.loads(out)
        assert isinstance(data, list)
        assert len(data) >= 4

    def test_text_output(self, capsys: pytest.CaptureFixture[str]):
        rc, out = _run(["files", "--days", "9999"], capsys)
        assert rc == 0
        assert "requirements" in out or "session-state" in out


# ---------------------------------------------------------------------------
# TestSessions
# ---------------------------------------------------------------------------


class TestSessions:
    def test_json_output(self, capsys: pytest.CaptureFixture[str]):
        rc, out = _run(["sessions", "--json", "--days", "9999"], capsys)
        assert rc == 0
        data = json.loads(out)
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["project"] == "demo"

    def test_text_output(self, capsys: pytest.CaptureFixture[str]):
        rc, out = _run(["sessions", "--days", "9999"], capsys)
        assert rc == 0
        assert "demo" in out


# ---------------------------------------------------------------------------
# TestSearch
# ---------------------------------------------------------------------------


class TestSearch:
    def test_found(self, capsys: pytest.CaptureFixture[str]):
        rc, out = _run(["search", "Requirements", "--json"], capsys)
        assert rc == 0
        data = json.loads(out)
        assert len(data) >= 1

    def test_not_found(self, capsys: pytest.CaptureFixture[str]):
        rc, out = _run(["search", "xyznonexistent"], capsys)
        assert rc == 0
        assert "No results" in out

    def test_project_filter(self, capsys: pytest.CaptureFixture[str]):
        rc, out = _run(["search", "WAF", "--project", "demo", "--json"], capsys)
        assert rc == 0
        data = json.loads(out)
        for item in data:
            assert item["project"] == "demo"


# ---------------------------------------------------------------------------
# TestShow
# ---------------------------------------------------------------------------


class TestShow:
    def test_json_output(self, capsys: pytest.CaptureFixture[str]):
        rc, out = _run(["show", "demo", "--json"], capsys)
        assert rc == 0
        data = json.loads(out)
        assert data["project"] == "demo"
        assert data["session_state"] is not None
        assert isinstance(data["artifacts"], list)

    def test_text_output(self, capsys: pytest.CaptureFixture[str]):
        rc, out = _run(["show", "demo"], capsys)
        assert rc == 0
        assert "demo" in out

    def test_nonexistent_project(self, capsys: pytest.CaptureFixture[str]):
        rc, out = _run(["show", "nope", "--json"], capsys)
        assert rc == 0
        data = json.loads(out)
        assert data["session_state"] is None


# ---------------------------------------------------------------------------
# TestDecisions
# ---------------------------------------------------------------------------


class TestDecisions:
    def test_json_output(self, capsys: pytest.CaptureFixture[str]):
        rc, out = _run(["decisions", "--json"], capsys)
        assert rc == 0
        data = json.loads(out)
        assert isinstance(data, list)
        assert any(d["project"] == "demo" for d in data)

    def test_project_filter(self, capsys: pytest.CaptureFixture[str]):
        rc, out = _run(["decisions", "--project", "demo", "--json"], capsys)
        assert rc == 0
        data = json.loads(out)
        assert len(data) == 1
        assert data[0]["decisions"]["compliance"] == "NIST"


# ---------------------------------------------------------------------------
# TestReindex
# ---------------------------------------------------------------------------


class TestReindex:
    def test_json_output(self, capsys: pytest.CaptureFixture[str]):
        rc, out = _run(["reindex", "--json"], capsys)
        assert rc == 0
        data = json.loads(out)
        assert "indexed" in data
        assert data["indexed"] >= 4


# ---------------------------------------------------------------------------
# TestHealth
# ---------------------------------------------------------------------------


class TestHealth:
    def test_json_output(self, capsys: pytest.CaptureFixture[str]):
        rc, out = _run(["health", "--json"], capsys)
        assert rc == 0
        data = json.loads(out)
        assert data["db_exists"] is True
        assert data["total_artifacts"] >= 4

    def test_text_output(self, capsys: pytest.CaptureFixture[str]):
        rc, out = _run(["health"], capsys)
        assert rc == 0
        assert "Artifacts" in out


# ---------------------------------------------------------------------------
# TestVersion
# ---------------------------------------------------------------------------


class TestVersion:
    def test_version_flag(self, capsys: pytest.CaptureFixture[str]):
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])
        assert exc_info.value.code == 0
        out = capsys.readouterr().out
        assert "alz-recall" in out

    def test_help_flag(self, capsys: pytest.CaptureFixture[str]):
        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])
        assert exc_info.value.code == 0

    def test_no_args(self, capsys: pytest.CaptureFixture[str]):
        rc, out = _run([], capsys)
        assert rc == 0
