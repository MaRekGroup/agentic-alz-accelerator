---
name: "step-output-contracts"
description: "How to stabilize workflow contracts between agent definitions and step prompts"
domain: "workflow-documentation"
confidence: "high"
source: "earned"
---

## Context

Use this pattern when one workflow step depends on artifacts from earlier steps and the contract has started to drift across agent definitions, prompts, and handoff expectations.

## Patterns

- Define a single canonical output manifest with exact file names and paths in both the agent definition and the step prompt
- State which artifact is canonical when multiple legacy names exist
- Document fallback behavior for optional upstream steps so downstream outputs never reference missing artifacts silently
- Separate **deployed-state evidence** from **artifact-derived context**
- Require explicit evidence-gap labeling instead of implying live validation that did not happen

## Examples

- Step 7 documentation contract:
  - Path: `agent-output/{customer}/deliverables/`
  - Files: `07-technical-design-document.md`, `07-operational-runbook.md`, `07-resource-inventory.md`, `07-compliance-summary.md`, `07-cost-baseline.md`
  - Fallback: if Step 3 is skipped, say so and generate an inline Mermaid diagram from Step 2 plus Step 6 artifacts

## Anti-Patterns

- Letting prompts and agent definitions describe different file sets
- Referring to optional upstream diagrams as if they always exist
- Claiming live-state verification when the step only read prior artifacts
