"""Tests for the assessment CLI."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.tools.assess_cli import main, run_assessment
from src.tools.discovery import DiscoveryResult, DiscoveryScope
from src.tools.wara_engine import AssessmentResult, Finding, PillarScore


def _mock_discovery():
    return DiscoveryResult(
        scope="test-sub",
        scope_type=DiscoveryScope.SUBSCRIPTION,
        subscriptions=[{"subscriptionId": "sub-001", "name": "test"}],
        policy_assignments=[{"name": "asb"}],
    )


def _mock_assessment(*, critical=0, high=0, medium=0):
    findings = []
    for i in range(critical):
        findings.append(Finding(
            rule_id=f"SEC-C{i}", title=f"Critical {i}", pillar="security",
            caf_area="security", alz_area="security", severity="critical",
            confidence="high", recommendation="Fix it",
        ))
    for i in range(high):
        findings.append(Finding(
            rule_id=f"SEC-H{i}", title=f"High {i}", pillar="security",
            caf_area="security", alz_area="security", severity="high",
            confidence="high", recommendation="Fix it",
        ))
    for i in range(medium):
        findings.append(Finding(
            rule_id=f"OPE-M{i}", title=f"Medium {i}", pillar="operational_excellence",
            caf_area="management", alz_area="logging", severity="medium",
            confidence="medium", recommendation="Improve it",
        ))
    return AssessmentResult(
        scope="test-sub",
        checks_run=10,
        checks_passed=10 - critical - high - medium,
        findings=findings,
        overall_score=90.0,
        pillar_scores={
            "security": PillarScore(pillar="security", score=80.0, critical=critical, high=high),
            "reliability": PillarScore(pillar="reliability"),
            "cost_optimization": PillarScore(pillar="cost_optimization"),
            "operational_excellence": PillarScore(pillar="operational_excellence", medium=medium),
            "performance": PillarScore(pillar="performance"),
        },
    )


def _mock_outputs(tmp_path):
    return {
        "current_state": tmp_path / "current-state-architecture.md",
        "target_state": tmp_path / "target-state-architecture.md",
        "assessment_report": tmp_path / "assessment-report.md",
        "assessment_json": tmp_path / "assessment-report.json",
        "architecture_diagram": tmp_path / "architecture-diagram.mmd",
        "adr": tmp_path / "ADR-assessment-findings.md",
    }


class TestRunAssessment:
    @pytest.mark.asyncio
    async def test_returns_summary(self, tmp_path):
        discovery = _mock_discovery()
        assessment = _mock_assessment(critical=0, high=1, medium=2)
        outputs = _mock_outputs(tmp_path)

        with (
            patch("src.tools.assess_cli.DefaultAzureCredential"),
            patch("src.tools.assess_cli.Settings") as mock_settings_cls,
            patch("src.tools.assess_cli.DiscoveryCollector") as mock_collector_cls,
            patch("src.tools.assess_cli.WaraEngine") as mock_engine_cls,
            patch("src.tools.assess_cli.ReportGenerator") as mock_reporter_cls,
        ):
            mock_settings = MagicMock()
            mock_settings.assess.output_dir = str(tmp_path)
            mock_settings.azure.subscription_id = "sub-001"
            mock_settings_cls.return_value = mock_settings

            mock_collector = MagicMock()
            mock_collector.discover = AsyncMock(return_value=discovery)
            mock_collector_cls.return_value = mock_collector

            mock_engine = MagicMock()
            mock_engine.assess = AsyncMock(return_value=assessment)
            mock_engine_cls.return_value = mock_engine

            mock_reporter = MagicMock()
            mock_reporter.generate_all.return_value = outputs
            mock_reporter_cls.return_value = mock_reporter

            result = await run_assessment("test-sub", "subscription", "assess")

        assert result["scope"] == "test-sub"
        assert result["scope_type"] == "subscription"
        assert result["mode"] == "assess"
        assert result["overall_score"] == 90.0
        assert result["findings_count"] == 3
        assert result["critical"] == 0
        assert result["high"] == 1
        assert result["medium"] == 2
        assert "outputs" in result

    @pytest.mark.asyncio
    async def test_fallback_subscription(self, tmp_path):
        """When discovery returns no subscriptions, falls back to settings."""
        discovery = DiscoveryResult(
            scope="empty", scope_type=DiscoveryScope.SUBSCRIPTION
        )
        assessment = _mock_assessment()
        outputs = _mock_outputs(tmp_path)

        with (
            patch("src.tools.assess_cli.DefaultAzureCredential"),
            patch("src.tools.assess_cli.Settings") as mock_settings_cls,
            patch("src.tools.assess_cli.DiscoveryCollector") as mock_collector_cls,
            patch("src.tools.assess_cli.WaraEngine") as mock_engine_cls,
            patch("src.tools.assess_cli.ReportGenerator") as mock_reporter_cls,
        ):
            mock_settings = MagicMock()
            mock_settings.assess.output_dir = str(tmp_path)
            mock_settings.azure.subscription_id = "fallback-sub"
            mock_settings_cls.return_value = mock_settings

            mock_collector = MagicMock()
            mock_collector.discover = AsyncMock(return_value=discovery)
            mock_collector_cls.return_value = mock_collector

            mock_engine = MagicMock()
            mock_engine.assess = AsyncMock(return_value=assessment)
            mock_engine_cls.return_value = mock_engine

            mock_reporter = MagicMock()
            mock_reporter.generate_all.return_value = outputs
            mock_reporter_cls.return_value = mock_reporter

            await run_assessment("empty", "subscription", "assess")

            # Verify assess was called with fallback subscription
            call_args = mock_engine.assess.call_args
            assert call_args[1]["subscriptions"] == ["fallback-sub"]


class TestMain:
    def test_exit_0_no_critical(self, tmp_path):
        """CLI exits 0 when no critical findings."""
        with (
            patch("src.tools.assess_cli.argparse.ArgumentParser.parse_args") as mock_args,
            patch("src.tools.assess_cli.asyncio.run") as mock_run,
        ):
            mock_args.return_value = MagicMock(
                scope="test", scope_type="subscription", mode="assess"
            )
            mock_run.return_value = {
                "scope": "test",
                "critical": 0,
                "high": 0,
                "overall_score": 100.0,
            }

            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_exit_1_with_critical(self, tmp_path):
        """CLI exits 1 when critical findings exist."""
        with (
            patch("src.tools.assess_cli.argparse.ArgumentParser.parse_args") as mock_args,
            patch("src.tools.assess_cli.asyncio.run") as mock_run,
        ):
            mock_args.return_value = MagicMock(
                scope="test", scope_type="subscription", mode="assess"
            )
            mock_run.return_value = {
                "scope": "test",
                "critical": 2,
                "high": 1,
                "overall_score": 60.0,
            }

            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
