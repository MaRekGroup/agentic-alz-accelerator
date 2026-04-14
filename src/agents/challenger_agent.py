"""
Challenger Agent — adversarial reviewer for architecture, plans, and code.

Inspired by the APEX Challenger pattern, this agent performs adversarial review
at each approval gate, challenging assumptions, finding gaps, and verifying
alignment with CAF design areas and security baseline.
"""

import logging
from typing import Annotated

from azure.identity import DefaultAzureCredential
from semantic_kernel import Kernel
from semantic_kernel.functions.kernel_function_decorator import kernel_function

from src.config.settings import Settings

logger = logging.getLogger(__name__)

CHALLENGER_SYSTEM_PROMPT = """You are the Challenger Agent (⚔️) for the Azure Landing Zone Accelerator.

Your role is adversarial review: you challenge architecture decisions, implementation
plans, and generated code to find gaps, risks, and non-compliance BEFORE deployment.

Review Framework:
1. **CAF Alignment** — Does it address all 8 design areas? (Billing, Identity, Resource Org,
   Networking, Security, Management, Governance, Platform Automation)
2. **WAF Pillars** — Reliability, Security, Cost Optimization, Operational Excellence, Performance
3. **Security Baseline** — TLS 1.2, HTTPS-only, no public blob, Managed Identity, AD-only SQL,
   no public network in prod
4. **Cost Governance** — Budget alerts at 80/100/120%, no hardcoded values, parameterized budgets
5. **AVM Compliance** — Uses Azure Verified Modules where available
6. **Naming & Tagging** — CAF naming convention, required tags present

For each finding, classify severity:
- **must_fix**: Blocks deployment. Security violations, missing governance, compliance gaps.
- **should_fix**: Should be addressed. Sub-optimal architecture, missing best practices.
- **consider**: Nice-to-have improvements. Optimization opportunities.

Be thorough but fair. Challenge creative decisions, not machine-discovered data.
"""


