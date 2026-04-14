"""
Requirements Agent (Scribe) — captures landing zone requirements through conversation.

Gathers functional, non-functional, compliance, and budgetary requirements,
mapping them to CAF design areas. Produces 01-requirements.md artifact.
"""

import logging
from typing import Annotated

from azure.identity import DefaultAzureCredential
from semantic_kernel import Kernel
from semantic_kernel.functions.kernel_function_decorator import kernel_function

from src.config.settings import Settings

logger = logging.getLogger(__name__)

SCRIBE_SYSTEM_PROMPT = """You are the Requirements Agent (📜 Scribe) for the Azure Landing Zone Accelerator.

Your role is to gather comprehensive landing zone requirements through interactive conversation,
ensuring coverage of all 8 CAF design areas.

## CAF Design Areas Checklist

You MUST capture requirements for each area:

1. **Billing & Tenant** — Target tenant, EA/MCA enrollment, subscription strategy, cost center
2. **Identity & Access** — Entra ID integration, RBAC model, PIM, external identity needs
3. **Resource Organization** — Management group hierarchy, subscription design, naming convention, tagging strategy
4. **Network Topology & Connectivity** — Hub-spoke vs standalone, address space, ExpressRoute/VPN, DNS, DDoS, Azure Firewall
5. **Security** — Compliance frameworks (CIS, NIST, ISO, SOC2), Defender plans, Sentinel, Key Vault, encryption at rest/transit
6. **Management** — Monitoring (Log Analytics, Azure Monitor), backup, update management, alerting
7. **Governance** — Azure Policy requirements, custom policies, cost governance, guardrails
8. **Platform Automation & DevOps** — IaC framework (Bicep/Terraform), CI/CD platform, GitOps, approval workflows

## Additional Requirements

- **Workload type** — internet-facing, internal corp, dev/test, SAP, AI/ML
- **Compliance** — Regulatory standards, data residency, sovereignty
- **Budget** — Monthly budget, cost alerts, approval for overages
- **Environments** — dev, staging, prod (and how many of each)
- **Regions** — Primary and DR regions
- **Timeline** — Target deployment date

## Complexity Classification

Based on gathered requirements, classify complexity:
- **Simple**: ≤3 resource types, single region, no custom policy, single env
- **Standard**: 4-8 types, multi-region OR multi-env, ≤3 custom policies
- **Complex**: >8 types, multi-region + multi-env, >3 custom policies, hub-spoke

## Output Format

Produce a structured `01-requirements.md` with all gathered requirements organized by
CAF design area, plus metadata (complexity, IaC tool, environments, regions).
"""


