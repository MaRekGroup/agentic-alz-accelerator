"""
PowerPoint Reporter — generates executive summary slide decks from WARA assessment results.

Produces a branded PowerPoint presentation compatible with Microsoft WARA output:
- Title slide with scope and date
- Executive summary with overall score and pillar breakdown
- Per-pillar slides with score gauge, finding counts, and top findings
- Remediation roadmap slide with priority-ordered actions
- Appendix slide with resource inventory summary
"""

import logging
from datetime import datetime, timezone
from pathlib import Path

try:
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.util import Emu, Inches, Pt
except ImportError as exc:
    Presentation = None
    _PPTX_IMPORT_ERROR: ImportError | None = exc
else:
    _PPTX_IMPORT_ERROR = None

from src.tools.discovery import DiscoveryResult
from src.tools.wara_engine import AssessmentResult, Finding

logger = logging.getLogger(__name__)

_PILLAR_NAMES = {
    "security": "Security",
    "reliability": "Reliability",
    "cost_optimization": "Cost Optimization",
    "operational_excellence": "Operational Excellence",
    "performance": "Performance Efficiency",
}

_PILLAR_ORDER = [
    "security",
    "reliability",
    "cost_optimization",
    "operational_excellence",
    "performance",
]

_SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}

_SEVERITY_COLORS = {
    "critical": RGBColor(0xCC, 0x00, 0x00) if RGBColor else None,
    "high": RGBColor(0xE6, 0x73, 0x00) if RGBColor else None,
    "medium": RGBColor(0xCC, 0xA3, 0x00) if RGBColor else None,
    "low": RGBColor(0x33, 0x66, 0xCC) if RGBColor else None,
}

_BRAND_BLUE = RGBColor(0x00, 0x78, 0xD4) if RGBColor else None
_BRAND_DARK = RGBColor(0x24, 0x29, 0x2E) if RGBColor else None
_WHITE = RGBColor(0xFF, 0xFF, 0xFF) if RGBColor else None
_LIGHT_GRAY = RGBColor(0xF2, 0xF2, 0xF2) if RGBColor else None


def _score_color(score: float) -> "RGBColor":
    if score >= 80:
        return RGBColor(0x10, 0x7C, 0x10)
    if score >= 60:
        return RGBColor(0xCA, 0x83, 0x00)
    return RGBColor(0xCC, 0x00, 0x00)


