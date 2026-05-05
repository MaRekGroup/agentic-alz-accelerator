---
name: assessment-report
description: "Report generation templates, format conventions, and output structure for brownfield assessment artifacts. USE FOR: report rendering, output formatting, architecture documentation. DO NOT USE FOR: discovery (use brownfield-discovery), compliance evaluation (use wara-assessment)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "1.1"
  category: azure-assessment
---

# Assessment Report Skill

Generates comprehensive assessment reports from WARA evaluation results and
discovery data. Produces multiple artifact types for different audiences.

## Implementation Reference

- **Module:** `src/tools/report_generator.py`
- **Class:** `ReportGenerator`
- **CLI integration:** `src/tools/assess_cli.py` (Phase 3)
- **Input models:**
  - `DiscoveryResult` from `src/tools/discovery.py`
  - `AssessmentResult` from `src/tools/wara_engine.py`
- **Key methods:**
  - `generate_all(discovery, assessment, scope_label=)` → `dict[str, Path]`
  - `render_current_state(discovery, label)` → Markdown string
  - `render_target_state(discovery, assessment, label)` → Markdown string
  - `render_assessment_report(assessment, label)` → Markdown string
  - `render_architecture_diagram(discovery, label)` → Mermaid string
  - `render_adr(assessment, label)` → Markdown string
  - `render_pillar_report(assessment, pillar_key, label)` → Markdown string

## Report Types

### Current-State Architecture (`current-state-architecture.md`)

Documents the as-is Azure environment:

- Management group hierarchy table
- Subscription inventory
- Resource counts by type (sorted descending)
- Network topology (VNets, address spaces, peering count)
- Policy assignments (capped at 20, with overflow indicator)
- RBAC assignment counts
- Logging/monitoring configuration (LAW count, diagnostic settings count)
- Security posture (Defender secure score, plan count)
- Discovery errors (if any collectors failed)

### Target-State Architecture (`target-state-architecture.md`)

Remediation roadmap based on assessment findings:

- Assessment score summary (overall score, checks run, findings count)
- Findings grouped by WAF pillar, ordered by severity (Critical → Low)
- Step-by-step remediation instructions per finding
- Affected resource count per finding
- Target state alignment goals (CAF, WAF, Security Baseline, Cost Governance)

### Assessment Report (`assessment-report.md` + `.json`)

Scored findings report:

- Executive summary table (overall score, checks run/passed, findings count)
- Pillar score table (score, critical/high/medium/low counts per pillar)
- Detailed findings with: severity badge, pillar, CAF area, ALZ area, confidence, resources affected, recommendation, remediation steps, references
- JSON variant for machine consumption / CI integration (uses `AssessmentResult.to_dict()`)

### Architecture Diagram (`architecture-diagram.mmd`)

Mermaid graph of the discovered environment:

- Management group hierarchy subgraph with parent→child edges
- Subscription nodes subgraph
- Network topology subgraph with VNet address spaces
- Peering connections as bidirectional edges

### ADR (`ADR-assessment-findings.md`)

Architecture Decision Record for critical/high findings:

- Context (scope, overall score, finding count)
- Each critical/high finding as a decision item with proposed remediation
- Decision placeholder (Accept / Modify / Defer)
- Consequences section linking to target-state-architecture.md

### Per-Pillar Reports (`pillar-reports/wara-{pillar}.md`)

Detailed report for each WAF pillar, written to `pillar-reports/` subdirectory:

| File | Pillar |
|------|--------|
| `wara-security.md` | Security |
| `wara-reliability.md` | Reliability |
| `wara-cost-optimization.md` | Cost Optimization |
| `wara-operational-excellence.md` | Operational Excellence |
| `wara-performance.md` | Performance Efficiency |

Each pillar report contains:

