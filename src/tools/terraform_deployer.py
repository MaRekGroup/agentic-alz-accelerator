"""
Terraform Deployer — executes Terraform plans and applies for landing zone provisioning.

Wraps the Terraform CLI to provide plan, apply, destroy, and state management
with Azure backend state storage.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Optional

from azure.identity import DefaultAzureCredential

from src.config.settings import Settings

logger = logging.getLogger(__name__)

TERRAFORM_DIR = Path(__file__).parent.parent.parent / "infra" / "terraform"


class TerraformDeployer:
    """Deploys Azure Landing Zone resources using Terraform."""

    def __init__(self, credential: DefaultAzureCredential, settings: Settings):
        self.credential = credential
        self.settings = settings
        self.working_dir = str(TERRAFORM_DIR)

    async def _run_terraform(
        self,
        args: list[str],
        env_override: Optional[dict] = None,
    ) -> dict:
        """Execute a Terraform command asynchronously."""
        env = os.environ.copy()

        # Set Azure authentication via service principal or CLI
        token = self.credential.get_token(
            "https://management.azure.com/.default"
        )
        env["ARM_ACCESS_TOKEN"] = token.token
        env["ARM_SUBSCRIPTION_ID"] = self.settings.azure.subscription_id
        if self.settings.azure.tenant_id:
            env["ARM_TENANT_ID"] = self.settings.azure.tenant_id

        if env_override:
            env.update(env_override)

        cmd = ["terraform"] + args
        logger.info(f"Running: {' '.join(cmd)}")

        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=self.working_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )

        stdout, stderr = await process.communicate()

        return {
            "returncode": process.returncode,
            "stdout": stdout.decode(),
            "stderr": stderr.decode(),
        }

    async def init(self, environment: str = "prod") -> dict:
        """Initialize Terraform with backend configuration."""
        backend_config = [
            f"-backend-config=storage_account_name={self.settings.iac.terraform_state_storage_account}",
            f"-backend-config=container_name={self.settings.iac.terraform_state_container}",
            f"-backend-config=key={environment}.terraform.tfstate",
        ]

        result = await self._run_terraform(
            ["init", "-input=false", "-no-color"] + backend_config
        )

        if result["returncode"] != 0:
            logger.error(f"Terraform init failed: {result['stderr']}")
            raise RuntimeError(f"Terraform init failed: {result['stderr']}")

        return result

    async def plan(
        self,
        profile: dict,
        subscription_id: str,
        location: str,
        environment: str = "prod",
    ) -> str:
        """Generate a Terraform execution plan."""
        await self.init(environment)

        var_args = self._build_var_args(profile, subscription_id, location)
        var_file = f"-var-file=environments/{environment}/terraform.tfvars"

        result = await self._run_terraform(
            ["plan", "-input=false", "-no-color", var_file] + var_args
        )

        if result["returncode"] != 0:
            logger.error(f"Terraform plan failed: {result['stderr']}")
            return f"Plan failed:\n{result['stderr']}"

        return result["stdout"]

    async def apply(
        self,
        profile: dict,
        subscription_id: str,
        location: str,
        environment: str = "prod",
    ) -> dict:
        """Apply a Terraform configuration."""
        await self.init(environment)

        var_args = self._build_var_args(profile, subscription_id, location)
        var_file = f"-var-file=environments/{environment}/terraform.tfvars"

        result = await self._run_terraform(
            ["apply", "-input=false", "-no-color", "-auto-approve", var_file]
            + var_args
        )

        if result["returncode"] != 0:
            logger.error(f"Terraform apply failed: {result['stderr']}")
            raise RuntimeError(f"Terraform apply failed: {result['stderr']}")

        # Get outputs
        output_result = await self._run_terraform(
            ["output", "-json", "-no-color"]
        )
        outputs = {}
        if output_result["returncode"] == 0 and output_result["stdout"].strip():
            outputs = json.loads(output_result["stdout"])

        return {
            "status": "succeeded",
            "outputs": outputs,
            "log": result["stdout"][-2000:],  # Last 2000 chars of log
        }

    async def apply_targeted(
        self,
        target_resource: str,
        environment: str = "prod",
    ) -> dict:
        """Apply Terraform targeting a specific resource (used for remediation)."""
        await self.init(environment)

        result = await self._run_terraform(
            [
                "apply",
                "-input=false",
                "-no-color",
                "-auto-approve",
                f"-target={target_resource}",
            ]
        )

        return {
            "status": "succeeded" if result["returncode"] == 0 else "failed",
            "log": result["stdout"][-1000:],
        }

    async def destroy(self, environment: str = "prod") -> dict:
        """Destroy Terraform-managed infrastructure (requires explicit confirmation)."""
        await self.init(environment)

        result = await self._run_terraform(
            ["destroy", "-input=false", "-no-color", "-auto-approve"]
        )

        return {
            "status": "destroyed" if result["returncode"] == 0 else "failed",
            "log": result["stdout"][-1000:],
        }

    def _build_var_args(
        self, profile: dict, subscription_id: str, location: str
    ) -> list[str]:
        """Build Terraform -var arguments from profile."""
        return [
            f"-var=subscription_id={subscription_id}",
            f"-var=location={location}",
            f"-var=management_group_name={profile.get('management_group', '')}",
            f"-var=profile_name={profile.get('name', '')}",
            f"-var=vnet_address_space={profile.get('networking', {}).get('vnet_address_space', '')}",
            f"-var=enable_ddos={str(profile.get('networking', {}).get('ddos_protection', False)).lower()}",
            f"-var=enable_defender={str(profile.get('security', {}).get('defender_for_cloud', False)).lower()}",
            f"-var=log_retention_days={profile.get('logging', {}).get('retention_days', 90)}",
        ]
