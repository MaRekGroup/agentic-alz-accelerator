<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Azure Validate Skill (Minimal)

**When to Use** — Before Gate 5, after Step 5 Code Gen completes, to validate IaC templates.

**Validation Steps** — 7 checks: Bicep lint, Terraform validate, security baseline, cost governance, parameter completeness, AVM versions, governance blockers.

**Security Baseline** — 6 non-negotiable rules (TLS 1.2, HTTPS-only, no public blob, managed identity, Entra-only SQL, no public network in prod).

**Cost Governance** — Budget resource with 80/100/120% forecast thresholds required; amounts must be parameterized.

**Workflow** — Step 5 → azure-validate → Gate 5 → Step 6 Deploy.

**Guardrails** — Never run deployments locally; never skip security baseline; never approve Gate 5 with failures.

Read `SKILL.md` or `SKILL.digest.md` for full content.
