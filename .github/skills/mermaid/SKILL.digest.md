<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Mermaid Diagrams Skill (Digest)

Generate Mermaid diagrams embedded in markdown fences for inline documentation.

## When to Use / Not Use

| Use Mermaid For | Use Instead |
|-----------------|-------------|
| Inline markdown diagrams, flowcharts, sequences, Gantt, state, ER | — |
| Architecture diagrams with Azure icons | `drawio` |
| WAF/cost charts | `python-diagrams` |
| Standalone diagrams for external use | `drawio` |

## Syntax Quick Reference

| Diagram Type | Directive | Use Case |
|-------------|-----------|----------|
| Flowchart (vertical) | `graph TB` | Workflow runbooks, MG hierarchy |
| Flowchart (horizontal) | `graph LR` | APEX workflow, pipelines |
| Sequence | `sequenceDiagram` | Auth flows, API interactions |
| Gantt | `gantt` | Deployment schedules |
| State | `stateDiagram-v2` | Landing zone lifecycle |
| ER | `erDiagram` | Resource relationships |

> _See SKILL.md for full syntax examples and ALZ-specific patterns._

## ALZ-Specific Patterns

Pre-built patterns available: Management Group Hierarchy (`graph TB` with `mrg-` prefix nodes), APEX Workflow (Steps 1–7 horizontal), and Deployment Pipeline (validate → what-if → gate → deploy → verify).

## Theming

Use `%%{init: {'theme': 'base', 'themeVariables': {...}}}%%` for dark-mode-compatible rendering. Use `classDef` for consistent node styling with `fill`, `stroke`, and `rx/ry` for rounded corners.

## Guardrails

**DO:** Use fenced code blocks with `mermaid` tag · Include theme directives · Use subgraphs for grouping · Use descriptive connection labels.

**DON'T:** Use for WAF/cost charts · Use for Azure icon diagrams · Create diagrams with >30 nodes · Omit theme directives.