class ChallengerAgent:
    """Adversarial review agent for validating outputs at approval gates."""

    def __init__(
        self,
        kernel: Kernel,
        credential: DefaultAzureCredential,
        settings: Settings,
    ):
        self.kernel = kernel
        self.credential = credential
        self.settings = settings
        self.kernel.add_plugin(self, plugin_name="challenger")

    @kernel_function(
        name="review_requirements",
        description="Challenge requirements for completeness and feasibility",
    )
    async def review_requirements(
        self,
        requirements: Annotated[str, "Requirements document content"],
    ) -> dict:
        """Review requirements at Gate 1."""
        checks = {
            "caf_design_areas_covered": self._check_caf_coverage(requirements),
            "compliance_requirements": "compliance" in requirements.lower()
            or "regulatory" in requirements.lower(),
            "budget_specified": "budget" in requirements.lower()
            or "cost" in requirements.lower(),
            "networking_defined": any(
                kw in requirements.lower()
                for kw in ["hub-spoke", "networking", "vnet", "connectivity"]
            ),
            "identity_defined": any(
                kw in requirements.lower()
                for kw in ["identity", "rbac", "entra", "managed identity"]
            ),
            "security_considered": any(
                kw in requirements.lower()
                for kw in ["security", "defender", "sentinel", "key vault"]
            ),
        }

        findings = []
        if not checks["caf_design_areas_covered"]:
            findings.append({
                "severity": "must_fix",
                "area": "CAF Coverage",
                "detail": "Requirements do not address all 8 CAF design areas",
            })
        if not checks["budget_specified"]:
            findings.append({
                "severity": "should_fix",
                "area": "Cost Governance",
                "detail": "No budget or cost constraints specified",
            })
        if not checks["security_considered"]:
            findings.append({
                "severity": "must_fix",
                "area": "Security",
                "detail": "Security requirements not explicitly defined",
            })

        return {
            "gate": "Gate 1 — Requirements",
            "checks": checks,
            "findings": findings,
            "must_fix_count": sum(1 for f in findings if f["severity"] == "must_fix"),
            "passed": all(f["severity"] != "must_fix" for f in findings),
        }

    @kernel_function(
        name="review_architecture",
        description="Challenge architecture assessment against WAF and CAF",
    )
    async def review_architecture(
        self,
        assessment: Annotated[str, "Architecture assessment content"],
        complexity: Annotated[str, "Complexity tier: simple, standard, complex"] = "standard",
    ) -> dict:
        """Review architecture at Gate 2."""
        findings = []

        # Check WAF pillar coverage
        waf_pillars = ["reliability", "security", "cost", "operational", "performance"]
        for pillar in waf_pillars:
            if pillar not in assessment.lower():
                findings.append({
                    "severity": "should_fix",
                    "area": f"WAF — {pillar.title()}",
                    "detail": f"WAF {pillar} pillar not addressed in assessment",
                })

        # Check for cost estimation
        if "cost" not in assessment.lower() or "estimate" not in assessment.lower():
            findings.append({
                "severity": "must_fix",
                "area": "Cost Estimation",
                "detail": "Architecture assessment missing cost estimation",
            })

        # Check for HA/DR
        if "availability" not in assessment.lower() and "disaster" not in assessment.lower():
            findings.append({
                "severity": "should_fix",
                "area": "Reliability",
                "detail": "No HA/DR strategy discussed",
            })

        return {
            "gate": "Gate 2 — Architecture",
            "findings": findings,
            "must_fix_count": sum(1 for f in findings if f["severity"] == "must_fix"),
            "passed": all(f["severity"] != "must_fix" for f in findings),
        }

    @kernel_function(
        name="review_code",
        description="Challenge generated IaC code against security baseline and AVM standards",
    )
    async def review_code(
        self,
        code_content: Annotated[str, "Generated IaC code content"],
        iac_tool: Annotated[str, "IaC tool: bicep or terraform"] = "bicep",
    ) -> dict:
        """Review generated code at Gate 5."""
        findings = []

        # Security baseline checks
        security_checks = self._check_security_baseline(code_content, iac_tool)
        findings.extend(security_checks)

        # Cost governance checks
        if "budget" not in code_content.lower() and "consumption" not in code_content.lower():
            findings.append({
                "severity": "must_fix",
                "area": "Cost Governance",
                "detail": "No budget resource found in generated code",
            })

        # Naming convention checks (CAF)
        if iac_tool == "bicep" and "param prefix" not in code_content.lower():
            findings.append({
                "severity": "should_fix",
                "area": "Naming",
                "detail": "Resource naming not parameterized with prefix",
            })

        # Tagging checks
        if "tags" not in code_content.lower():
            findings.append({
                "severity": "must_fix",
                "area": "Resource Organization",
                "detail": "No tagging strategy found in code",
            })

        # Diagnostic settings check
        if "diagnosticsettings" not in code_content.lower().replace(" ", "").replace("_", ""):
            findings.append({
                "severity": "should_fix",
                "area": "Management",
                "detail": "Diagnostic settings not configured for resources",
            })

        return {
            "gate": "Gate 5 — Code Review",
            "findings": findings,
            "must_fix_count": sum(1 for f in findings if f["severity"] == "must_fix"),
            "passed": all(f["severity"] != "must_fix" for f in findings),
        }

    @kernel_function(
        name="review_deployment",
        description="Challenge deployment plan and what-if/plan output",
    )
    async def review_deployment(
        self,
        what_if_output: Annotated[str, "What-if or terraform plan output"],
    ) -> dict:
        """Review deployment at Gate 5 (pre-deploy security review)."""
        findings = []

        # Check for destructive changes
        destructive_keywords = ["delete", "destroy", "remove", "replace"]
        for kw in destructive_keywords:
            if kw in what_if_output.lower():
                findings.append({
                    "severity": "must_fix",
                    "area": "Deployment Safety",
                    "detail": f"Destructive operation detected: '{kw}' — requires explicit approval",
                })

        # Check for public IP creation
        if "publicipaddress" in what_if_output.lower().replace(" ", ""):
            findings.append({
                "severity": "should_fix",
                "area": "Security Baseline",
                "detail": "Public IP address being created — verify this is intentional",
            })

        return {
            "gate": "Gate 5 — Deployment Review",
            "findings": findings,
            "must_fix_count": sum(1 for f in findings if f["severity"] == "must_fix"),
            "passed": all(f["severity"] != "must_fix" for f in findings),
        }

    def _check_caf_coverage(self, content: str) -> bool:
        """Check if content addresses all 8 CAF design areas."""
        caf_areas = [
            "billing", "identity", "resource organization", "network",
            "security", "management", "governance", "automation",
        ]
        content_lower = content.lower()
        covered = sum(1 for area in caf_areas if area in content_lower)
        return covered >= 6  # At least 6 of 8 areas

    def _check_security_baseline(self, code: str, iac_tool: str) -> list[dict]:
        """Check code against the non-negotiable security baseline."""
        findings = []
        code_lower = code.lower()

        if iac_tool == "bicep":
            checks = [
                ("TLS1_2" in code or "tls1_2" in code_lower, "TLS 1.2 minimum"),
                ("supportsHttpsTrafficOnly: true" in code or "httpsonly" in code_lower, "HTTPS-only"),
                ("allowBlobPublicAccess: false" in code or "allowblobpublicaccess" not in code_lower, "No public blob"),
                ("SystemAssigned" in code, "Managed Identity"),
            ]
        else:
            checks = [
                ("min_tls_version" in code_lower, "TLS 1.2 minimum"),
                ("https_traffic_only" in code_lower, "HTTPS-only"),
                ("allow_nested_items_to_be_public" in code_lower or "allow_blob_public_access" not in code_lower, "No public blob"),
                ("SystemAssigned" in code, "Managed Identity"),
            ]

        for passed, rule_name in checks:
            if not passed:
                findings.append({
                    "severity": "must_fix",
                    "area": "Security Baseline",
                    "detail": f"Security baseline violation: {rule_name} not enforced",
                })

        return findings
