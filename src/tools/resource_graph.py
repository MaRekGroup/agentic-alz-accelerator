"""
Resource Graph Client — queries Azure Resource Graph for inventory, compliance, and drift data.

Provides typed query methods for common landing zone queries plus a generic
query interface for ad-hoc Resource Graph Explorer queries.
"""

import logging

from azure.identity import DefaultAzureCredential
from azure.mgmt.resourcegraph import ResourceGraphClient as AzureRGClient
from azure.mgmt.resourcegraph.models import (
    QueryRequest,
    QueryRequestOptions,
    ResultFormat,
)

from src.config.settings import Settings

logger = logging.getLogger(__name__)


class ResourceGraphClient:
    """Wraps Azure Resource Graph for landing zone queries."""

    def __init__(self, credential: DefaultAzureCredential, settings: Settings):
        self.credential = credential
        self.settings = settings
        self.client = AzureRGClient(credential)

    async def query(
        self,
        query_str: str,
        subscriptions: list[str] | None = None,
        management_groups: list[str] | None = None,
        max_results: int = 100,
    ) -> list[dict]:
        """Execute a Resource Graph query."""
        options = QueryRequestOptions(
            result_format=ResultFormat.OBJECT_ARRAY,
            top=max_results,
        )

        request = QueryRequest(
            query=query_str,
            subscriptions=subscriptions or [self.settings.azure.subscription_id],
            management_groups=management_groups,
            options=options,
        )

        logger.debug(f"Resource Graph query: {query_str[:200]}")
        result = self.client.resources(request)

        rows = result.data if isinstance(result.data, list) else []
        logger.debug(f"Query returned {len(rows)} results")
        return rows

    async def get_resource_inventory(self, scope: str) -> dict:
        """Get resource inventory summary for a scope."""
        count_query = """
        resources
        | summarize total=count(), byType=count() by type
        | order by byType desc
        """

        results = await self.query(count_query)

        total = sum(r.get("total", 0) for r in results) if results else 0
        by_type = {r.get("type", ""): r.get("byType", 0) for r in results}

        return {
            "total_count": total,
            "by_type": by_type,
            "scope": scope,
        }

    async def get_resource_details(self, resource_id: str) -> dict:
        """Get detailed properties of a specific resource."""
        query = f"""
        resources
        | where id =~ "{resource_id}"
        | project id, name, type, location, resourceGroup,
                  subscriptionId, tags, properties, sku, kind
        """

        results = await self.query(query)
        return results[0] if results else {}

    async def validate_landing_zone(self, subscription_id: str) -> dict:
        """Validate that key landing zone resources exist."""
        checks = {}

        # Check for VNet
        vnets = await self.query(
            f"""
            resources
            | where type == "microsoft.network/virtualnetworks"
            | where subscriptionId == "{subscription_id}"
            | project id, name, location, properties.addressSpace.addressPrefixes
            """,
            subscriptions=[subscription_id],
        )
        checks["virtual_networks"] = {
            "exists": len(vnets) > 0,
            "count": len(vnets),
            "details": vnets,
        }

        # Check for NSGs
        nsgs = await self.query(
            f"""
            resources
            | where type == "microsoft.network/networksecuritygroups"
            | where subscriptionId == "{subscription_id}"
            | project id, name, location
            """,
            subscriptions=[subscription_id],
        )
        checks["network_security_groups"] = {
            "exists": len(nsgs) > 0,
            "count": len(nsgs),
        }

        # Check for Log Analytics
        law = await self.query(
            f"""
            resources
            | where type == "microsoft.operationalinsights/workspaces"
            | where subscriptionId == "{subscription_id}"
            | project id, name, location, properties.retentionInDays
            """,
            subscriptions=[subscription_id],
        )
        checks["log_analytics_workspace"] = {
            "exists": len(law) > 0,
            "count": len(law),
            "details": law,
        }

        # Check for Key Vault
        kv = await self.query(
            f"""
            resources
            | where type == "microsoft.keyvault/vaults"
            | where subscriptionId == "{subscription_id}"
            | project id, name, location
            """,
            subscriptions=[subscription_id],
        )
        checks["key_vault"] = {
            "exists": len(kv) > 0,
            "count": len(kv),
        }

        # Check for Policy Assignments
        policies = await self.query(
            """
            policyresources
            | where type == "microsoft.authorization/policyassignments"
            | project id, name, properties.displayName, properties.policyDefinitionId
            """,
            subscriptions=[subscription_id],
        )
        checks["policy_assignments"] = {
            "exists": len(policies) > 0,
            "count": len(policies),
        }

        all_passed = all(c.get("exists", False) for c in checks.values())
        return {
            "subscription_id": subscription_id,
            "validation_passed": all_passed,
            "checks": checks,
        }

    async def find_resources_without_tags(
        self,
        required_tags: list[str],
        subscription_id: str | None = None,
    ) -> list[dict]:
        """Find resources missing required tags."""
        sub = subscription_id or self.settings.azure.subscription_id
        tag_conditions = " or ".join(
            [f"isnull(tags.{tag})" for tag in required_tags]
        )

        query = f"""
        resources
        | where subscriptionId == "{sub}"
        | where {tag_conditions}
        | project id, name, type, resourceGroup, tags
        | limit 100
        """
        return await self.query(query, subscriptions=[sub])

    async def get_public_ip_resources(
        self, subscription_id: str | None = None
    ) -> list[dict]:
        """Find all resources with public IP addresses."""
        sub = subscription_id or self.settings.azure.subscription_id
        return await self.query(
            f"""
            resources
            | where type == "microsoft.network/publicipaddresses"
            | where subscriptionId == "{sub}"
            | project id, name, resourceGroup,
                      ipAddress=properties.ipAddress,
                      allocationMethod=properties.publicIPAllocationMethod,
                      associatedTo=properties.ipConfiguration.id
            """,
            subscriptions=[sub],
        )
