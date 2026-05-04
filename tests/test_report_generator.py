"""Tests for the report generator."""

import json

import pytest

from src.tools.discovery import DiscoveryResult, DiscoveryScope
from src.tools.report_generator import (
    ReportGenerator,
    _extract_mg_name,
    _mermaid_id,
    _safe_filename,
)
from src.tools.wara_engine import AssessmentResult, Finding, PillarScore


@pytest.fixture
def discovery():
    return DiscoveryResult(
        scope="mrg",
        scope_type=DiscoveryScope.MANAGEMENT_GROUP,
        management_groups=[
            {"name": "mrg", "displayName": "Root", "parent": ""},
            {"name": "mrg-platform", "displayName": "Platform", "parent": "mrg"},
            {"name": "mrg-landingzones", "displayName": "Landing Zones", "parent": "mrg"},
        ],
        subscriptions=[
            {"name": "mgmt-sub", "subscriptionId": "sub-001", "state": "Enabled"},
            {"name": "conn-sub", "subscriptionId": "sub-002", "state": "Enabled"},
        ],
        resources={"by_type": {"microsoft.storage/storageaccounts": 5, "microsoft.compute/virtualmachines": 3}, "total": 8},
        policy_assignments=[
            {"displayName": "Azure Security Benchmark", "policyType": "BuiltIn"},
            {"displayName": "Allowed Locations", "name": "allowed-locations"},
        ],
        rbac_assignments=[{"principalId": "p1"}, {"principalId": "p2"}],
        network_topology={
            "vnets": [
                {
                    "name": "hub-vnet",
                    "addressPrefixes": ["10.0.0.0/16"],
                    "peerings": [{"remoteVNet": "spoke-vnet"}],
                },
                {
                    "name": "spoke-vnet",
                    "addressPrefixes": ["10.1.0.0/16"],
                    "peerings": [{"remoteVNet": "hub-vnet"}],
                },
            ]
        },
        logging_config={
            "log_analytics_workspaces": [{"name": "law-mgmt"}],
            "diagnostic_settings": [{"name": "ds-1"}, {"name": "ds-2"}],
        },
        security_posture={"secure_score": 72, "defender_plans": ["AppServices", "Storage"]},
    )


@pytest.fixture
def assessment():
    return AssessmentResult(
        scope="mrg",
        assessed_at="2026-04-23T10:00:00Z",
        findings=[
            Finding(
                rule_id="SEC-001",
                title="Storage without TLS 1.2",
                pillar="security",
                caf_area="security",
                alz_area="security",
                severity="critical",
                confidence="high",
                recommendation="Set minimum TLS to 1.2",
                evidence=[{"id": "sa-1", "name": "badsa"}],
                remediation_steps=["Update TLS setting", "Verify connectivity"],
                references=["https://example.com/tls"],
            ),
            Finding(
                rule_id="OPE-001",
                title="No diagnostic settings",
                pillar="operational_excellence",
                caf_area="management",
                alz_area="logging",
                severity="high",
                confidence="high",
                recommendation="Enable diagnostic settings",
                evidence=[],
                remediation_steps=["Deploy diagnostic settings policy"],
            ),
            Finding(
                rule_id="COS-001",
                title="Unattached disks",
                pillar="cost_optimization",
                caf_area="management",
                alz_area="logging",
                severity="medium",
                confidence="medium",
                recommendation="Delete unattached disks",
                evidence=[{"id": "disk-1"}],
            ),
        ],
        pillar_scores={
            "security": PillarScore(pillar="security", score=80.0, critical=1),
            "reliability": PillarScore(pillar="reliability", score=100.0),
            "cost_optimization": PillarScore(pillar="cost_optimization", score=95.0, medium=1),
            "operational_excellence": PillarScore(pillar="operational_excellence", score=90.0, high=1),
            "performance": PillarScore(pillar="performance", score=100.0),
        },
        overall_score=93.0,
        checks_run=22,
        checks_passed=19,
    )


@pytest.fixture
def reporter(tmp_path):
    return ReportGenerator(output_dir=tmp_path)


class TestHelpers:
    def test_safe_filename(self):
        assert _safe_filename("mrg-platform") == "mrg-platform"
        assert _safe_filename("my scope/sub") == "my-scope-sub"
        assert _safe_filename("sub-001") == "sub-001"

    def test_mermaid_id(self):
        assert _mermaid_id("hub-vnet") == "hub_vnet"
        assert _mermaid_id("mrg-platform") == "mrg_platform"

    def test_extract_mg_name(self):
        assert _extract_mg_name("mrg") == "mrg"
        assert _extract_mg_name(
            "/providers/Microsoft.Management/managementGroups/mrg-platform"
        ) == "mrg-platform"