class RequirementsAgent:
    """Captures landing zone requirements mapped to CAF design areas."""

    def __init__(
        self,
        kernel: Kernel,
        credential: DefaultAzureCredential,
        settings: Settings,
    ):
        self.kernel = kernel
        self.credential = credential
        self.settings = settings
        self.kernel.add_plugin(self, plugin_name="requirements")

    @kernel_function(
        name="get_requirements_template",
        description="Get the requirements template with all CAF design area sections",
    )
    def get_requirements_template(self) -> str:
        """Return the requirements template."""
        return """# Landing Zone Requirements

## Metadata
- **Project Name**:
- **Complexity**: [simple | standard | complex]
- **IaC Framework**: [bicep | terraform]
- **Primary Region**:
- **DR Region**:
- **Environments**: [dev, staging, prod]
- **Target Date**:

## 1. Billing & Tenant
- **Tenant ID**:
- **Enrollment Type**: [EA | MCA | PAYG]
- **Subscription Strategy**: [single | multi-subscription]
- **Cost Center**:

## 2. Identity & Access
- **Entra ID Tenant**:
- **RBAC Model**: [custom roles | built-in only]
- **PIM Required**: [yes | no]
- **External Identities**: [B2B | B2C | none]
- **Break-glass Accounts**: [yes | no]

## 3. Resource Organization
- **Management Group Hierarchy**: [enterprise-scale | custom]
- **Subscription Design**: [per-workload | per-environment | per-team]
- **Naming Convention**: [CAF standard | custom]
- **Required Tags**: [environment, cost-center, owner, project]

## 4. Network Topology & Connectivity
- **Topology**: [hub-spoke | vwan | standalone]
- **Address Space**:
- **On-premises Connectivity**: [ExpressRoute | VPN | none]
- **DNS Strategy**: [Azure DNS | custom | hybrid]
- **DDoS Protection**: [yes | no]
- **Azure Firewall**: [yes | no]
- **Network Segmentation**: [NSGs | ASGs | both]

## 5. Security
- **Compliance Frameworks**: [CIS | NIST 800-53 | ISO 27001 | SOC2 | custom]
- **Defender for Cloud**: [yes | no]
- **Defender Plans**: [VMs, SQL, Storage, KeyVault, DNS, ARM]
- **Microsoft Sentinel**: [yes | no]
- **Key Vault**: [yes | no]
- **Data Encryption**: [at-rest | in-transit | both]
- **Data Residency**: [region-specific | global]

## 6. Management
- **Log Analytics Workspace**: [centralized | per-subscription]
- **Log Retention**: [30 | 90 | 365 days]
- **Azure Monitor**: [yes | no]
- **Backup Strategy**: [Azure Backup | custom]
- **Update Management**: [Azure Update Manager | custom]
- **Alert Configuration**: [action groups | email | Teams webhook]

## 7. Governance
- **Azure Policy**: [built-in initiatives | custom policies | both]
- **Policy Initiatives**: [Azure Security Benchmark | CIS | NIST | ISO]
- **Custom Policies**: [list specific requirements]
- **Cost Governance**: [budget alerts | anomaly detection | both]
- **Monthly Budget**: $
- **Guardrails**: [deny public IP | enforce encryption | require tags]

## 8. Platform Automation & DevOps
- **IaC Framework**: [Bicep | Terraform]
- **CI/CD Platform**: [GitHub Actions | Azure DevOps | both]
- **Approval Workflows**: [environment-based | role-based]
- **GitOps**: [yes | no]
- **Automated Testing**: [what-if | policy compliance | both]
"""

    @kernel_function(
        name="classify_complexity",
        description="Classify project complexity based on gathered requirements",
    )
    def classify_complexity(
        self,
        resource_type_count: Annotated[int, "Number of distinct resource types"],
        region_count: Annotated[int, "Number of Azure regions"],
        environment_count: Annotated[int, "Number of environments"],
        custom_policy_count: Annotated[int, "Number of custom policies"],
        networking_type: Annotated[str, "Network topology: hub_spoke, vwan, standalone"],
    ) -> dict:
        """Classify project complexity and determine challenger review depth."""
        if (
            resource_type_count <= 3
            and region_count <= 1
            and custom_policy_count == 0
            and environment_count <= 1
        ):
            tier = "simple"
            challenger_passes = {"requirements": 1, "architecture": 1, "plan": 1, "code": 1}
        elif (
            resource_type_count > 8
            or (region_count > 1 and environment_count > 1)
            or custom_policy_count > 3
            or networking_type == "hub_spoke"
        ):
            tier = "complex"
            challenger_passes = {"requirements": 1, "architecture": 3, "plan": 2, "code": 3}
        else:
            tier = "standard"
            challenger_passes = {"requirements": 1, "architecture": 2, "plan": 2, "code": 2}

        return {
            "complexity_tier": tier,
            "challenger_passes": challenger_passes,
            "inputs": {
                "resource_types": resource_type_count,
                "regions": region_count,
                "environments": environment_count,
                "custom_policies": custom_policy_count,
                "networking": networking_type,
            },
        }

    @kernel_function(
        name="validate_requirements_completeness",
        description="Check if requirements cover all 8 CAF design areas",
    )
    def validate_requirements_completeness(
        self,
        requirements_content: Annotated[str, "Requirements document content"],
    ) -> dict:
        """Validate that all CAF design areas are addressed."""
        caf_areas = {
            "billing_tenant": ["billing", "tenant", "enrollment", "subscription strategy"],
            "identity_access": ["identity", "rbac", "entra", "pim", "access"],
            "resource_organization": ["management group", "naming", "tagging", "resource org"],
            "network_topology": ["network", "vnet", "hub-spoke", "connectivity", "dns"],
            "security": ["security", "defender", "sentinel", "encryption", "compliance"],
            "management": ["log analytics", "monitor", "backup", "update management"],
            "governance": ["policy", "governance", "guardrail", "budget"],
            "platform_automation": ["iac", "bicep", "terraform", "ci/cd", "devops", "automation"],
        }

        content_lower = requirements_content.lower()
        coverage = {}
        for area, keywords in caf_areas.items():
            covered = any(kw in content_lower for kw in keywords)
            coverage[area] = covered

        covered_count = sum(1 for v in coverage.values() if v)
        missing = [area for area, covered in coverage.items() if not covered]

        return {
            "complete": covered_count == len(caf_areas),
            "coverage": coverage,
            "covered_count": covered_count,
            "total_areas": len(caf_areas),
            "missing_areas": missing,
            "completeness_pct": round(covered_count / len(caf_areas) * 100, 1),
        }