- Pillar description and purpose
- Score with interpretation (see [Score Interpretation](#score-interpretation))
- Related CAF design areas mapping
- Findings summary table (ID, severity, title, confidence, resource count)
- Detailed findings with affected resources table (capped at 20 per finding)
- Remediation priority matrix (effort vs impact)

## Output Directory

All artifacts are written to:

```
agent-output/{customer}/assessment/<scope-label>/
├── current-state-architecture.md
├── target-state-architecture.md
├── assessment-report.md
├── assessment-report.json
├── architecture-diagram.mmd
├── ADR-assessment-findings.md
└── pillar-reports/
    ├── wara-security.md
    ├── wara-reliability.md
    ├── wara-cost-optimization.md
    ├── wara-operational-excellence.md
    └── wara-performance.md
```

Where `<scope-label>` is derived from the assessment scope, sanitized to be
filesystem-safe (alphanumeric, hyphens, underscores only).

## Usage

```python
from src.tools.report_generator import ReportGenerator

reporter = ReportGenerator(output_dir="agent-output/{customer}/assessment")
outputs = reporter.generate_all(discovery_result, assessment_result, scope_label="sub-001")
# Returns dict mapping report type to file Path:
# {
#   "current_state": Path(...),
#   "target_state": Path(...),
#   "assessment_report": Path(...),
#   "assessment_json": Path(...),
#   "architecture_diagram": Path(...),
#   "adr": Path(...),
#   "pillar_security": Path(...),
#   "pillar_reliability": Path(...),
#   "pillar_cost_optimization": Path(...),
#   "pillar_operational_excellence": Path(...),
#   "pillar_performance": Path(...),
# }
```

## Format Conventions

### Severity Badges

| Severity | Badge | Markdown |
|----------|-------|----------|
| Critical | 🔴 Critical | `🔴 Critical` |
| High | 🟠 High | `🟠 High` |
| Medium | 🟡 Medium | `🟡 Medium` |
| Low | 🔵 Low | `🔵 Low` |

### Score Interpretation

| Score Range | Assessment | Indicator |
|-------------|------------|-----------|
| ≥ 90 | Excellent — minimal remediation needed | ✅ |
| ≥ 70 | Good — some improvements recommended | ⚠️ |
| ≥ 50 | Fair — significant gaps require attention | 🟡 |
| < 50 | Poor — critical remediation required | 🔴 |

### Pillar → CAF Design Area Mapping

| Pillar | Related CAF Areas |
|--------|-------------------|
| Security | Security, Identity & Access, Network |
| Reliability | Network, Management, Security |
| Cost Optimization | Governance, Management |
| Operational Excellence | Governance, Management, Platform Automation |
| Performance | Network, Management |

### Remediation Priority Matrix

Generated in per-pillar reports based on:

| Column | Derivation |
|--------|-----------|
| Effort | Low (≤1 step), Medium (2–3 steps), High (>3 steps) |
| Impact | Maps directly from finding severity |

### Caps and Limits

- Evidence/affected resources: capped at 20 per finding in pillar reports
- Policy assignments: capped at 20 in current-state doc (with overflow count)
- All timestamps in UTC
- Mermaid node IDs: alphanumeric only (special chars replaced with underscore)

## Integration with assess.yml Workflow

The `assess.yml` GitHub Actions workflow calls the reporter via `assess_cli.py`
and reads outputs for the job summary:

```yaml
# Workflow reads assessment-report.json for summary metrics:
SCORE=$(python -c "import json; d=json.load(open('assessment-report.json')); print(d['overall_score'])")
FINDINGS=$(python -c "import json; d=json.load(open('assessment-report.json')); print(len(d.get('findings',[])))")
```

The JSON artifact is uploaded via `actions/upload-artifact@v4` for downstream consumption.

## Post-Report Actions (via alz-recall)

After report generation, the orchestrator should:

```bash
alz-recall complete-step {customer} 0 --json          # Mark assessment complete
alz-recall decide {customer} --key architecture_pattern --value {pattern} --json
alz-recall finding {customer} --severity critical --message "..." --json  # Per critical finding
```

Assessment artifacts feed into Step 1 (Requirements) as brownfield context —
the Requirements agent reads `current-state-architecture.md` and
`assessment-report.json` to pre-populate known constraints.
