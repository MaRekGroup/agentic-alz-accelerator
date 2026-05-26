"""Tests for the PowerPoint reporter."""

import pytest

from src.tools.discovery import DiscoveryResult, DiscoveryScope
from src.tools.pptx_reporter import PptxReporter
from src.tools.wara_engine import AssessmentResult, Finding, PillarScore


@pytest.fixture
def sample_discovery():
    return DiscoveryResult(
        scope="test-sub",
        scope_type=DiscoveryScope.SUBSCRIPTION,
        resources={
            "by_type": [
                {"type": "microsoft.compute/virtualmachines", "count": 5},
                {"type": "microsoft.storage/storageaccounts", "count": 2},
            ],
            "total_count": 7,
        },
    )


@pytest.fixture
def sample_assessment():
    findings = [
        Finding(
            rule_id="SEC-001",
            title="TLS check",
            pillar="security",
            caf_area="security",
            alz_area="security",
            severity="critical",
            confidence="high",
            recommendation="Fix TLS",
            remediation_steps=["Step 1"],
        ),
        Finding(
            rule_id="REL-001",
            title="Backup check",
            pillar="reliability",
            caf_area="management",
            alz_area="management",
            severity="high",
            confidence="high",
            recommendation="Enable backup",
            remediation_steps=["Enable backup"],
        ),
    ]
    result = AssessmentResult(scope="test-sub")
    result.findings = findings
    result.checks_run = 10
    result.checks_passed = 8
    result.overall_score = 85.0
    result.pillar_scores = {
        "security": PillarScore(pillar="security", score=80.0, findings_count=1, critical=1),
        "reliability": PillarScore(pillar="reliability", score=90.0, findings_count=1, high=1),
        "cost_optimization": PillarScore(pillar="cost_optimization", score=100.0),
        "operational_excellence": PillarScore(pillar="operational_excellence", score=100.0),
        "performance": PillarScore(pillar="performance", score=100.0),
    }
    return result


@pytest.fixture
def reporter(tmp_path):
    return PptxReporter(output_dir=tmp_path)


def test_generate_creates_pptx_file(reporter, sample_discovery, sample_assessment):
    output_path = reporter.generate(sample_discovery, sample_assessment, scope_label="test-sub")

    assert output_path.exists()
    assert output_path.suffix == ".pptx"
    assert output_path.name == "wara-executive-summary.pptx"


def test_slide_count(reporter, sample_discovery, sample_assessment):
    """Deck has: title + exec summary + 5 pillars + remediation + inventory = 9."""
    from pptx import Presentation

    output_path = reporter.generate(sample_discovery, sample_assessment, scope_label="test-sub")
    prs = Presentation(str(output_path))
    assert len(prs.slides) == 9


def test_title_slide_content(reporter, sample_discovery, sample_assessment):
    from pptx import Presentation

    output_path = reporter.generate(sample_discovery, sample_assessment, scope_label="test-sub")
    prs = Presentation(str(output_path))
    title_slide = prs.slides[0]

    texts = [shape.text_frame.text for shape in title_slide.shapes if shape.has_text_frame]
    combined = "\n".join(texts)
    assert "Well-Architected Reliability Assessment" in combined
    assert "test-sub" in combined


def test_executive_summary_shows_score(reporter, sample_discovery, sample_assessment):
    from pptx import Presentation

    output_path = reporter.generate(sample_discovery, sample_assessment, scope_label="test-sub")
    prs = Presentation(str(output_path))
    summary_slide = prs.slides[1]

    texts = [shape.text_frame.text for shape in summary_slide.shapes if shape.has_text_frame]
    combined = "\n".join(texts)
    assert "85/100" in combined


def test_remediation_slide_has_findings(reporter, sample_discovery, sample_assessment):
    from pptx import Presentation

    output_path = reporter.generate(sample_discovery, sample_assessment, scope_label="test-sub")
    prs = Presentation(str(output_path))
    remediation_slide = prs.slides[7]

    has_table = any(shape.has_table for shape in remediation_slide.shapes)
    assert has_table


def test_inventory_slide_has_resources(reporter, sample_discovery, sample_assessment):
    from pptx import Presentation

    output_path = reporter.generate(sample_discovery, sample_assessment, scope_label="test-sub")
    prs = Presentation(str(output_path))
    inventory_slide = prs.slides[8]

    has_table = any(shape.has_table for shape in inventory_slide.shapes)
    assert has_table


def test_empty_assessment(reporter, sample_discovery):
    """Deck generates cleanly with zero findings."""
    from pptx import Presentation

    empty_assessment = AssessmentResult(scope="test-sub")
    empty_assessment.pillar_scores = {
        "security": PillarScore(pillar="security"),
        "reliability": PillarScore(pillar="reliability"),
        "cost_optimization": PillarScore(pillar="cost_optimization"),
        "operational_excellence": PillarScore(pillar="operational_excellence"),
        "performance": PillarScore(pillar="performance"),
    }
    output_path = reporter.generate(sample_discovery, empty_assessment, scope_label="empty")
    prs = Presentation(str(output_path))
    assert len(prs.slides) == 9


def test_generate_all_includes_pptx(tmp_path, sample_discovery, sample_assessment):
    """ReportGenerator.generate_all() includes pptx_executive_summary."""
    from src.tools.report_generator import ReportGenerator

    gen = ReportGenerator(output_dir=tmp_path)
    outputs = gen.generate_all(sample_discovery, sample_assessment, scope_label="test")
    assert "pptx_executive_summary" in outputs
    assert outputs["pptx_executive_summary"].suffix == ".pptx"
