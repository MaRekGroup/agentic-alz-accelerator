"""
Governance Agent (Warden) — Azure Policy discovery and compliance constraint generation.

Discovers Azure Policy assignments at the target scope, classifies effects,
and produces governance constraints that the IaC Planner and Code Gen agents
must satisfy. Aligned with CAF Governance design area.
"""

import logging
from typing import Annotated

from azure.identity import DefaultAzureCredential
from semantic_kernel import Kernel
from semantic_kernel.functions.kernel_function_decorator import kernel_function

from src.config.settings import Settings
from src.tools.policy_checker import PolicyChecker
from src.tools.resource_graph import ResourceGraphClient

logger = logging.getLogger(__name__)

# Non-negotiable security baseline rules
SECURITY_BASELINE = [
    {
        "id": "sec-001",
        "rule": "TLS 1.2 minimum",
        "bicep_property": "minimumTlsVersion: 'TLS1_2'",
        "terraform_argument": 'min_tls_version = "1.2"',
        "severity": "blocks_deployment",
    },
    {
        "id": "sec-002",
        "rule": "HTTPS-only traffic",
        "bicep_property": "supportsHttpsTrafficOnly: true",
        "terraform_argument": "https_traffic_only_enabled = true",
        "severity": "blocks_deployment",
    },
    {
        "id": "sec-003",
        "rule": "No public blob access",
        "bicep_property": "allowBlobPublicAccess: false",
        "terraform_argument": "allow_nested_items_to_be_public = false",
        "severity": "blocks_deployment",
    },
    {
        "id": "sec-004",
        "rule": "Managed Identity preferred",
        "bicep_property": "identity: { type: 'SystemAssigned' }",
        "terraform_argument": 'identity { type = "SystemAssigned" }',
        "severity": "blocks_deployment",
    },
    {
        "id": "sec-005",
        "rule": "Azure AD-only SQL auth",
        "bicep_property": "azureADOnlyAuthentication: true",
        "terraform_argument": "azuread_authentication_only = true",
        "severity": "blocks_deployment",
    },
    {
        "id": "sec-006",
        "rule": "Public network disabled (prod)",
        "bicep_property": "publicNetworkAccess: 'Disabled'",
        "terraform_argument": "public_network_access_enabled = false",
        "severity": "blocks_deployment",
        "environments": ["prod", "production"],
    },
]

# Extended anti-pattern checks
EXTENDED_CHECKS = [
    {"pattern": "enableNonSslPort: true", "tf_pattern": "enable_non_ssl_port = true", "description": "Redis non-SSL port", "severity": "blocks_deployment"},
    {"pattern": "ftpsState: 'AllAllowed'", "tf_pattern": 'ftps_state = "AllAllowed"', "description": "FTPS allowed", "severity": "blocks_deployment"},
    {"pattern": "remoteDebuggingEnabled: true", "tf_pattern": "remote_debugging_enabled = true", "description": "Remote debugging", "severity": "blocks_deployment"},
    {"pattern": "disableLocalAuth: false", "tf_pattern": "local_authentication_disabled = false", "description": "Cosmos DB local auth", "severity": "blocks_deployment"},
    {"pattern": "sslEnforcement: 'Disabled'", "tf_pattern": "ssl_enforcement_enabled = false", "description": "PostgreSQL SSL disabled", "severity": "blocks_deployment"},
    {"pattern": "networkAcls.defaultAction: 'Allow'", "tf_pattern": 'default_action = "Allow"', "description": "Key Vault network open", "severity": "warning"},
    {"pattern": "allowedOrigins: ['*']", "tf_pattern": 'allowed_origins = ["*"]', "description": "Wildcard CORS", "severity": "warning"},
]


