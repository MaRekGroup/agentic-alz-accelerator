---
name: diagram-generation-patterns
description: "Reusable patterns for architecture diagram generation across Azure Landing Zone workflows—routing, templating, and multi-engine coordination."
category: diagrams-workflow
author: basher
version: "1.0"
---

# Diagram Generation Patterns

## Problem

Architecture diagram generation in ALZ scenarios requires:
1. **Right tool selection** — When should you use Draw.io vs Python diagrams vs Mermaid?
2. **Consistent output** — How do you ensure all diagrams include required elements (CIDRs, icons, constraints)?
3. **Multi-engine coordination** — How do you support both quick PNG generation and editable Draw.io files?
4. **Sync with decisions** — How do diagrams stay current as architecture evolves?

## Solution Pattern: Routing + Dual-Format Generation

### 1. Diagram Type Routing (Decision Tree)

Use the routing skill (`azure-diagrams/SKILL.md`) decision tree to classify requests:

```
Is it a data visualization (charts, scores, metrics)?
├── YES → python-diagrams (PNG output)
└── NO → Does it need Azure service icons?
    ├── YES → drawio (interactive .drawio files)
    └── NO → Is it inline in markdown?
        ├── YES → mermaid (fenced code blocks)
        └── NO → drawio (default)
```

**Routing table reference:**

| Diagram Type | Engine | Output | When |
|---|---|---|---|
| Architecture overview | drawio | `.drawio` + `.png` | Design phase (Step 3) |
| Network topology | drawio | `.drawio` + `.png` | Design phase + TDD |
| Security posture | drawio | `.drawio` + `.png` | Design phase + TDD |
| Management group hierarchy | mermaid | Markdown fence | Inline docs + Design phase |
| Deployment sequence | mermaid | Markdown fence | Runbooks, workflows |
| WAF score chart | python-diagrams | `.png` | Assessment reports |
| Cost projection | python-diagrams | `.png` | Cost governance reports |

### 2. Dual-Format Output Pattern

For architecture diagrams at Step 3 and Step 7, always generate **both** formats:

```
Design Agent (Step 3) Output:
├── agent-output/{customer}/diagrams/
│   ├── 01-management-group-hierarchy.drawio    (editable)
│   ├── 01-management-group-hierarchy.png       (quick ref)
│   ├── 01-management-group-hierarchy.md        (Mermaid for GitHub)
│   ├── 02-hub-spoke-network-topology.drawio
│   ├── 02-hub-spoke-network-topology.png
│   └── ... (3 more diagram types)
├── agent-output/{customer}/adr/
│   └── ADR-001.md ... ADR-007.md               (decisions driving diagrams)
```

### 3. Key Files

| File | Purpose |
|------|---------|
| `.github/skills/azure-diagrams/SKILL.md` | Routing skill + decision tree |
| `.github/skills/drawio/SKILL.md` | Draw.io MCP server usage |
| `.github/skills/python-diagrams/SKILL.md` | Python diagrams library |
| `.github/skills/mermaid/SKILL.md` | Mermaid inline diagrams |
| `src/tools/azure_diagram_generator.py` | SVG engine with Azure colors |
| `src/tools/python_diagram_generator.py` | DiagramEngine class (4 templates) |
| `.github/agents/design.md` | Design agent (Step 3) definition |
| `.github/agents/documentation.md` | Documentation agent (Step 7) definition |

## Pattern Application

Use this pattern when:
- Designing architecture diagrams for ALZ deployments (Step 3)
- Documenting landing zones in TDDs (Step 7)
- Embedding diagrams in PR reviews (use Mermaid)
- Generating data visualizations for reports (use Python diagrams)

