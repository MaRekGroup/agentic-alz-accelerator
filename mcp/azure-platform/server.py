"""
Azure Platform MCP Server

Consolidated MCP server for Azure platform operations. Combines:
- Resource Graph queries (inventory, drift detection, LZ validation)
- Policy management (discovery, compliance, violations, governance constraints)
- Monitor operations (secure score, recommendations, activity log, alerts, diagnostics)
- Deployment operations (Bicep what-if/deploy, Terraform plan/apply, status)

Uses the official MCP Python SDK with async support.
"""

import asyncio
import json
import logging
import os
import subprocess
from datetime import datetime, timedelta, timezone
from typing import Any

from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# ---------------------------------------------------------------------------
# Azure SDK imports (lazy — only used when tools are actually called)
# ---------------------------------------------------------------------------
from azure.identity import DefaultAzureCredential
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.policyinsights import PolicyInsightsClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import (
    QueryRequest,
    QueryRequestOptions,
    ResultFormat,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    # --- Resource Graph ---
    Tool(
        name="query_resources",
        description="Execute an Azure Resource Graph KQL query and return results",
        inputSchema={
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
    ),
    Tool(
        name="get_resource_inventory",
        description="Get resource inventory summary grouped by type",
        inputSchema={
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
            },
        },
    ),
    Tool(
        name="get_resource_details",
        description="Get detailed properties of a specific Azure resource",
        inputSchema={
            "type": "object",
            "properties": {
                "resource_id": {"type": "string", "description": "Full Azure resource ID"},
            },
            "required": ["resource_id"],
        },
    ),
    Tool(
        name="validate_landing_zone",
        description="Validate that key landing zone resources exist in a subscription",
        inputSchema={
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
            },
            "required": ["subscription_id"],
        },
    ),
    Tool(
        name="find_public_resources",
        description="Find resources with public IP addresses or endpoints",
        inputSchema={
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
            },
        },
    ),
    Tool(
        name="detect_drift",
        description="Detect recent manual changes using Resource Graph change tracking",
        inputSchema={
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
                "lookback_hours": {"type": "integer", "default": 1},
            },
        },
    ),
    # --- Discovery (brownfield) ---
    Tool(
        name="discover_mg_hierarchy",
        description="Discover management group hierarchy with subscription placement (read-only)",
        inputSchema={
            "type": "object",
            "properties": {
                "management_group": {
                    "type": "string",
                    "description": "Root MG name to discover under (optional — discovers all if omitted)",
                },
            },
        },
    ),
    Tool(
        name="discover_subscription_inventory",
        description="Discover subscriptions with resource counts, tags, and MG placement (read-only)",
        inputSchema={
            "type": "object",
            "properties": {
                "subscription_id": {
                    "type": "string",
                    "description": "Specific subscription (optional — discovers all accessible if omitted)",
                },
            },
        },
    ),
    Tool(
        name="discover_rbac_snapshot",
        description="Discover RBAC role assignments across a scope (read-only)",
        inputSchema={
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
                "max_results": {"type": "integer", "default": 200},
            },
        },
    ),
    # --- Assessment ---
    Tool(
        name="run_wara_assessment",
        description="Run a WARA/CAF assessment against discovered Azure environment data. Returns scored findings by WAF pillar.",
        inputSchema={
            "type": "object",
            "properties": {
                "scope": {
                    "type": "string",
                    "description": "Assessment scope (subscription ID or management group name)",
                },
                "scope_type": {
                    "type": "string",
                    "enum": ["tenant", "management_group", "subscription"],
                    "description": "Scope type",
                    "default": "subscription",
                },
            },
            "required": ["scope"],
        },
    ),
    Tool(
        name="generate_assessment_reports",
        description="Generate assessment report artifacts (MD, JSON, Mermaid, ADR) from prior assessment results.",
        inputSchema={
            "type": "object",
            "properties": {
                "scope": {
                    "type": "string",
                    "description": "Assessment scope label for output directory naming",
                },
                "scope_type": {
                    "type": "string",
                    "enum": ["tenant", "management_group", "subscription"],
                    "default": "subscription",
                },
            },
            "required": ["scope"],
        },
    ),
    # --- Policy ---
    Tool(
        name="discover_policies",
        description="Discover Azure Policy assignments at a scope",
        inputSchema={
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string", "description": "Subscription ID to query"},
                "filter_effect": {
                    "type": "string",
                    "description": "Filter by effect (Deny, Audit, Modify, DeployIfNotExists)",
                },
            },
        },
    ),
    Tool(
        name="get_compliance_state",
        description="Get compliance summary for a scope",
        inputSchema={
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
            },
        },
    ),
    Tool(
        name="get_violations",
        description="Get non-compliant resources with details",
        inputSchema={
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
                "max_results": {"type": "integer", "default": 50},
            },
        },
    ),
    Tool(
        name="classify_policy_effects",
        description="Classify policies by effect (Deny, Audit, Modify, DINE)",
        inputSchema={
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
            },
        },
    ),
    Tool(
        name="generate_governance_constraints",
        description="Produce governance constraints JSON for IaC planning",
        inputSchema={
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
            },
        },
    ),
    # --- Monitor ---
    Tool(
        name="get_secure_score",
        description="Get Defender for Cloud secure score",
        inputSchema={
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
            },
        },
    ),
    Tool(
        name="get_recommendations",
        description="Get security recommendations",
        inputSchema={
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
                "max_results": {"type": "integer", "default": 20},
            },
        },
    ),
    Tool(
        name="query_activity_log",
        description="Query activity log for manual changes",
        inputSchema={
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
    ),
    Tool(
        name="get_alert_rules",
        description="List configured alert rules",
        inputSchema={
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
            },
        },
    ),
    Tool(
        name="check_diagnostic_settings",
        description="Verify diagnostic settings are configured for key resource types",
        inputSchema={
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
                "resource_id": {
                    "type": "string",
                    "description": "Specific resource to check (optional — checks all key types if omitted)",
                },
            },
        },
    ),
    # --- Deployment ---
    Tool(
        name="bicep_what_if",
        description="Run Bicep what-if analysis at subscription scope",
        inputSchema={
            "type": "object",
            "properties": {
                "template_file": {"type": "string", "description": "Path to Bicep template"},
                "parameters": {"type": "object", "description": "Template parameters"},
                "location": {"type": "string", "default": "southcentralus"},
                "subscription_id": {"type": "string"},
            },
            "required": ["template_file"],
        },
    ),
    Tool(
        name="bicep_deploy",
        description="Deploy Bicep template at subscription scope",
        inputSchema={
            "type": "object",
            "properties": {
                "template_file": {"type": "string", "description": "Path to Bicep template"},
                "parameters": {"type": "object", "description": "Template parameters"},
                "deployment_name": {"type": "string"},
                "location": {"type": "string", "default": "southcentralus"},
                "subscription_id": {"type": "string"},
            },
            "required": ["template_file", "deployment_name"],
        },
    ),
    Tool(
        name="terraform_plan",
        description="Run Terraform plan",
        inputSchema={
            "type": "object",
            "properties": {
                "working_directory": {"type": "string", "description": "Terraform module directory"},
                "var_file": {"type": "string", "description": "Path to tfvars file"},
            },
            "required": ["working_directory"],
        },
    ),
    Tool(
        name="terraform_apply",
        description="Apply Terraform configuration",
        inputSchema={
            "type": "object",
            "properties": {
                "working_directory": {"type": "string"},
                "plan_file": {"type": "string", "default": "tfplan"},
            },
            "required": ["working_directory"],
        },
    ),
    Tool(
        name="get_deployment_status",
        description="Get deployment status and outputs",
        inputSchema={
            "type": "object",
            "properties": {
                "deployment_name": {"type": "string"},
                "subscription_id": {"type": "string"},
            },
            "required": ["deployment_name"],
        },
    ),
    Tool(
        name="validate_deployment",
        description="Post-deployment resource validation — checks expected resource types exist",
        inputSchema={
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string"},
                "resource_group": {"type": "string"},
                "expected_resources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Expected resource types",
                },
            },
            "required": ["resource_group"],
        },
    ),
]