class TestCurrentState:
    def test_contains_mg_table(self, reporter, discovery):
        md = reporter.render_current_state(discovery, "test")
        assert "## Management Group Hierarchy" in md
        assert "mrg-platform" in md
        assert "Platform" in md

    def test_contains_subscriptions(self, reporter, discovery):
        md = reporter.render_current_state(discovery, "test")
        assert "## Subscriptions" in md
        assert "sub-001" in md

    def test_contains_resources(self, reporter, discovery):
        md = reporter.render_current_state(discovery, "test")
        assert "## Resource Inventory" in md
        assert "microsoft.storage/storageaccounts" in md
        assert "8" in md  # total

    def test_contains_network(self, reporter, discovery):
        md = reporter.render_current_state(discovery, "test")
        assert "## Network Topology" in md
        assert "hub-vnet" in md
        assert "10.0.0.0/16" in md

    def test_contains_policy(self, reporter, discovery):
        md = reporter.render_current_state(discovery, "test")
        assert "## Policy Assignments" in md
        assert "Azure Security Benchmark" in md

    def test_contains_rbac(self, reporter, discovery):
        md = reporter.render_current_state(discovery, "test")
        assert "## RBAC Assignments" in md
        assert "2" in md

    def test_contains_logging(self, reporter, discovery):
        md = reporter.render_current_state(discovery, "test")
        assert "## Logging & Monitoring" in md
        assert "1" in md  # 1 LAW

    def test_contains_security(self, reporter, discovery):
        md = reporter.render_current_state(discovery, "test")
        assert "## Security Posture" in md
        assert "72" in md

    def test_empty_discovery(self, reporter):
        empty = DiscoveryResult(scope="empty", scope_type=DiscoveryScope.SUBSCRIPTION)
        md = reporter.render_current_state(empty, "empty")
        assert "# Current-State Architecture" in md
        assert "Management Group" not in md

    def test_discovery_errors_shown(self, reporter):
        d = DiscoveryResult(
            scope="err", scope_type=DiscoveryScope.SUBSCRIPTION, errors=["API timeout"]
        )
        md = reporter.render_current_state(d, "err")
        assert "## Discovery Errors" in md
        assert "API timeout" in md


class TestTargetState:
    def test_contains_roadmap(self, reporter, discovery, assessment):
        md = reporter.render_target_state(discovery, assessment, "test")
        assert "## Remediation Roadmap" in md
        assert "SEC-001" in md
        assert "OPE-001" in md

    def test_contains_score(self, reporter, discovery, assessment):
        md = reporter.render_target_state(discovery, assessment, "test")
        assert "93.0/100" in md

    def test_contains_steps(self, reporter, discovery, assessment):
        md = reporter.render_target_state(discovery, assessment, "test")
        assert "Update TLS setting" in md

    def test_no_findings(self, reporter, discovery):
        clean = AssessmentResult(scope="clean", checks_run=10, checks_passed=10)
        md = reporter.render_target_state(discovery, clean, "clean")
        assert "Remediation Roadmap" not in md
        assert "## Target State" in md


class TestAssessmentReport:
    def test_executive_summary(self, reporter, assessment):
        md = reporter.render_assessment_report(assessment, "test")
        assert "## Executive Summary" in md
        assert "93.0/100" in md
        assert "22" in md  # checks run

    def test_pillar_scores_table(self, reporter, assessment):
        md = reporter.render_assessment_report(assessment, "test")
        assert "## Pillar Scores" in md
        assert "Security" in md
        assert "80.0" in md

    def test_findings_detail(self, reporter, assessment):
        md = reporter.render_assessment_report(assessment, "test")
        assert "## Findings" in md
        assert "SEC-001" in md
        assert "Set minimum TLS" in md

    def test_no_findings_message(self, reporter):
        clean = AssessmentResult(scope="clean", checks_run=5, checks_passed=5)
        md = reporter.render_assessment_report(clean, "clean")
        assert "all checks passed" in md


class TestArchitectureDiagram:
    def test_mermaid_format(self, reporter, discovery):
        mmd = reporter.render_architecture_diagram(discovery, "test")
        assert "graph TD" in mmd
        assert "subgraph MG" in mmd

    def test_mg_nodes(self, reporter, discovery):
        mmd = reporter.render_architecture_diagram(discovery, "test")
        assert "mrg_platform" in mmd
        assert "Platform" in mmd

    def test_subscription_nodes(self, reporter, discovery):
        mmd = reporter.render_architecture_diagram(discovery, "test")
        assert "subgraph SUBS" in mmd
        assert "mgmt_sub" in mmd

    def test_vnet_nodes(self, reporter, discovery):
        mmd = reporter.render_architecture_diagram(discovery, "test")
        assert "subgraph NET" in mmd
        assert "hub_vnet" in mmd
        assert "10.0.0.0/16" in mmd

    def test_peering_edges(self, reporter, discovery):
        mmd = reporter.render_architecture_diagram(discovery, "test")
        assert "<-->" in mmd

    def test_empty_diagram(self, reporter):
        empty = DiscoveryResult(scope="e", scope_type=DiscoveryScope.SUBSCRIPTION)
        mmd = reporter.render_architecture_diagram(empty, "e")
        assert "graph TD" in mmd
        assert "subgraph" not in mmd


