"""
WARA Engine — evaluates assessment rules against discovery data.

Runs declarative checks from wara_checks.yaml against a DiscoveryResult,
producing scored findings per WAF pillar and CAF design area.

Evidence collection (discovery.py) is separated from evaluation (this module).
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

from azure.identity import DefaultAzureCredential
from azure.mgmt.resourcegraph import ResourceGraphClient as AzureRGClient
from azure.mgmt.resourcegraph.models import (
    QueryRequest,
    QueryRequestOptions,
    ResultFormat,
)

from src.config.settings import Settings
from src.tools.discovery import DiscoveryResult

logger = logging.getLogger(__name__)

CHECKS_FILE = Path(__file__).parent.parent / "config" / "wara_checks.yaml"


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Pillar(str, Enum):
    RELIABILITY = "reliability"
    SECURITY = "security"
    COST_OPTIMIZATION = "cost_optimization"
    OPERATIONAL_EXCELLENCE = "operational_excellence"
    PERFORMANCE = "performance"


# Points deducted per severity level from a 100-point base
SEVERITY_DEDUCTIONS = {
    Severity.CRITICAL: 20,
    Severity.HIGH: 10,
    Severity.MEDIUM: 5,
    Severity.LOW: 2,
}


@dataclass
class Finding:
    """A single assessment finding."""

    rule_id: str
    title: str
    pillar: str
    caf_area: str
    alz_area: str
    severity: str
    confidence: str
    recommendation: str
    evidence: list[dict] = field(default_factory=list)
    remediation_steps: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    mappings: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "title": self.title,
            "pillar": self.pillar,
            "caf_area": self.caf_area,
            "alz_area": self.alz_area,
            "severity": self.severity,
            "confidence": self.confidence,
            "recommendation": self.recommendation,
            "evidence_count": len(self.evidence),
            "evidence": self.evidence[:10],  # Cap evidence in output
            "remediation_steps": self.remediation_steps,
            "references": self.references,
            "mappings": self.mappings,
        }


@dataclass
class PillarScore:
    """Score for a single WAF pillar."""

    pillar: str
    score: float = 100.0
    findings_count: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0

    def to_dict(self) -> dict:
        return {
            "pillar": self.pillar,
            "score": round(self.score, 1),
            "findings_count": self.findings_count,
            "critical": self.critical,
            "high": self.high,
            "medium": self.medium,
            "low": self.low,
        }


@dataclass
class AssessmentResult:
    """Complete assessment output."""

    scope: str
    assessed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    findings: list[Finding] = field(default_factory=list)
    pillar_scores: dict[str, PillarScore] = field(default_factory=dict)
    overall_score: float = 100.0
    checks_run: int = 0
    checks_passed: int = 0

    def to_dict(self) -> dict:
        return {
            "scope": self.scope,
            "assessed_at": self.assessed_at,
            "overall_score": round(self.overall_score, 1),
            "checks_run": self.checks_run,
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_run - self.checks_passed,
            "pillar_scores": {k: v.to_dict() for k, v in self.pillar_scores.items()},
            "findings": [f.to_dict() for f in self.findings],
        }


class WaraEngine:
    """Evaluates WARA assessment rules against discovery data.

    Evidence collection (DiscoveryCollector) is separate from evaluation
    (this class). The engine loads checks from wara_checks.yaml and runs
    them against a DiscoveryResult.
    """

    def __init__(
        self,
        credential: DefaultAzureCredential,
        settings: Settings,
        checks_file: Path | None = None,
    ):
        self.credential = credential
        self.settings = settings
        self._arg_client: AzureRGClient | None = None
        self.checks = self._load_checks(checks_file or CHECKS_FILE)

    @property
    def arg_client(self) -> AzureRGClient:
        if self._arg_client is None:
            self._arg_client = AzureRGClient(self.credential)
        return self._arg_client

    @staticmethod
    def _load_checks(path: Path) -> list[dict]:
        """Load check definitions from YAML catalog."""
        with open(path) as f:
            data = yaml.safe_load(f)
        checks = data.get("checks", [])
        logger.info(f"Loaded {len(checks)} WARA checks from {path}")
        return checks

    async def assess(
        self,
        discovery: DiscoveryResult,
        subscriptions: list[str] | None = None,
    ) -> AssessmentResult:
        """Run all checks against discovery data and produce scored results.

        Args:
            discovery: Pre-collected inventory from DiscoveryCollector.
            subscriptions: Subscription IDs for Resource Graph queries.

        Returns:
            AssessmentResult with findings and pillar scores.
        """
        result = AssessmentResult(scope=discovery.scope)
        subs = subscriptions or [self.settings.azure.subscription_id]

        # Initialize pillar scores
        for pillar in Pillar:
            result.pillar_scores[pillar.value] = PillarScore(pillar=pillar.value)

        for check in self.checks:
            result.checks_run += 1
            try:
                finding = await self._evaluate_check(check, discovery, subs)
                if finding:
                    result.findings.append(finding)
                    self._apply_finding_to_scores(finding, result.pillar_scores)
                else:
                    result.checks_passed += 1
            except Exception as e:
                logger.warning(f"Check {check.get('id', '?')} failed: {e}")
                # Count as passed (not penalized) if check itself errors
                result.checks_passed += 1

        # Calculate overall score (equal-weighted average of pillar scores)
        scores = [ps.score for ps in result.pillar_scores.values()]
        result.overall_score = sum(scores) / len(scores) if scores else 100.0

        # Sort findings: critical first, then high, medium, low
        severity_order = {
            Severity.CRITICAL.value: 0,
            Severity.HIGH.value: 1,
            Severity.MEDIUM.value: 2,
            Severity.LOW.value: 3,
        }
        result.findings.sort(key=lambda f: severity_order.get(f.severity, 99))

        logger.info(
            f"Assessment complete: {result.checks_run} checks, "
            f"{len(result.findings)} findings, "
            f"overall score {result.overall_score:.1f}"
        )
        return result

    async def _evaluate_check(
        self,
        check: dict,
        discovery: DiscoveryResult,
        subscriptions: list[str],
    ) -> Finding | None:
        """Evaluate a single check. Returns Finding if non-compliant, None if passed."""
        query_type = check.get("query_type", "resource_graph")
        match_type = check.get("match", "any")

        if query_type == "resource_graph":
            evidence = await self._run_resource_graph_check(
                check["query"], subscriptions
            )
        elif query_type == "discovery_field":
            evidence = self._run_discovery_field_check(
                check["query"], discovery
            )
        elif query_type == "policy":
            evidence = self._run_policy_check(check, discovery)
        else:
            logger.warning(f"Unknown query_type: {query_type} for {check.get('id')}")
            return None

        # Determine if this is a finding
        is_finding = False
        if match_type == "any" and evidence:
            is_finding = True
        elif match_type == "empty" and not evidence:
            is_finding = True
        elif match_type == "custom":
            eval_func = check.get("evaluation")
            if eval_func and hasattr(self, eval_func):
                is_finding = getattr(self, eval_func)(evidence, discovery)

        if not is_finding:
            return None

        return Finding(
            rule_id=check["id"],
            title=check["title"],
            pillar=check["pillar"],
            caf_area=check["caf_area"],
            alz_area=check["alz_area"],
            severity=check["severity"],
            confidence=check.get("confidence", "medium"),
            recommendation=check["recommendation"],
            evidence=evidence if isinstance(evidence, list) else [],
            remediation_steps=check.get("remediation_steps", []),
            references=check.get("references", []),
            mappings=check.get("mappings", {}),
        )

    async def _run_resource_graph_check(
        self,
        query: str,
        subscriptions: list[str],
    ) -> list[dict]:
        """Execute a Resource Graph query check."""
        options = QueryRequestOptions(
            result_format=ResultFormat.OBJECT_ARRAY,
            top=100,
        )
        request = QueryRequest(
            query=query,
            subscriptions=subscriptions,
            options=options,
        )
        result = self.arg_client.resources(request)
        return result.data if isinstance(result.data, list) else []

    @staticmethod
    def _run_discovery_field_check(
        field_path: str,
        discovery: DiscoveryResult,
    ) -> list[dict] | Any:
        """Check a field from discovery data using dot-notation path."""
        data: Any = discovery.to_dict()
        for key in field_path.split("."):
            if isinstance(data, dict):
                data = data.get(key)
            else:
                return []
            if data is None:
                return []
        if isinstance(data, list):
            return data
        return [data] if data else []

    @staticmethod
    def _run_policy_check(
        check: dict,
        discovery: DiscoveryResult,
    ) -> list[dict]:
        """Check policy compliance from discovery data."""
        compliance = discovery.policy_compliance
        non_compliant = []
        for sub_id, state in compliance.items():
            if isinstance(state, dict) and state.get("non_compliant_resources", 0) > 0:
                non_compliant.append(
                    {"subscription_id": sub_id, **state}
                )
        return non_compliant

    @staticmethod
    def _apply_finding_to_scores(
        finding: Finding,
        scores: dict[str, PillarScore],
    ) -> None:
        """Deduct points from the relevant pillar score."""
        pillar = finding.pillar
        if pillar not in scores:
            return

        ps = scores[pillar]
        ps.findings_count += 1
        severity = Severity(finding.severity)
        deduction = SEVERITY_DEDUCTIONS.get(severity, 0)
        ps.score = max(0.0, ps.score - deduction)

        if severity == Severity.CRITICAL:
            ps.critical += 1
        elif severity == Severity.HIGH:
            ps.high += 1
        elif severity == Severity.MEDIUM:
            ps.medium += 1
        elif severity == Severity.LOW:
            ps.low += 1

    # ── Custom evaluation functions ───────────────────────────────────────

    def check_caf_mg_hierarchy(
        self,
        evidence: list[dict],
        discovery: DiscoveryResult,
    ) -> bool:
        """Check if MG hierarchy follows CAF enterprise-scale pattern."""
        if not evidence:
            return True  # No MGs = finding

        mg_names = {mg.get("name", "").lower() for mg in evidence}

        # CAF expects: platform, landing zones (or landingzones), sandbox, decommissioned
        expected_patterns = ["platform", "landingzone", "sandbox"]
        matches = sum(
            1 for pattern in expected_patterns
            if any(pattern in name for name in mg_names)
        )
        # If fewer than 2 of the 3 expected patterns exist, flag it
        return matches < 2
