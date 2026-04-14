"""
Azure Resource Graph MCP Server

Exposes Azure Resource Graph queries as MCP tools for the agent workflow.
Supports resource inventory, compliance checking, drift detection, and
landing zone validation.
"""

import json
import logging
import os
import sys
from typing import Any

from azure.identity import DefaultAzureCredential
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import (
    QueryRequest,
    QueryRequestOptions,
    ResultFormat,
)

logger = logging.getLogger(__name__)

# MCP tool definitions
TOOLS = [
    {
        "name": "query_resources",
        "description": "Execute an Azure Resource Graph query and return results",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "KQL query for Resource Graph"},
                "subscriptions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Subscription IDs to query (defaults to configured subscription)",
                },
                "max_results": {"type": "integer", "default": 100},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_resource_inventory",
        "description": "Get resource inventory summary grouped by type",
        "inputSchema": {
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
            },
        },
    },
    {
        "name": "get_resource_details",
        "description": "Get detailed properties of a specific Azure resource",
        "inputSchema": {
            "type": "object",
            "properties": {
                "resource_id": {"type": "string", "description": "Full Azure resource ID"},
            },
            "required": ["resource_id"],
        },
    },
    {
        "name": "validate_landing_zone",
        "description": "Validate that key landing zone resources exist in a subscription",
        "inputSchema": {
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
            },
            "required": ["subscription_id"],
        },
    },
    {
        "name": "find_public_resources",
        "description": "Find resources with public IP addresses or endpoints",
        "inputSchema": {
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
            },
        },
    },
    {
        "name": "detect_drift",
        "description": "Detect recent manual changes using Resource Graph change tracking",
        "inputSchema": {
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
                "lookback_hours": {"type": "integer", "default": 1},
            },
        },
    },
]


class AzureResourceGraphServer:
    """MCP server exposing Azure Resource Graph capabilities."""

    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.client = ResourceGraphClient(self.credential)
        self.default_subscription = os.environ.get("AZURE_SUBSCRIPTION_ID", "")

    def query(self, query_str: str, subscriptions: list[str] = None, max_results: int = 100) -> list[dict]:
        """Execute a Resource Graph query."""
        options = QueryRequestOptions(
            result_format=ResultFormat.OBJECT_ARRAY,
            top=max_results,
        )
        request = QueryRequest(
            query=query_str,
            subscriptions=subscriptions or [self.default_subscription],
            options=options,
        )
        result = self.client.resources(request)
        return result.data if isinstance(result.data, list) else []

    def handle_tool_call(self, tool_name: str, arguments: dict) -> Any:
        """Route MCP tool calls to the appropriate handler."""
        sub = arguments.get("subscription_id", self.default_subscription)

        if tool_name == "query_resources":
            return self.query(
                arguments["query"],
                arguments.get("subscriptions", [sub]),
                arguments.get("max_results", 100),
            )

        elif tool_name == "get_resource_inventory":
            return self.query(
                "resources | summarize count() by type | order by count_ desc",
                [sub],
            )

        elif tool_name == "get_resource_details":
            return self.query(
                f'resources | where id =~ "{arguments["resource_id"]}" '
                f"| project id, name, type, location, resourceGroup, tags, properties, sku",
                [sub],
            )

        elif tool_name == "validate_landing_zone":
            checks = {}
            for resource_type, label in [
                ("microsoft.network/virtualnetworks", "vnet"),
                ("microsoft.network/networksecuritygroups", "nsg"),
                ("microsoft.operationalinsights/workspaces", "log_analytics"),
                ("microsoft.keyvault/vaults", "key_vault"),
            ]:
                results = self.query(
                    f'resources | where type == "{resource_type}" '
                    f'| where subscriptionId == "{sub}" | project id, name',
                    [sub],
                )
                checks[label] = {"exists": len(results) > 0, "count": len(results)}

            policies = self.query(
                "policyresources | where type == 'microsoft.authorization/policyassignments' | project id, name",
                [sub],
            )
            checks["policy_assignments"] = {"exists": len(policies) > 0, "count": len(policies)}

            return {
                "subscription_id": sub,
                "validation_passed": all(c["exists"] for c in checks.values()),
                "checks": checks,
            }

        elif tool_name == "find_public_resources":
            return self.query(
                f'resources | where type == "microsoft.network/publicipaddresses" '
                f'| where subscriptionId == "{sub}" '
                f"| project id, name, resourceGroup, ipAddress=properties.ipAddress",
                [sub],
            )

        elif tool_name == "detect_drift":
            hours = arguments.get("lookback_hours", 1)
            return self.query(
                f"resourcechanges "
                f"| where properties.changeAttributes.timestamp > ago({hours}h) "
                f'| where properties.changeAttributes.changedBy !contains "deploymentScript" '
                f"| project resourceId=properties.targetResourceId, "
                f"changedBy=properties.changeAttributes.changedBy, "
                f"timestamp=properties.changeAttributes.timestamp",
                [sub],
            )

        return {"error": f"Unknown tool: {tool_name}"}


def main():
    """MCP server entry point — reads JSON-RPC from stdin, writes to stdout."""
    server = AzureResourceGraphServer()
    logger.info("Azure Resource Graph MCP Server started")

    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            method = request.get("method", "")

            if method == "tools/list":
                response = {"tools": TOOLS}
            elif method == "tools/call":
                params = request.get("params", {})
                result = server.handle_tool_call(params["name"], params.get("arguments", {}))
                response = {"content": [{"type": "text", "text": json.dumps(result, default=str)}]}
            else:
                response = {"error": f"Unknown method: {method}"}

            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

        except Exception as e:
            error_response = {"error": str(e)}
            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
