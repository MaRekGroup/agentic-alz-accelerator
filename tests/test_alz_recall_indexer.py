"""Tests for alz_recall.indexer module."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from alz_recall.indexer import (
    _classify,
    ensure_db,
    ensure_fresh,
    reindex,
    reindex_file,
)


@pytest.fixture()
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    ao = tmp_path / "agent-output"
    ao.mkdir()
    db = tmp_path / "tmp" / ".alz-recall.db"
    monkeypatch.setattr("alz_recall.indexer.AGENT_OUTPUT_DIR", str(ao))
    monkeypatch.setattr("alz_recall.indexer.DB_PATH", db)
    monkeypatch.setattr("alz_recall.config.AGENT_OUTPUT_DIR", str(ao))
    monkeypatch.setattr("alz_recall.config.DB_PATH", db)

    proj = ao / "demo"
    proj.mkdir()
    (proj / "00-session-state.json").write_text(
        '{"schema_version":"3.0","project":"demo","current_step":2}'
    )
    (proj / "01-requirements.md").write_text("# Requirements\nDeploy hub-spoke.\n")
    (proj / "02-architecture-assessment.md").write_text("# Architecture\nWAF assessment.\n")
    (proj / "00-handoff.md").write_text("# Handoff\n")
    return tmp_path


# ---------------------------------------------------------------------------
# TestClassify
# ---------------------------------------------------------------------------


class TestClassify:
    def test_estate_state(self):
        assert _classify("00-estate-state.json") == "estate-state"

    def test_session_state(self):
        assert _classify("00-session-state.json") == "session-state"

    def test_assessment_md(self):
        assert _classify("00-assessment-report.md") == "assessment"

    def test_assessment_json(self):
        assert _classify("00-assessment-data.json") == "assessment-json"

    def test_handoff(self):
        assert _classify("00-handoff.md") == "handoff"

    def test_requirements(self):
        assert _classify("01-requirements.md") == "requirements"

    def test_architecture(self):
        assert _classify("02-architecture-assessment.md") == "architecture"

    def test_design(self):
        assert _classify("03-design-diagram.md") == "design"

    def test_governance_json(self):
        assert _classify("04-governance-constraints.json") == "governance-json"

    def test_governance_md(self):
        assert _classify("04-governance-constraints.md") == "governance"

    def test_implementation_plan(self):
        assert _classify("04-implementation-plan.md") == "implementation-plan"

    def test_deployment_summary(self):
        assert _classify("06-deployment-summary.md") == "deployment-summary"

    def test_as_built(self):
        assert _classify("07-design-document.md") == "as-built"

    def test_compliance(self):
        assert _classify("08-compliance-report.md") == "compliance"

    def test_remediation(self):
        assert _classify("09-remediation-log.md") == "remediation"

    def test_unknown_fallback(self):
        assert _classify("random-file.txt") == "unknown"


# ---------------------------------------------------------------------------
# TestEnsureDb
# ---------------------------------------------------------------------------


class TestEnsureDb:
    def test_creates_tables(self, workspace: Path):
        conn = ensure_db()
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table','view')"
            ).fetchall()
        }
        assert "artifacts" in tables
        assert "meta" in tables
        assert "artifacts_fts" in tables
        conn.close()


# ---------------------------------------------------------------------------
# TestReindex
# ---------------------------------------------------------------------------


class TestReindex:
    def test_full_reindex_counts(self, workspace: Path):
        conn = ensure_db()
        result = reindex(conn)
        assert result["indexed"] == 4
        assert "timestamp" in result
        conn.close()

    def test_empty_dir(self, workspace: Path):
        # Remove all files from the project
        ao = workspace / "agent-output" / "demo"
        for f in ao.iterdir():
            f.unlink()
        conn = ensure_db()
        result = reindex(conn)
        assert result["indexed"] == 0
        conn.close()

    def test_reindex_file_single(self, workspace: Path):
        conn = ensure_db()
        reindex(conn)

        # Add a new file and reindex just that one
        new_file = workspace / "agent-output" / "demo" / "04-implementation-plan.md"
        new_file.write_text("# Plan\nPhase 1.\n")
        reindex_file(conn, new_file)

        row = conn.execute(
            "SELECT kind FROM artifacts WHERE path = ?", (str(new_file),)
        ).fetchone()
        assert row is not None
        assert row["kind"] == "implementation-plan"
        conn.close()


# ---------------------------------------------------------------------------
# TestEnsureFresh
# ---------------------------------------------------------------------------


class TestEnsureFresh:
    def test_creates_index_if_missing(self, workspace: Path):
        conn = ensure_fresh()
        count = conn.execute("SELECT COUNT(*) AS cnt FROM artifacts").fetchone()["cnt"]
        assert count == 4
        conn.close()

    def test_skips_if_fresh(self, workspace: Path):
        conn = ensure_db()
        reindex(conn)
        ts1 = conn.execute(
            "SELECT value FROM meta WHERE key='last_index'"
        ).fetchone()["value"]

        conn2 = ensure_fresh(conn)
        ts2 = conn2.execute(
            "SELECT value FROM meta WHERE key='last_index'"
        ).fetchone()["value"]
        # Should not have reindexed — timestamps equal
        assert ts1 == ts2
        conn.close()

    def test_reindexes_if_stale(self, workspace: Path):
        conn = ensure_db()
        reindex(conn)

        # Manually backdate the last_index to force staleness
        conn.execute(
            "UPDATE meta SET value = ? WHERE key = 'last_index'",
            (str(time.time() - 10000),),
        )
        conn.commit()

        # Touch a file so it appears newer
        f = workspace / "agent-output" / "demo" / "01-requirements.md"
        f.write_text("# Requirements\nUpdated.\n")

        conn2 = ensure_fresh(conn)
        count = conn2.execute("SELECT COUNT(*) AS cnt FROM artifacts").fetchone()["cnt"]
        assert count == 4
        conn.close()
