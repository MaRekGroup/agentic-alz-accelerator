<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Azure Diagrams Skill (Digest)

Routing skill that delegates diagram requests to the appropriate specialized skill.

## Routing Table

| Diagram Type | Target Skill | Output Format |
|-------------|--------------|---------------|
| Architecture diagrams (default) | `drawio` | `.drawio` |
| Dependency / runtime diagrams | `drawio` | `.drawio` |
| As-built / TDD diagrams | `drawio` | `.drawio` / `.svg` |
| WAF score / cost / compliance charts | `python-diagrams` | `.py` + `.png` |
| Python architecture diagrams | `python-diagrams` | `.py` + `.png` |
| Inline flowcharts, sequence, state, ER, Gantt | `mermaid` | fenced code block |
| Management group hierarchy | `mermaid` | fenced code block |

## Decision Tree

```text
Data visualization (charts, scores, metrics)?
├── YES → python-diagrams
└── NO → Needs Azure service icons?
    ├── YES → drawio
    └── NO → Inline in markdown?
        ├── YES → mermaid
        └── NO → drawio (default)
```

## ALZ-Specific Routing

| Request | Route To |
|---------|----------|
| Architecture diagram | `drawio` |
| Management group hierarchy | `mermaid` |
| WAF score chart | `python-diagrams` |
| Deployment pipeline | `mermaid` |
| Hub-spoke network | `drawio` |
| Cost breakdown chart | `python-diagrams` |

This skill does NOT generate diagrams — load the target skill instead:
- `.github/skills/drawio/SKILL.md`
- `.github/skills/python-diagrams/SKILL.md`
- `.github/skills/mermaid/SKILL.md`
