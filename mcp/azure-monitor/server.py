"""
Azure Monitor MCP Server

Exposes Azure Monitor operations as MCP tools for the agent workflow.
Supports secure score queries, security recommendations, activity log
analysis, alert rule inspection, and diagnostic settings validation.
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Any

from azure.identity import DefaultAzureCredential
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.resource import ResourceManagementClient

logger = logging.getLogger(__name__)

TOOLS = [
    {
        "name": "get_secure_score",
        "description": "Get Defender for Cloud secure score",
        "inputSchema": {
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
            },
        },
    },
    {
        "name": "get_recommendations",
        "description": "Get security recommendations",
        "inputSchema": {
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
                "max_results": {"type": "integer", "default": 20},
            },
        },
    },
    {
        "name": "query_activity_log",
        "description": "Query activity log for manual changes",
        "inputSchema": {
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
                "lookback_hours": {"type": "integer", "default": 24},
                "operation_filter": {
                    "type": "string",
                    "description": "Filter by operation (e.g., 'Microsoft.Resources/deployments/write')",
                },
            },
        },
    },
    {
        "name": "get_alert_rules",
        "description": "List configured alert rules",
        "inputSchema": {
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
            },
        },
    },
    {
        "name": "check_diagnostic_settings",
        "description": "Verify diagnostic settings are configured",
        "inputSchema": {
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
                "resource_id": {
                    "type": "string",
                    "description": "Specific resource to check (optional - checks all if omitted)",
                },
            },
        },
    },
]


class AzureMonitorServer:
    """MCP server exposing Azure Monitor capabilities."""

    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.default_subscription = os.environ.get("AZURE_SUBSCRIPTION_ID", "")

    def _get_monitor_client(self, subscription_id: str) -> MonitorManagementClient:
        return MonitorManagementClient(self.credential, subscription_id)

    def _get_resource_client(self, subscription_id: str) -> ResourceManagementClient:
        return ResourceManagementClient(self.credential, subscription_id)

    def handle_tool_call(self, tool_name: str, arguments: dict) -> Any:
        """Route MCP tool calls to the appropriate handler."""
        sub = arguments.get("subscription_id", self.default_subscription)

        if tool_name == "get_secure_score":
            return self._get_secure_score(sub)
        elif tool_name == "get_recommendations":
            return self._get_recommendations(sub, arguments.get("max_results", 20))
        elif tool_name == "query_activity_log":
            return self._query_activity_log(
                sub, arguments.get("lookback_hours", 24), arguments.get("operation_filter")
            )
        elif tool_name == "get_alert_rules":
            return self._get_alert_rules(sub)
        elif tool_name == "check_diagnostic_settings":
            return self._check_diagnostic_settings(sub, arguments.get("resource_id"))
        return {"error": f"Unknown tool: {tool_name}"}

    def _get_secure_score(self, subscription_id: str) -> dict:
        """Get Defender for Cloud secure score via REST."""
        import subprocess

        result = subprocess.run(
            [
                "az", "security", "secure-score-controls", "list",
                "--subscription", subscription_id,
                "--output", "json",
            ],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                total_score = sum(item.get("score", {}).get("current", 0) for item in data)
                max_score = sum(item.get("score", {}).get("max", 0) for item in data)
                return {
                    "subscription_id": subscription_id,
                    "current_score": total_score,
                    "max_score": max_score,
                    "percentage": round(total_score / max(max_score, 1) * 100, 1),
                    "control_count": len(data),
                }
            except json.JSONDecodeError:
                return {"error": "Failed to parse secure score data"}
        return {"error": result.stderr or "Failed to get secure score"}

    def _get_recommendations(self, subscription_id: str, max_results: int = 20) -> list[dict]:
        """Get security recommendations via Azure CLI."""
        import subprocess

        result = subprocess.run(
            [
                "az", "security", "assessment", "list",
                "--subscription", subscription_id,
                "--output", "json",
            ],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                recommendations = []
                for item in data[:max_results]:
                    status = item.get("status", {})
                    recommendations.append({
                        "name": item.get("displayName", ""),
                        "status": status.get("code", "Unknown"),
                        "severity": item.get("metadata", {}).get("severity", "Unknown"),
                        "resource_id": item.get("resourceDetails", {}).get("id", ""),
                    })
                return recommendations
            except json.JSONDecodeError:
                return [{"error": "Failed to parse recommendations"}]
        return [{"error": result.stderr or "Failed to get recommendations"}]

    def _query_activity_log(
        self, subscription_id: str, lookback_hours: int = 24, operation_filter: str = None
    ) -> list[dict]:
        """Query activity log for recent operations."""
        client = self._get_monitor_client(subscription_id)
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=lookback_hours)

        filter_str = (
            f"eventTimestamp ge '{start_time.isoformat()}' "
            f"and eventTimestamp le '{end_time.isoformat()}'"
        )
        if operation_filter:
            filter_str += f" and operationName.value eq '{operation_filter}'"

        events = []
        for event in client.activity_logs.list(filter=filter_str):
            events.append({
                "operation": event.operation_name.value if event.operation_name else "",
                "status": event.status.value if event.status else "",
                "caller": event.caller or "Unknown",
                "timestamp": str(event.event_timestamp) if event.event_timestamp else "",
                "resource_id": event.resource_id or "",
                "level": event.level.value if event.level else "",
            })
        return events

    def _get_alert_rules(self, subscription_id: str) -> list[dict]:
        """List configured metric alert rules."""
        client = self._get_monitor_client(subscription_id)
        alerts = []
        for alert in client.metric_alerts.list_by_subscription():
            alerts.append({
                "name": alert.name,
                "description": alert.description or "",
                "severity": alert.severity,
                "enabled": alert.enabled,
                "scopes": alert.scopes,
                "evaluation_frequency": str(alert.evaluation_frequency) if alert.evaluation_frequency else "",
            })
        return alerts

    def _check_diagnostic_settings(self, subscription_id: str, resource_id: str = None) -> dict:
        """Check diagnostic settings on resources."""
        client = self._get_monitor_client(subscription_id)

        if resource_id:
            # Check a specific resource
            try:
                settings = list(client.diagnostic_settings.list(resource_id))
                return {
                    "resource_id": resource_id,
                    "has_diagnostic_settings": len(settings) > 0,
                    "settings_count": len(settings),
                    "settings": [
                        {
                            "name": s.name,
                            "workspace_id": s.workspace_id or "",
                            "storage_account_id": s.storage_account_id or "",
                        }
                        for s in settings
                    ],
                }
            except Exception as e:
                return {"resource_id": resource_id, "error": str(e)}

        # Check key resource types across the subscription
        resource_client = self._get_resource_client(subscription_id)
        checked = []
        key_types = [
            "Microsoft.KeyVault/vaults",
            "Microsoft.Network/virtualNetworks",
            "Microsoft.Network/azureFirewalls",
            "Microsoft.Network/networkSecurityGroups",
        ]
        for resource in resource_client.resources.list():
            if resource.type in key_types:
                try:
                    settings = list(client.diagnostic_settings.list(resource.id))
                    checked.append({
                        "resource_id": resource.id,
                        "resource_type": resource.type,
                        "has_diagnostic_settings": len(settings) > 0,
                    })
                except Exception:
                    checked.append({
                        "resource_id": resource.id,
                        "resource_type": resource.type,
                        "has_diagnostic_settings": False,
                        "error": "Unable to check",
                    })
        unconfigured = [r for r in checked if not r["has_diagnostic_settings"]]
        return {
            "total_checked": len(checked),
            "configured": len(checked) - len(unconfigured),
            "unconfigured": len(unconfigured),
            "unconfigured_resources": unconfigured[:20],
        }


def main():
    """MCP server entry point — reads JSON-RPC from stdin, writes to stdout."""
    server = AzureMonitorServer()
    logger.info("Azure Monitor MCP Server started")

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
