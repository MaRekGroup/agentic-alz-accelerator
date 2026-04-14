"""
Azure Policy MCP Server

Exposes Azure Policy operations as MCP tools for the agent workflow.
Supports policy discovery, compliance checking, violation analysis,
and governance constraint generation.
"""

import json
import logging
import os
import sys
from typing import Any

from azure.identity import DefaultAzureCredential
from azure.mgmt.policyinsights import PolicyInsightsClient
from azure.mgmt.resource import PolicyClient

logger = logging.getLogger(__name__)

TOOLS = [
    {
        "name": "discover_policies",
        "description": "Discover Azure Policy assignments at a scope",
        "inputSchema": {
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string", "description": "Subscription ID to query"},
                "filter_effect": {
                    "type": "string",
                    "description": "Filter by effect (Deny, Audit, Modify, DeployIfNotExists)",
                },
            },
        },
    },
    {
        "name": "get_compliance_state",
        "description": "Get compliance summary for a scope",
        "inputSchema": {
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
            },
        },
    },
    {
        "name": "get_violations",
        "description": "Get non-compliant resources with details",
        "inputSchema": {
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
                "max_results": {"type": "integer", "default": 50},
            },
        },
    },
    {
        "name": "classify_policy_effects",
        "description": "Classify policies by effect (Deny, Audit, Modify, DINE)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
            },
        },
    },
    {
        "name": "generate_governance_constraints",
        "description": "Produce governance constraints JSON for IaC planning",
        "inputSchema": {
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
            },
        },
    },
]


class AzurePolicyServer:
    """MCP server exposing Azure Policy capabilities."""

    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.default_subscription = os.environ.get("AZURE_SUBSCRIPTION_ID", "")

    def _get_policy_client(self, subscription_id: str) -> PolicyClient:
        return PolicyClient(self.credential, subscription_id)

    def _get_insights_client(self, subscription_id: str) -> PolicyInsightsClient:
        return PolicyInsightsClient(self.credential, subscription_id)

    def handle_tool_call(self, tool_name: str, arguments: dict) -> Any:
        """Route MCP tool calls to the appropriate handler."""
        sub = arguments.get("subscription_id", self.default_subscription)

        if tool_name == "discover_policies":
            return self._discover_policies(sub, arguments.get("filter_effect"))
        elif tool_name == "get_compliance_state":
            return self._get_compliance_state(sub)
        elif tool_name == "get_violations":
            return self._get_violations(sub, arguments.get("max_results", 50))
        elif tool_name == "classify_policy_effects":
            return self._classify_policy_effects(sub)
        elif tool_name == "generate_governance_constraints":
            return self._generate_governance_constraints(sub)
        return {"error": f"Unknown tool: {tool_name}"}

    def _discover_policies(self, subscription_id: str, filter_effect: str = None) -> list[dict]:
        """Discover policy assignments at subscription scope."""
        client = self._get_policy_client(subscription_id)
        assignments = []
        for assignment in client.policy_assignments.list():
            entry = {
                "id": assignment.id,
                "name": assignment.name,
                "display_name": assignment.display_name,
                "policy_definition_id": assignment.policy_definition_id,
                "enforcement_mode": assignment.enforcement_mode,
                "scope": assignment.scope,
            }
            if filter_effect:
                # Only include if we can determine the effect matches
                definition_id = assignment.policy_definition_id or ""
                if filter_effect.lower() in definition_id.lower():
                    assignments.append(entry)
            else:
                assignments.append(entry)
        return assignments

    def _get_compliance_state(self, subscription_id: str) -> dict:
        """Get compliance summary for the subscription."""
        client = self._get_insights_client(subscription_id)
        scope = f"/subscriptions/{subscription_id}"
        summaries = list(client.policy_states.summarize_for_subscription(
            subscription_id=subscription_id
        ))
        if summaries and summaries[0].results:
            result = summaries[0].results
            return {
                "subscription_id": subscription_id,
                "total_resources": result.total_resources or 0,
                "non_compliant_resources": result.non_compliant_resources or 0,
                "non_compliant_policies": result.non_compliant_policies or 0,
                "compliance_percentage": (
                    round(
                        (1 - (result.non_compliant_resources or 0) / max(result.total_resources or 1, 1)) * 100, 1
                    )
                ),
            }
        return {"subscription_id": subscription_id, "error": "No compliance data available"}

    def _get_violations(self, subscription_id: str, max_results: int = 50) -> list[dict]:
        """Get non-compliant resources."""
        client = self._get_insights_client(subscription_id)
        violations = []
        results = client.policy_states.list_query_results_for_subscription(
            policy_states_resource="latest",
            subscription_id=subscription_id,
            query_options={"filter": "complianceState eq 'NonCompliant'", "top": max_results},
        )
        for state in results:
            violations.append({
                "resource_id": state.resource_id,
                "resource_type": state.resource_type,
                "policy_assignment_name": state.policy_assignment_name,
                "policy_definition_name": state.policy_definition_name,
                "compliance_state": state.compliance_state,
                "timestamp": str(state.timestamp) if state.timestamp else None,
            })
        return violations

    def _classify_policy_effects(self, subscription_id: str) -> dict:
        """Classify policies by their enforcement effect."""
        client = self._get_policy_client(subscription_id)
        classification = {"Deny": [], "Audit": [], "Modify": [], "DeployIfNotExists": [], "Other": []}
        for definition in client.policy_definitions.list():
            effect = "Other"
            if definition.policy_rule:
                then_block = definition.policy_rule.get("then", {})
                effect_value = then_block.get("effect", "Other")
                if isinstance(effect_value, str) and effect_value in classification:
                    effect = effect_value
            classification[effect].append({
                "name": definition.name,
                "display_name": definition.display_name,
            })
        return {k: {"count": len(v), "policies": v[:10]} for k, v in classification.items()}

    def _generate_governance_constraints(self, subscription_id: str) -> dict:
        """Generate governance constraints JSON for IaC planning."""
        deny_policies = self._discover_policies(subscription_id, "deny")
        compliance = self._get_compliance_state(subscription_id)
        return {
            "subscription_id": subscription_id,
            "constraints": {
                "deny_policies_count": len(deny_policies),
                "deny_policies": [{"name": p["name"], "display_name": p["display_name"]} for p in deny_policies[:20]],
                "compliance_state": compliance,
                "enforced_rules": [
                    "TLS 1.2 minimum",
                    "HTTPS only for web apps",
                    "No public IP on NICs",
                    "No public blob access",
                    "Key Vault purge protection",
                    "Managed Identity required",
                ],
            },
        }


def main():
    """MCP server entry point — reads JSON-RPC from stdin, writes to stdout."""
    server = AzurePolicyServer()
    logger.info("Azure Policy MCP Server started")

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
