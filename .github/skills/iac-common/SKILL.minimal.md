<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# IaC Common Skill (Minimal)

**Module Organization** — Both Bicep and Terraform use matching module directories per CAF design area with environment-specific parameter files.

**Parameter Strategy** — Environment differentiation table covers budget, SKUs, network access, and retention; never commit secrets.

**Deployment Order** — 10-step sequence from management groups through landing zone subscriptions.

**AVM Module Selection** — Always check AVM registry before writing native resources.

**Validation Checklist** — 7-item pre-PR checklist covering security, budgets, diagnostics, naming, tags, AVM, and secrets.

Read `SKILL.md` or `SKILL.digest.md` for full content.
