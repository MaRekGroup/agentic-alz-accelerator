"""Tests for the WARA assessment engine."""

import pytest
from unittest.mock import MagicMock, patch

from src.tools.wara_engine import (
    AssessmentResult,
    Finding,
    PillarScore,
    Severity,
    SEVERITY_DEDUCTIONS,
    WaraEngine,
)
from src.tools.discovery import DiscoveryResult, DiscoveryScope


@pytest.fixture
def mock_credential():
    return MagicMock()


@pytest.fixture
def mock_settings():
    settings = MagicMock()
    settings.azure.subscription_id = "test-sub-id"
    return settings


@pytest.fixture
def checks_file(tmp_path):
    """Create a minimal test checks file."""
    content = """
checks:
  - id: SEC-TEST-001
    title: "Test storage TLS check"
    pillar: security
    caf_area: security
    alz_area: security
    severity: critical
    confidence: high
    scope: subscription
    query_type: resource_graph
    query: |
      resources
      | where type =~ 'microsoft.storage/storageaccounts'
      | where properties.minimumTlsVersion != 'TLS1_2'
    match: any
    recommendation: "Set TLS to 1.2"
    remediation_steps:
      - "Update storage account"
    references:
      - "https://example.com"
    mappings:
      waf_pillar: [security]
      caf_lifecycle: [govern]

  - id: OPE-TEST-001
    title: "Test missing policies"
    pillar: operational_excellence
    caf_area: governance
    alz_area: policy
    severity: high
    confidence: high
    scope: subscription
    query_type: discovery_field
    query: "policy_assignments"
    match: empty
    recommendation: "Assign policies"
    remediation_steps:
      - "Assign ASB initiative"
    references:
      - "https://example.com"
    mappings:
      waf_pillar: [operational_excellence]
      caf_lifecycle: [govern]

  - id: COS-TEST-001
    title: "Test unattached disks"
    pillar: cost_optimization
    caf_area: management
    alz_area: logging
    severity: medium
    confidence: high
    scope: subscription
    query_type: resource_graph
    query: |
      resources
      | where type =~ 'microsoft.compute/disks'
      | where properties.diskState =~ 'Unattached'
    match: any
    recommendation: "Delete unattached disks"
    remediation_steps:
      - "Delete disk"
    references:
      - "https://example.com"
    mappings:
      waf_pillar: [cost_optimization]
      caf_lifecycle: [manage]
"""
    f = tmp_path / "test_checks.yaml"
    f.write_text(content)
    return f


@pytest.fixture
def engine(mock_credential, mock_settings, checks_file):
    with patch("src.tools.wara_engine.AzureRGClient"):
        e = WaraEngine(mock_credential, mock_settings, checks_file=checks_file)
        return e


@pytest.fixture
def empty_discovery():
    return DiscoveryResult(
        scope="test-sub",
        scope_type=DiscoveryScope.SUBSCRIPTION,
        policy_assignments=[],
    )


@pytest.fixture
def populated_discovery():
    return DiscoveryResult(
        scope="test-sub",
        scope_type=DiscoveryScope.SUBSCRIPTION,
        policy_assignments=[
            {"name": "ASB", "displayName": "Azure Security Benchmark"},
        ],
        management_groups=[
            {"name": "mrg", "displayName": "Root"},
            {"name": "mrg-platform", "displayName": "Platform"},
            {"name": "mrg-landingzones", "displayName": "Landing Zones"},
            {"name": "mrg-sandbox", "displayName": "Sandbox"},
        ],
    )


def _mock_arg_result(data: list[dict]):
    result = MagicMock()
    result.data = data
    return result


class TestFinding:
    def test_to_dict(self):
        f = Finding(
            rule_id="SEC-001",
            title="TLS check",
            pillar="security",
            caf_area="security",
            alz_area="security",
            severity="critical",
            confidence="high",
            recommendation="Fix TLS",
            evidence=[{"id": "res-1"}],
        )
        d = f.to_dict()
        assert d["rule_id"] == "SEC-001"
        assert d["severity"] == "critical"
        assert d["evidence_count"] == 1

    def test_evidence_capped(self):
        """Evidence in output is capped at 10 items."""
        f = Finding(
            rule_id="X-001",
            title="T",
            pillar="security",
            caf_area="security",
            alz_area="security",
            severity="low",
            confidence="low",
            recommendation="R",
            evidence=[{"id": f"res-{i}"} for i in range(20)],
        )
        d = f.to_dict()
        assert d["evidence_count"] == 20
        assert len(d["evidence"]) == 10


