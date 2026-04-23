"""Tests for the assessment agent."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.assessment_agent import AssessmentAgent
from src.tools.discovery import DiscoveryResult, DiscoveryScope
from src.tools.wara_engine import AssessmentResult, Finding, PillarScore


@pytest.fixture
def mock_kernel():
    kernel = MagicMock()
    kernel.add_plugin = MagicMock()
    return kernel


@pytest.fixture
def mock_credential():
    return MagicMock()


@pytest.fixture
def mock_settings(tmp_path):
    settings = MagicMock()
    settings.assess.scope = "default-scope"
    settings.assess.scope_type = "subscription"
    settings.assess.output_dir = str(tmp_path)
    settings.azure.subscription_id = "fallback-sub"
    return settings


@pytest.fixture
def discovery():
    return DiscoveryResult(
        scope="test-sub",
        scope_type=DiscoveryScope.SUBSCRIPTION,
        subscriptions=[{"subscriptionId": "sub-001"}],
        management_groups=[{"name": "root"}],
        policy_assignments=[{"name": "asb"}],
    )


@pytest.fixture
def assessment():
    return AssessmentResult(
        scope="test-sub",
        checks_run=10,
        checks_passed=8,
        overall_score=85.0,
        findings=[
            Finding(
                rule_id="SEC-001", title="TLS issue", pillar="security",
                caf_area="security", alz_area="security", severity="critical",
                confidence="high", recommendation="Fix TLS",
            ),
            Finding(
                rule_id="OPE-001", title="No logs", pillar="operational_excellence",
                caf_area="management", alz_area="logging", severity="high",
                confidence="high", recommendation="Enable logs",
            ),
        ],
        pillar_scores={
            "security": PillarScore(pillar="security", score=80.0, critical=1),
            "reliability": PillarScore(pillar="reliability"),
            "cost_optimization": PillarScore(pillar="cost_optimization"),
            "operational_excellence": PillarScore(pillar="operational_excellence", score=90.0, high=1),
            "performance": PillarScore(pillar="performance"),
        },
    )


class TestAssessmentAgentInit:
    def test_registers_plugin(self, mock_kernel, mock_credential, mock_settings):
        with (
            patch("src.agents.assessment_agent.DiscoveryCollector"),
            patch("src.agents.assessment_agent.WaraEngine"),
        ):
            agent = AssessmentAgent(mock_kernel, mock_credential, mock_settings)
            mock_kernel.add_plugin.assert_called_once_with(agent, plugin_name="assessment")

    def test_creates_components(self, mock_kernel, mock_credential, mock_settings):
        with (
            patch("src.agents.assessment_agent.DiscoveryCollector") as mock_dc,
            patch("src.agents.assessment_agent.WaraEngine") as mock_we,
        ):
            agent = AssessmentAgent(mock_kernel, mock_credential, mock_settings)
            mock_dc.assert_called_once_with(mock_credential, mock_settings)
            mock_we.assert_called_once_with(mock_credential, mock_settings)
            assert agent.reporter is not None


class TestRunAssessment:
    @pytest.mark.asyncio
    async def test_full_pipeline(
        self, mock_kernel, mock_credential, mock_settings, discovery, assessment, tmp_path
    ):
        with (
            patch("src.agents.assessment_agent.DiscoveryCollector") as mock_dc_cls,
            patch("src.agents.assessment_agent.WaraEngine") as mock_we_cls,
        ):
            mock_collector = MagicMock()
            mock_collector.discover = AsyncMock(return_value=discovery)
            mock_dc_cls.return_value = mock_collector

            mock_engine = MagicMock()
            mock_engine.assess = AsyncMock(return_value=assessment)
            mock_we_cls.return_value = mock_engine

            agent = AssessmentAgent(mock_kernel, mock_credential, mock_settings)
            result = await agent.run_assessment(scope="test-sub", scope_type="subscription")

        assert result["scope"] == "test-sub"
        assert result["overall_score"] == 85.0
        assert result["findings_count"] == 2
        assert result["critical"] == 1
        assert result["high"] == 1
        assert "outputs" in result
        assert len(result["outputs"]) == 6

    @pytest.mark.asyncio
    async def test_uses_settings_defaults(
        self, mock_kernel, mock_credential, mock_settings, discovery, assessment
    ):
        """Uses settings.assess.scope when no scope arg provided."""
        with (
            patch("src.agents.assessment_agent.DiscoveryCollector") as mock_dc_cls,
            patch("src.agents.assessment_agent.WaraEngine") as mock_we_cls,
        ):
            mock_collector = MagicMock()
            mock_collector.discover = AsyncMock(return_value=discovery)
            mock_dc_cls.return_value = mock_collector

            mock_engine = MagicMock()
            mock_engine.assess = AsyncMock(return_value=assessment)
            mock_we_cls.return_value = mock_engine

            agent = AssessmentAgent(mock_kernel, mock_credential, mock_settings)
            result = await agent.run_assessment()  # No args — use defaults

        assert result["scope"] == "default-scope"
        assert result["scope_type"] == "subscription"

    @pytest.mark.asyncio
    async def test_fallback_subscription(
        self, mock_kernel, mock_credential, mock_settings, assessment
    ):
        """Falls back to settings.azure.subscription_id when no subs discovered."""
        empty_discovery = DiscoveryResult(
            scope="empty", scope_type=DiscoveryScope.SUBSCRIPTION
        )
        with (
            patch("src.agents.assessment_agent.DiscoveryCollector") as mock_dc_cls,
            patch("src.agents.assessment_agent.WaraEngine") as mock_we_cls,
        ):
            mock_collector = MagicMock()
            mock_collector.discover = AsyncMock(return_value=empty_discovery)
            mock_dc_cls.return_value = mock_collector

            mock_engine = MagicMock()
            mock_engine.assess = AsyncMock(return_value=assessment)
            mock_we_cls.return_value = mock_engine

            agent = AssessmentAgent(mock_kernel, mock_credential, mock_settings)
            await agent.run_assessment(scope="empty", scope_type="subscription")

            call_args = mock_engine.assess.call_args
            assert call_args[1]["subscriptions"] == ["fallback-sub"]


class TestRunDiscoveryOnly:
    @pytest.mark.asyncio
    async def test_returns_discovery_dict(
        self, mock_kernel, mock_credential, mock_settings, discovery
    ):
        with (
            patch("src.agents.assessment_agent.DiscoveryCollector") as mock_dc_cls,
            patch("src.agents.assessment_agent.WaraEngine"),
        ):
            mock_collector = MagicMock()
            mock_collector.discover = AsyncMock(return_value=discovery)
            mock_dc_cls.return_value = mock_collector

            agent = AssessmentAgent(mock_kernel, mock_credential, mock_settings)
            result = await agent.run_discovery_only(scope="test-sub", scope_type="subscription")

        assert result["scope"] == "test-sub"
        assert "management_groups" in result
        assert "subscriptions" in result
