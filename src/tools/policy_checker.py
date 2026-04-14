"""
Policy Checker — evaluates Azure Policy compliance for landing zone governance.

Provides methods to check compliance state, enumerate violations, and validate
individual resources against specific policy definitions.
"""

import logging
from typing import Optional

from azure.identity import DefaultAzureCredential
from azure.mgmt.policyinsights import PolicyInsightsClient
from azure.mgmt.policyinsights.models import QueryOptions

from src.config.settings import Settings

logger = logging.getLogger(__name__)


class PolicyChecker:
    """Checks Azure Policy compliance for landing zone governance."""

    def __init__(self, credential: DefaultAzureCredential, settings: Settings):
        self.credential = credential
        self.settings = settings
        self.client = PolicyInsightsClient(credential)

    async def get_compliance_state(self, scope: str) -> dict:
        """Get overall compliance state for a scope."""
        logger.info(f"Checking compliance state at scope: {scope}")

        try:
            summary = self.client.policy_states.summarize_for_subscription(
                subscription_id=self.settings.azure.subscription_id,
                policy_states_resource="latest",
            )

            results = summary.value[0] if summary.value else None
            if not results:
                return {
                    "compliant": 0,
                    "non_compliant": 0,
                    "exempt": 0,
                    "compliance_pct": 100.0,
                }

            total = results.results.total_resources or 0
            non_compliant = results.results.non_compliant_resources or 0
            compliant = total - non_compliant

            return {
                "compliant": compliant,
                "non_compliant": non_compliant,
                "exempt": 0,
                "total": total,
                "compliance_pct": (compliant / total * 100) if total > 0 else 100.0,
                "policy_assignments": len(
                    results.policy_assignments or []
                ),
            }
        except Exception as e:
            logger.error(f"Failed to get compliance state: {e}")
            return {
                "compliant": 0,
                "non_compliant": 0,
                "exempt": 0,
                "compliance_pct": 0,
                "error": str(e),
            }

    async def get_violations(
        self,
        scope: str,
        top: int = 100,
    ) -> list[dict]:
        """Get non-compliant resources with details."""
        logger.info(f"Fetching policy violations at scope: {scope}")

        try:
            query_options = QueryOptions(top=top, order_by="timestamp desc")

            states = self.client.policy_states.list_query_results_for_subscription(
                subscription_id=self.settings.azure.subscription_id,
                policy_states_resource="latest",
                query_options=query_options,
            )

            violations = []
            for state in states:
                if state.compliance_state == "NonCompliant":
                    violations.append({
                        "resource_id": state.resource_id,
                        "resource_type": state.resource_type,
                        "policy_name": state.policy_definition_name,
                        "policy_definition_id": state.policy_definition_id,
                        "policy_assignment_id": state.policy_assignment_id,
                        "severity": self._get_severity(state),
                        "timestamp": state.timestamp.isoformat()
                        if state.timestamp
                        else None,
                        "compliance_state": state.compliance_state,
                    })

            logger.info(f"Found {len(violations)} policy violations")
            return violations

        except Exception as e:
            logger.error(f"Failed to get violations: {e}")
            return []

    async def check_single_resource(
        self,
        resource_id: str,
        policy_definition_id: str,
    ) -> bool:
        """Check if a specific resource is compliant with a policy."""
        try:
            states = self.client.policy_states.list_query_results_for_resource(
                resource_id=resource_id,
                policy_states_resource="latest",
            )

            for state in states:
                if (
                    state.policy_definition_id == policy_definition_id
                    and state.compliance_state == "NonCompliant"
                ):
                    return False
            return True
        except Exception as e:
            logger.error(f"Failed to check resource compliance: {e}")
            return False

    async def get_policy_assignments(
        self, scope: Optional[str] = None
    ) -> list[dict]:
        """List policy assignments at the given scope."""
        from azure.mgmt.resource.policy import PolicyClient

        policy_client = PolicyClient(
            self.credential, self.settings.azure.subscription_id
        )

        assignments = policy_client.policy_assignments.list()
        return [
            {
                "id": a.id,
                "name": a.name,
                "display_name": a.display_name,
                "policy_definition_id": a.policy_definition_id,
                "scope": a.scope,
                "enforcement_mode": a.enforcement_mode,
            }
            for a in assignments
        ]

    def _get_severity(self, state) -> str:
        """Extract severity from policy state metadata."""
        # Map common policy patterns to severity levels
        name = (state.policy_definition_name or "").lower()
        if any(kw in name for kw in ["deny", "audit-public", "require-encryption"]):
            return "critical"
        if any(kw in name for kw in ["enforce", "require"]):
            return "high"
        if any(kw in name for kw in ["audit", "diagnostic"]):
            return "medium"
        return "low"
