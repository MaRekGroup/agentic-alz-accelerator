"""Tests for the Deployment Agent."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.deployment_agent import DeploymentAgent


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
    settings.iac.framework = "bicep"
    settings.ai.openai_deployment = "gpt-4o"
    settings.ai.openai_endpoint = "https://test.openai.azure.com/"
    settings.ai.openai_api_version = "2025-01-01-preview"
    return settings


@pytest.fixture
def agent(mock_kernel, mock_credential, mock_settings):
    with patch("src.agents.deployment_agent.BicepDeployer"):
        with patch("src.agents.deployment_agent.TerraformDeployer"):
            with patch("src.agents.deployment_agent.ResourceGraphClient"):
                return DeploymentAgent(mock_kernel, mock_credential, mock_settings)


class TestDeploymentAgent:
    def test_list_profiles(self, agent):
        result = agent.list_profiles()
        assert "online" in result
        assert "corp" in result
        assert "sandbox" in result
        assert "sap" in result

    def test_get_profile_details_valid(self, agent):
        result = agent.get_profile_details("online")
        assert "Online Landing Zone" in result

    def test_get_profile_details_invalid(self, agent):
        result = agent.get_profile_details("nonexistent")
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_deploy_with_bicep_what_if(self, agent):
        agent.bicep.what_if = AsyncMock(return_value="No changes")
        result = await agent.deploy_with_bicep(
            profile_name="online",
            subscription_id="test-sub",
            location="eastus2",
            what_if=True,
        )
        assert "What-if" in result
        agent.bicep.what_if.assert_called_once()

    @pytest.mark.asyncio
    async def test_deploy_with_bicep_invalid_profile(self, agent):
        result = await agent.deploy_with_bicep(
            profile_name="nonexistent",
            subscription_id="test-sub",
        )
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_deploy_profile_bicep(self, agent):
        agent.bicep.deploy = AsyncMock(
            return_value={"status": "Succeeded", "outputs": {}}
        )
        # Patch deploy_with_bicep to avoid what-if
        with patch.object(agent, "deploy_with_bicep", new_callable=AsyncMock) as mock_deploy:
            mock_deploy.return_value = "Deployment complete"
            result = await agent.deploy_profile("online")
            assert result["status"] == "deployed"

    @pytest.mark.asyncio
    async def test_deploy_profile_invalid(self, agent):
        with pytest.raises(ValueError, match="not found"):
            await agent.deploy_profile("nonexistent")

    @pytest.mark.asyncio
    async def test_validate_deployment(self, agent):
        agent.resource_graph.validate_landing_zone = AsyncMock(
            return_value={"validation_passed": True, "checks": {}}
        )
        result = await agent.validate_deployment(subscription_id="test-sub")
        assert "validation_passed" in result
