<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Assessment Report Skill (Digest)

Generates comprehensive brownfield assessment reports from WARA evaluation and discovery data.

## Implementation Reference

- **Module:** `src/tools/report_generator.py` — Class: `ReportGenerator`
- **CLI:** `src/tools/assess_cli.py`
- **Key method:** `generate_all(discovery, assessment, scope_label=)` → `dict[str, Path]`

## Report Types

| Report | File | Content |
|--------|------|---------|
| Current-State Architecture | `current-state-architecture.md` | MG hierarchy, subscriptions, resource counts, network topology, policy/RBAC, logging, security posture |
| Target-State Architecture | `target-state-architecture.md` | Score summary, findings by WAF pillar (Critical→Low), remediation steps |
| Assessment Report | `assessment-report.md` + `.json` | Executive summary, pillar scores, detailed findings with severity badges |
| Architecture Diagram | `architecture-diagram.mmd` | Mermaid graph: MG hierarchy, subscriptions, network topology, peering |
| ADR | `ADR-assessment-findings.md` | Critical/high findings as decision items with proposed remediation |
| Per-Pillar Reports | `pillar-reports/wara-{pillar}.md` | Score, CAF mapping, findings table, remediation priority matrix |

## Output Directory

```
agent-output/{customer}/assessment/<scope-label>/
├── current-state-architecture.md
├── target-state-architecture.md
├── assessment-report.md / .json
├── architecture-diagram.mmd
├── ADR-assessment-findings.md
└── pillar-reports/wara-{pillar}.md (×5)
```

## Format Conventions

| Severity | Badge |
|----------|-------|
| Critical | 🔴 Critical |
| High | 🟠 High |
| Medium | 🟡 Medium |
| Low | 🔵 Low |

| Score Range | Assessment | Indicator |
|-------------|------------|-----------|
| ≥ 90 | Excellent | ✅ |
| ≥ 70 | Good | ⚠️ |
| ≥ 50 | Fair | 🟡 |
| < 50 | Poor | 🔴 |

| Pillar | Related CAF Areas |
|--------|-------------------|
| Security | Security, Identity & Access, Network |
| Reliability | Network, Management, Security |
| Cost Optimization | Governance, Management |
| Operational Excellence | Governance, Management, Platform Automation |
| Performance | Network, Management |

## Caps and Limits

- Evidence/affected resources: capped at 20 per finding
- Policy assignments: capped at 20 (with overflow count)
- All timestamps in UTC
- Mermaid node IDs: alphanumeric only

> _See SKILL.md for full usage examples, code snippets, and workflow integration details._
