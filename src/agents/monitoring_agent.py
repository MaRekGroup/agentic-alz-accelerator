"""
Monitoring Agent — continuous compliance and drift detection for Azure Landing Zones.

Periodically scans the landing zone using Azure Policy, Resource Graph, and custom
drift detection to identify violations and configuration changes.
"""

import logging
from datetime import datetime, timezone
from typing import Annotated

from azure.identity import DefaultAzureCredential
from semantic_kernel import Kernel
from semantic_kernel.functions.kernel_function_decorator import kernel_function

from src.config.settings import Settings
from src.tools.policy_checker import PolicyChecker
from src.tools.resource_graph import ResourceGraphClient
from src.tools.drift_detector import DriftDetector

logger = logging.getLogger(__name__)


class MonitoringAgent:
    """Monitors Azure Landing Zone compliance and detects drift."""

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
        self.drift_detector = DriftDetector(credential, settings)

        self.kernel.add_plugin(self, plugin_name="monitoring")

    @kernel_function(
        name="run_compliance_scan",
        description="Run a full compliance scan across the landing zone",
    )
    async def run_compliance_scan(
        self,
        scope: Annotated[
            str, "Scope for compliance scan (management group or subscription ID)"
        ] = "",
    ) -> dict:
        """Execute comprehensive compliance scan."""
        scan_scope = scope or (
            f"/providers/Microsoft.Management/managementGroups/"
            f"{self.settings.azure.management_group_prefix}"
        )

        logger.info(f"Running compliance scan at scope: {scan_scope}")
        scan_start = datetime.now(timezone.utc)

        # Run policy compliance check
        policy_results = await self.policy_checker.get_compliance_state(scan_scope)

        # Query resource inventory
        inventory = await self.resource_graph.get_resource_inventory(scan_scope)

        # Check for non-compliant resources
        violations = await self.policy_checker.get_violations(scan_scope)

        scan_duration = (datetime.now(timezone.utc) - scan_start).total_seconds()

        report = {
            "scan_time": scan_start.isoformat(),
            "scan_duration_seconds": scan_duration,
            "scope": scan_scope,
            "summary": {
                "total_resources": inventory.get("total_count", 0),
                "compliant_resources": policy_results.get("compliant", 0),
                "non_compliant_resources": policy_results.get("non_compliant", 0),
                "exempt_resources": policy_results.get("exempt", 0),
                "compliance_percentage": policy_results.get("compliance_pct", 0),
            },
            "violations": violations,
            "resource_inventory": inventory,
        }

        logger.info(
            f"Scan complete: {report['summary']['compliance_percentage']:.1f}% compliant, "
            f"{len(violations)} violations found"
        )
        return report

    @kernel_function(
        name="detect_drift",
        description="Detect configuration drift from the desired landing zone state",
    )
    async def detect_drift(
        self,
        scope: Annotated[
            str, "Scope for drift detection (management group or subscription ID)"
        ] = "",
    ) -> dict:
        """Detect configuration drift in the landing zone."""
        scan_scope = scope or (
            f"/providers/Microsoft.Management/managementGroups/"
            f"{self.settings.azure.management_group_prefix}"
        )

        logger.info(f"Running drift detection at scope: {scan_scope}")

        # Compare current state against desired state
        drift_results = await self.drift_detector.detect(scan_scope)

        drifted = drift_results.get("drifted_resources", [])
        if drifted:
            logger.warning(
                f"Drift detected in {len(drifted)} resources"
            )
            for resource in drifted:
                logger.warning(
                    f"  - {resource['resource_id']}: {resource['drift_type']} "
                    f"({resource.get('details', 'no details')})"
                )

        return drift_results

    @kernel_function(
        name="get_security_posture",
        description="Get the current security posture of the landing zone from Defender for Cloud",
    )
    async def get_security_posture(
        self,
        subscription_id: Annotated[str, "Subscription ID to check"] = "",
    ) -> dict:
        """Query Defender for Cloud secure score and recommendations."""
        sub_id = subscription_id or self.settings.azure.subscription_id

        secure_score = await self.resource_graph.query(
            f"""
            securityresources
            | where type == "microsoft.security/securescores"
            | where subscriptionId == "{sub_id}"
            | project subscriptionId,
                      score=properties.score.current,
                      maxScore=properties.score.max,
                      percentage=properties.score.percentage
            """
        )

        recommendations = await self.resource_graph.query(
            f"""
            securityresources
            | where type == "microsoft.security/assessments"
            | where subscriptionId == "{sub_id}"
            | where properties.status.code == "Unhealthy"
            | project name=properties.displayName,
                      severity=properties.metadata.severity,
                      category=properties.metadata.categories[0],
                      resourceId=properties.resourceDetails.Id
            | order by severity asc
            | limit 50
            """
        )

        return {
            "secure_score": secure_score,
            "unhealthy_recommendations": recommendations,
        }

    @kernel_function(
        name="get_cost_summary",
        description="Get a cost summary for the landing zone subscriptions",
    )
    async def get_cost_summary(
        self,
        subscription_id: Annotated[str, "Subscription ID to check"] = "",
    ) -> dict:
        """Query cost data via Resource Graph."""
        sub_id = subscription_id or self.settings.azure.subscription_id

        resources_by_type = await self.resource_graph.query(
            f"""
            resources
            | where subscriptionId == "{sub_id}"
            | summarize count() by type
            | order by count_ desc
            | limit 20
            """
        )

        return {
            "subscription_id": sub_id,
            "resources_by_type": resources_by_type,
        }

    @kernel_function(
        name="generate_compliance_report",
        description="Generate a formatted compliance report for stakeholders",
    )
    async def generate_compliance_report(self) -> str:
        """Generate a markdown compliance report."""
        scan = await self.run_compliance_scan()
        security = await self.get_security_posture()

        summary = scan["summary"]
        report_lines = [
            "# Azure Landing Zone Compliance Report",
            f"**Generated:** {scan['scan_time']}",
            f"**Scope:** {scan['scope']}",
            "",
            "## Compliance Summary",
            f"- **Total Resources:** {summary['total_resources']}",
            f"- **Compliant:** {summary['compliant_resources']}",
            f"- **Non-Compliant:** {summary['non_compliant_resources']}",
            f"- **Compliance Rate:** {summary['compliance_percentage']:.1f}%",
            "",
            "## Policy Violations",
        ]

        for v in scan.get("violations", [])[:10]:
            report_lines.append(
                f"- [{v.get('severity', 'unknown').upper()}] "
                f"{v.get('policy_name', 'Unknown policy')}: "
                f"{v.get('resource_id', 'Unknown resource')}"
            )

        report_lines.extend([
            "",
            "## Security Posture",
            f"- **Secure Score:** "
            f"{security.get('secure_score', [{}])[0].get('percentage', 'N/A')}%",
            f"- **Unhealthy Recommendations:** "
            f"{len(security.get('unhealthy_recommendations', []))}",
        ])

        return "\n".join(report_lines)
