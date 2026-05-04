"""
Report Generator — produces assessment reports and environment documentation.

Generates from DiscoveryResult + AssessmentResult:
- Current-state architecture documentation (Markdown)
- Target-state architecture documentation (Markdown)
- Architecture diagrams (Mermaid)
- Architecture Decision Records (ADRs)
- Assessment summary report (Markdown + JSON)

Output directory: agent-output/{customer}/assessment/<scope>/
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from src.tools.discovery import DiscoveryResult
from src.tools.wara_engine import AssessmentResult, Finding

logger = logging.getLogger(__name__)

# Severity badge mapping for Markdown
_SEVERITY_BADGE = {
    "critical": "🔴 Critical",
    "high": "🟠 High",
    "medium": "🟡 Medium",
    "low": "🔵 Low",
}

# Pillar display names
_PILLAR_NAMES = {
    "security": "Security",
    "reliability": "Reliability",
    "cost_optimization": "Cost Optimization",
    "operational_excellence": "Operational Excellence",
    "performance": "Performance Efficiency",
}

# Pillar descriptions for per-pillar reports
_PILLAR_DESCRIPTIONS = {
    "security": (
        "Protect your workload against security threats. Security controls include "
        "network segmentation, identity management, encryption, threat detection, "
        "and vulnerability management."
    ),
    "reliability": (
        "Ensure your workload meets uptime commitments. Reliability encompasses "
        "availability zones, redundancy, disaster recovery, backup, and monitoring."
    ),
    "cost_optimization": (
        "Deliver business value while minimizing cost. Cost optimization covers "
        "right-sizing, reserved instances, waste elimination, budgets, and governance."
    ),
    "operational_excellence": (
        "Maintain operational health of your workload. Operational excellence includes "
        "IaC practices, policy-driven governance, logging, alerting, and automation."
    ),
    "performance": (
        "Ensure your workload meets performance targets. Performance efficiency covers "
        "scaling, caching, load balancing, and resource sizing."
    ),
}

# Pillar → relevant CAF design areas
_PILLAR_CAF_AREAS = {
    "security": ["security", "identity_access", "network"],
    "reliability": ["network", "management", "security"],
    "cost_optimization": ["governance", "management"],
    "operational_excellence": ["governance", "management", "platform_automation"],
    "performance": ["network", "management"],
}


class ReportGenerator:
    """Generates assessment reports and environment documentation."""

    def __init__(self, output_dir: str | Path = "agent-output/assessment"):
        self.output_dir = Path(output_dir)

    def generate_all(
        self,
        discovery: DiscoveryResult,
        assessment: AssessmentResult,
        *,
        scope_label: str | None = None,
    ) -> dict[str, Path]:
        """Generate all report artifacts. Returns mapping of report type to file path."""
        label = scope_label or discovery.scope
        safe_label = _safe_filename(label)
        report_dir = self.output_dir / safe_label
        report_dir.mkdir(parents=True, exist_ok=True)

        outputs: dict[str, Path] = {}

        outputs["current_state"] = self._write(
            report_dir / "current-state-architecture.md",
            self.render_current_state(discovery, label),
        )
        outputs["target_state"] = self._write(
            report_dir / "target-state-architecture.md",
            self.render_target_state(discovery, assessment, label),
        )
        outputs["assessment_report"] = self._write(
            report_dir / "assessment-report.md",
            self.render_assessment_report(assessment, label),
        )
        outputs["assessment_json"] = self._write(
            report_dir / "assessment-report.json",
            json.dumps(assessment.to_dict(), indent=2, default=str),
        )
        outputs["architecture_diagram"] = self._write(
            report_dir / "architecture-diagram.mmd",
            self.render_architecture_diagram(discovery, label),
        )
        outputs["adr"] = self._write(
            report_dir / "ADR-assessment-findings.md",
            self.render_adr(assessment, label),
        )

        # Per-pillar detailed reports
        pillar_dir = report_dir / "pillar-reports"
        pillar_dir.mkdir(parents=True, exist_ok=True)
        for pillar_key in _PILLAR_NAMES:
            filename = f"wara-{pillar_key.replace('_', '-')}.md"
            outputs[f"pillar_{pillar_key}"] = self._write(
                pillar_dir / filename,
                self.render_pillar_report(assessment, pillar_key, label),
            )

        logger.info("Generated %d report artifacts in %s", len(outputs), report_dir)
        return outputs

    # ── Current-State Architecture ────────────────────────────────────────

    def render_current_state(self, discovery: DiscoveryResult, label: str) -> str:
        """Render current-state architecture doc from discovery data."""
        lines = [
            f"# Current-State Architecture — {label}",
            "",
            f"> Auto-generated by the ALZ Accelerator assessment engine on "
            f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            "",
            f"**Scope**: `{discovery.scope}` ({discovery.scope_type.value})",
            f"**Discovered at**: {discovery.discovered_at}",
            "",
        ]

        # Management Groups
        if discovery.management_groups:
            lines += [
                "## Management Group Hierarchy",
                "",
                "| Name | Display Name | Parent |",
                "|------|-------------|--------|",
            ]
            for mg in discovery.management_groups:
                name = mg.get("name", "—")
                display = mg.get("displayName", mg.get("display_name", "—"))
                parent = mg.get("parent", mg.get("parentId", "—"))
                lines.append(f"| {name} | {display} | {parent} |")
            lines.append("")

        # Subscriptions
        if discovery.subscriptions:
            lines += [
                "## Subscriptions",
                "",
                "| Name | Subscription ID | State |",
                "|------|----------------|-------|",
            ]
            for sub in discovery.subscriptions:
                name = sub.get("name", sub.get("displayName", "—"))
                sub_id = sub.get("subscriptionId", sub.get("id", "—"))
                state = sub.get("state", "—")
                lines.append(f"| {name} | `{sub_id}` | {state} |")
            lines.append("")

        # Resources summary
        if discovery.resources:
            lines += ["## Resource Inventory", ""]
            if isinstance(discovery.resources, dict):
                if "by_type" in discovery.resources:
                    lines += [
                        "### By Type",
                        "",
                        "| Resource Type | Count |",
                        "|--------------|-------|",
                    ]
                    for rtype, count in sorted(
                        discovery.resources["by_type"].items(),
                        key=lambda x: x[1],
                        reverse=True,
                    ):
                        lines.append(f"| `{rtype}` | {count} |")
                    lines.append("")
                if "total" in discovery.resources:
                    lines.append(f"**Total resources**: {discovery.resources['total']}")
                    lines.append("")
            else:
                lines.append(f"Resources discovered: {len(discovery.resources)}")
                lines.append("")

        # Network Topology
        if discovery.network_topology:
            lines += ["## Network Topology", ""]
            topo = discovery.network_topology
            if "vnets" in topo:
                lines += [
                    "### Virtual Networks",
                    "",
                    "| Name | Address Space | Peerings |",
                    "|------|--------------|----------|",
                ]
                for vnet in topo["vnets"]:
                    name = vnet.get("name", "—")
                    addr = ", ".join(vnet.get("addressPrefixes", vnet.get("address_space", [])))
                    peers = len(vnet.get("peerings", []))
                    lines.append(f"| {name} | `{addr}` | {peers} |")
                lines.append("")

        # Policy Assignments
        if discovery.policy_assignments:
            lines += [
                "## Policy Assignments",
                "",
                f"**Total assignments**: {len(discovery.policy_assignments)}",
                "",
                "| Name | Type |",
                "|------|------|",
            ]
            for pa in discovery.policy_assignments[:20]:
                name = pa.get("displayName", pa.get("name", "—"))
                pa_type = "Initiative" if pa.get("policyType") == "BuiltIn" else "Policy"
                lines.append(f"| {name} | {pa_type} |")
            if len(discovery.policy_assignments) > 20:
                lines.append(f"| ... and {len(discovery.policy_assignments) - 20} more | |")
            lines.append("")

        # RBAC
        if discovery.rbac_assignments:
            lines += [
                "## RBAC Assignments",
                "",
                f"**Total assignments**: {len(discovery.rbac_assignments)}",
                "",
            ]

        # Logging
        if discovery.logging_config:
            lines += ["## Logging & Monitoring", ""]
            lc = discovery.logging_config
            if "log_analytics_workspaces" in lc:
                lines.append(
                    f"**Log Analytics Workspaces**: {len(lc['log_analytics_workspaces'])}"
                )
            if "diagnostic_settings" in lc:
                lines.append(
                    f"**Diagnostic Settings**: {len(lc['diagnostic_settings'])}"
                )
            lines.append("")

        # Security Posture
        if discovery.security_posture:
            lines += ["## Security Posture", ""]
            sp = discovery.security_posture
            if "secure_score" in sp:
                lines.append(f"**Defender Secure Score**: {sp['secure_score']}")
            if "defender_plans" in sp:
                lines.append(f"**Defender Plans**: {len(sp['defender_plans'])} enabled")
            lines.append("")

        # Errors
        if discovery.errors:
            lines += [
                "## Discovery Errors",
                "",
                "The following collectors encountered errors:",
                "",
            ]
            for err in discovery.errors:
                lines.append(f"- {err}")
            lines.append("")

        return "\n".join(lines)

    # ── Target-State Architecture ─────────────────────────────────────────

    def render_target_state(
        self,
        discovery: DiscoveryResult,
        assessment: AssessmentResult,
        label: str,
    ) -> str:
        """Render target-state architecture doc with remediation roadmap."""
        lines = [
            f"# Target-State Architecture — {label}",
            "",
            f"> Auto-generated by the ALZ Accelerator assessment engine on "
            f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            "",
            "## Assessment Summary",
            "",
            f"- **Overall Score**: {assessment.overall_score:.1f}/100",
            f"- **Checks Run**: {assessment.checks_run}",
            f"- **Findings**: {len(assessment.findings)}",
            "",
        ]

        # Group findings by pillar for remediation roadmap
        by_pillar: dict[str, list[Finding]] = {}
        for f in assessment.findings:
            by_pillar.setdefault(f.pillar, []).append(f)

        if by_pillar:
            lines += ["## Remediation Roadmap", ""]
            lines += [
                "Priority order: Critical → High → Medium → Low within each pillar.",
                "",
            ]

            for pillar_key, pillar_name in _PILLAR_NAMES.items():
                findings = by_pillar.get(pillar_key, [])
                if not findings:
                    continue
                score = assessment.pillar_scores.get(pillar_key)
                score_str = f" (Score: {score.score:.1f}/100)" if score else ""
                lines += [
                    f"### {pillar_name}{score_str}",
                    "",
                ]
                for f in findings:
                    badge = _SEVERITY_BADGE.get(f.severity, f.severity)
                    lines += [
                        f"#### {badge} — {f.title} (`{f.rule_id}`)",
                        "",
                        f"**Recommendation**: {f.recommendation}",
                        "",
                    ]
                    if f.remediation_steps:
                        lines.append("**Steps**:")
                        for i, step in enumerate(f.remediation_steps, 1):
                            lines.append(f"{i}. {step}")
                        lines.append("")
                    if f.evidence:
                        lines.append(
                            f"*{len(f.evidence)} resource(s) affected*"
                        )
                        lines.append("")

        # Target state description
        lines += [
            "## Target State",
            "",
            "After remediating all findings, the environment will align with:",
            "",
            "- **CAF Enterprise-Scale** management group hierarchy",
            "- **WAF 5-Pillar** best practices across all resources",
            "- **Security Baseline** (TLS 1.2, HTTPS-only, no public blob, managed identity, AAD-only SQL, no public endpoints in prod)",
            "- **Cost Governance** (budgets with 80%/100%/120% alerts)",
            "- **Operational Excellence** (centralized logging, policy-driven governance, tagging standards)",
            "",
        ]

        return "\n".join(lines)

    # ── Assessment Report ─────────────────────────────────────────────────

    def render_assessment_report(self, assessment: AssessmentResult, label: str) -> str:
        """Render the main assessment report in Markdown."""
        lines = [
            f"# WARA Assessment Report — {label}",
            "",
            f"> Assessed on {assessment.assessed_at}",
            "",
            "## Executive Summary",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Overall Score | **{assessment.overall_score:.1f}/100** |",
            f"| Checks Run | {assessment.checks_run} |",
            f"| Checks Passed | {assessment.checks_passed} |",
            f"| Findings | {len(assessment.findings)} |",
            "",
            "## Pillar Scores",
            "",
            "| Pillar | Score | Critical | High | Medium | Low |",
            "|--------|-------|----------|------|--------|-----|",
        ]

        for pillar_key, pillar_name in _PILLAR_NAMES.items():
            ps = assessment.pillar_scores.get(pillar_key)
            if ps:
                lines.append(
                    f"| {pillar_name} | {ps.score:.1f} | {ps.critical} | {ps.high} | {ps.medium} | {ps.low} |"
                )
            else:
                lines.append(f"| {pillar_name} | — | — | — | — | — |")
        lines.append("")

        # Findings detail
        if assessment.findings:
            lines += ["## Findings", ""]
            for f in assessment.findings:
                badge = _SEVERITY_BADGE.get(f.severity, f.severity)
                lines += [
                    f"### {badge} — {f.title} (`{f.rule_id}`)",
                    "",
                    f"- **Pillar**: {_PILLAR_NAMES.get(f.pillar, f.pillar)}",
                    f"- **CAF Area**: {f.caf_area}",
                    f"- **ALZ Area**: {f.alz_area}",
                    f"- **Confidence**: {f.confidence}",
                    f"- **Resources affected**: {len(f.evidence)}",
                    "",
                    f"**Recommendation**: {f.recommendation}",
                    "",
                ]
                if f.remediation_steps:
                    lines.append("**Remediation**:")
                    for i, step in enumerate(f.remediation_steps, 1):
                        lines.append(f"{i}. {step}")
                    lines.append("")
                if f.references:
                    lines.append("**References**:")
                    for ref in f.references:
                        lines.append(f"- {ref}")
                    lines.append("")
        else:
            lines += ["## Findings", "", "No findings — all checks passed. ✅", ""]

        return "\n".join(lines)

    # ── Architecture Diagram (Mermaid) ────────────────────────────────────

    def render_architecture_diagram(self, discovery: DiscoveryResult, label: str) -> str:
        """Render a Mermaid diagram of the current architecture."""
        lines = [
            "---",
            f"title: {label} — Current Architecture",
            "---",
            "graph TD",
        ]

        # Management groups
        if discovery.management_groups:
            lines.append("  subgraph MG[Management Groups]")
            for i, mg in enumerate(discovery.management_groups):
                name = mg.get("name", f"mg-{i}")
                display = mg.get("displayName", mg.get("display_name", name))
                node_id = _mermaid_id(name)
                lines.append(f"    {node_id}[{display}]")
            lines.append("  end")
            lines.append("")

            # Parent-child edges
            for mg in discovery.management_groups:
                name = mg.get("name", "")
                parent = mg.get("parent", mg.get("parentId", ""))
                if parent and name:
                    parent_id = _extract_mg_name(parent)
                    # Check parent exists in our MG list
                    mg_names = [m.get("name", "") for m in discovery.management_groups]
                    if parent_id in mg_names:
                        lines.append(f"  {_mermaid_id(parent_id)} --> {_mermaid_id(name)}")

        # Subscriptions
        if discovery.subscriptions:
            lines.append("")
            lines.append("  subgraph SUBS[Subscriptions]")
            for sub in discovery.subscriptions:
                name = sub.get("name", sub.get("displayName", "sub"))
                node_id = _mermaid_id(name)
                lines.append(f"    {node_id}[{name}]")
            lines.append("  end")

        # Network topology
        if discovery.network_topology and discovery.network_topology.get("vnets"):
            lines.append("")
            lines.append("  subgraph NET[Network]")
            for vnet in discovery.network_topology["vnets"]:
                name = vnet.get("name", "vnet")
                addr = ", ".join(
                    vnet.get("addressPrefixes", vnet.get("address_space", []))
                )
                node_id = _mermaid_id(name)
                lines.append(f"    {node_id}[{name}<br/>{addr}]")
            lines.append("  end")

            # Peering edges
            for vnet in discovery.network_topology["vnets"]:
                src = _mermaid_id(vnet.get("name", ""))
                for peer in vnet.get("peerings", []):
                    dst_name = peer.get("remoteVNet", peer.get("name", ""))
                    if dst_name:
                        dst = _mermaid_id(dst_name)
                        lines.append(f"  {src} <--> {dst}")

        lines.append("")
        return "\n".join(lines)

    # ── ADR ───────────────────────────────────────────────────────────────

    def render_adr(self, assessment: AssessmentResult, label: str) -> str:
        """Render an Architecture Decision Record for assessment findings."""
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        critical_high = [
            f for f in assessment.findings if f.severity in ("critical", "high")
        ]

        lines = [
            f"# ADR — Assessment Findings for {label}",
            "",
            f"**Date**: {date_str}",
            "**Status**: Proposed",
            "**Deciders**: Platform team",
            "",
            "## Context",
            "",
            f"A WARA/CAF assessment was performed on `{assessment.scope}` "
            f"scoring **{assessment.overall_score:.1f}/100** overall.",
            f"The assessment identified **{len(assessment.findings)}** findings "
            f"across {assessment.checks_run} checks.",
            "",
        ]

        if critical_high:
            lines += [
                "## Critical/High Findings Requiring Decision",
                "",
            ]
            for f in critical_high:
                badge = _SEVERITY_BADGE.get(f.severity, f.severity)
                lines += [
                    f"### {badge} — {f.title} (`{f.rule_id}`)",
                    "",
                    f"**Problem**: {f.recommendation}",
                    "",
                ]
                if f.remediation_steps:
                    lines.append("**Proposed remediation**:")
                    for i, step in enumerate(f.remediation_steps, 1):
                        lines.append(f"{i}. {step}")
                    lines.append("")

        lines += [
            "## Decision",
            "",
            "<!-- TO BE FILLED: Accept / Modify / Defer each finding -->",
            "",
            "## Consequences",
            "",
            "- Accepted findings will be remediated according to the roadmap in target-state-architecture.md",
            "- Deferred findings will be tracked in the next assessment cycle",
            "",
        ]

        return "\n".join(lines)

    # ── Per-Pillar Detailed Report ──────────────────────────────────────

    def render_pillar_report(
        self,
        assessment: AssessmentResult,
        pillar_key: str,
        label: str,
    ) -> str:
        """Render a detailed report for a single WAF pillar."""
        pillar_name = _PILLAR_NAMES.get(pillar_key, pillar_key)
        description = _PILLAR_DESCRIPTIONS.get(pillar_key, "")
        caf_areas = _PILLAR_CAF_AREAS.get(pillar_key, [])
        score_obj = assessment.pillar_scores.get(pillar_key)
        pillar_findings = [f for f in assessment.findings if f.pillar == pillar_key]

        lines = [
            f"# {pillar_name} — Detailed Assessment Report",
            "",
            f"> **Scope**: `{assessment.scope}` | **Assessed**: {assessment.assessed_at}",
            "",
            "---",
            "",
            "## Overview",
            "",
            description,
            "",
        ]

        # Score summary
        if score_obj:
            lines += [
                "## Score",
                "",
                "| Metric | Value |",
                "|--------|-------|",
                f"| **Pillar Score** | **{score_obj.score:.1f}/100** |",
                f"| Critical findings | {score_obj.critical} |",
                f"| High findings | {score_obj.high} |",
                f"| Medium findings | {score_obj.medium} |",
                f"| Low findings | {score_obj.low} |",
                f"| Total findings | {len(pillar_findings)} |",
                "",
            ]

            # Score interpretation
            if score_obj.score >= 90:
                lines.append("**Assessment**: ✅ Excellent — minimal remediation needed.")
            elif score_obj.score >= 70:
                lines.append("**Assessment**: ⚠️ Good — some improvements recommended.")
            elif score_obj.score >= 50:
                lines.append("**Assessment**: 🟡 Fair — significant gaps require attention.")
            else:
                lines.append("**Assessment**: 🔴 Poor — critical remediation required.")
            lines.append("")
        else:
            lines += [
                "## Score",
                "",
                "No score data available for this pillar.",
                "",
            ]

        # Related CAF design areas
        if caf_areas:
            lines += [
                "## Related CAF Design Areas",
                "",
                "| Design Area | Relevance |",
                "|-------------|-----------|",
            ]
            area_names = {
                "security": "Security",
                "identity_access": "Identity & Access Management",
                "network": "Network Topology & Connectivity",
                "governance": "Governance",
                "management": "Management",
                "platform_automation": "Platform Automation & DevOps",
            }
            for area in caf_areas:
                lines.append(f"| {area_names.get(area, area)} | Primary |")
            lines.append("")

        # Findings by severity
        if pillar_findings:
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            pillar_findings.sort(key=lambda f: severity_order.get(f.severity, 99))

            # Summary table
            lines += [
                "## Findings Summary",
                "",
                "| # | ID | Severity | Title | Confidence | Resources |",
                "|---|-----|----------|-------|-----------|-----------|",
            ]
            for i, f in enumerate(pillar_findings, 1):
                badge = _SEVERITY_BADGE.get(f.severity, f.severity)
                res_count = len(f.evidence) if f.evidence else 0
                lines.append(
                    f"| {i} | `{f.rule_id}` | {badge} | {f.title} | {f.confidence} | {res_count} |"
                )
            lines.append("")

            # Detailed findings
            lines += ["## Detailed Findings", ""]
            for f in pillar_findings:
                badge = _SEVERITY_BADGE.get(f.severity, f.severity)
                lines += [
                    f"### {f.rule_id}: {f.title}",
                    "",
                    "| Attribute | Value |",
                    "|-----------|-------|",
                    f"| Severity | {badge} |",
                    f"| Confidence | {f.confidence} |",
                    f"| CAF Area | {f.caf_area} |",
                    f"| ALZ Area | {f.alz_area} |",
                    f"| Resources Affected | {len(f.evidence) if f.evidence else 0} |",
                    "",
                    f"**Recommendation**: {f.recommendation}",
                    "",
                ]

                if f.remediation_steps:
                    lines.append("**Remediation Steps**:")
                    lines.append("")
                    for i, step in enumerate(f.remediation_steps, 1):
                        lines.append(f"{i}. {step}")
                    lines.append("")

                if f.evidence:
                    lines += [
                        "**Affected Resources**:",
                        "",
                        "| Resource ID | Name |",
                        "|------------|------|",
                    ]
                    for res in f.evidence[:20]:
                        res_id = res.get("id", "—")
                        res_name = res.get("name", "—")
                        lines.append(f"| `{res_id}` | {res_name} |")
                    if len(f.evidence) > 20:
                        lines.append(f"| ... | *{len(f.evidence) - 20} more* |")
                    lines.append("")

                if f.references:
                    lines.append("**References**:")
                    lines.append("")
                    for ref in f.references:
                        lines.append(f"- [{ref}]({ref})")
                    lines.append("")

                lines.append("---")
                lines.append("")
        else:
            lines += [
                "## Findings",
                "",
                "✅ No findings — all checks passed for this pillar.",
                "",
            ]

        # Remediation priority matrix (only if findings exist)
        if pillar_findings:
            lines += [
                "## Remediation Priority Matrix",
                "",
                "| Priority | ID | Title | Effort | Impact |",
                "|----------|-----|-------|--------|--------|",
            ]
            for i, f in enumerate(pillar_findings, 1):
                # Estimate effort based on remediation steps count
                steps = len(f.remediation_steps) if f.remediation_steps else 0
                effort = "Low" if steps <= 1 else ("Medium" if steps <= 3 else "High")
                impact = "Critical" if f.severity == "critical" else (
                    "High" if f.severity == "high" else "Medium"
                )
                lines.append(f"| {i} | `{f.rule_id}` | {f.title} | {effort} | {impact} |")
            lines.append("")

        return "\n".join(lines)

    # ── Helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _write(path: Path, content: str) -> Path:
        path.write_text(content, encoding="utf-8")
        logger.debug("Wrote %s (%d bytes)", path, len(content))
        return path


def _safe_filename(name: str) -> str:
    """Convert a scope name to a filesystem-safe directory name."""
    return "".join(c if c.isalnum() or c in "-_" else "-" for c in name).strip("-")


def _mermaid_id(name: str) -> str:
    """Convert a name to a valid Mermaid node ID."""
    return "".join(c if c.isalnum() else "_" for c in name).strip("_") or "node"


def _extract_mg_name(parent_ref: str) -> str:
    """Extract management group name from a full resource ID or plain name."""
    if "/" in parent_ref:
        return parent_ref.rstrip("/").rsplit("/", 1)[-1]
    return parent_ref
