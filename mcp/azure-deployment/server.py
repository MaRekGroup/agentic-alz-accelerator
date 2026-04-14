"""
Azure Deployment MCP Server

Exposes Bicep and Terraform deployment operations as MCP tools.
Supports what-if analysis, deployment execution, status tracking,
and post-deployment validation.
"""

import json
import logging
import os
import subprocess
import sys
from typing import Any

from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient

logger = logging.getLogger(__name__)

TOOLS = [
    {
        "name": "bicep_what_if",
        "description": "Run Bicep what-if analysis",
        "inputSchema": {
            "type": "object",
            "properties": {
                "template_file": {"type": "string", "description": "Path to Bicep template"},
                "parameters": {"type": "object", "description": "Template parameters"},
                "location": {"type": "string", "default": "southcentralus"},
                "subscription_id": {"type": "string"},
            },
            "required": ["template_file"],
        },
    },
    {
        "name": "bicep_deploy",
        "description": "Deploy Bicep templates",
        "inputSchema": {
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
    },
    {
        "name": "terraform_plan",
        "description": "Run Terraform plan",
        "inputSchema": {
            "type": "object",
            "properties": {
                "working_directory": {"type": "string", "description": "Terraform module directory"},
                "var_file": {"type": "string", "description": "Path to tfvars file"},
            },
            "required": ["working_directory"],
        },
    },
    {
        "name": "terraform_apply",
        "description": "Apply Terraform configuration",
        "inputSchema": {
            "type": "object",
            "properties": {
                "working_directory": {"type": "string"},
                "plan_file": {"type": "string", "default": "tfplan"},
            },
            "required": ["working_directory"],
        },
    },
    {
        "name": "get_deployment_status",
        "description": "Get deployment status and outputs",
        "inputSchema": {
            "type": "object",
            "properties": {
                "deployment_name": {"type": "string"},
                "subscription_id": {"type": "string"},
            },
            "required": ["deployment_name"],
        },
    },
    {
        "name": "validate_deployment",
        "description": "Post-deployment resource validation",
        "inputSchema": {
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
    },
]


class AzureDeploymentServer:
    """MCP server exposing Azure deployment capabilities."""

    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.default_subscription = os.environ.get("AZURE_SUBSCRIPTION_ID", "")
        self.iac_framework = os.environ.get("IAC_FRAMEWORK", "bicep")

    def _get_resource_client(self, subscription_id: str) -> ResourceManagementClient:
        return ResourceManagementClient(self.credential, subscription_id)

    def handle_tool_call(self, tool_name: str, arguments: dict) -> Any:
        """Route MCP tool calls to the appropriate handler."""
        sub = arguments.get("subscription_id", self.default_subscription)

        if tool_name == "bicep_what_if":
            return self._bicep_what_if(sub, arguments)
        elif tool_name == "bicep_deploy":
            return self._bicep_deploy(sub, arguments)
        elif tool_name == "terraform_plan":
            return self._terraform_plan(arguments)
        elif tool_name == "terraform_apply":
            return self._terraform_apply(arguments)
        elif tool_name == "get_deployment_status":
            return self._get_deployment_status(sub, arguments["deployment_name"])
        elif tool_name == "validate_deployment":
            return self._validate_deployment(sub, arguments)
        return {"error": f"Unknown tool: {tool_name}"}

    def _bicep_what_if(self, subscription_id: str, arguments: dict) -> dict:
        """Run Bicep what-if analysis via Azure CLI."""
        template_file = arguments["template_file"]
        location = arguments.get("location", "southcentralus")
        params = arguments.get("parameters", {})

        cmd = [
            "az", "deployment", "sub", "what-if",
            "--location", location,
            "--template-file", template_file,
            "--subscription", subscription_id,
        ]
        for key, value in params.items():
            cmd.extend(["--parameters", f"{key}={value}"])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr if result.returncode != 0 else None,
        }

    def _bicep_deploy(self, subscription_id: str, arguments: dict) -> dict:
        """Deploy Bicep template via Azure CLI."""
        template_file = arguments["template_file"]
        deployment_name = arguments["deployment_name"]
        location = arguments.get("location", "southcentralus")
        params = arguments.get("parameters", {})

        cmd = [
            "az", "deployment", "sub", "create",
            "--location", location,
            "--template-file", template_file,
            "--name", deployment_name,
            "--subscription", subscription_id,
        ]
        for key, value in params.items():
            cmd.extend(["--parameters", f"{key}={value}"])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return {
            "success": result.returncode == 0,
            "deployment_name": deployment_name,
            "output": result.stdout[:5000] if result.stdout else None,
            "errors": result.stderr if result.returncode != 0 else None,
        }

    def _terraform_plan(self, arguments: dict) -> dict:
        """Run Terraform plan."""
        working_dir = arguments["working_directory"]
        var_file = arguments.get("var_file")

        cmd = ["terraform", "plan", "-out=tfplan", "-no-color"]
        if var_file:
            cmd.extend(["-var-file", var_file])

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=working_dir, timeout=300)
        return {
            "success": result.returncode == 0,
            "output": result.stdout[:5000],
            "errors": result.stderr if result.returncode != 0 else None,
        }

    def _terraform_apply(self, arguments: dict) -> dict:
        """Apply Terraform plan."""
        working_dir = arguments["working_directory"]
        plan_file = arguments.get("plan_file", "tfplan")

        cmd = ["terraform", "apply", "-auto-approve", "-no-color", plan_file]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=working_dir, timeout=600)
        return {
            "success": result.returncode == 0,
            "output": result.stdout[:5000],
            "errors": result.stderr if result.returncode != 0 else None,
        }

    def _get_deployment_status(self, subscription_id: str, deployment_name: str) -> dict:
        """Get deployment status."""
        client = self._get_resource_client(subscription_id)
        try:
            deployment = client.deployments.get_at_subscription_scope(deployment_name)
            outputs = {}
            if deployment.properties and deployment.properties.outputs:
                for k, v in deployment.properties.outputs.items():
                    outputs[k] = v.get("value")
            return {
                "deployment_name": deployment_name,
                "provisioning_state": deployment.properties.provisioning_state if deployment.properties else "Unknown",
                "timestamp": str(deployment.properties.timestamp) if deployment.properties else None,
                "outputs": outputs,
            }
        except Exception as e:
            return {"error": str(e), "deployment_name": deployment_name}

    def _validate_deployment(self, subscription_id: str, arguments: dict) -> dict:
        """Validate deployed resources exist in resource group."""
        client = self._get_resource_client(subscription_id)
        rg = arguments["resource_group"]
        expected = set(arguments.get("expected_resources", []))

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


def main():
    """MCP server entry point — reads JSON-RPC from stdin, writes to stdout."""
    server = AzureDeploymentServer()
    logger.info("Azure Deployment MCP Server started")

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
