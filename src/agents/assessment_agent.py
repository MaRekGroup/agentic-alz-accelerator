"""
Assessment Agent — orchestrates brownfield discovery, WARA assessment, and report generation.

Workflow:
1. Discover — collect Azure environment inventory (read-only)
2. Assess — evaluate against WAF/CAF checks, produce scored findings
3. Report — generate current-state docs, target-state docs, diagrams, ADRs
"""

import logging

from azure.identity import DefaultAzureCredential
from semantic_kernel import Kernel
from semantic_kernel.functions.kernel_function_decorator import kernel_function

from src.config.settings import Settings
from src.tools.discovery import DiscoveryCollector, DiscoveryScope
from src.tools.wara_engine import WaraEngine
from src.tools.report_generator import ReportGenerator

logger = logging.getLogger(__name__)


class AssessmentAgent:
    """Orchestrates discovery → assessment → report generation."""

    def __init__(
        self,
        kernel: Kernel,
        credential: DefaultAzureCredential,
        settings: Settings,
    ):
        self.kernel = kernel
        self.credential = credential
        self.settings = settings

        self.collector = DiscoveryCollector(credential, settings)
        self.engine = WaraEngine(credential, settings)
        self.reporter = ReportGenerator(
            output_dir=settings.assess.output_dir,
        )

        self.kernel.add_plugin(self, plugin_name="assessment")

    @kernel_function(
        name="run_assessment",
        description="Run a full brownfield assessment: discover, evaluate, and generate reports",
    )
    async def run_assessment(
        self,
        scope: str = "",
        scope_type: str = "",
    ) -> dict:
        """Execute the full assessment pipeline.

        Args:
            scope: Target scope (subscription ID, MG name, etc.).
                   Defaults to settings.assess.scope.
            scope_type: One of tenant, management_group, subscription, resource_group.
                        Defaults to settings.assess.scope_type.

        Returns:
            dict with assessment summary and output file paths.
        """
        assess_scope = scope or self.settings.assess.scope
        assess_scope_type = scope_type or self.settings.assess.scope_type

        logger.info(
            "Starting assessment — scope=%s type=%s",
            assess_scope,
            assess_scope_type,
        )

        # 1. Discover
        logger.info("Phase 1/3: Discovery")
        discovery_scope = DiscoveryScope(assess_scope_type)
        discovery = await self.collector.discover(
            scope=assess_scope,
            scope_type=discovery_scope,
        )
        logger.info(
            "Discovery complete — %d MGs, %d subs, %d policy assignments",
            len(discovery.management_groups),
            len(discovery.subscriptions),
            len(discovery.policy_assignments),
        )

        # 2. Assess
        logger.info("Phase 2/3: Assessment")
        subscriptions = [
            s.get("subscriptionId", s.get("id", ""))
            for s in discovery.subscriptions
            if s.get("subscriptionId") or s.get("id")
        ]
        # Fall back to settings subscription if no subs discovered
        if not subscriptions and self.settings.azure.subscription_id:
            subscriptions = [self.settings.azure.subscription_id]

        assessment = await self.engine.assess(
            discovery,
            subscriptions=subscriptions,
        )
        logger.info(
            "Assessment complete — score=%.1f, findings=%d, checks=%d/%d passed",
            assessment.overall_score,
            len(assessment.findings),
            assessment.checks_passed,
            assessment.checks_run,
        )

        # 3. Report
        logger.info("Phase 3/3: Report generation")
        outputs = self.reporter.generate_all(
            discovery,
            assessment,
            scope_label=assess_scope,
        )
        output_paths = {k: str(v) for k, v in outputs.items()}
        logger.info("Reports generated: %s", list(output_paths.keys()))

        return {
            "scope": assess_scope,
            "scope_type": assess_scope_type,
            "overall_score": assessment.overall_score,
            "checks_run": assessment.checks_run,
            "checks_passed": assessment.checks_passed,
            "findings_count": len(assessment.findings),
            "critical": sum(1 for f in assessment.findings if f.severity == "critical"),
            "high": sum(1 for f in assessment.findings if f.severity == "high"),
            "outputs": output_paths,
        }

    @kernel_function(
        name="run_discovery_only",
        description="Run discovery without assessment — useful for environment inventory",
    )
    async def run_discovery_only(
        self,
        scope: str = "",
        scope_type: str = "",
    ) -> dict:
        """Run discovery phase only and return raw inventory."""
        assess_scope = scope or self.settings.assess.scope
        assess_scope_type = scope_type or self.settings.assess.scope_type

        discovery_scope = DiscoveryScope(assess_scope_type)
        discovery = await self.collector.discover(
            scope=assess_scope,
            scope_type=discovery_scope,
        )
        return discovery.to_dict()
