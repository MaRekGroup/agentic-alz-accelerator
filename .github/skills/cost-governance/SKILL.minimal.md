<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Cost Governance Skill (Minimal)

**Core Rule** — No budget resource, no merge; every deployment needs `Microsoft.Consumption/budgets`.

**Required Alerts** — Forecast thresholds at 80%, 100%, and 120% with email + action group notifications.

**Validation** — 6 rules (COST-001 through COST-004); budget amounts must be parameterized, never hardcoded.

**Per-Environment** — Budget amounts parameterized: Dev $500–$2K, Staging $2K–$5K, Prod $5K–$50K+.

**Validator** — `python scripts/validators/validate_cost_governance.py infra/`

Read `SKILL.md` or `SKILL.digest.md` for full content.