# ---------------------------------------------------------------------------
# Platform server — single class holding all Azure SDK clients
# ---------------------------------------------------------------------------


class AzurePlatformServer:
    """Consolidated Azure platform MCP server.

    Manages Azure SDK clients for Resource Graph, Policy, Monitor,
    and Deployment operations. Clients are created lazily on first use.
    """

    def __init__(self) -> None:
        self.credential = DefaultAzureCredential()
        self.default_sub = os.environ.get("AZURE_SUBSCRIPTION_ID", "")
        self._arg_client: ResourceGraphClient | None = None

    @property
    def arg_client(self) -> ResourceGraphClient:
        if self._arg_client is None:
            self._arg_client = ResourceGraphClient(self.credential)
        return self._arg_client

    def _sub(self, arguments: dict) -> str:
        return arguments.get("subscription_id") or self.default_sub

    # ── Resource Graph ────────────────────────────────────────────────────

    def _arg_query(
        self, query: str, subscriptions: list[str] | None = None, max_results: int = 100
    ) -> list[dict]:
        options = QueryRequestOptions(result_format=ResultFormat.OBJECT_ARRAY, top=max_results)
        request = QueryRequest(
            query=query,
            subscriptions=subscriptions or [self.default_sub],
            options=options,
        )
        result = self.arg_client.resources(request)
        return result.data if isinstance(result.data, list) else []

    def handle_query_resources(self, args: dict) -> list[dict]:
        sub = self._sub(args)
        return self._arg_query(
            args["query"],
            args.get("subscriptions", [sub]),
            args.get("max_results", 100),
        )

    def handle_get_resource_inventory(self, args: dict) -> list[dict]:
        return self._arg_query(
            "resources | summarize count() by type | order by count_ desc",
            [self._sub(args)],
        )

    def handle_get_resource_details(self, args: dict) -> list[dict]:
        sub = self._sub(args)
        rid = args["resource_id"]
        return self._arg_query(
            f'resources | where id =~ "{rid}" '
            f"| project id, name, type, location, resourceGroup, tags, properties, sku",
            [sub],
        )

    def handle_validate_landing_zone(self, args: dict) -> dict:
        sub = self._sub(args)
        checks: dict[str, dict] = {}
        for rtype, label in [
            ("microsoft.network/virtualnetworks", "vnet"),
            ("microsoft.network/networksecuritygroups", "nsg"),
            ("microsoft.operationalinsights/workspaces", "log_analytics"),
            ("microsoft.keyvault/vaults", "key_vault"),
        ]:
            results = self._arg_query(
                f'resources | where type == "{rtype}" '
                f'| where subscriptionId == "{sub}" | project id, name',
                [sub],
            )
            checks[label] = {"exists": len(results) > 0, "count": len(results)}

        policies = self._arg_query(
            "policyresources | where type == 'microsoft.authorization/policyassignments' | project id, name",
            [sub],
        )
        checks["policy_assignments"] = {"exists": len(policies) > 0, "count": len(policies)}

        return {
            "subscription_id": sub,
            "validation_passed": all(c["exists"] for c in checks.values()),
            "checks": checks,
        }

    def handle_find_public_resources(self, args: dict) -> list[dict]:
        sub = self._sub(args)
        return self._arg_query(
            'resources | where type == "microsoft.network/publicipaddresses" '
            f'| where subscriptionId == "{sub}" '
            "| project id, name, resourceGroup, ipAddress=properties.ipAddress",
            [sub],
        )

    def handle_detect_drift(self, args: dict) -> list[dict]:
        sub = self._sub(args)
        hours = args.get("lookback_hours", 1)
        return self._arg_query(
            f"resourcechanges "
            f"| where properties.changeAttributes.timestamp > ago({hours}h) "
            '| where properties.changeAttributes.changedBy !contains "deploymentScript" '
            "| project resourceId=properties.targetResourceId, "
            "changedBy=properties.changeAttributes.changedBy, "
            "timestamp=properties.changeAttributes.timestamp",
            [sub],
        )

    # ── Discovery (brownfield) ────────────────────────────────────────────

    def handle_discover_mg_hierarchy(self, args: dict) -> list[dict]:
        mg = args.get("management_group")
        mg_list = [mg] if mg else None
        subs = [self.default_sub] if self.default_sub else None
        # MG hierarchy
        mgs = self._arg_query(
            "resourcecontainers "
            "| where type == 'microsoft.management/managementgroups' "
            "| project id, name, displayName=properties.displayName, "
            "parent=properties.details.parent.id, tenantId=tenantId "
            "| order by name asc",
            subscriptions=subs,
            management_groups=mg_list,
            max_results=500,
        )
        # Subscriptions under those MGs
        sub_results = self._arg_query(
            "resourcecontainers "
            "| where type == 'microsoft.resources/subscriptions' "
            "| project subscriptionId, name, displayName=properties.displayName, "
            "state=properties.state, "
            "managementGroup=properties.managementGroupAncestorsChain "
            "| order by name asc",
            subscriptions=subs,
            management_groups=mg_list,
            max_results=500,
        )
        return {"management_groups": mgs, "subscriptions": sub_results}

    def handle_discover_subscription_inventory(self, args: dict) -> dict:
        sub = self._sub(args)
        subs = [sub] if sub else None
        # Resource counts by type
        by_type = self._arg_query(
            "resources | summarize count=count() by type | order by count desc",
            subs,
        )
        # Resource counts by location
        by_location = self._arg_query(
            "resources | summarize count=count() by location | order by count desc",
            subs,
        )
        # Subscription metadata
        sub_info = self._arg_query(
            "resourcecontainers "
            "| where type == 'microsoft.resources/subscriptions' "
            f"| where subscriptionId == '{sub}' "
            "| project subscriptionId, name, tags, "
            "managementGroup=properties.managementGroupAncestorsChain",
            subs,
        )
        total = sum(r.get("count", 0) for r in by_type)
        return {
            "subscription_id": sub,
            "subscription_info": sub_info[0] if sub_info else {},
            "total_resources": total,
            "by_type": by_type,
            "by_location": by_location,
        }

    def handle_discover_rbac_snapshot(self, args: dict) -> list[dict]:
        sub = self._sub(args)
        max_results = args.get("max_results", 200)
        return self._arg_query(
            "authorizationresources "
            "| where type == 'microsoft.authorization/roleassignments' "
            "| project id, name, "
            "principalId=properties.principalId, "
            "principalType=properties.principalType, "
            "roleDefinitionId=properties.roleDefinitionId, "
            "scope=properties.scope, "
            "createdOn=properties.createdOn "
            "| order by name asc",
            [sub],
            max_results=max_results,
        )

    # ── Assessment ────────────────────────────────────────────────────────

    def handle_run_wara_assessment(self, args: dict) -> dict:
        """Run WARA assessment: discover → evaluate → return scored results."""
        import asyncio as _asyncio
        from src.config.settings import Settings
        from src.tools.discovery import DiscoveryCollector, DiscoveryScope
        from src.tools.wara_engine import WaraEngine

        scope = args["scope"]
        scope_type = args.get("scope_type", "subscription")

        settings = Settings()
        collector = DiscoveryCollector(self.credential, settings)
        engine = WaraEngine(self.credential, settings)

        discovery_scope = DiscoveryScope(scope_type)
        discovery = _asyncio.get_event_loop().run_until_complete(
            collector.discover(scope=scope, scope_type=discovery_scope)
        )

        subscriptions = [
            s.get("subscriptionId", s.get("id", ""))
            for s in discovery.subscriptions
            if s.get("subscriptionId") or s.get("id")
        ]
        if not subscriptions and settings.azure.subscription_id:
            subscriptions = [settings.azure.subscription_id]

        assessment = _asyncio.get_event_loop().run_until_complete(
            engine.assess(discovery, subscriptions=subscriptions)
        )
        return assessment.to_dict()

    def handle_generate_assessment_reports(self, args: dict) -> dict:
        """Generate report artifacts from a fresh discovery + assessment."""
        import asyncio as _asyncio
        from src.config.settings import Settings
        from src.tools.discovery import DiscoveryCollector, DiscoveryScope
        from src.tools.wara_engine import WaraEngine
        from src.tools.report_generator import ReportGenerator

        scope = args["scope"]
        scope_type = args.get("scope_type", "subscription")

        settings = Settings()
        collector = DiscoveryCollector(self.credential, settings)
        engine = WaraEngine(self.credential, settings)
        reporter = ReportGenerator(output_dir=settings.assess.output_dir)

        discovery_scope = DiscoveryScope(scope_type)
        discovery = _asyncio.get_event_loop().run_until_complete(
            collector.discover(scope=scope, scope_type=discovery_scope)
        )

        subscriptions = [
            s.get("subscriptionId", s.get("id", ""))
            for s in discovery.subscriptions
            if s.get("subscriptionId") or s.get("id")
        ]
        if not subscriptions and settings.azure.subscription_id:
            subscriptions = [settings.azure.subscription_id]

        assessment = _asyncio.get_event_loop().run_until_complete(
            engine.assess(discovery, subscriptions=subscriptions)
        )

        outputs = reporter.generate_all(discovery, assessment, scope_label=scope)
        return {
            "overall_score": assessment.overall_score,
            "findings_count": len(assessment.findings),
            "outputs": {k: str(v) for k, v in outputs.items()},
        }

    # ── Policy ────────────────────────────────────────────────────────────

    def _insights_client(self, sub: str) -> PolicyInsightsClient:
        return PolicyInsightsClient(self.credential, sub)

    def handle_discover_policies(self, args: dict) -> list[dict]:
        sub = self._sub(args)
        filter_effect = args.get("filter_effect")
        query = (
            "policyresources "
            "| where type == 'microsoft.authorization/policyassignments' "
            "| project id, name, properties"
        )
        rows = self._arg_query(query, [sub], max_results=1000)
        assignments = []
        for r in rows:
            props = r.get("properties", {})
            entry = {
                "id": r.get("id"),
                "name": r.get("name"),
                "display_name": props.get("displayName"),
                "policy_definition_id": props.get("policyDefinitionId"),
                "enforcement_mode": props.get("enforcementMode"),
                "scope": props.get("scope"),
            }
            if filter_effect:
                defn_id = (props.get("policyDefinitionId") or "").lower()
                if filter_effect.lower() in defn_id:
                    assignments.append(entry)
            else:
                assignments.append(entry)
        return assignments

    def handle_get_compliance_state(self, args: dict) -> dict:
        sub = self._sub(args)
        client = self._insights_client(sub)
        summaries = list(client.policy_states.summarize_for_subscription(subscription_id=sub))
        if summaries and summaries[0].results:
            r = summaries[0].results
            total = r.total_resources or 0
            non_compliant = r.non_compliant_resources or 0
            return {
                "subscription_id": sub,
                "total_resources": total,
                "non_compliant_resources": non_compliant,
                "non_compliant_policies": r.non_compliant_policies or 0,
                "compliance_percentage": round((1 - non_compliant / max(total, 1)) * 100, 1),
            }
        return {"subscription_id": sub, "error": "No compliance data available"}

    def handle_get_violations(self, args: dict) -> list[dict]:
        sub = self._sub(args)
        max_results = args.get("max_results", 50)
        client = self._insights_client(sub)
        violations = []
        results = client.policy_states.list_query_results_for_subscription(
            policy_states_resource="latest",
            subscription_id=sub,
            query_options={"filter": "complianceState eq 'NonCompliant'", "top": max_results},
        )
        for s in results:
            violations.append({
                "resource_id": s.resource_id,
                "resource_type": s.resource_type,
                "policy_assignment_name": s.policy_assignment_name,
                "policy_definition_name": s.policy_definition_name,
                "compliance_state": s.compliance_state,
                "timestamp": str(s.timestamp) if s.timestamp else None,
            })
        return violations

    def handle_classify_policy_effects(self, args: dict) -> dict:
        sub = self._sub(args)
        query = (
            "policyresources "
            "| where type == 'microsoft.authorization/policydefinitions' "
            "| project name, properties"
        )
        rows = self._arg_query(query, [sub], max_results=1000)
        classification: dict[str, list] = {
            "Deny": [], "Audit": [], "Modify": [], "DeployIfNotExists": [], "Other": [],
        }
        for r in rows:
            props = r.get("properties", {})
            effect = "Other"
            rule = props.get("policyRule", {})
            if isinstance(rule, dict):
                then_block = rule.get("then", {})
                ev = then_block.get("effect", "Other")
                if isinstance(ev, str) and ev in classification:
                    effect = ev
            display_name = props.get("displayName")
            classification[effect].append({"name": r.get("name"), "display_name": display_name})
        return {k: {"count": len(v), "policies": v[:10]} for k, v in classification.items()}

    def handle_generate_governance_constraints(self, args: dict) -> dict:
        sub = self._sub(args)
        deny_policies = self.handle_discover_policies({"subscription_id": sub, "filter_effect": "deny"})
        compliance = self.handle_get_compliance_state({"subscription_id": sub})
        return {
            "subscription_id": sub,
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

    # ── Monitor ───────────────────────────────────────────────────────────

    def _monitor_client(self, sub: str) -> MonitorManagementClient:
        return MonitorManagementClient(self.credential, sub)

    def _resource_client(self, sub: str) -> ResourceManagementClient:
        return ResourceManagementClient(self.credential, sub)

    def handle_get_secure_score(self, args: dict) -> dict:
        sub = self._sub(args)
        result = subprocess.run(
            ["az", "security", "secure-score-controls", "list",
             "--subscription", sub, "--output", "json"],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                total = sum(item.get("score", {}).get("current", 0) for item in data)
                maximum = sum(item.get("score", {}).get("max", 0) for item in data)
                return {
                    "subscription_id": sub,
                    "current_score": total,
                    "max_score": maximum,
                    "percentage": round(total / max(maximum, 1) * 100, 1),
                    "control_count": len(data),
                }
            except json.JSONDecodeError:
                return {"error": "Failed to parse secure score data"}
        return {"error": result.stderr or "Failed to get secure score"}

    def handle_get_recommendations(self, args: dict) -> list[dict]:
        sub = self._sub(args)
        max_results = args.get("max_results", 20)
        result = subprocess.run(
            ["az", "security", "assessment", "list",
             "--subscription", sub, "--output", "json"],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                return [
                    {
                        "name": item.get("displayName", ""),
                        "status": item.get("status", {}).get("code", "Unknown"),
                        "severity": item.get("metadata", {}).get("severity", "Unknown"),
                        "resource_id": item.get("resourceDetails", {}).get("id", ""),
                    }
                    for item in data[:max_results]
                ]
            except json.JSONDecodeError:
                return [{"error": "Failed to parse recommendations"}]
        return [{"error": result.stderr or "Failed to get recommendations"}]

    def handle_query_activity_log(self, args: dict) -> list[dict]:
        sub = self._sub(args)
        lookback = args.get("lookback_hours", 24)
        op_filter = args.get("operation_filter")
        client = self._monitor_client(sub)
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=lookback)
        filter_str = (
            f"eventTimestamp ge '{start_time.isoformat()}' "
            f"and eventTimestamp le '{end_time.isoformat()}'"
        )
        if op_filter:
            filter_str += f" and operationName.value eq '{op_filter}'"
        events = []
        for ev in client.activity_logs.list(filter=filter_str):
            events.append({
                "operation": ev.operation_name.value if ev.operation_name else "",
                "status": ev.status.value if ev.status else "",
                "caller": ev.caller or "Unknown",
                "timestamp": str(ev.event_timestamp) if ev.event_timestamp else "",
                "resource_id": ev.resource_id or "",
                "level": ev.level.value if ev.level else "",
            })
        return events

    def handle_get_alert_rules(self, args: dict) -> list[dict]:
        sub = self._sub(args)
        client = self._monitor_client(sub)
        return [
            {
                "name": a.name,
                "description": a.description or "",
                "severity": a.severity,
                "enabled": a.enabled,
                "scopes": a.scopes,
                "evaluation_frequency": str(a.evaluation_frequency) if a.evaluation_frequency else "",
            }
            for a in client.metric_alerts.list_by_subscription()
        ]

    def handle_check_diagnostic_settings(self, args: dict) -> dict:
        sub = self._sub(args)
        client = self._monitor_client(sub)
        resource_id = args.get("resource_id")

        if resource_id:
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

        resource_client = self._resource_client(sub)
        key_types = [
            "Microsoft.KeyVault/vaults",
            "Microsoft.Network/virtualNetworks",
            "Microsoft.Network/azureFirewalls",
            "Microsoft.Network/networkSecurityGroups",
        ]
        checked = []
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

    # ── Deployment ────────────────────────────────────────────────────────

    def handle_bicep_what_if(self, args: dict) -> dict:
        sub = self._sub(args)
        template = args["template_file"]
        location = args.get("location", "southcentralus")
        params = args.get("parameters", {})
        cmd = [
            "az", "deployment", "sub", "what-if",
            "--location", location,
            "--template-file", template,
            "--subscription", sub,
        ]
        for k, v in params.items():
            cmd.extend(["--parameters", f"{k}={v}"])
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr if result.returncode != 0 else None,
        }

    def handle_bicep_deploy(self, args: dict) -> dict:
        sub = self._sub(args)
        template = args["template_file"]
        name = args["deployment_name"]
        location = args.get("location", "southcentralus")
        params = args.get("parameters", {})
        cmd = [
            "az", "deployment", "sub", "create",
            "--location", location,
            "--template-file", template,
            "--name", name,
            "--subscription", sub,
        ]
        for k, v in params.items():
            cmd.extend(["--parameters", f"{k}={v}"])
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return {
            "success": result.returncode == 0,
            "deployment_name": name,
            "output": result.stdout[:5000] if result.stdout else None,
            "errors": result.stderr if result.returncode != 0 else None,
        }

    def handle_terraform_plan(self, args: dict) -> dict:
        working_dir = args["working_directory"]
        var_file = args.get("var_file")
        cmd = ["terraform", "plan", "-out=tfplan", "-no-color"]
        if var_file:
            cmd.extend(["-var-file", var_file])
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=working_dir, timeout=300)
        return {
            "success": result.returncode == 0,
            "output": result.stdout[:5000],
            "errors": result.stderr if result.returncode != 0 else None,
        }

    def handle_terraform_apply(self, args: dict) -> dict:
        working_dir = args["working_directory"]
        plan_file = args.get("plan_file", "tfplan")
        cmd = ["terraform", "apply", "-auto-approve", "-no-color", plan_file]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=working_dir, timeout=600)
        return {
            "success": result.returncode == 0,
            "output": result.stdout[:5000],
            "errors": result.stderr if result.returncode != 0 else None,
        }

    def handle_get_deployment_status(self, args: dict) -> dict:
        sub = self._sub(args)
        name = args["deployment_name"]
        client = self._resource_client(sub)
        try:
            dep = client.deployments.get_at_subscription_scope(name)
            outputs = {}
            if dep.properties and dep.properties.outputs:
                for k, v in dep.properties.outputs.items():
                    outputs[k] = v.get("value")
            return {
                "deployment_name": name,
                "provisioning_state": dep.properties.provisioning_state if dep.properties else "Unknown",
                "timestamp": str(dep.properties.timestamp) if dep.properties else None,
                "outputs": outputs,
            }
        except Exception as e:
            return {"error": str(e), "deployment_name": name}

    def handle_validate_deployment(self, args: dict) -> dict:
        sub = self._sub(args)
        client = self._resource_client(sub)
        rg = args["resource_group"]
        expected = set(args.get("expected_resources", []))
        found_types = set()
        for resource in client.resources.list_by_resource_group(rg):
            found_types.add(resource.type)
        missing = expected - found_types
        return {
            "resource_group": rg,
            "validation_passed": len(missing) == 0,
            "found_resource_types": sorted(found_types),
            "missing_resource_types": sorted(missing),
            "total_resources": len(found_types),
        }


