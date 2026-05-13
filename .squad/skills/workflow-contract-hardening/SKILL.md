---
name: "workflow-contract-hardening"
description: "Make shared workflow contracts explicit when optional steps and downstream artifact handoffs exist"
domain: "workflow"
confidence: "high"
source: "earned"
---

## Context

Use this pattern when a shared workflow step can be skipped, retried, or partially completed and downstream agents depend on its artifacts.

## Patterns

- Tie optionality to an explicit condition such as complexity tier. Never rely on an implied skip.
- Record step disposition in session state with explicit status values instead of inferring state from missing files.
- Add a post-step validation checkpoint before any downstream gate or consumer uses the artifacts.
- Keep shared-doc artifact naming prefix-based unless a stronger canonical basename is already approved in the decisions ledger.

## Examples

- Step 3 design: Simple may skip; Standard and Complex must complete.
- `step_3_status`: `skipped`, `completed`, `failed`
- Post-Step-3 validation blocks Step 3.5 and Gate 3 until the expected `03-*` artifacts are complete.
- Post-Step-7 validation blocks Step 8 until required `07-*.md` artifacts are complete.

## Anti-Patterns

- Detecting skipped work by checking whether files exist
- Letting downstream agents consume partial artifact sets
- Mixing prefix-based naming rules with undocumented single-file assumptions
