<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Security Baseline Skill (Minimal)

**Core Rules** — 6 non-negotiable rules: TLS 1.2, HTTPS-only, no public blob, managed identity, Azure AD-only SQL, public network disabled (prod).

**Extended Anti-Pattern Checks** — 7 additional checks for Redis SSL, FTPS, remote debugging, Cosmos auth, PostgreSQL SSL, Key Vault network, and CORS wildcards.

**Enforcement Points** — Enforced at 5 stages: code gen, deploy preflight, pre-commit hook, CI pipeline, and continuous monitoring.

**Validator** — Run `python scripts/validators/validate_security_baseline.py infra/`.

Read `SKILL.md` or `SKILL.digest.md` for full content.