class GovernanceAgent:
    """Discovers Azure Policy constraints and enforces security baseline."""

    def __init__(
        self,
        kernel: Kernel,
        credential: DefaultAzureCredential,
        settings: Settings,
    ):
        self.kernel = kernel
        self.credential = credential
        self.settings = settings
        self.policy_checker = PolicyChecker(credential, settings)
        self.resource_graph = ResourceGraphClient(credential, settings)
        self.kernel.add_plugin(self, plugin_name="governance")

    @kernel_function(
        name="discover_policy_constraints",
        description="Discover Azure Policy assignments and produce governance constraints",
    )
    async def discover_policy_constraints(
        self,
        scope: Annotated[str, "Azure scope for policy discovery"] = "",
    ) -> dict:
        """Discover policies and produce constraints for IaC planning."""
        discovery_scope = scope or (
            f"/providers/Microsoft.Management/managementGroups/"
            f"{self.settings.azure.management_group_prefix}"
        )

        logger.info(f"Discovering policy constraints at scope: {discovery_scope}")

        # Get policy assignments
        assignments = await self.policy_checker.get_policy_assignments(discovery_scope)

        # Classify by effect
        deny_policies = []
        audit_policies = []
        modify_policies = []
        deploy_if_not_exists = []

        for assignment in assignments:
            effect = self._classify_effect(assignment)
            entry = {
                "name": assignment.get("name", ""),
                "display_name": assignment.get("display_name", ""),
                "policy_definition_id": assignment.get("policy_definition_id", ""),
                "scope": assignment.get("scope", ""),
                "effect": effect,
                "enforcement_mode": assignment.get("enforcement_mode", "Default"),
            }

            if effect == "Deny":
                deny_policies.append(entry)
            elif effect == "Audit":
                audit_policies.append(entry)
            elif effect == "Modify":
                modify_policies.append(entry)
            elif effect == "DeployIfNotExists":
                deploy_if_not_exists.append(entry)

        constraints = {
            "discovery_status": "COMPLETE",
            "scope": discovery_scope,
            "security_baseline": SECURITY_BASELINE,
            "extended_checks": EXTENDED_CHECKS,
            "policy_constraints": {
                "deny": deny_policies,
                "audit": audit_policies,
                "modify": modify_policies,
                "deploy_if_not_exists": deploy_if_not_exists,
            },
            "total_policies": len(assignments),
            "deny_count": len(deny_policies),
            "summary": (
                f"Discovered {len(assignments)} policies: "
                f"{len(deny_policies)} Deny, {len(audit_policies)} Audit, "
                f"{len(modify_policies)} Modify, {len(deploy_if_not_exists)} DINE"
            ),
        }

        logger.info(constraints["summary"])
        return constraints

    @kernel_function(
        name="get_security_baseline",
        description="Get the non-negotiable security baseline rules",
    )
    def get_security_baseline(self) -> list[dict]:
        """Return the security baseline rules."""
        return SECURITY_BASELINE

    @kernel_function(
        name="validate_against_governance",
        description="Validate IaC code against discovered governance constraints",
    )
    async def validate_against_governance(
        self,
        code_content: Annotated[str, "IaC code to validate"],
        constraints: Annotated[dict, "Governance constraints from discovery"],
        iac_tool: Annotated[str, "bicep or terraform"] = "bicep",
    ) -> dict:
        """Validate code against governance constraints."""
        violations = []

        # Check security baseline
        for rule in SECURITY_BASELINE:
            prop_key = "bicep_property" if iac_tool == "bicep" else "terraform_argument"
            expected = rule[prop_key]

            # Simple presence check (the Challenger does deeper analysis)
            key_part = expected.split(":")[0].strip() if iac_tool == "bicep" else expected.split("=")[0].strip()
            if key_part.lower() not in code_content.lower():
                violations.append({
                    "rule_id": rule["id"],
                    "rule": rule["rule"],
                    "severity": rule["severity"],
                    "expected": expected,
                    "status": "missing",
                })

        # Check extended anti-patterns
        for check in EXTENDED_CHECKS:
            pattern = check["pattern"] if iac_tool == "bicep" else check["tf_pattern"]
            if pattern.lower() in code_content.lower():
                violations.append({
                    "pattern": check["description"],
                    "severity": check["severity"],
                    "found": pattern,
                    "status": "anti_pattern_detected",
                })

        blocking = [v for v in violations if v.get("severity") == "blocks_deployment"]

        return {
            "valid": len(blocking) == 0,
            "total_violations": len(violations),
            "blocking_violations": len(blocking),
            "violations": violations,
        }

    def _classify_effect(self, assignment: dict) -> str:
        """Classify the policy effect from assignment metadata."""
        name = (assignment.get("display_name") or assignment.get("name", "")).lower()
        policy_id = (assignment.get("policy_definition_id") or "").lower()

        if "deny" in name or "deny" in policy_id:
            return "Deny"
        if "audit" in name or "audit" in policy_id:
            return "Audit"
        if "modify" in name or "modify" in policy_id:
            return "Modify"
        if "deployifnotexists" in policy_id or "deploy" in name:
            return "DeployIfNotExists"
        return "Audit"  # Default
