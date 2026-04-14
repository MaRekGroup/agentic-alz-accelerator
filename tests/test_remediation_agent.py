"""Tests for the Remediation Agent."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.remediation_agent import RemediationAgent, REMEDIATION_STRATEGIES


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
    settings.iac.framework = "bicep"
    return settings


@pytest.fixture
def agent(mock_kernel, mock_credential, mock_settings):
    with patch("src.agents.remediation_agent.BicepDeployer") as MockBicep:
        with patch("src.agents.remediation_agent.TerraformDeployer"):
            with patch("src.agents.remediation_agent.ResourceGraphClient") as MockRG:
                with patch("src.agents.remediation_agent.PolicyChecker") as MockPolicy:
                    a = RemediationAgent(mock_kernel, mock_credential, mock_settings)
                    a.bicep = MockBicep.return_value
                    a.resource_graph = MockRG.return_value
                    a.policy_checker = MockPolicy.return_value
                    return a


class TestRemediationAgent:
    def test_available_strategies(self, agent):
        strategies = agent.get_available_strategies()
        assert "deny-public-ip" in strategies
        assert "require-tls-1-2" in strategies
        assert "enforce-https-ingress" in strategies

    @pytest.mark.asyncio
    async def test_remediate_single_known_policy(self, agent):
        agent.resource_graph.get_resource_details = AsyncMock(return_value={"id": "test"})
        agent.bicep.deploy_template = AsyncMock(return_value={"status": "Succeeded"})
        agent.policy_checker.check_single_resource = AsyncMock(return_value=True)

        violation = {
            "resource_id": "/subscriptions/test/resourceGroups/rg/providers/Microsoft.Network/networkInterfaces/nic1",
            "policy_name": "deny-public-ip",
            "policy_definition_id": "test-policy-def",
        }

        result = await agent.remediate_single(violation)
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_remediate_single_unknown_policy(self, agent):
        violation = {
            "resource_id": "test-resource",
            "policy_name": "unknown-policy-xyz",
        }

        result = await agent.remediate_single(violation)
        assert result["status"] == "skipped"

    @pytest.mark.asyncio
    async def test_remediate_multiple(self, agent):
        agent.resource_graph.get_resource_details = AsyncMock(return_value={"id": "test"})
        agent.bicep.deploy_template = AsyncMock(return_value={"status": "Succeeded"})
        agent.policy_checker.check_single_resource = AsyncMock(return_value=True)

        violations = [
            {"resource_id": "r1", "policy_name": "deny-public-ip", "policy_definition_id": "p1"},
            {"resource_id": "r2", "policy_name": "unknown-policy", "policy_definition_id": "p2"},
            {"resource_id": "r3", "policy_name": "require-tls-1-2", "policy_definition_id": "p3"},
        ]

        result = await agent.remediate(violations)
        assert result["total"] == 3
        assert result["succeeded"] == 2
        assert result["skipped"] == 1

    def test_remediation_history_empty(self, agent):
        history = agent.get_remediation_history()
        assert history == []

    @pytest.mark.asyncio
    async def test_remediation_history_after_action(self, agent):
        agent.resource_graph.get_resource_details = AsyncMock(return_value={"id": "test"})
        agent.bicep.deploy_template = AsyncMock(return_value={"status": "Succeeded"})
        agent.policy_checker.check_single_resource = AsyncMock(return_value=True)

        await agent.remediate_single({
            "resource_id": "r1",
            "policy_name": "deny-public-ip",
            "policy_definition_id": "p1",
        })

        history = agent.get_remediation_history()
        assert len(history) == 1
        assert history[0]["status"] == "success"
