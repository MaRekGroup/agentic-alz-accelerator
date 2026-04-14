"""
Drift Detector — detects configuration drift from desired landing zone state.

Compares current Azure resource state against the declared IaC state to identify
resources that have been modified outside of the IaC pipeline.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from azure.identity import DefaultAzureCredential

from src.config.settings import Settings
from src.tools.resource_graph import ResourceGraphClient

logger = logging.getLogger(__name__)

# Resource properties that indicate drift when changed
MONITORED_PROPERTIES = {
    "microsoft.network/virtualnetworks": [
        "properties.addressSpace.addressPrefixes",
        "properties.subnets",
        "properties.dhcpOptions.dnsServers",
    ],
    "microsoft.network/networksecuritygroups": [
        "properties.securityRules",
    ],
    "microsoft.network/routetables": [
        "properties.routes",
    ],
    "microsoft.keyvault/vaults": [
        "properties.accessPolicies",
        "properties.networkAcls",
        "properties.enableSoftDelete",
        "properties.enablePurgeProtection",
    ],
    "microsoft.storage/storageaccounts": [
        "properties.networkAcls",
        "properties.encryption",
        "properties.supportsHttpsTrafficOnly",
        "properties.minimumTlsVersion",
        "properties.allowBlobPublicAccess",
    ],
    "microsoft.operationalinsights/workspaces": [
        "properties.retentionInDays",
        "properties.sku",
    ],
}


class DriftDetector:
    """Detects configuration drift in Azure Landing Zone resources."""

    def __init__(self, credential: DefaultAzureCredential, settings: Settings):
        self.credential = credential
        self.settings = settings
        self.resource_graph = ResourceGraphClient(credential, settings)
        self._baseline_state: dict[str, dict] = {}

    async def capture_baseline(self, scope: str) -> dict:
        """Capture the current state as the baseline for drift detection."""
        logger.info(f"Capturing baseline state for scope: {scope}")

        baseline = {}
        for resource_type, properties in MONITORED_PROPERTIES.items():
            prop_projections = ", ".join(properties)
            query = f"""
            resources
            | where type =~ "{resource_type}"
            | project id, name, type, location, {prop_projections}
            """

            resources = await self.resource_graph.query(query)
            for resource in resources:
                baseline[resource.get("id", "")] = resource

        self._baseline_state = baseline
        logger.info(f"Baseline captured: {len(baseline)} resources")
        return {"resources_tracked": len(baseline)}

    async def detect(self, scope: str) -> dict:
        """Detect drift by comparing current state against baseline."""
        if not self._baseline_state:
            logger.info("No baseline found, capturing initial baseline...")
            await self.capture_baseline(scope)
            return {"drifted_resources": [], "message": "Baseline captured, no drift to report yet"}

        logger.info("Detecting drift against baseline...")
        drifted_resources = []

        for resource_type, properties in MONITORED_PROPERTIES.items():
            prop_projections = ", ".join(properties)
            query = f"""
            resources
            | where type =~ "{resource_type}"
            | project id, name, type, location, {prop_projections}
            """

            current_resources = await self.resource_graph.query(query)

            for current in current_resources:
                resource_id = current.get("id", "")
                baseline = self._baseline_state.get(resource_id)

                if not baseline:
                    drifted_resources.append({
                        "resource_id": resource_id,
                        "resource_type": resource_type,
                        "drift_type": "new_resource",
                        "details": "Resource exists but was not in baseline",
                        "severity": "medium",
                    })
                    continue

                # Compare properties
                for prop in properties:
                    current_value = self._get_nested(current, prop)
                    baseline_value = self._get_nested(baseline, prop)

                    if current_value != baseline_value:
                        drifted_resources.append({
                            "resource_id": resource_id,
                            "resource_type": resource_type,
                            "drift_type": "property_changed",
                            "property": prop,
                            "baseline_value": str(baseline_value)[:200],
                            "current_value": str(current_value)[:200],
                            "details": f"Property '{prop}' changed from baseline",
                            "severity": self._assess_severity(prop, resource_type),
                        })

            # Check for deleted resources
            current_ids = {r.get("id", "") for r in current_resources}
            for resource_id, baseline in self._baseline_state.items():
                if (
                    baseline.get("type", "").lower() == resource_type
                    and resource_id not in current_ids
                ):
                    drifted_resources.append({
                        "resource_id": resource_id,
                        "resource_type": resource_type,
                        "drift_type": "deleted",
                        "details": "Resource was deleted outside of IaC",
                        "severity": "critical",
                    })

        # Also check for recent manual changes via Activity Log
        manual_changes = await self._check_activity_log()
        for change in manual_changes:
            if not any(
                d["resource_id"] == change["resource_id"] for d in drifted_resources
            ):
                drifted_resources.append(change)

        return {
            "scan_time": datetime.now(timezone.utc).isoformat(),
            "drifted_resources": drifted_resources,
            "total_drifted": len(drifted_resources),
            "baseline_resources": len(self._baseline_state),
        }

    async def _check_activity_log(self) -> list[dict]:
        """Check Activity Log for manual (non-IaC) modifications."""
        lookback = datetime.now(timezone.utc) - timedelta(hours=1)
        lookback_str = lookback.strftime("%Y-%m-%dT%H:%M:%SZ")

        query = f"""
        resourcechanges
        | where properties.changeAttributes.timestamp > datetime("{lookback_str}")
        | where properties.changeAttributes.changedBy !contains "deploymentScript"
        | where properties.changeAttributes.changedBy !contains "terraform"
        | where properties.changeAttributes.changedBy !contains "bicep"
        | project resourceId=properties.targetResourceId,
                  changedBy=properties.changeAttributes.changedBy,
                  timestamp=properties.changeAttributes.timestamp,
                  changeType=properties.changeType
        | limit 50
        """

        try:
            results = await self.resource_graph.query(query)
            return [
                {
                    "resource_id": r.get("resourceId", ""),
                    "drift_type": "manual_change",
                    "details": f"Manual change by {r.get('changedBy', 'unknown')}",
                    "changed_by": r.get("changedBy", ""),
                    "timestamp": r.get("timestamp", ""),
                    "severity": "high",
                }
                for r in results
            ]
        except Exception as e:
            logger.warning(f"Activity log query failed (may not be available): {e}")
            return []

    def _get_nested(self, obj: dict, path: str):
        """Traverse a nested dictionary using dot-notation path."""
        parts = path.split(".")
        current = obj
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current

    def _assess_severity(self, property_path: str, resource_type: str) -> str:
        """Assess severity of a drift based on property and resource type."""
        critical_patterns = [
            "networkAcls",
            "accessPolicies",
            "securityRules",
            "encryption",
            "enableSoftDelete",
            "allowBlobPublicAccess",
        ]
        high_patterns = [
            "addressPrefixes",
            "dnsServers",
            "routes",
            "supportsHttpsTrafficOnly",
            "minimumTlsVersion",
        ]

        for pattern in critical_patterns:
            if pattern in property_path:
                return "critical"
        for pattern in high_patterns:
            if pattern in property_path:
                return "high"
        return "medium"
