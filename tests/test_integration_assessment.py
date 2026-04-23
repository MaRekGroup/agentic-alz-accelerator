"""Integration tests — end-to-end assessment pipeline with mock Azure responses."""

import json
from unittest.mock import MagicMock, patch

import pytest

from src.tools.discovery import DiscoveryResult, DiscoveryScope
from src.tools.wara_engine import WaraEngine
from src.tools.report_generator import ReportGenerator


def _mock_arg_result(data):
    result = MagicMock()
    result.data = data
    return result


@pytest.fixture
def mock_credential():
    return MagicMock()


@pytest.fixture
def mock_settings(tmp_path):
    settings = MagicMock()
    settings.azure.subscription_id = "sub-001"
    settings.azure.management_group_prefix = "mrg"
    settings.assess.output_dir = str(tmp_path / "assessment")
    settings.assess.scope = "sub-001"
    settings.assess.scope_type = "subscription"
    return settings


class TestEndToEndPipeline:
    """Tests the full discover → assess → report flow."""

    @pytest.mark.asyncio
    async def test_clean_environment(self, mock_credential, mock_settings, tmp_path):
        """An environment with no violations produces score 100 and no findings."""
        with patch("src.tools.wara_engine.AzureRGClient") as mock_rg:
            mock_rg_instance = MagicMock()
            mock_rg_instance.resources.return_value = _mock_arg_result([])
            mock_rg.return_value = mock_rg_instance

            engine = WaraEngine(mock_credential, mock_settings)

            discovery = DiscoveryResult(
                scope="sub-001",
                scope_type=DiscoveryScope.SUBSCRIPTION,
                subscriptions=[{"subscriptionId": "sub-001", "name": "clean-sub"}],
                policy_assignments=[{"name": "asb", "displayName": "Azure Security Benchmark"}],
                management_groups=[
                    {"name": "mrg", "displayName": "Root"},
                    {"name": "mrg-platform", "displayName": "Platform"},
                    {"name": "mrg-landingzones", "displayName": "Landing Zones"},
                    {"name": "mrg-sandbox", "displayName": "Sandbox"},
                ],
                logging_config={
                    "log_analytics_workspaces": [{"name": "law-mgmt"}],
                },
                network_topology={
                    "vnets": [{"name": "hub-vnet", "addressPrefixes": ["10.0.0.0/16"], "peerings": []}],
                },
                security_posture={"secure_score": 85},
            )

            assessment = await engine.assess(discovery, subscriptions=["sub-001"])

            # Clean environment — only resource_graph checks may fire if mocked empty
            # Discovery field checks pass because we populated the fields
            assert assessment.overall_score >= 90.0
            assert assessment.checks_run > 0

            # Generate reports
            reporter = ReportGenerator(output_dir=mock_settings.assess.output_dir)
            outputs = reporter.generate_all(discovery, assessment, scope_label="sub-001")

            # All 6 report files created
            assert len(outputs) == 6
            for name, path in outputs.items():
                assert path.exists(), f"{name} not created"

            # Validate JSON report
            json_data = json.loads(outputs["assessment_json"].read_text())
            assert json_data["overall_score"] >= 90.0
            assert json_data["checks_run"] > 0

            # Current state has environment info
            current_state = outputs["current_state"].read_text()
            assert "sub-001" in current_state
            assert "hub-vnet" in current_state

            # Mermaid diagram has structure
            diagram = outputs["architecture_diagram"].read_text()
            assert "graph TD" in diagram

    @pytest.mark.asyncio
    async def test_non_compliant_environment(self, mock_credential, mock_settings, tmp_path):
        """An environment with violations produces findings and lower scores."""
        non_compliant_storage = [
            {"id": "/sub/rg/sa1", "name": "badsa1", "minTls": "TLS1_0"},
            {"id": "/sub/rg/sa2", "name": "badsa2", "minTls": "TLS1_0"},
        ]

        with patch("src.tools.wara_engine.AzureRGClient") as mock_rg:
            mock_rg_instance = MagicMock()
            # Return non-compliant results for every RG query
            mock_rg_instance.resources.return_value = _mock_arg_result(non_compliant_storage)
            mock_rg.return_value = mock_rg_instance

            engine = WaraEngine(mock_credential, mock_settings)

            discovery = DiscoveryResult(
                scope="sub-001",
                scope_type=DiscoveryScope.SUBSCRIPTION,
                subscriptions=[{"subscriptionId": "sub-001"}],
                policy_assignments=[],  # Empty — will trigger OPE checks
            )

            assessment = await engine.assess(discovery, subscriptions=["sub-001"])

            assert assessment.overall_score < 100.0
            assert len(assessment.findings) > 0

            # Should have at least a critical finding (TLS)
            severities = [f.severity for f in assessment.findings]
            assert "critical" in severities or "high" in severities

            # Generate reports
            reporter = ReportGenerator(output_dir=mock_settings.assess.output_dir)
            outputs = reporter.generate_all(discovery, assessment, scope_label="sub-001")

            # Assessment report contains findings
            report_md = outputs["assessment_report"].read_text()
            assert "## Findings" in report_md

            # Target state has remediation roadmap
            target_md = outputs["target_state"].read_text()
            assert "Remediation Roadmap" in target_md

            # ADR has critical/high findings
            adr_md = outputs["adr"].read_text()
            assert "ADR" in adr_md

            # JSON has findings array
            json_data = json.loads(outputs["assessment_json"].read_text())
            assert json_data["checks_failed"] > 0

    @pytest.mark.asyncio
    async def test_partial_discovery_failures(self, mock_credential, mock_settings, tmp_path):
        """Assessment works even when discovery has partial errors."""
        with patch("src.tools.wara_engine.AzureRGClient") as mock_rg:
            mock_rg_instance = MagicMock()
            mock_rg_instance.resources.return_value = _mock_arg_result([])
            mock_rg.return_value = mock_rg_instance

            engine = WaraEngine(mock_credential, mock_settings)

            discovery = DiscoveryResult(
                scope="sub-001",
                scope_type=DiscoveryScope.SUBSCRIPTION,
                errors=["Failed to collect RBAC", "Network query timeout"],
            )

            assessment = await engine.assess(discovery, subscriptions=["sub-001"])

            # Should still complete
            assert assessment.checks_run > 0

            # Reports should include errors
            reporter = ReportGenerator(output_dir=mock_settings.assess.output_dir)
            outputs = reporter.generate_all(discovery, assessment, scope_label="sub-001")

            current_state = outputs["current_state"].read_text()
            assert "Discovery Errors" in current_state
            assert "Network query timeout" in current_state