class PptxReporter:
    """Generates PowerPoint executive summary decks for WARA assessments."""

    def __init__(self, output_dir: Path):
        if _PPTX_IMPORT_ERROR is not None:
            raise ImportError("python-pptx is required for PowerPoint report generation") from _PPTX_IMPORT_ERROR
        self.output_dir = Path(output_dir)

    def generate(
        self,
        discovery: DiscoveryResult,
        assessment: AssessmentResult,
        *,
        scope_label: str | None = None,
    ) -> Path:
        """Generate the PowerPoint executive summary deck.

        Args:
            discovery: Discovery inventory for resource context.
            assessment: Assessment results with scores and findings.
            scope_label: Optional label for the title slide.

        Returns:
            Path to the generated .pptx file.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        label = scope_label or discovery.scope

        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)

        self._add_title_slide(prs, label)
        self._add_executive_summary(prs, discovery, assessment)
        for pillar_key in _PILLAR_ORDER:
            self._add_pillar_slide(prs, assessment, pillar_key)
        self._add_remediation_slide(prs, assessment)
        self._add_inventory_slide(prs, discovery)

        output_path = self.output_dir / "wara-executive-summary.pptx"
        prs.save(str(output_path))
        logger.info("Generated PowerPoint executive summary: %s", output_path)
        return output_path

    def _add_title_slide(self, prs: "Presentation", label: str) -> None:
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank layout
        self._fill_background(slide, _BRAND_BLUE)

        title_box = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(11), Inches(1.5))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = "Well-Architected Reliability Assessment"
        p.font.size = Pt(36)
        p.font.bold = True
        p.font.color.rgb = _WHITE
        p.alignment = PP_ALIGN.LEFT

        subtitle_box = slide.shapes.add_textbox(Inches(1), Inches(3.8), Inches(11), Inches(1))
        tf2 = subtitle_box.text_frame
        tf2.word_wrap = True
        p2 = tf2.paragraphs[0]
        p2.text = f"Scope: {label}"
        p2.font.size = Pt(20)
        p2.font.color.rgb = _WHITE
        p2.alignment = PP_ALIGN.LEFT

        p3 = tf2.add_paragraph()
        p3.text = f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
        p3.font.size = Pt(16)
        p3.font.color.rgb = _WHITE
        p3.alignment = PP_ALIGN.LEFT

    def _add_executive_summary(
        self,
        prs: "Presentation",
        discovery: DiscoveryResult,
        assessment: AssessmentResult,
    ) -> None:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._add_slide_title(slide, "Executive Summary")

        score_box = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(3), Inches(2))
        tf = score_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = "Overall Score"
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = _BRAND_DARK

        p2 = tf.add_paragraph()
        p2.text = f"{assessment.overall_score:.0f}/100"
        p2.font.size = Pt(48)
        p2.font.bold = True
        p2.font.color.rgb = _score_color(assessment.overall_score)

        stats_box = slide.shapes.add_textbox(Inches(1), Inches(3.8), Inches(3), Inches(2.5))
        stf = stats_box.text_frame
        stf.word_wrap = True
        resource_total = self._resource_total(discovery)
        stats = [
            f"Resources: {resource_total}",
            f"Checks Run: {assessment.checks_run}",
            f"Checks Passed: {assessment.checks_passed}",
            f"Findings: {len(assessment.findings)}",
        ]
        for i, stat in enumerate(stats):
            para = stf.paragraphs[0] if i == 0 else stf.add_paragraph()
            para.text = stat
            para.font.size = Pt(14)
            para.font.color.rgb = _BRAND_DARK
            para.space_after = Pt(4)

        self._add_pillar_score_table(slide, assessment, left=Inches(5), top=Inches(1.5))

    def _add_pillar_slide(self, prs: "Presentation", assessment: AssessmentResult, pillar_key: str) -> None:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        pillar_name = _PILLAR_NAMES.get(pillar_key, pillar_key)
        self._add_slide_title(slide, f"Pillar: {pillar_name}")

        ps = assessment.pillar_scores.get(pillar_key)
        score = ps.score if ps else 100.0
        findings_count = ps.findings_count if ps else 0

        score_box = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(3), Inches(2))
        tf = score_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"{score:.0f}/100"
        p.font.size = Pt(48)
        p.font.bold = True
        p.font.color.rgb = _score_color(score)

        counts_box = slide.shapes.add_textbox(Inches(1), Inches(3.5), Inches(3), Inches(2))
        ctf = counts_box.text_frame
        ctf.word_wrap = True
        if ps:
            counts = [
                f"Critical: {ps.critical}",
                f"High: {ps.high}",
                f"Medium: {ps.medium}",
                f"Low: {ps.low}",
                f"Total: {findings_count}",
            ]
        else:
            counts = ["No findings"]
        for i, c in enumerate(counts):
            para = ctf.paragraphs[0] if i == 0 else ctf.add_paragraph()
            para.text = c
            para.font.size = Pt(14)
            para.font.color.rgb = _BRAND_DARK

        pillar_findings = [f for f in assessment.findings if f.pillar == pillar_key]
        top_findings = sorted(
            pillar_findings,
            key=lambda f: _SEVERITY_ORDER.get(f.severity, 99),
        )[:5]

        if top_findings:
            self._add_findings_table(slide, top_findings, left=Inches(5), top=Inches(1.5))

    def _add_remediation_slide(self, prs: "Presentation", assessment: AssessmentResult) -> None:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._add_slide_title(slide, "Remediation Roadmap")

        sorted_findings = sorted(
            assessment.findings,
            key=lambda f: (_SEVERITY_ORDER.get(f.severity, 99), f.rule_id),
        )
        top = sorted_findings[:10]

        if not top:
            info_box = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(10), Inches(1))
            info_box.text_frame.paragraphs[0].text = "No findings — all checks passed."
            info_box.text_frame.paragraphs[0].font.size = Pt(18)
            return

        rows = len(top) + 1
        cols = 5
        table_shape = slide.shapes.add_table(rows, cols, Inches(0.5), Inches(1.5), Inches(12), Inches(5))
        table = table_shape.table

        headers = ["Priority", "Rule ID", "Severity", "Title", "Recommendation"]
        for ci, h in enumerate(headers):
            cell = table.cell(0, ci)
            cell.text = h
            self._style_header_cell(cell)

        for ri, finding in enumerate(top, start=1):
            table.cell(ri, 0).text = str(ri)
            table.cell(ri, 1).text = finding.rule_id
            table.cell(ri, 2).text = finding.severity.capitalize()
            table.cell(ri, 3).text = finding.title
            table.cell(ri, 4).text = finding.recommendation
            sev_color = _SEVERITY_COLORS.get(finding.severity)
            if sev_color:
                table.cell(ri, 2).fill.solid()
                table.cell(ri, 2).fill.fore_color.rgb = sev_color
                for paragraph in table.cell(ri, 2).text_frame.paragraphs:
                    for run in paragraph.runs:
                        run.font.color.rgb = _WHITE
            for ci in range(cols):
                for paragraph in table.cell(ri, ci).text_frame.paragraphs:
                    paragraph.font.size = Pt(10)

        table.columns[0].width = Inches(0.8)
        table.columns[1].width = Inches(1.2)
        table.columns[2].width = Inches(1.2)
        table.columns[3].width = Inches(4)
        table.columns[4].width = Inches(4.8)

    def _add_inventory_slide(self, prs: "Presentation", discovery: DiscoveryResult) -> None:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._add_slide_title(slide, "Resource Inventory")

        resource_rows = self._resource_rows(discovery)
        top_resources = resource_rows[:15]

        if not top_resources:
            info_box = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(10), Inches(1))
            info_box.text_frame.paragraphs[0].text = "No resources discovered."
            info_box.text_frame.paragraphs[0].font.size = Pt(18)
            return

        rows = len(top_resources) + 1
        table_shape = slide.shapes.add_table(rows, 2, Inches(1), Inches(1.5), Inches(8), Inches(0.4 * rows))
        table = table_shape.table

        for ci, h in enumerate(["Resource Type", "Count"]):
            cell = table.cell(0, ci)
            cell.text = h
            self._style_header_cell(cell)

        for ri, (rtype, count) in enumerate(top_resources, start=1):
            table.cell(ri, 0).text = rtype
            table.cell(ri, 1).text = str(count)
            for ci in range(2):
                for paragraph in table.cell(ri, ci).text_frame.paragraphs:
                    paragraph.font.size = Pt(11)

        table.columns[0].width = Inches(6)
        table.columns[1].width = Inches(2)

    def _add_pillar_score_table(
        self,
        slide,
        assessment: AssessmentResult,
        left: "Emu",
        top: "Emu",
    ) -> None:
        rows = len(_PILLAR_ORDER) + 1
        cols = 4
        table_shape = slide.shapes.add_table(rows, cols, left, top, Inches(7.5), Inches(0.4 * rows))
        table = table_shape.table

        for ci, h in enumerate(["Pillar", "Score", "Findings", "Critical"]):
            cell = table.cell(0, ci)
            cell.text = h
            self._style_header_cell(cell)

        for ri, pillar_key in enumerate(_PILLAR_ORDER, start=1):
            ps = assessment.pillar_scores.get(pillar_key)
            score = ps.score if ps else 100.0
            findings = ps.findings_count if ps else 0
            critical = ps.critical if ps else 0

            table.cell(ri, 0).text = _PILLAR_NAMES[pillar_key]
            table.cell(ri, 1).text = f"{score:.0f}"
            table.cell(ri, 2).text = str(findings)
            table.cell(ri, 3).text = str(critical)

            score_cell = table.cell(ri, 1)
            score_cell.fill.solid()
            score_cell.fill.fore_color.rgb = _score_color(score)
            for paragraph in score_cell.text_frame.paragraphs:
                for run in paragraph.runs:
                    run.font.color.rgb = _WHITE
                    run.font.bold = True

            for ci in range(cols):
                for paragraph in table.cell(ri, ci).text_frame.paragraphs:
                    paragraph.font.size = Pt(12)

        table.columns[0].width = Inches(3)
        table.columns[1].width = Inches(1.5)
        table.columns[2].width = Inches(1.5)
        table.columns[3].width = Inches(1.5)

    def _add_findings_table(
        self,
        slide,
        findings: list[Finding],
        left: "Emu",
        top: "Emu",
    ) -> None:
        rows = len(findings) + 1
        cols = 3
        table_shape = slide.shapes.add_table(rows, cols, left, top, Inches(7.5), Inches(0.4 * rows))
        table = table_shape.table

        for ci, h in enumerate(["Severity", "Rule ID", "Title"]):
            cell = table.cell(0, ci)
            cell.text = h
            self._style_header_cell(cell)

        for ri, finding in enumerate(findings, start=1):
            table.cell(ri, 0).text = finding.severity.capitalize()
            table.cell(ri, 1).text = finding.rule_id
            table.cell(ri, 2).text = finding.title

            sev_color = _SEVERITY_COLORS.get(finding.severity)
            if sev_color:
                table.cell(ri, 0).fill.solid()
                table.cell(ri, 0).fill.fore_color.rgb = sev_color
                for paragraph in table.cell(ri, 0).text_frame.paragraphs:
                    for run in paragraph.runs:
                        run.font.color.rgb = _WHITE

            for ci in range(cols):
                for paragraph in table.cell(ri, ci).text_frame.paragraphs:
                    paragraph.font.size = Pt(11)

        table.columns[0].width = Inches(1.2)
        table.columns[1].width = Inches(1.5)
        table.columns[2].width = Inches(4.8)

    def _add_slide_title(self, slide, text: str) -> None:
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12), Inches(0.8))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = text
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = _BRAND_DARK
        p.alignment = PP_ALIGN.LEFT

    @staticmethod
    def _fill_background(slide, color: "RGBColor") -> None:
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = color

    @staticmethod
    def _style_header_cell(cell) -> None:
        cell.fill.solid()
        cell.fill.fore_color.rgb = _BRAND_BLUE
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.size = Pt(12)
            paragraph.font.bold = True
            paragraph.font.color.rgb = _WHITE
            paragraph.alignment = PP_ALIGN.LEFT

    @staticmethod
    def _resource_rows(discovery: DiscoveryResult) -> list[tuple[str, int]]:
        by_type = discovery.resources.get("by_type", {}) if isinstance(discovery.resources, dict) else {}
        if isinstance(by_type, dict):
            rows = list(by_type.items())
        else:
            rows = [
                (
                    item.get("type", "unknown"),
                    int(item.get("resource_count", item.get("count", 0))),
                )
                for item in by_type
            ]
        return sorted(rows, key=lambda r: r[1], reverse=True)

    @staticmethod
    def _resource_total(discovery: DiscoveryResult) -> int:
        if not isinstance(discovery.resources, dict):
            return 0
        return int(discovery.resources.get("total_count", discovery.resources.get("total", 0)))
