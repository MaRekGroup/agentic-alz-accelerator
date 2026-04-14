"""Tests for the Monitoring Agent."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.monitoring_agent import MonitoringAgent


@pytest.fixture
def mock_kernel():
    kernel = MagicMock()
    kernel.add_plugin = MagicMock()
    return kernel


@pytest.fixture
def mock_credential():
    return MagicMock()


@pytest.fixture
def mock_settings():
    settings = MagicMock()
    settings.azure.subscription_id = "test-sub-id"
    settings.azure.management_group_prefix = "alz"
    return settings


@pytest.fixture
def agent(mock_kernel, mock_credential, mock_settings):
    with patch("src.agents.monitoring_agent.PolicyChecker") as MockPolicy:
        with patch("src.agents.monitoring_agent.ResourceGraphClient") as MockRG:
            with patch("src.agents.monitoring_agent.DriftDetector") as MockDrift:
                a = MonitoringAgent(mock_kernel, mock_credential, mock_settings)
                a.policy_checker = MockPolicy.return_value
                a.resource_graph = MockRG.return_value
                a.drift_detector = MockDrift.return_value
                return a


class TestMonitoringAgent:
    @pytest.mark.asyncio
    async def test_compliance_scan(self, agent):
        agent.policy_checker.get_compliance_state = AsyncMock(
            return_value={"compliant": 95, "non_compliant": 5, "exempt": 0, "compliance_pct": 95.0}
        )
        agent.resource_graph.get_resource_inventory = AsyncMock(
            return_value={"total_count": 100, "by_type": {}}
        )
        agent.policy_checker.get_violations = AsyncMock(return_value=[])

        result = await agent.run_compliance_scan()

        assert "summary" in result
        assert result["summary"]["compliance_percentage"] == 95.0
        assert result["violations"] == []

    @pytest.mark.asyncio
    async def test_compliance_scan_with_violations(self, agent):
        violations = [
            {
                "resource_id": "/subscriptions/test/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/sa1",
                "policy_name": "deny-public-storage-access",
                "severity": "critical",
            }
        ]
        agent.policy_checker.get_compliance_state = AsyncMock(
            return_value={"compliant": 90, "non_compliant": 10, "exempt": 0, "compliance_pct": 90.0}
        )
        agent.resource_graph.get_resource_inventory = AsyncMock(
            return_value={"total_count": 100, "by_type": {}}
        )
        agent.policy_checker.get_violations = AsyncMock(return_value=violations)

        result = await agent.run_compliance_scan()

        assert len(result["violations"]) == 1
        assert result["violations"][0]["severity"] == "critical"

    @pytest.mark.asyncio
    async def test_detect_drift(self, agent):
        agent.drift_detector.detect = AsyncMock(
            return_value={"drifted_resources": [], "total_drifted": 0}
        )

        result = await agent.detect_drift()

        assert result["total_drifted"] == 0

    @pytest.mark.asyncio
    async def test_get_security_posture(self, agent):
        agent.resource_graph.query = AsyncMock(return_value=[])

        result = await agent.get_security_posture()

        assert "secure_score" in result
        assert "unhealthy_recommendations" in result
