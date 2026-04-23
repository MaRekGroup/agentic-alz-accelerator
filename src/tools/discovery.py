"""
Discovery — read-only Azure environment inventory collectors for brownfield assessment.

Collects:
- Management group hierarchy
- Subscription inventory
- Resource inventory (via Resource Graph)
- Policy assignments and compliance state
- RBAC role assignments
- Network topology (VNets, peerings, DNS)
- Logging and monitoring configuration
- Security posture (Defender, Key Vault)
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from azure.identity import DefaultAzureCredential
from azure.mgmt.resourcegraph import ResourceGraphClient as AzureRGClient
from azure.mgmt.resourcegraph.models import (
    QueryRequest,
    QueryRequestOptions,
    ResultFormat,
)

from src.config.settings import Settings

logger = logging.getLogger(__name__)


class DiscoveryScope(str, Enum):
    """Scope levels for discovery."""

    TENANT = "tenant"
    MANAGEMENT_GROUP = "management_group"
    SUBSCRIPTION = "subscription"
    RESOURCE_GROUP = "resource_group"


@dataclass
class DiscoveryResult:
    """Container for all discovery data from an Azure environment."""

    scope: str
    scope_type: DiscoveryScope
    discovered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    management_groups: list[dict] = field(default_factory=list)
    subscriptions: list[dict] = field(default_factory=list)
    resources: dict = field(default_factory=dict)
    policy_assignments: list[dict] = field(default_factory=list)
    policy_compliance: dict = field(default_factory=dict)
    rbac_assignments: list[dict] = field(default_factory=list)
    network_topology: dict = field(default_factory=dict)
    logging_config: dict = field(default_factory=dict)
    security_posture: dict = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialize to dict for JSON output."""
        return {
            "scope": self.scope,
            "scope_type": self.scope_type.value,
            "discovered_at": self.discovered_at,
            "management_groups": self.management_groups,
            "subscriptions": self.subscriptions,
            "resources": self.resources,
            "policy_assignments": self.policy_assignments,
            "policy_compliance": self.policy_compliance,
            "rbac_assignments": self.rbac_assignments,
            "network_topology": self.network_topology,
            "logging_config": self.logging_config,
            "security_posture": self.security_posture,
            "errors": self.errors,
        }