class TestPillarScore:
    def test_defaults(self):
        ps = PillarScore(pillar="security")
        assert ps.score == 100.0
        assert ps.findings_count == 0

    def test_to_dict(self):
        ps = PillarScore(pillar="reliability", score=80.0, findings_count=2, high=2)
        d = ps.to_dict()
        assert d["score"] == 80.0
        assert d["high"] == 2


class TestAssessmentResult:
    def test_to_dict(self):
        ar = AssessmentResult(scope="test", checks_run=5, checks_passed=3)
        d = ar.to_dict()
        assert d["checks_run"] == 5
        assert d["checks_failed"] == 2


class TestSeverityDeductions:
    def test_all_severities_defined(self):
        for s in Severity:
            assert s in SEVERITY_DEDUCTIONS

    def test_critical_highest(self):
        assert SEVERITY_DEDUCTIONS[Severity.CRITICAL] > SEVERITY_DEDUCTIONS[Severity.HIGH]
        assert SEVERITY_DEDUCTIONS[Severity.HIGH] > SEVERITY_DEDUCTIONS[Severity.MEDIUM]
        assert SEVERITY_DEDUCTIONS[Severity.MEDIUM] > SEVERITY_DEDUCTIONS[Severity.LOW]


class TestWaraEngine:
    def test_load_checks(self, engine):
        assert len(engine.checks) == 3
        ids = [c["id"] for c in engine.checks]
        assert "SEC-TEST-001" in ids
        assert "OPE-TEST-001" in ids
        assert "COS-TEST-001" in ids

    def test_load_real_checks(self, mock_credential, mock_settings):
        """Verify the real wara_checks.yaml loads without errors."""
        with patch("src.tools.wara_engine.AzureRGClient"):
            e = WaraEngine(mock_credential, mock_settings)
            assert len(e.checks) > 0
            for check in e.checks:
                assert "id" in check
                assert "pillar" in check
                assert "severity" in check

    @pytest.mark.asyncio
    async def test_assess_resource_graph_finding(self, engine, empty_discovery):
        """Resource graph check returns non-compliant resources → finding created."""
        non_compliant = [{"id": "sa-1", "name": "badsa", "minTls": "TLS1_0"}]
        engine._arg_client = MagicMock()
        engine._arg_client.resources.return_value = _mock_arg_result(non_compliant)

        result = await engine.assess(empty_discovery, subscriptions=["test-sub-id"])

        sec_findings = [f for f in result.findings if f.rule_id == "SEC-TEST-001"]
        assert len(sec_findings) == 1
        assert sec_findings[0].severity == "critical"
        assert sec_findings[0].evidence == non_compliant

    @pytest.mark.asyncio
    async def test_assess_resource_graph_passes(self, engine, empty_discovery):
        """Resource graph check returns empty → no finding (passes)."""
        engine._arg_client = MagicMock()
        engine._arg_client.resources.return_value = _mock_arg_result([])

        result = await engine.assess(empty_discovery, subscriptions=["test-sub-id"])

        # SEC-TEST-001 and COS-TEST-001 pass (empty results, match=any)
        # OPE-TEST-001 fires (empty policy_assignments, match=empty)
        sec_findings = [f for f in result.findings if f.rule_id == "SEC-TEST-001"]
        assert len(sec_findings) == 0

    @pytest.mark.asyncio
    async def test_assess_discovery_field_empty_match(self, engine, empty_discovery):
        """Discovery field check with match=empty fires when field is empty."""
        engine._arg_client = MagicMock()
        engine._arg_client.resources.return_value = _mock_arg_result([])

        result = await engine.assess(empty_discovery, subscriptions=["test-sub-id"])

        ope_findings = [f for f in result.findings if f.rule_id == "OPE-TEST-001"]
        assert len(ope_findings) == 1
        assert ope_findings[0].pillar == "operational_excellence"

    @pytest.mark.asyncio
    async def test_assess_discovery_field_populated(self, engine, populated_discovery):
        """Discovery field check with match=empty does NOT fire when field has data."""
        engine._arg_client = MagicMock()
        engine._arg_client.resources.return_value = _mock_arg_result([])

        result = await engine.assess(populated_discovery, subscriptions=["test-sub-id"])

        ope_findings = [f for f in result.findings if f.rule_id == "OPE-TEST-001"]
        assert len(ope_findings) == 0

    @pytest.mark.asyncio
    async def test_scoring_critical_deduction(self, engine, empty_discovery):
        """Critical finding deducts 20 points from pillar score."""
        non_compliant = [{"id": "sa-1", "name": "badsa"}]
        engine._arg_client = MagicMock()
        engine._arg_client.resources.return_value = _mock_arg_result(non_compliant)

        result = await engine.assess(empty_discovery, subscriptions=["test-sub-id"])

        sec_score = result.pillar_scores["security"]
        assert sec_score.score == 80.0  # 100 - 20 (critical)
        assert sec_score.critical == 1

    @pytest.mark.asyncio
    async def test_overall_score_average(self, engine, empty_discovery):
        """Overall score is average of all pillar scores."""
        engine._arg_client = MagicMock()
        engine._arg_client.resources.return_value = _mock_arg_result([])

        result = await engine.assess(empty_discovery, subscriptions=["test-sub-id"])

        # Only OPE fires (high=-10, score=90). Others stay at 100.
        # Average = (100 + 100 + 100 + 90 + 100) / 5 = 98
        assert result.overall_score == 98.0

    @pytest.mark.asyncio
    async def test_findings_sorted_by_severity(self, engine, empty_discovery):
        """Findings are sorted critical → high → medium → low."""
        non_compliant = [{"id": "res-1"}]
        engine._arg_client = MagicMock()
        engine._arg_client.resources.return_value = _mock_arg_result(non_compliant)

        result = await engine.assess(empty_discovery, subscriptions=["test-sub-id"])

        if len(result.findings) >= 2:
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            for i in range(len(result.findings) - 1):
                current = severity_order.get(result.findings[i].severity, 99)
                next_sev = severity_order.get(result.findings[i + 1].severity, 99)
                assert current <= next_sev

    @pytest.mark.asyncio
    async def test_check_error_does_not_crash(self, engine, empty_discovery):
        """Engine errors on individual checks gracefully (counts as passed)."""
        engine._arg_client = MagicMock()
        engine._arg_client.resources.side_effect = Exception("API error")

        result = await engine.assess(empty_discovery, subscriptions=["test-sub-id"])

        # 2 resource_graph checks error (counted as passed), 1 discovery_field check fires
        assert result.checks_run == 3
        assert result.checks_passed == 2  # SEC-TEST-001 + COS-TEST-001 errored → passed
        assert len(result.findings) == 1  # OPE-TEST-001 fires (discovery_field, no API call)

    def test_discovery_field_check_dotted_path(self, engine):
        """Discovery field check navigates dot-notation paths."""
        discovery = DiscoveryResult(
            scope="test",
            scope_type=DiscoveryScope.SUBSCRIPTION,
            logging_config={
                "log_analytics_workspaces": [{"name": "law-1"}],
                "automation_accounts": [],
            },
        )
        # Non-empty field
        result = engine._run_discovery_field_check(
            "logging_config.log_analytics_workspaces", discovery
        )
        assert len(result) == 1

        # Empty field
        result = engine._run_discovery_field_check(
            "logging_config.automation_accounts", discovery
        )
        assert len(result) == 0

    def test_check_caf_mg_hierarchy_compliant(self, engine):
        """CAF MG hierarchy check passes when expected MGs exist."""
        mgs = [
            {"name": "mrg-platform"},
            {"name": "mrg-landingzones"},
            {"name": "mrg-sandbox"},
        ]
        discovery = DiscoveryResult(
            scope="mrg", scope_type=DiscoveryScope.MANAGEMENT_GROUP
        )
        assert engine.check_caf_mg_hierarchy(mgs, discovery) is False  # False = no finding

    def test_check_caf_mg_hierarchy_non_compliant(self, engine):
        """CAF MG hierarchy check fires when expected MGs are missing."""
        mgs = [
            {"name": "corp-mg"},
            {"name": "prod-mg"},
        ]
        discovery = DiscoveryResult(
            scope="test", scope_type=DiscoveryScope.MANAGEMENT_GROUP
        )
        assert engine.check_caf_mg_hierarchy(mgs, discovery) is True  # True = finding


