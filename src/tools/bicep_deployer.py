"""
Bicep Deployer — executes Azure Bicep deployments for landing zone provisioning.

Wraps the Azure Resource Management SDK to provide what-if analysis, deployment
execution, and status tracking for Bicep templates.
"""

import asyncio
import json
import logging
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient

from src.config.settings import Settings

logger = logging.getLogger(__name__)

BICEP_DIR = Path(__file__).parent.parent.parent / "infra" / "bicep"


class BicepDeployer:
    """Deploys Azure Landing Zone resources using Bicep templates."""

    def __init__(self, credential: DefaultAzureCredential, settings: Settings):
        self.credential = credential
        self.settings = settings

    def _get_client(self, subscription_id: str) -> ResourceManagementClient:
        return ResourceManagementClient(self.credential, subscription_id)

    def _compile_bicep(self, bicep_path: str) -> str:
        """Compile Bicep to ARM JSON template."""
        import subprocess

        result = subprocess.run(
            ["az", "bicep", "build", "--file", bicep_path, "--stdout"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout

    def _build_parameters(self, profile: dict, location: str) -> dict:
        """Generate deployment parameters from a landing zone profile."""
        return {
            "location": {"value": location},
            "managementGroupName": {"value": profile.get("management_group", "")},
            "networkingConfig": {"value": profile.get("networking", {})},
            "identityConfig": {"value": profile.get("identity", {})},
            "policyConfig": {"value": profile.get("policies", {})},
            "loggingConfig": {"value": profile.get("logging", {})},
            "securityConfig": {"value": profile.get("security", {})},
        }

    async def what_if(
        self,
        profile: dict,
        subscription_id: str,
        location: str,
        template_file: str = "main.bicep",
    ) -> str:
        """Run what-if analysis for a Bicep deployment."""
        client = self._get_client(subscription_id)
        template_path = BICEP_DIR / template_file
        arm_template = json.loads(self._compile_bicep(str(template_path)))
        parameters = self._build_parameters(profile, location)

        deployment_name = f"alz-whatif-{profile.get('management_group', 'default')}"

        what_if_params = {
            "properties": {
                "mode": "Incremental",
                "template": arm_template,
                "parameters": parameters,
            }
        }

        logger.info(f"Running what-if: {deployment_name}")
        poller = client.deployments.begin_what_if(
            resource_group_name="",  # Subscription-level deployment
            deployment_name=deployment_name,
            parameters=what_if_params,
        )

        result = await asyncio.to_thread(poller.result)
        return self._format_what_if_result(result)

    async def deploy(
        self,
        profile: dict,
        subscription_id: str,
        location: str,
        template_file: str = "main.bicep",
    ) -> dict:
        """Deploy a landing zone using Bicep."""
        client = self._get_client(subscription_id)
        template_path = BICEP_DIR / template_file
        arm_template = json.loads(self._compile_bicep(str(template_path)))
        parameters = self._build_parameters(profile, location)

        deployment_name = f"alz-{profile.get('management_group', 'default')}"

        deploy_params = {
            "properties": {
                "mode": "Incremental",
                "template": arm_template,
                "parameters": parameters,
            },
            "location": location,
        }

        logger.info(f"Starting deployment: {deployment_name}")
        poller = client.deployments.begin_create_or_update(
            resource_group_name="",
            deployment_name=deployment_name,
            parameters=deploy_params,
        )

        result = await asyncio.to_thread(poller.result)

        return {
            "deployment_name": deployment_name,
            "status": result.properties.provisioning_state,
            "outputs": result.properties.outputs or {},
            "duration": str(result.properties.duration),
        }

    async def deploy_template(
        self,
        template_path: str,
        parameters: dict,
        resource_group: str | None = None,
    ) -> dict:
        """Deploy a specific Bicep template (used for remediation)."""
        subscription_id = self.settings.azure.subscription_id
        client = self._get_client(subscription_id)

        full_path = BICEP_DIR / template_path
        arm_template = json.loads(self._compile_bicep(str(full_path)))

        formatted_params = {
            k: {"value": v} for k, v in parameters.items()
        }

        deployment_name = f"alz-remediation-{template_path.split('/')[-1].replace('.bicep', '')}"

        deploy_params = {
            "properties": {
                "mode": "Incremental",
                "template": arm_template,
                "parameters": formatted_params,
            }
        }

        rg = resource_group or ""
        poller = client.deployments.begin_create_or_update(
            resource_group_name=rg,
            deployment_name=deployment_name,
            parameters=deploy_params,
        )

        result = await asyncio.to_thread(poller.result)
        return {
            "deployment_name": deployment_name,
            "status": result.properties.provisioning_state,
        }

    def _format_what_if_result(self, result) -> str:
        """Format what-if results into readable text."""
        lines = ["## What-If Analysis Results\n"]
        change_type_map = {
            "Create": "➕ Create",
            "Delete": "❌ Delete",
            "Modify": "✏️  Modify",
            "NoChange": "⏸️  No Change",
            "Deploy": "🚀 Deploy",
        }

        if hasattr(result, "changes") and result.changes:
            for change in result.changes:
                change_label = change_type_map.get(
                    str(change.change_type), str(change.change_type)
                )
                lines.append(f"- {change_label}: {change.resource_id}")
                if change.delta and change.delta.properties:
                    for prop in change.delta.properties[:5]:
                        lines.append(f"    - {prop.path}: {prop.before} → {prop.after}")
        else:
            lines.append("No changes detected.")

        return "\n".join(lines)
