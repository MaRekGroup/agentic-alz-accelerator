"""
Deployment Agent — gathers requirements and deploys Azure Landing Zones.

Uses Semantic Kernel function calling to interact with Bicep/Terraform
deployers and Azure Resource Graph for validation.
"""

import logging
from pathlib import Path
from typing import Annotated, Optional

import yaml
from azure.identity import DefaultAzureCredential
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import (
    FunctionChoiceBehavior,
)
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_function_decorator import kernel_function

from src.config.settings import Settings
from src.tools.bicep_deployer import BicepDeployer
from src.tools.terraform_deployer import TerraformDeployer
from src.tools.resource_graph import ResourceGraphClient

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Azure Landing Zone Deployment Agent. Your role is to help
users deploy enterprise-scale Azure Landing Zones by:

1. Gathering requirements through natural conversation
2. Recommending the appropriate landing zone profile
3. Customizing parameters based on specific needs
4. Executing the deployment using the user's preferred IaC framework (Bicep or Terraform)
5. Validating the deployment was successful

Available profiles: online, corp, sandbox, sap

Always confirm the deployment plan with the user before executing. Use what-if/plan
operations first so the user can review changes before applying them.

When gathering requirements, ask about:
- Workload type (internet-facing, internal, dev/test, SAP)
- Compliance requirements (ISO 27001, NIST, CIS, SOC 2)
- Networking needs (hub-spoke, standalone, ExpressRoute)
- Security requirements (Defender plans, Sentinel, Key Vault)
- Preferred IaC framework (Bicep or Terraform)
"""


class DeploymentAgent:
    """Conversational agent for deploying Azure Landing Zones."""

    def __init__(
        self,
        kernel: Kernel,
        credential: DefaultAzureCredential,
        settings: Settings,
    ):
        self.kernel = kernel
        self.credential = credential
        self.settings = settings
        self.profiles = self._load_profiles()
        self.chat_history = ChatHistory(system_message=SYSTEM_PROMPT)

        # Register tools as kernel plugins
        self.bicep = BicepDeployer(credential, settings)
        self.terraform = TerraformDeployer(credential, settings)
        self.resource_graph = ResourceGraphClient(credential, settings)

        self.kernel.add_plugin(self, plugin_name="deployment")

    def _load_profiles(self) -> dict:
        """Load landing zone profiles from YAML."""
        profile_path = (
            Path(__file__).parent.parent / "config" / "landing_zone_profiles.yaml"
        )
        with open(profile_path) as f:
            data = yaml.safe_load(f)
        return data.get("profiles", {})

    @kernel_function(
        name="list_profiles",
        description="List available landing zone profiles with descriptions",
    )
    def list_profiles(self) -> str:
        """Return a formatted list of available profiles."""
        lines = []
        for key, profile in self.profiles.items():
            lines.append(f"- **{key}**: {profile['name']} — {profile['description']}")
        return "\n".join(lines)

    @kernel_function(
        name="get_profile_details",
        description="Get detailed configuration for a specific landing zone profile",
    )
    def get_profile_details(
        self,
        profile_name: Annotated[str, "Profile name: online, corp, sandbox, or sap"],
    ) -> str:
        """Return full profile configuration as YAML."""
        profile = self.profiles.get(profile_name)
        if not profile:
            return f"Profile '{profile_name}' not found. Available: {list(self.profiles.keys())}"
        return yaml.dump(profile, default_flow_style=False)

    @kernel_function(
        name="deploy_with_bicep",
        description="Deploy a landing zone using Azure Bicep templates",
    )
    async def deploy_with_bicep(
        self,
        profile_name: Annotated[str, "Landing zone profile to deploy"],
        subscription_id: Annotated[str, "Target Azure subscription ID"],
        location: Annotated[str, "Azure region for deployment"] = "southcentralus",
        what_if: Annotated[bool, "Run what-if analysis before deploying"] = True,
    ) -> str:
        """Deploy landing zone using Bicep."""
        profile = self.profiles.get(profile_name)
        if not profile:
            return f"Profile '{profile_name}' not found."

        if what_if:
            logger.info(f"Running what-if for profile '{profile_name}'...")
            what_if_result = await self.bicep.what_if(
                profile=profile,
                subscription_id=subscription_id,
                location=location,
            )
            return (
                f"What-if analysis complete:\n{what_if_result}\n\n"
                "Review the changes above. Call deploy_with_bicep with "
                "what_if=False to apply."
            )

        logger.info(f"Deploying profile '{profile_name}' with Bicep...")
        result = await self.bicep.deploy(
            profile=profile,
            subscription_id=subscription_id,
            location=location,
        )
        return f"Deployment complete:\n{result}"

    @kernel_function(
        name="deploy_with_terraform",
        description="Deploy a landing zone using Terraform",
    )
    async def deploy_with_terraform(
        self,
        profile_name: Annotated[str, "Landing zone profile to deploy"],
        subscription_id: Annotated[str, "Target Azure subscription ID"],
        location: Annotated[str, "Azure region for deployment"] = "southcentralus",
        plan_only: Annotated[bool, "Run plan before applying"] = True,
    ) -> str:
        """Deploy landing zone using Terraform."""
        profile = self.profiles.get(profile_name)
        if not profile:
            return f"Profile '{profile_name}' not found."

        if plan_only:
            logger.info(f"Running Terraform plan for profile '{profile_name}'...")
            plan_result = await self.terraform.plan(
                profile=profile,
                subscription_id=subscription_id,
                location=location,
            )
            return (
                f"Terraform plan:\n{plan_result}\n\n"
                "Review the plan above. Call deploy_with_terraform with "
                "plan_only=False to apply."
            )

        logger.info(f"Applying Terraform for profile '{profile_name}'...")
        result = await self.terraform.apply(
            profile=profile,
            subscription_id=subscription_id,
            location=location,
        )
        return f"Terraform apply complete:\n{result}"

    @kernel_function(
        name="validate_deployment",
        description="Validate a landing zone deployment by checking resources exist and policies are assigned",
    )
    async def validate_deployment(
        self,
        subscription_id: Annotated[str, "Subscription ID to validate"],
    ) -> str:
        """Run post-deployment validation."""
        results = await self.resource_graph.validate_landing_zone(subscription_id)
        return yaml.dump(results, default_flow_style=False)

    async def run_interactive(self) -> dict:
        """Run the deployment agent in interactive conversation mode."""
        from rich.console import Console
        from rich.markdown import Markdown

        console = Console()
        console.print(
            Markdown("# Azure Landing Zone Deployment Agent\n"
                     "I'll help you deploy an Azure Landing Zone. "
                     "Tell me about your workload requirements, or type "
                     "`list profiles` to see available options.\n\n"
                     "Type `exit` to quit.\n")
        )

        execution_settings = self.kernel.get_prompt_execution_settings_from_service_id(
            "default"
        )
        execution_settings.function_choice_behavior = (
            FunctionChoiceBehavior.Auto()
        )

        while True:
            user_input = console.input("[bold blue]You:[/bold blue] ")
            if user_input.strip().lower() in ("exit", "quit", "q"):
                break

            self.chat_history.add_user_message(user_input)

            response = await self.kernel.invoke_prompt(
                prompt="{{$chat_history}}",
                chat_history=self.chat_history,
                settings=execution_settings,
            )

            assistant_message = str(response)
            self.chat_history.add_assistant_message(assistant_message)
            console.print(Markdown(f"\n{assistant_message}\n"))

        return {"status": "completed", "history_length": len(self.chat_history)}

    async def deploy_profile(self, profile_name: str) -> dict:
        """Deploy a specific profile non-interactively."""
        profile = self.profiles.get(profile_name)
        if not profile:
            raise ValueError(
                f"Profile '{profile_name}' not found. "
                f"Available: {list(self.profiles.keys())}"
            )

        framework = self.settings.iac.framework
        subscription_id = self.settings.azure.subscription_id
        location = self.settings.azure.deployment_region

        if framework == "bicep":
            result = await self.deploy_with_bicep(
                profile_name=profile_name,
                subscription_id=subscription_id,
                location=location,
                what_if=False,
            )
        else:
            result = await self.deploy_with_terraform(
                profile_name=profile_name,
                subscription_id=subscription_id,
                location=location,
                plan_only=False,
            )

        return {"status": "deployed", "framework": framework, "result": result}