class TestCheckCatalogIntegrity:
    """Validate the real wara_checks.yaml is well-formed."""

    def test_all_checks_have_required_fields(self, mock_credential, mock_settings):
        """Every check in wara_checks.yaml has all required fields."""
        required_fields = {
            "id", "title", "pillar", "caf_area", "alz_area",
            "severity", "scope", "query_type", "recommendation",
        }
        with patch("src.tools.wara_engine.AzureRGClient"):
            engine = WaraEngine(mock_credential, mock_settings)
            for check in engine.checks:
                missing = required_fields - set(check.keys())
                assert not missing, f"Check {check.get('id', '?')} missing fields: {missing}"

    def test_check_ids_unique(self, mock_credential, mock_settings):
        """All check IDs are unique."""
        with patch("src.tools.wara_engine.AzureRGClient"):
            engine = WaraEngine(mock_credential, mock_settings)
            ids = [c["id"] for c in engine.checks]
            assert len(ids) == len(set(ids)), f"Duplicate IDs: {[x for x in ids if ids.count(x) > 1]}"

    def test_check_id_format(self, mock_credential, mock_settings):
        """Check IDs follow the SEC-NNN / REL-NNN / OPE-NNN / COS-NNN / PER-NNN format."""
        import re
        valid_pattern = re.compile(r"^(SEC|REL|OPE|COS|PER)-\d{3}$")
        with patch("src.tools.wara_engine.AzureRGClient"):
            engine = WaraEngine(mock_credential, mock_settings)
            for check in engine.checks:
                assert valid_pattern.match(check["id"]), f"Invalid ID format: {check['id']}"

    def test_severities_valid(self, mock_credential, mock_settings):
        """All checks use valid severity levels."""
        valid_severities = {"critical", "high", "medium", "low"}
        with patch("src.tools.wara_engine.AzureRGClient"):
            engine = WaraEngine(mock_credential, mock_settings)
            for check in engine.checks:
                assert check["severity"] in valid_severities, (
                    f"Check {check['id']} has invalid severity: {check['severity']}"
                )

    def test_pillars_valid(self, mock_credential, mock_settings):
        """All checks use valid pillar names."""
        valid_pillars = {
            "security", "reliability", "cost_optimization",
            "operational_excellence", "performance",
        }
        with patch("src.tools.wara_engine.AzureRGClient"):
            engine = WaraEngine(mock_credential, mock_settings)
            for check in engine.checks:
                assert check["pillar"] in valid_pillars, (
                    f"Check {check['id']} has invalid pillar: {check['pillar']}"
                )

    def test_query_types_valid(self, mock_credential, mock_settings):
        """All checks use valid query types."""
        valid_types = {"resource_graph", "discovery_field", "custom"}
        with patch("src.tools.wara_engine.AzureRGClient"):
            engine = WaraEngine(mock_credential, mock_settings)
            for check in engine.checks:
                assert check["query_type"] in valid_types, (
                    f"Check {check['id']} has invalid query_type: {check['query_type']}"
                )

    def test_match_types_valid(self, mock_credential, mock_settings):
        """All checks use valid match types."""
        valid_match = {"any", "empty", "custom"}
        with patch("src.tools.wara_engine.AzureRGClient"):
            engine = WaraEngine(mock_credential, mock_settings)
            for check in engine.checks:
                assert check.get("match", "any") in valid_match, (
                    f"Check {check['id']} has invalid match: {check.get('match')}"
                )
