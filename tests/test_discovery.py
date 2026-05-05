"""Tests for the brownfield Discovery module."""

from unittest.mock import MagicMock, patch

import pytest

from src.tools.discovery import DiscoveryCollector, DiscoveryResult, DiscoveryScope


@pytest.fixture
def mock_credential():
    return MagicMock()


@pytest.fixture
def mock_settings():
    settings = MagicMock()
    settings.azure.subscription_id = "test-sub-id"
    settings.azure.management_group_prefix = "mrg"
    return settings


@pytest.fixture
def collector(mock_credential, mock_settings):
    with patch("src.tools.discovery.AzureRGClient") as MockRGClient:
        c = DiscoveryCollector(mock_credential, mock_settings)
        c._arg_client = MockRGClient.return_value
        return c


def _mock_arg_result(data: list[dict]):
    """Create a mock Resource Graph query result."""
    result = MagicMock()
    result.data = data
    return result


class TestDiscoveryResult:
    def test_empty_result(self):
        result = DiscoveryResult(scope="test-sub", scope_type=DiscoveryScope.SUBSCRIPTION)
        d = result.to_dict()
        assert d["scope"] == "test-sub"
        assert d["scope_type"] == "subscription"
        assert d["management_groups"] == []
        assert d["subscriptions"] == []
        assert d["resources"] == {}
        assert d["errors"] == []

    def test_result_with_data(self):
        result = DiscoveryResult(
            scope="mrg",
            scope_type=DiscoveryScope.MANAGEMENT_GROUP,
            management_groups=[{"name": "mrg", "displayName": "Root"}],
            subscriptions=[{"subscriptionId": "sub-1", "name": "Platform"}],
        )
        d = result.to_dict()
        assert len(d["management_groups"]) == 1
        assert d["management_groups"][0]["name"] == "mrg"
        assert len(d["subscriptions"]) == 1


class TestDiscoveryCollector:
    def test_init(self, collector, mock_credential, mock_settings):
        assert collector.credential is mock_credential
        assert collector.settings is mock_settings

    @pytest.mark.asyncio
    async def test_discover_management_groups(self, collector):
        mg_data = [
            {"name": "mrg", "displayName": "Root MG", "parent": None},
            {"name": "mrg-platform", "displayName": "Platform", "parent": "/providers/Microsoft.Management/managementGroups/mrg"},
        ]
        collector._arg_client.resources.return_value = _mock_arg_result(mg_data)

        result = await collector._discover_management_groups(
            management_groups=["mrg"],
            subscriptions=["test-sub-id"],
        )
        assert len(result) == 2
        assert result[0]["name"] == "mrg"

    @pytest.mark.asyncio
    async def test_discover_subscriptions(self, collector):
        sub_data = [
            {"subscriptionId": "sub-1", "name": "mgmt", "displayName": "Management", "state": "Enabled"},
        ]
        collector._arg_client.resources.return_value = _mock_arg_result(sub_data)

        result = await collector._discover_subscriptions(
            management_groups=None,
            subscriptions=["test-sub-id"],
        )
        assert len(result) == 1
        assert result[0]["subscriptionId"] == "sub-1"

    @pytest.mark.asyncio
    async def test_discover_resources(self, collector):
        type_data = [
            {"type": "microsoft.storage/storageaccounts", "count": 5},
            {"type": "microsoft.compute/virtualmachines", "count": 3},
        ]
        location_data = [{"location": "southcentralus", "count": 8}]
        rg_data = [{"resourceGroup": "rg1", "subscriptionId": "sub-1", "count": 8}]

        call_count = 0

        def side_effect(request):
            nonlocal call_count
            data_sets = [type_data, location_data, rg_data]
            result = _mock_arg_result(data_sets[min(call_count, 2)])
            call_count += 1
            return result

        collector._arg_client.resources.side_effect = side_effect

        result = await collector._discover_resources(
            management_groups=None,
            subscriptions=["test-sub-id"],
        )
        assert result["total_count"] == 8
        assert len(result["by_type"]) == 2

    @pytest.mark.asyncio
    async def test_discover_network(self, collector):
        vnet_data = [
            {
                "name": "hub-vnet",
                "location": "southcentralus",
                "addressSpace": ["10.0.0.0/16"],
                "subnets": 3,
                "peerings": 2,
            }
        ]
        collector._arg_client.resources.return_value = _mock_arg_result(vnet_data)

        result = await collector._discover_network(
            management_groups=None,
            subscriptions=["test-sub-id"],
        )
        assert "virtual_networks" in result
        assert "peerings" in result
        assert "network_security_groups" in result
        assert "private_dns_zones" in result
        assert "firewalls" in result

    @pytest.mark.asyncio
    async def test_discover_security(self, collector):
        kv_data = [
            {
                "name": "kv-1",
                "enableSoftDelete": True,
                "enablePurgeProtection": True,
                "enableRbacAuthorization": True,
                "networkAcls": "Deny",
            }
        ]
        collector._arg_client.resources.return_value = _mock_arg_result(kv_data)

        result = await collector._discover_security(
            management_groups=None,
            subscriptions=["test-sub-id"],
        )
        assert "key_vaults" in result
        assert "sentinel" in result
        assert "storage_accounts" in result

    @pytest.mark.asyncio
    async def test_discover_full_handles_errors_gracefully(self, collector):
        """Partial failures should not break the full discovery run."""
        collector._arg_client.resources.side_effect = Exception("Resource Graph unavailable")

        result = await collector.discover(
            scope="test-sub-id",
            scope_type=DiscoveryScope.SUBSCRIPTION,
            subscriptions=["test-sub-id"],
        )
        # Should still return a result with errors logged
        assert len(result.errors) > 0
        assert "Resource Graph unavailable" in result.errors[0]

    @pytest.mark.asyncio
    async def test_discover_logging(self, collector):
        law_data = [
            {
                "name": "mrg-law",
                "location": "southcentralus",
                "sku": "PerGB2018",
                "retentionDays": 90,
            }
        ]
        collector._arg_client.resources.return_value = _mock_arg_result(law_data)

        result = await collector._discover_logging(
            management_groups=None,
            subscriptions=["test-sub-id"],
        )
        assert "log_analytics_workspaces" in result
        assert "automation_accounts" in result
        assert "diagnostic_settings" in result

    @pytest.mark.asyncio
    async def test_discover_rbac(self, collector):
        rbac_data = [
            {
                "principalId": "user-1",
                "principalType": "User",
                "roleDefinitionId": "/providers/Microsoft.Authorization/roleDefinitions/acdd72a7",
                "scope": "/subscriptions/test-sub-id",
            }
        ]
        collector._arg_client.resources.return_value = _mock_arg_result(rbac_data)

        result = await collector._discover_rbac(
            management_groups=None,
            subscriptions=["test-sub-id"],
        )
        assert len(result) == 1
        assert result[0]["principalType"] == "User"


class TestAssessSettings:
    def test_defaults(self):
        from src.config.settings import AssessSettings

        s = AssessSettings()
        assert s.mode == "assess"
        assert s.scope_type == "subscription"
        assert s.output_dir == "agent-output/assessment"
        assert s.allow_remediation is False

    def test_settings_includes_assess(self):
        from src.config.settings import Settings

        s = Settings()
        assert hasattr(s, "assess")
        assert s.assess.mode == "assess"
