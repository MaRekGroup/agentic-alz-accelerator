"""
Excel Reporter — generates Excel action plan workbooks from WARA assessment results.

Produces a multi-sheet Excel workbook compatible with enterprise assessment workflows:
- Executive Summary: pillar scores, finding counts, overall score
- Findings Detail: all findings sortable by pillar/severity
- Resource Inventory: discovered resource types and counts
- Remediation Roadmap: priority-ordered remediation actions
"""

import logging
from datetime import datetime, timezone
from pathlib import Path

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
except ImportError as exc:
    Workbook = None
    Alignment = None
    Font = None
    PatternFill = None
    get_column_letter = None
    _OPENPYXL_IMPORT_ERROR: ImportError | None = exc
else:
    _OPENPYXL_IMPORT_ERROR = None

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

_SEVERITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}

_SEVERITY_FILL_COLORS = {
    "critical": "F4CCCC",
    "high": "FCE5CD",
    "medium": "FFF2CC",
    "low": "D9EAF7",
}

_HEADER_FILL_COLOR = "D9E2F3"
_SCORE_FILL_GOOD = "C6EFCE"
_SCORE_FILL_WARNING = "FFEB9C"
_SCORE_FILL_RISK = "F4CCCC"


class ExcelReporter:
    """Generates Excel action plan workbooks for WARA assessment results."""

    def __init__(self, output_dir: Path):
        """Initialize the reporter.

        Args:
            output_dir: Directory where the workbook will be written.
        """
        if _OPENPYXL_IMPORT_ERROR is not None:
            raise ImportError("openpyxl is required for Excel report generation") from _OPENPYXL_IMPORT_ERROR

        self.output_dir = Path(output_dir)

    def generate(
        self,
        discovery: DiscoveryResult,
        assessment: AssessmentResult,
        *,
        scope_label: str | None = None,
    ) -> Path:
        """Generate the Excel action plan workbook.

        Args:
            discovery: Discovery inventory used to populate resource summary data.
            assessment: Assessment results used to populate scores and findings.
            scope_label: Optional label to show in the workbook title.

        Returns:
            Path to the generated `.xlsx` workbook.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        label = scope_label or discovery.scope

        workbook = Workbook()
        summary_sheet = workbook.active
        summary_sheet.title = "Executive Summary"
        self._populate_executive_summary(summary_sheet, discovery, assessment, label)

        findings_sheet = workbook.create_sheet("Findings Detail")
        self._populate_findings_detail(findings_sheet, assessment)

        inventory_sheet = workbook.create_sheet("Resource Inventory")
        self._populate_resource_inventory(inventory_sheet, discovery)

        roadmap_sheet = workbook.create_sheet("Remediation Roadmap")
        self._populate_remediation_roadmap(roadmap_sheet, assessment)

        output_path = self.output_dir / "wara-action-plan.xlsx"
        workbook.save(output_path)
        logger.info("Generated Excel action plan workbook: %s", output_path)
        return output_path

    def _populate_executive_summary(
        self,
        worksheet,
        discovery: DiscoveryResult,
        assessment: AssessmentResult,
        label: str,
    ) -> None:
        worksheet.merge_cells("A1:G1")
        worksheet["A1"] = f"WARA Assessment — {label}"
        worksheet["A1"].font = Font(bold=True, size=14)
        worksheet["A2"] = f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"

        worksheet["A5"] = "Overall Score"
        worksheet["A5"].font = Font(bold=True)
        worksheet["B5"] = round(assessment.overall_score, 1)
        worksheet["B5"].font = Font(bold=True)
        worksheet["B5"].fill = self._score_fill(assessment.overall_score)
        worksheet["C5"] = "/100"

        pillar_headers = ["Pillar", "Score", "Critical", "High", "Medium", "Low", "Total"]
        worksheet.append([])
        worksheet.append(pillar_headers)
        self._style_header_row(worksheet, 7)

        for pillar_key in _PILLAR_ORDER:
            pillar_score = assessment.pillar_scores.get(pillar_key)
            score = pillar_score.score if pillar_score else 100.0
            critical = pillar_score.critical if pillar_score else 0
            high = pillar_score.high if pillar_score else 0
            medium = pillar_score.medium if pillar_score else 0
            low = pillar_score.low if pillar_score else 0
            total = pillar_score.findings_count if pillar_score else 0
            worksheet.append(
                [
                    _PILLAR_NAMES[pillar_key],
                    round(score, 1),
                    critical,
                    high,
                    medium,
                    low,
                    total,
                ]
            )
            worksheet[f"B{worksheet.max_row}"].fill = self._score_fill(score)

        stats_start_row = 14
        worksheet[f"A{stats_start_row}"] = "Metric"
        worksheet[f"B{stats_start_row}"] = "Value"
        self._style_header_row(worksheet, stats_start_row)

        severity_counts = self._severity_counts(assessment.findings)
        stats = [
            ("Total Resources", self._resource_total(discovery)),
            ("Total Findings", len(assessment.findings)),
            ("Critical Findings", severity_counts["critical"]),
            ("High Findings", severity_counts["high"]),
            ("Medium Findings", severity_counts["medium"]),
            ("Low Findings", severity_counts["low"]),
            ("Checks Run", assessment.checks_run),
            ("Checks Passed", assessment.checks_passed),
        ]
        for index, (metric, value) in enumerate(stats, start=stats_start_row + 1):
            worksheet[f"A{index}"] = metric
            worksheet[f"B{index}"] = value

        worksheet.freeze_panes = "A7"
        self._auto_width(worksheet)

    def _populate_findings_detail(self, worksheet, assessment: AssessmentResult) -> None:
        headers = [
            "Rule ID",
            "Title",
            "Pillar",
            "CAF Area",
            "Severity",
            "Confidence",
            "Recommendation",
            "Evidence Count",
            "References",
        ]
        worksheet.append(headers)
        self._style_header_row(worksheet, 1)

        for finding in self._sorted_findings(assessment.findings):
            worksheet.append(
                [
                    finding.rule_id,
                    finding.title,
                    _PILLAR_NAMES.get(finding.pillar, finding.pillar),
                    finding.caf_area,
                    finding.severity,
                    finding.confidence,
                    finding.recommendation,
                    len(finding.evidence),
                    "\n".join(finding.references),
                ]
            )
            worksheet[f"E{worksheet.max_row}"].fill = self._severity_fill(finding.severity)

        self._apply_wrap(worksheet, ["G", "I"])
        worksheet.auto_filter.ref = worksheet.dimensions
        worksheet.freeze_panes = "A2"
        self._auto_width(worksheet)

    def _populate_resource_inventory(self, worksheet, discovery: DiscoveryResult) -> None:
        worksheet.append(["Resource Type", "Count"])
        self._style_header_row(worksheet, 1)

        for resource_type, count in self._resource_rows(discovery):
            worksheet.append([resource_type, count])

        worksheet.auto_filter.ref = worksheet.dimensions
        worksheet.freeze_panes = "A2"
        self._auto_width(worksheet)

    def _populate_remediation_roadmap(self, worksheet, assessment: AssessmentResult) -> None:
        headers = [
            "Priority",
            "Rule ID",
            "Title",
            "Severity",
            "Recommendation",
            "Remediation Steps",
        ]
        worksheet.append(headers)
        self._style_header_row(worksheet, 1)

        sorted_findings = sorted(
            assessment.findings,
            key=lambda finding: (
                _SEVERITY_ORDER.get(finding.severity, 99),
                _PILLAR_NAMES.get(finding.pillar, finding.pillar),
                finding.rule_id,
            ),
        )
        for priority, finding in enumerate(sorted_findings, start=1):
            worksheet.append(
                [
                    priority,
                    finding.rule_id,
                    finding.title,
                    finding.severity,
                    finding.recommendation,
                    "\n".join(finding.remediation_steps),
                ]
            )
            worksheet[f"D{worksheet.max_row}"].fill = self._severity_fill(finding.severity)

        self._apply_wrap(worksheet, ["E", "F"])
        worksheet.auto_filter.ref = worksheet.dimensions
        worksheet.freeze_panes = "A2"
        self._auto_width(worksheet)

    def _sorted_findings(self, findings: list[Finding]) -> list[Finding]:
        return sorted(
            findings,
            key=lambda finding: (
                _SEVERITY_ORDER.get(finding.severity, 99),
                _PILLAR_NAMES.get(finding.pillar, finding.pillar),
                finding.rule_id,
            ),
        )

    def _resource_rows(self, discovery: DiscoveryResult) -> list[tuple[str, int]]:
        by_type = discovery.resources.get("by_type", {}) if isinstance(discovery.resources, dict) else {}
        if isinstance(by_type, dict):
            rows = [(resource_type, count) for resource_type, count in by_type.items()]
        else:
            rows = [
                (
                    item.get("type", "unknown"),
                    int(item.get("resource_count", item.get("count", 0))),
                )
                for item in by_type
            ]
        return sorted(rows, key=lambda row: row[1], reverse=True)

    def _resource_total(self, discovery: DiscoveryResult) -> int:
        if not isinstance(discovery.resources, dict):
            return 0
        return int(discovery.resources.get("total_count", discovery.resources.get("total", 0)))

    def _severity_counts(self, findings: list[Finding]) -> dict[str, int]:
        counts = dict.fromkeys(_SEVERITY_ORDER, 0)
        for finding in findings:
            if finding.severity in counts:
                counts[finding.severity] += 1
        return counts

    def _style_header_row(self, worksheet, row_number: int) -> None:
        for cell in worksheet[row_number]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill(fill_type="solid", fgColor=_HEADER_FILL_COLOR)
            cell.alignment = Alignment(wrap_text=True, vertical="top")

    def _apply_wrap(self, worksheet, columns: list[str]) -> None:
        for column in columns:
            for row in range(2, worksheet.max_row + 1):
                worksheet[f"{column}{row}"].alignment = Alignment(wrap_text=True, vertical="top")

    def _auto_width(self, worksheet) -> None:
        for column_index in range(1, worksheet.max_column + 1):
            column_letter = get_column_letter(column_index)
            max_length = 0
            for cell in worksheet[column_letter]:
                value = "" if cell.value is None else str(cell.value)
                max_length = max(max_length, len(value))
            worksheet.column_dimensions[column_letter].width = min(max_length + 2, 60)

    def _severity_fill(self, severity: str):
        return PatternFill(
            fill_type="solid",
            fgColor=_SEVERITY_FILL_COLORS.get(severity, _SEVERITY_FILL_COLORS["low"]),
        )

    def _score_fill(self, score: float):
        if score > 80:
            color = _SCORE_FILL_GOOD
        elif score >= 60:
            color = _SCORE_FILL_WARNING
        else:
            color = _SCORE_FILL_RISK
        return PatternFill(fill_type="solid", fgColor=color)