class TestADR:
    def test_contains_findings(self, reporter, assessment):
        adr = reporter.render_adr(assessment, "test")
        assert "# ADR" in adr
        assert "SEC-001" in adr
        assert "OPE-001" in adr
        # Medium finding not in critical/high section
        assert "COS-001" not in adr

    def test_decision_placeholder(self, reporter, assessment):
        adr = reporter.render_adr(assessment, "test")
        assert "## Decision" in adr
        assert "Accept / Modify / Defer" in adr

    def test_no_critical_high(self, reporter):
        clean = AssessmentResult(
            scope="clean",
            checks_run=5,
            checks_passed=5,
            findings=[
                Finding(
                    rule_id="COS-010", title="Minor cost", pillar="cost_optimization",
                    caf_area="management", alz_area="logging", severity="low",
                    confidence="low", recommendation="Consider cleanup",
                ),
            ],
        )
        adr = reporter.render_adr(clean, "clean")
        assert "Critical/High Findings" not in adr


class TestGenerateAll:
    def test_creates_all_files(self, reporter, discovery, assessment):
        outputs = reporter.generate_all(discovery, assessment, scope_label="test-scope")
        assert len(outputs) == 11  # 6 base + 5 pillar reports
        for key, path in outputs.items():
            assert path.exists(), f"{key} file not created: {path}"

    def test_json_valid(self, reporter, discovery, assessment):
        outputs = reporter.generate_all(discovery, assessment, scope_label="test-scope")
        json_path = outputs["assessment_json"]
        data = json.loads(json_path.read_text())
        assert data["overall_score"] == 93.0
        assert data["checks_run"] == 22

    def test_output_directory_structure(self, reporter, discovery, assessment):
        outputs = reporter.generate_all(discovery, assessment, scope_label="my-scope")
        for path in outputs.values():
            assert "my-scope" in str(path)

    def test_pillar_reports_in_subdirectory(self, reporter, discovery, assessment):
        outputs = reporter.generate_all(discovery, assessment, scope_label="test-scope")
        pillar_keys = [k for k in outputs if k.startswith("pillar_")]
        assert len(pillar_keys) == 5
        for key in pillar_keys:
            assert "pillar-reports" in str(outputs[key])


class TestPillarReport:
    def test_security_report_has_findings(self, reporter, assessment):
        md = reporter.render_pillar_report(assessment, "security", "test")
        assert "# Security — Detailed Assessment Report" in md
        assert "SEC-001" in md
        assert "Storage without TLS 1.2" in md

    def test_pillar_score_shown(self, reporter, assessment):
        md = reporter.render_pillar_report(assessment, "security", "test")
        assert "80.0/100" in md

    def test_score_interpretation_excellent(self, reporter, assessment):
        md = reporter.render_pillar_report(assessment, "reliability", "test")
        assert "Excellent" in md

    def test_score_interpretation_good(self, reporter, assessment):
        md = reporter.render_pillar_report(assessment, "security", "test")
        assert "Good" in md

    def test_no_findings_pillar(self, reporter, assessment):
        md = reporter.render_pillar_report(assessment, "performance", "test")
        assert "No findings — all checks passed" in md

    def test_remediation_steps_shown(self, reporter, assessment):
        md = reporter.render_pillar_report(assessment, "security", "test")
        assert "Update TLS setting" in md
        assert "Verify connectivity" in md

    def test_references_shown(self, reporter, assessment):
        md = reporter.render_pillar_report(assessment, "security", "test")
        assert "https://example.com/tls" in md

    def test_affected_resources_table(self, reporter, assessment):
        md = reporter.render_pillar_report(assessment, "security", "test")
        assert "Affected Resources" in md
        assert "badsa" in md

    def test_findings_summary_table(self, reporter, assessment):
        md = reporter.render_pillar_report(assessment, "cost_optimization", "test")
        assert "Findings Summary" in md
        assert "COS-001" in md

    def test_remediation_priority_matrix(self, reporter, assessment):
        md = reporter.render_pillar_report(assessment, "security", "test")
        assert "Remediation Priority Matrix" in md

    def test_caf_design_areas_section(self, reporter, assessment):
        md = reporter.render_pillar_report(assessment, "security", "test")
        assert "Related CAF Design Areas" in md
        assert "Security" in md

    def test_operational_excellence_report(self, reporter, assessment):
        md = reporter.render_pillar_report(assessment, "operational_excellence", "test")
        assert "OPE-001" in md
        assert "No diagnostic settings" in md
        assert "Enable diagnostic settings" in md

    def test_pillar_report_filenames(self, reporter, discovery, assessment):
        outputs = reporter.generate_all(discovery, assessment, scope_label="test")
        assert outputs["pillar_security"].name == "wara-security.md"
        assert outputs["pillar_cost_optimization"].name == "wara-cost-optimization.md"
        assert outputs["pillar_reliability"].name == "wara-reliability.md"
        assert outputs["pillar_operational_excellence"].name == "wara-operational-excellence.md"
        assert outputs["pillar_performance"].name == "wara-performance.md"
