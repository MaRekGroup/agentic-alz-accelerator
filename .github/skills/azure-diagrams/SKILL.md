---
name: azure-diagrams
description: "ROUTING SKILL — delegates to specialized diagram skills (drawio, python-diagrams, mermaid) based on diagram type. USE FOR: any diagram request when the caller does not know which tool to use. DO NOT USE FOR: direct diagram generation (load the target skill instead)."
compatibility: Works with VS Code Copilot, Claude Code, and any MCP-compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "1.0"
  category: diagrams
---

# Azure Diagrams — Routing Skill

This skill routes diagram requests to the appropriate specialized skill.
Do NOT load this skill's references directly — load the target skill instead.

## Routing Table

| Diagram Type | Target Skill | Output Format | When to Use |
|-------------|--------------|---------------|-------------|
| Architecture diagrams (default) | `drawio` | `.drawio` | Hub-spoke topology, platform LZ layout, resource relationships |
| Dependency / runtime diagrams | `drawio` | `.drawio` | Service dependencies, network flows |
| As-built diagrams | `drawio` | `.drawio` | Post-deployment documentation |
| TDD architecture diagrams | `drawio` | `.drawio` / `.svg` | Technical Design Document visuals |
| WAF score bar charts | `python-diagrams` | `.py` + `.png` | Assessment reports, WAF pillar visualization |
| Cost donut / projection charts | `python-diagrams` | `.py` + `.png` | Cost governance reports |
| Compliance gap charts | `python-diagrams` | `.py` + `.png` | Monitoring reports |
| Python architecture diagrams | `python-diagrams` | `.py` + `.png` | Programmatic diagram generation |
| Inline markdown flowcharts | `mermaid` | fenced code block | Documentation, runbooks |
| Sequence diagrams | `mermaid` | fenced code block | Auth flows, deployment sequences |
| State diagrams | `mermaid` | fenced code block | Landing zone lifecycle |
| Management group hierarchy | `mermaid` | fenced code block | Organization structure |
| ER diagrams | `mermaid` | fenced code block | Resource relationship docs |
| Gantt charts | `mermaid` | fenced code block | Deployment schedules |

## How to Use

1. Identify the diagram type from the request
2. Look up the target skill in the routing table above
3. Read `.github/skills/{target-skill}/SKILL.md` instead of this file
4. Follow that skill's generation workflow and guardrails

## ALZ-Specific Routing

| Request | Route To | Reason |
|---------|----------|--------|
| "Create an architecture diagram" | `drawio` | Azure icons needed |
| "Show the management group hierarchy" | `mermaid` | Simple tree, inline in docs |
| "Generate a WAF score chart" | `python-diagrams` | Data visualization |
| "Visualize the deployment pipeline" | `mermaid` | Flowchart in documentation |
| "Create a TDD diagram" | `drawio` | Detailed architecture with icons |
| "Show the hub-spoke network" | `drawio` | Network topology with Azure icons |
| "Diagram the APEX workflow" | `mermaid` | Process flow in markdown |
| "Create a cost breakdown chart" | `python-diagrams` | Data chart |

## Decision Tree

```text
Is it a data visualization (charts, scores, metrics)?
├── YES → python-diagrams
└── NO → Does it need Azure service icons?
    ├── YES → drawio
    └── NO → Is it inline in a markdown document?
        ├── YES → mermaid
        └── NO → drawio (default)
```

## Scope Exclusions

This skill does NOT generate diagrams itself. It only routes to:
- `.github/skills/drawio/SKILL.md`
- `.github/skills/python-diagrams/SKILL.md`
- `.github/skills/mermaid/SKILL.md`