class TestApplyFindingToScores:
    def test_critical_deduction(self):
        scores = {"security": PillarScore(pillar="security")}
        finding = Finding(
            rule_id="SEC-001", title="T", pillar="security", caf_area="security",
            alz_area="security", severity="critical", confidence="high", recommendation="R",
        )
        WaraEngine._apply_finding_to_scores(finding, scores)
        assert scores["security"].score == 80.0
        assert scores["security"].critical == 1

    def test_score_floor_zero(self):
        scores = {"security": PillarScore(pillar="security", score=10.0)}
        finding = Finding(
            rule_id="SEC-001", title="T", pillar="security", caf_area="security",
            alz_area="security", severity="critical", confidence="high", recommendation="R",
        )
        WaraEngine._apply_finding_to_scores(finding, scores)
        assert scores["security"].score == 0.0  # Floored at 0

    def test_unknown_pillar_ignored(self):
        scores = {"security": PillarScore(pillar="security")}
        finding = Finding(
            rule_id="X-001", title="T", pillar="nonexistent", caf_area="x",
            alz_area="x", severity="high", confidence="high", recommendation="R",
        )
        WaraEngine._apply_finding_to_scores(finding, scores)
        assert scores["security"].score == 100.0  # Unchanged


class TestDirectoryLoader:
    """Tests for the per-pillar directory-based check loading."""

    def test_load_from_directory(self, tmp_path):
        """Loads and merges checks from multiple YAML files."""
        (tmp_path / "security.yaml").write_text("""
checks:
  - id: SEC-T01
    title: Test sec
    pillar: security
    severity: high
    scope: subscription
    query_type: resource_graph
    query: "resources | where 1==0"
    match: any
    recommendation: Fix
""")
        (tmp_path / "reliability.yaml").write_text("""
checks:
  - id: REL-T01
    title: Test rel
    pillar: reliability
    severity: medium
    scope: subscription
    query_type: resource_graph
    query: "resources | where 1==0"
    match: any
    recommendation: Fix
""")
        checks = WaraEngine._load_from_directory(tmp_path)
        assert len(checks) == 2
        ids = {c["id"] for c in checks}
        assert ids == {"SEC-T01", "REL-T01"}

    def test_deduplication(self, tmp_path):
        """Duplicate IDs across files are deduplicated (first wins)."""
        (tmp_path / "a_first.yaml").write_text("""
checks:
  - id: DUP-001
    title: First version
    pillar: security
    severity: high
    scope: subscription
    query_type: resource_graph
    query: "resources | where 1==0"
    match: any
    recommendation: First
""")
        (tmp_path / "b_second.yaml").write_text("""
checks:
  - id: DUP-001
    title: Second version (should be skipped)
    pillar: security
    severity: low
    scope: subscription
    query_type: resource_graph
    query: "resources | where 1==0"
    match: any
    recommendation: Second
""")
        checks = WaraEngine._load_from_directory(tmp_path)
        assert len(checks) == 1
        assert checks[0]["title"] == "First version"

    def test_real_checks_directory(self, mock_credential, mock_settings):
        """The real wara_checks/ directory loads all per-pillar + APRL checks."""
        with patch("src.tools.wara_engine.AzureRGClient"):
            e = WaraEngine(mock_credential, mock_settings)
            # Should load from directory (20 custom + APRL synced)
            assert len(e.checks) >= 20
            # All checks have required fields
            for check in e.checks:
                assert "id" in check
                assert "pillar" in check
                assert "severity" in check
                assert "query" in check
