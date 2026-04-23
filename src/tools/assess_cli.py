"""
CLI entry point for the assessment pipeline.

Usage:
    python -m src.tools.assess_cli --scope <scope> --scope-type <type> [--mode assess]

Called by the assess.yml GitHub Actions workflow.
"""

import argparse
import asyncio
import json
import logging
import sys

from azure.identity import DefaultAzureCredential

from src.config.settings import Settings
from src.tools.discovery import DiscoveryCollector, DiscoveryScope
from src.tools.wara_engine import WaraEngine
from src.tools.report_generator import ReportGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


async def run_assessment(scope: str, scope_type: str, mode: str) -> dict:
    """Execute the assessment pipeline."""
    credential = DefaultAzureCredential()
    settings = Settings()

    # Override settings from CLI args
    settings.assess.scope = scope
    settings.assess.scope_type = scope_type
    settings.assess.mode = mode

    collector = DiscoveryCollector(credential, settings)
    engine = WaraEngine(credential, settings)
    reporter = ReportGenerator(output_dir=settings.assess.output_dir)

    # Phase 1: Discover
    logger.info("Phase 1/3: Discovery — scope=%s type=%s", scope, scope_type)
    discovery_scope = DiscoveryScope(scope_type)
    discovery = await collector.discover(scope=scope, scope_type=discovery_scope)
    logger.info(
        "Discovery complete — %d MGs, %d subs, %d policies, %d errors",
        len(discovery.management_groups),
        len(discovery.subscriptions),
        len(discovery.policy_assignments),
        len(discovery.errors),
    )

    # Phase 2: Assess
    logger.info("Phase 2/3: Assessment")
    subscriptions = [
        s.get("subscriptionId", s.get("id", ""))
        for s in discovery.subscriptions
        if s.get("subscriptionId") or s.get("id")
    ]
    if not subscriptions and settings.azure.subscription_id:
        subscriptions = [settings.azure.subscription_id]

    assessment = await engine.assess(discovery, subscriptions=subscriptions)
    logger.info(
        "Assessment complete — score=%.1f, findings=%d, checks=%d/%d passed",
        assessment.overall_score,
        len(assessment.findings),
        assessment.checks_passed,
        assessment.checks_run,
    )

    # Phase 3: Report
    logger.info("Phase 3/3: Report generation")
    outputs = reporter.generate_all(discovery, assessment, scope_label=scope)
    for name, path in outputs.items():
        logger.info("  %s → %s", name, path)

    # Write summary JSON for CI consumption
    summary = {
        "scope": scope,
        "scope_type": scope_type,
        "mode": mode,
        "overall_score": assessment.overall_score,
        "checks_run": assessment.checks_run,
        "checks_passed": assessment.checks_passed,
        "findings_count": len(assessment.findings),
        "critical": sum(1 for f in assessment.findings if f.severity == "critical"),
        "high": sum(1 for f in assessment.findings if f.severity == "high"),
        "medium": sum(1 for f in assessment.findings if f.severity == "medium"),
        "low": sum(1 for f in assessment.findings if f.severity == "low"),
        "outputs": {k: str(v) for k, v in outputs.items()},
    }

    logger.info("Assessment complete — overall score: %.1f/100", assessment.overall_score)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="ALZ Accelerator Assessment CLI")
    parser.add_argument("--scope", required=True, help="Assessment scope")
    parser.add_argument(
        "--scope-type",
        required=True,
        choices=["tenant", "management_group", "subscription", "resource_group"],
        help="Scope type",
    )
    parser.add_argument(
        "--mode",
        default="assess",
        choices=["assess", "assess-and-plan", "assess-and-remediate", "onboard"],
        help="Assessment mode",
    )
    args = parser.parse_args()

    result = asyncio.run(run_assessment(args.scope, args.scope_type, args.mode))

    # Print summary to stdout for CI parsing
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["critical"] == 0 else 1)


if __name__ == "__main__":
    main()
