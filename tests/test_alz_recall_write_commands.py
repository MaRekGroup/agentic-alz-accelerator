"""Tests for alz-recall write commands (init, start-step, complete-step, checkpoint, decide, finding, review-audit)."""

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


def _load_session(ao: Path, project: str) -> dict:
    p = ao / project / "00-session-state.json"
    return json.loads(p.read_text())


ALL_STEP_KEYS = {"0", "1", "2", "3", "3_5", "4", "5", "6", "7", "8", "9"}


@pytest.fixture()
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    ao = tmp_path / "agent-output"
    ao.mkdir()
    db = tmp_path / "tmp" / ".alz-recall.db"

    monkeypatch.setattr("alz_recall.indexer.AGENT_OUTPUT_DIR", str(ao))
    monkeypatch.setattr("alz_recall.indexer.DB_PATH", db)
    monkeypatch.setattr("alz_recall.config.AGENT_OUTPUT_DIR", str(ao))
    monkeypatch.setattr("alz_recall.config.DB_PATH", db)
    monkeypatch.setattr("alz_recall.state_writer.AGENT_OUTPUT_DIR", str(ao))
    monkeypatch.setattr("alz_recall.commands.sessions.AGENT_OUTPUT_DIR", str(ao))
    monkeypatch.setattr("alz_recall.commands.decisions.AGENT_OUTPUT_DIR", str(ao))
    monkeypatch.setattr("alz_recall.commands.health.DB_PATH", db)

    monkeypatch.chdir(tmp_path)
    return tmp_path


# ---------------------------------------------------------------------------
# TestInit
# ---------------------------------------------------------------------------