class DiscoveryCollector:
    """Read-only Azure environment inventory collector.

    All methods are read-only — no Azure resources are created, modified, or deleted.
    Requires Reader + Policy Reader + Security Reader roles at the target scope.
    """

    def __init__(self, credential: DefaultAzureCredential, settings: Settings):
        self.credential = credential
        self.settings = settings
        self._arg_client: AzureRGClient | None = None

    @property
    def arg_client(self) -> AzureRGClient:
        if self._arg_client is None:
            self._arg_client = AzureRGClient(self.credential)
        return self._arg_client

    def _arg_query(
        self,
        query: str,
        subscriptions: list[str] | None = None,
        management_groups: list[str] | None = None,
        max_results: int = 1000,
    ) -> list[dict]:
        """Execute a Resource Graph query. Read-only."""
        options = QueryRequestOptions(
            result_format=ResultFormat.OBJECT_ARRAY,
            top=max_results,
        )
        request = QueryRequest(
            query=query,
            subscriptions=subscriptions,
            management_groups=management_groups,
            options=options,
        )
        result = self.arg_client.resources(request)
        return result.data if isinstance(result.data, list) else []

    async def discover(
        self,
        scope: str,
        scope_type: DiscoveryScope,
        subscriptions: list[str] | None = None,
    ) -> DiscoveryResult:
        """Run full discovery for the given scope.

        Args:
            scope: Azure scope string (e.g., MG name, subscription ID).
            scope_type: Level of discovery scope.
            subscriptions: Explicit subscription list (overrides scope-based resolution).

        Returns:
            DiscoveryResult with all collected inventory data.
        """
        result = DiscoveryResult(scope=scope, scope_type=scope_type)
        subs = subscriptions or [self.settings.azure.subscription_id]

        mg_groups = None
        if scope_type in (DiscoveryScope.TENANT, DiscoveryScope.MANAGEMENT_GROUP):
            mg_groups = [scope] if scope_type == DiscoveryScope.MANAGEMENT_GROUP else None

        collectors = [
            ("management_groups", self._discover_management_groups, mg_groups, subs),
            ("subscriptions", self._discover_subscriptions, mg_groups, subs),
            ("resources", self._discover_resources, mg_groups, subs),
            ("policy_assignments", self._discover_policies, mg_groups, subs),
            ("policy_compliance", self._discover_compliance, subs),
            ("rbac_assignments", self._discover_rbac, mg_groups, subs),
            ("network_topology", self._discover_network, mg_groups, subs),
            ("logging_config", self._discover_logging, mg_groups, subs),
            ("security_posture", self._discover_security, mg_groups, subs),
        ]

        for name, collector, *args in collectors:
            try:
                logger.info(f"Discovering {name} at scope {scope}")
                data = await collector(*args)
                setattr(result, name, data)
            except Exception as e:
                msg = f"Failed to discover {name}: {e}"
                logger.warning(msg)
                result.errors.append(msg)

        return result

    async def _discover_management_groups(
        self,
        management_groups: list[str] | None,
        subscriptions: list[str],
    ) -> list[dict]:
        """Discover management group hierarchy."""
        query = """
        resourcecontainers
        | where type == 'microsoft.management/managementgroups'
        | project id, name, displayName=properties.displayName,
                  parent=properties.details.parent.id,
                  tenantId=tenantId
        | order by name asc
        """
        return self._arg_query(
            query,
            subscriptions=subscriptions,
            management_groups=management_groups,
        )

    async def _discover_subscriptions(
        self,
        management_groups: list[str] | None,
        subscriptions: list[str],
    ) -> list[dict]:
        """Discover subscriptions and their MG placement."""
        query = """
        resourcecontainers
        | where type == 'microsoft.resources/subscriptions'
        | project subscriptionId, name, displayName=properties.displayName,
                  state=properties.state, tags,
                  managementGroup=properties.managementGroupAncestorsChain
        | order by name asc
        """
        return self._arg_query(
            query,
            subscriptions=subscriptions,
            management_groups=management_groups,
        )

    async def _discover_resources(
        self,
        management_groups: list[str] | None,
        subscriptions: list[str],
    ) -> dict:
        """Discover resource inventory grouped by type and location."""
        by_type_query = """
        resources
        | summarize count=count() by type
        | order by count desc
        """
        by_type = self._arg_query(
            by_type_query,
            subscriptions=subscriptions,
            management_groups=management_groups,
        )

        by_location_query = """
        resources
        | summarize count=count() by location
        | order by count desc
        """
        by_location = self._arg_query(
            by_location_query,
            subscriptions=subscriptions,
            management_groups=management_groups,
        )

        by_rg_query = """
        resources
        | summarize count=count() by resourceGroup, subscriptionId
        | order by count desc
        """
        by_rg = self._arg_query(
            by_rg_query,
            subscriptions=subscriptions,
            management_groups=management_groups,
        )

        total = sum(r.get("count", 0) for r in by_type)

        return {
            "total_count": total,
            "by_type": by_type,
            "by_location": by_location,
            "by_resource_group": by_rg,
        }

    async def _discover_policies(
        self,
        management_groups: list[str] | None,
        subscriptions: list[str],
    ) -> list[dict]:
        """Discover policy assignments."""
        query = """
        policyresources
        | where type == 'microsoft.authorization/policyassignments'
        | project id, name, displayName=properties.displayName,
                  policyDefinitionId=properties.policyDefinitionId,
                  enforcementMode=properties.enforcementMode,
                  scope=properties.scope,
                  parameters=properties.parameters
        | order by name asc
        """
        return self._arg_query(
            query,
            subscriptions=subscriptions,
            management_groups=management_groups,
        )

    async def _discover_compliance(
        self,
        subscriptions: list[str],
    ) -> dict:
        """Discover policy compliance state per subscription."""
        from azure.mgmt.policyinsights import PolicyInsightsClient

        compliance: dict[str, dict] = {}
        for sub_id in subscriptions:
            try:
                client = PolicyInsightsClient(self.credential, sub_id)
                summaries = list(
                    client.policy_states.summarize_for_subscription(
                        subscription_id=sub_id,
                    )
                )
                if summaries and summaries[0].results:
                    r = summaries[0].results
                    total = r.total_resources or 0
                    non_compliant = r.non_compliant_resources or 0
                    compliance[sub_id] = {
                        "total_resources": total,
                        "non_compliant_resources": non_compliant,
                        "compliance_pct": round(
                            (1 - non_compliant / max(total, 1)) * 100, 1
                        ),
                    }
                else:
                    compliance[sub_id] = {"error": "No compliance data"}
            except Exception as e:
                compliance[sub_id] = {"error": str(e)}
        return compliance

    async def _discover_rbac(
        self,
        management_groups: list[str] | None,
        subscriptions: list[str],
    ) -> list[dict]:
        """Discover RBAC role assignments."""
        query = """
        authorizationresources
        | where type == 'microsoft.authorization/roleassignments'
        | project id, name,
                  principalId=properties.principalId,
                  principalType=properties.principalType,
                  roleDefinitionId=properties.roleDefinitionId,
                  scope=properties.scope,
                  createdOn=properties.createdOn
        | order by name asc
        """
        return self._arg_query(
            query,
            subscriptions=subscriptions,
            management_groups=management_groups,
            max_results=500,
        )

    async def _discover_network(
        self,
        management_groups: list[str] | None,
        subscriptions: list[str],
    ) -> dict:
        """Discover network topology: VNets, peerings, NSGs, DNS zones."""
        vnets_query = """
        resources
        | where type == 'microsoft.network/virtualnetworks'
        | project id, name, location, resourceGroup, subscriptionId,
                  addressSpace=properties.addressSpace.addressPrefixes,
                  subnets=array_length(properties.subnets),
                  peerings=array_length(properties.virtualNetworkPeerings),
                  dnsServers=properties.dhcpOptions.dnsServers
        """
        vnets = self._arg_query(
            vnets_query,
            subscriptions=subscriptions,
            management_groups=management_groups,
        )

        peerings_query = """
        resources
        | where type == 'microsoft.network/virtualnetworks'
        | mv-expand peering = properties.virtualNetworkPeerings
        | project localVnet=name, remoteVnet=peering.properties.remoteVirtualNetwork.id,
                  peeringState=peering.properties.peeringState,
                  allowForwarding=peering.properties.allowForwardedTraffic
        """
        peerings = self._arg_query(
            peerings_query,
            subscriptions=subscriptions,
            management_groups=management_groups,
        )

        nsgs_query = """
        resources
        | where type == 'microsoft.network/networksecuritygroups'
        | project id, name, location, resourceGroup,
                  ruleCount=array_length(properties.securityRules)
        """
        nsgs = self._arg_query(
            nsgs_query,
            subscriptions=subscriptions,
            management_groups=management_groups,
        )

        dns_query = """
        resources
        | where type == 'microsoft.network/privatednszones'
        | project id, name, recordSets=properties.numberOfRecordSets
        """
        dns_zones = self._arg_query(
            dns_query,
            subscriptions=subscriptions,
            management_groups=management_groups,
        )

        fw_query = """
        resources
        | where type == 'microsoft.network/azurefirewalls'
        | project id, name, location, sku=properties.sku,
                  threatIntelMode=properties.threatIntelMode
        """
        firewalls = self._arg_query(
            fw_query,
            subscriptions=subscriptions,
            management_groups=management_groups,
        )

        return {
            "virtual_networks": vnets,
            "peerings": peerings,
            "network_security_groups": nsgs,
            "private_dns_zones": dns_zones,
            "firewalls": firewalls,
        }

    async def _discover_logging(
        self,
        management_groups: list[str] | None,
        subscriptions: list[str],
    ) -> dict:
        """Discover logging and monitoring configuration."""
        law_query = """
        resources
        | where type == 'microsoft.operationalinsights/workspaces'
        | project id, name, location, resourceGroup,
                  sku=properties.sku.name,
                  retentionDays=properties.retentionInDays,
                  dailyCapGb=properties.workspaceCapping.dailyQuotaGb
        """
        workspaces = self._arg_query(
            law_query,
            subscriptions=subscriptions,
            management_groups=management_groups,
        )

        automation_query = """
        resources
        | where type == 'microsoft.automation/automationaccounts'
        | project id, name, location, resourceGroup,
                  sku=properties.sku.name
        """
        automation = self._arg_query(
            automation_query,
            subscriptions=subscriptions,
            management_groups=management_groups,
        )

        diag_query = """
        resources
        | where type =~ 'microsoft.insights/diagnosticsettings'
        | project id, name, resourceGroup,
                  workspaceId=properties.workspaceId,
                  storageAccountId=properties.storageAccountId
        """
        diag_settings = self._arg_query(
            diag_query,
            subscriptions=subscriptions,
            management_groups=management_groups,
        )

        return {
            "log_analytics_workspaces": workspaces,
            "automation_accounts": automation,
            "diagnostic_settings": diag_settings,
        }

    async def _discover_security(
        self,
        management_groups: list[str] | None,
        subscriptions: list[str],
    ) -> dict:
        """Discover security posture: Key Vaults, Defender plans, Sentinel."""
        kv_query = """
        resources
        | where type == 'microsoft.keyvault/vaults'
        | project id, name, location, resourceGroup,
                  enableSoftDelete=properties.enableSoftDelete,
                  enablePurgeProtection=properties.enablePurgeProtection,
                  enableRbacAuthorization=properties.enableRbacAuthorization,
                  networkAcls=properties.networkAcls.defaultAction
        """
        key_vaults = self._arg_query(
            kv_query,
            subscriptions=subscriptions,
            management_groups=management_groups,
        )

        sentinel_query = """
        resources
        | where type == 'microsoft.securityinsights/settings'
           or type == 'microsoft.operationsmanagement/solutions'
        | where name contains 'SecurityInsights'
        | project id, name, type, location
        """
        sentinel = self._arg_query(
            sentinel_query,
            subscriptions=subscriptions,
            management_groups=management_groups,
        )

        storage_query = """
        resources
        | where type == 'microsoft.storage/storageaccounts'
        | project id, name, location,
                  httpsOnly=properties.supportsHttpsTrafficOnly,
                  minTls=properties.minimumTlsVersion,
                  publicBlob=properties.allowBlobPublicAccess,
                  networkDefault=properties.networkAcls.defaultAction
        """
        storage = self._arg_query(
            storage_query,
            subscriptions=subscriptions,
            management_groups=management_groups,
        )

        return {
            "key_vaults": key_vaults,
            "sentinel": sentinel,
            "storage_accounts": storage,
        }