# ---------------------------------------------------------------------------
# Tool dispatch map
# ---------------------------------------------------------------------------

_DISPATCH: dict[str, str] = {
    # Resource Graph
    "query_resources": "handle_query_resources",
    "get_resource_inventory": "handle_get_resource_inventory",
    "get_resource_details": "handle_get_resource_details",
    "validate_landing_zone": "handle_validate_landing_zone",
    "find_public_resources": "handle_find_public_resources",
    "detect_drift": "handle_detect_drift",
    # Discovery (brownfield)
    "discover_mg_hierarchy": "handle_discover_mg_hierarchy",
    "discover_subscription_inventory": "handle_discover_subscription_inventory",
    "discover_rbac_snapshot": "handle_discover_rbac_snapshot",
    # Assessment
    "run_wara_assessment": "handle_run_wara_assessment",
    "generate_assessment_reports": "handle_generate_assessment_reports",
    # Policy
    "discover_policies": "handle_discover_policies",
    "get_compliance_state": "handle_get_compliance_state",
    "get_violations": "handle_get_violations",
    "classify_policy_effects": "handle_classify_policy_effects",
    "generate_governance_constraints": "handle_generate_governance_constraints",
    # Monitor
    "get_secure_score": "handle_get_secure_score",
    "get_recommendations": "handle_get_recommendations",
    "query_activity_log": "handle_query_activity_log",
    "get_alert_rules": "handle_get_alert_rules",
    "check_diagnostic_settings": "handle_check_diagnostic_settings",
    # Deployment
    "bicep_what_if": "handle_bicep_what_if",
    "bicep_deploy": "handle_bicep_deploy",
    "terraform_plan": "handle_terraform_plan",
    "terraform_apply": "handle_terraform_apply",
    "get_deployment_status": "handle_get_deployment_status",
    "validate_deployment": "handle_validate_deployment",
}

# ---------------------------------------------------------------------------
# MCP server setup
# ---------------------------------------------------------------------------


def create_server() -> tuple[Server, AzurePlatformServer]:
    """Create and configure the MCP server instance."""
    server = Server("azure-platform")
    platform = AzurePlatformServer()

    @server.list_tools()
    async def handle_list_tools() -> list[Tool]:
        return TOOLS

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        handler_name = _DISPATCH.get(name)
        if not handler_name:
            return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]
        handler = getattr(platform, handler_name)
        result = handler(arguments or {})
        return [TextContent(type="text", text=json.dumps(result, default=str))]

    return server, platform


async def main() -> None:
    """Entry point — runs the MCP server over stdio."""
    server, _platform = create_server()
    logger.info("Azure Platform MCP Server started (25 tools)")

    async with stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options(
            notification_options=NotificationOptions(tools_changed=True)
        )
        await server.run(read_stream, write_stream, init_options)


def run() -> None:
    """Synchronous entry point."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