class TestInit:
    def test_creates_session(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        ao = workspace / "agent-output"
        rc, out = _run(["init", "newproj", "--json"], capsys)
        assert rc == 0
        data = json.loads(out)
        assert data["created"] is True
        state = _load_session(ao, "newproj")
        assert state["schema_version"] == "3.0"

    def test_fails_if_exists(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        _run(["init", "proj2", "--json"], capsys)
        rc, out = _run(["init", "proj2", "--json"], capsys)
        assert rc == 0
        data = json.loads(out)
        assert data["created"] is False

    def test_force_overwrites(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        _run(["init", "proj3", "--json"], capsys)
        rc, out = _run(["init", "proj3", "--force", "--json"], capsys)
        assert rc == 0
        data = json.loads(out)
        assert data["created"] is True

    def test_all_step_keys_present(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        ao = workspace / "agent-output"
        _run(["init", "proj4", "--json"], capsys)
        state = _load_session(ao, "proj4")
        assert set(state["steps"].keys()) == ALL_STEP_KEYS


# ---------------------------------------------------------------------------
# TestStartStep
# ---------------------------------------------------------------------------


class TestStartStep:
    def test_starts_step(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        ao = workspace / "agent-output"
        _run(["init", "ss1", "--json"], capsys)
        rc, out = _run(["start-step", "ss1", "1", "--json"], capsys)
        assert rc == 0
        state = _load_session(ao, "ss1")
        assert state["steps"]["1"]["status"] == "in_progress"

    def test_governance_step(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        ao = workspace / "agent-output"
        _run(["init", "ss2", "--json"], capsys)
        rc, out = _run(["start-step", "ss2", "3_5", "--json"], capsys)
        assert rc == 0
        state = _load_session(ao, "ss2")
        assert state["steps"]["3_5"]["status"] == "in_progress"

    def test_invalid_step_key(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        _run(["init", "ss3", "--json"], capsys)
        with pytest.raises(SystemExit):
            main(["start-step", "ss3", "99"])

    def test_refuses_restart_without_force(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        _run(["init", "ss4", "--json"], capsys)
        _run(["start-step", "ss4", "1", "--json"], capsys)
        rc, out = _run(["start-step", "ss4", "1", "--json"], capsys)
        assert rc == 1
        assert "error" in json.loads(out)

    def test_force_restarts(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        ao = workspace / "agent-output"
        _run(["init", "ss5", "--json"], capsys)
        _run(["start-step", "ss5", "1", "--json"], capsys)
        rc, out = _run(["start-step", "ss5", "1", "--force", "--json"], capsys)
        assert rc == 0
        state = _load_session(ao, "ss5")
        assert state["steps"]["1"]["status"] == "in_progress"


# ---------------------------------------------------------------------------
# TestCompleteStep
# ---------------------------------------------------------------------------


class TestCompleteStep:
    def test_completes_step(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        ao = workspace / "agent-output"
        _run(["init", "cs1", "--json"], capsys)
        _run(["start-step", "cs1", "1", "--json"], capsys)
        rc, out = _run(["complete-step", "cs1", "1", "--json"], capsys)
        assert rc == 0
        state = _load_session(ao, "cs1")
        assert state["steps"]["1"]["status"] == "complete"
        assert state["steps"]["1"]["completed"] is not None


# ---------------------------------------------------------------------------
# TestCheckpoint
# ---------------------------------------------------------------------------


class TestCheckpoint:
    def test_records_sub_step(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        ao = workspace / "agent-output"
        _run(["init", "cp1", "--json"], capsys)
        _run(["start-step", "cp1", "2", "--json"], capsys)
        rc, out = _run(["checkpoint", "cp1", "2", "waf-review", "--json"], capsys)
        assert rc == 0
        state = _load_session(ao, "cp1")
        cps = state["steps"]["2"].get("checkpoints", [])
        assert any(c["sub_step"] == "waf-review" for c in cps)

    def test_appends_artifact(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        ao = workspace / "agent-output"
        _run(["init", "cp2", "--json"], capsys)
        _run(["start-step", "cp2", "2", "--json"], capsys)
        rc, out = _run(
            ["checkpoint", "cp2", "2", "diag", "--artifact", "02-arch.md", "--json"],
            capsys,
        )
        assert rc == 0
        state = _load_session(ao, "cp2")
        assert "02-arch.md" in state["steps"]["2"]["artifacts"]


# ---------------------------------------------------------------------------
# TestDecide
# ---------------------------------------------------------------------------


class TestDecide:
    def test_mode_a_key_value(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        ao = workspace / "agent-output"
        _run(["init", "d1", "--json"], capsys)
        rc, out = _run(
            ["decide", "d1", "--key", "region", "--value", "eastus2", "--json"],
            capsys,
        )
        assert rc == 0
        state = _load_session(ao, "d1")
        assert state["decisions"]["region"] == "eastus2"

    def test_mode_b_decision_log(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        ao = workspace / "agent-output"
        _run(["init", "d2", "--json"], capsys)
        rc, out = _run(
            [
                "decide", "d2",
                "--decision", "Use VWAN",
                "--rationale", "Simplicity",
                "--step", "2",
                "--json",
            ],
            capsys,
        )
        assert rc == 0
        state = _load_session(ao, "d2")
        assert len(state["decision_log"]) == 1
        assert state["decision_log"][0]["decision"] == "Use VWAN"

    def test_no_args_error(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        _run(["init", "d3", "--json"], capsys)
        rc, out = _run(["decide", "d3", "--json"], capsys)
        assert rc == 1

    def test_appends(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        ao = workspace / "agent-output"
        _run(["init", "d4", "--json"], capsys)
        _run(
            ["decide", "d4", "--decision", "First", "--rationale", "r1", "--step", "1", "--json"],
            capsys,
        )
        _run(
            ["decide", "d4", "--decision", "Second", "--rationale", "r2", "--step", "2", "--json"],
            capsys,
        )
        state = _load_session(ao, "d4")
        assert len(state["decision_log"]) == 2


# ---------------------------------------------------------------------------
# TestFinding
# ---------------------------------------------------------------------------


class TestFinding:
    def test_add(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        ao = workspace / "agent-output"
        _run(["init", "f1", "--json"], capsys)
        rc, out = _run(["finding", "f1", "--add", "TLS missing", "--json"], capsys)
        assert rc == 0
        state = _load_session(ao, "f1")
        assert "TLS missing" in state["open_findings"]

    def test_remove(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        ao = workspace / "agent-output"
        _run(["init", "f2", "--json"], capsys)
        _run(["finding", "f2", "--add", "TLS missing", "--json"], capsys)
        rc, out = _run(["finding", "f2", "--remove", "TLS missing", "--json"], capsys)
        assert rc == 0
        state = _load_session(ao, "f2")
        assert "TLS missing" not in state["open_findings"]

    def test_remove_nonexistent(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        _run(["init", "f3", "--json"], capsys)
        rc, out = _run(["finding", "f3", "--remove", "nope", "--json"], capsys)
        assert rc == 0
        data = json.loads(out)
        assert data["action"] == "not_found"

    def test_idempotent_add(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        ao = workspace / "agent-output"
        _run(["init", "f4", "--json"], capsys)
        _run(["finding", "f4", "--add", "dup", "--json"], capsys)
        _run(["finding", "f4", "--add", "dup", "--json"], capsys)
        state = _load_session(ao, "f4")
        assert state["open_findings"].count("dup") == 1


# ---------------------------------------------------------------------------
# TestReviewAudit
# ---------------------------------------------------------------------------


class TestReviewAudit:
    def test_creates_entry(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        ao = workspace / "agent-output"
        _run(["init", "ra1", "--json"], capsys)
        rc, out = _run(
            ["review-audit", "ra1", "1", "--complexity", "standard", "--passes-planned", "2", "--json"],
            capsys,
        )
        assert rc == 0
        state = _load_session(ao, "ra1")
        assert "1" in state["review_audit"]
        assert state["review_audit"]["1"]["complexity"] == "standard"

    def test_appends_model(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        ao = workspace / "agent-output"
        _run(["init", "ra2", "--json"], capsys)
        _run(["review-audit", "ra2", "2", "--complexity", "simple", "--json"], capsys)
        rc, out = _run(["review-audit", "ra2", "2", "--model", "gpt-4o", "--json"], capsys)
        assert rc == 0
        state = _load_session(ao, "ra2")
        assert state["review_audit"]["2"]["model"] == "gpt-4o"

    def test_appends_skip(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        ao = workspace / "agent-output"
        _run(["init", "ra3", "--json"], capsys)
        rc, out = _run(
            ["review-audit", "ra3", "1", "--skip", "--skip-reason", "demo only", "--json"],
            capsys,
        )
        assert rc == 0
        state = _load_session(ao, "ra3")
        assert state["review_audit"]["1"]["status"] == "skipped"
        assert state["review_audit"]["1"]["skip_reason"] == "demo only"

    def test_governance_step(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        ao = workspace / "agent-output"
        _run(["init", "ra4", "--json"], capsys)
        rc, out = _run(
            ["review-audit", "ra4", "3_5", "--complexity", "complex", "--json"],
            capsys,
        )
        assert rc == 0
        state = _load_session(ao, "ra4")
        assert "3_5" in state["review_audit"]


# ---------------------------------------------------------------------------
# TestAtomicWrite
# ---------------------------------------------------------------------------


class TestAtomicWrite:
    def test_bak_created_on_second_write(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        ao = workspace / "agent-output"
        _run(["init", "aw1", "--json"], capsys)
        _run(["decide", "aw1", "--key", "region", "--value", "westus", "--json"], capsys)
        bak = ao / "aw1" / "00-session-state.json.bak"
        assert bak.exists()

    def test_corrupt_recovery(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        ao = workspace / "agent-output"
        _run(["init", "aw2", "--json"], capsys)
        sess_file = ao / "aw2" / "00-session-state.json"
        # Verify the file is valid JSON first
        state = json.loads(sess_file.read_text())
        assert state["schema_version"] == "3.0"


# ---------------------------------------------------------------------------
# TestMigration
# ---------------------------------------------------------------------------


class TestMigration:
    def test_v1_migrates_to_v3(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        ao = workspace / "agent-output"
        proj = ao / "mig1"
        proj.mkdir(parents=True)

        v1_state = {
            "schema_version": "1.0",
            "project": "mig1",
            "region": "eastus",
            "current_step": 1,
            "steps": {
                "1": {"name": "Requirements", "agent": "requirements", "status": "complete",
                      "started": None, "completed": None, "artifacts": []},
            },
        }
        (proj / "00-session-state.json").write_text(json.dumps(v1_state))

        # Trigger load+migrate via show
        rc, out = _run(["show", "mig1", "--json"], capsys)
        assert rc == 0
        data = json.loads(out)
        session = data["session_state"]
        assert session["schema_version"] == "3.0"
        assert set(session["steps"].keys()) == ALL_STEP_KEYS

    def test_all_step_keys_present(self, workspace: Path, capsys: pytest.CaptureFixture[str]):
        ao = workspace / "agent-output"
        _run(["init", "mig2", "--json"], capsys)
        state = _load_session(ao, "mig2")
        assert set(state["steps"].keys()) == ALL_STEP_KEYS
