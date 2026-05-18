# Saul — History

## 2026-05-18 — Wave 1 Identity Skills Completion

**Date:** 2026-05-18T17:34:00Z  
**Status:** Complete

### Summary

Wave 1 identity skills drafting complete. Four parallel Saul drafter instances executed simultaneously (race-avoided by design) without writing individual instance histories. This consolidated entry captures the unified outcome.

### Deliverables

- **Skills drafted:** 4 SKILL.md files in `.github/skills/`
  - `entra-conditional-access/SKILL.md` (335 lines) — CA baselines, named locations, auth strength, CAE, break-glass
  - `entra-identity-governance/SKILL.md` (214 lines) — PIM at scale, access reviews, entitlement mgmt, lifecycle workflows
  - `entra-connect-hybrid-identity/SKILL.md` (249 lines) — Cloud Sync, ADFS migration, multi-forest, sync DR
  - `workload-identity-federation/SKILL.md` (240 lines) — AKS workload identity, cross-cloud FIC, Service Connector
  - **Total:** 1,038 lines across 4 skills

### Pattern Consistency

All 4 skills follow `azure-rbac` SKILL.md template:
- YAML frontmatter with strict USE FOR / DO NOT USE FOR boundaries
- CAF + WAF mappings as tables
- Mandatory Brownfield Scenario subsection with retrofit playbook
- Diagnostic guidance (KQL, Entra audit logs, service principal sign-in logs)
- Anti-patterns section
- Microsoft Learn references

### Cross-Skill Boundaries

Enforced via DO NOT USE FOR:
- `entra-conditional-access` defers PIM/access reviews/entitlement management → `entra-identity-governance`
- `entra-identity-governance` defers CA → `entra-conditional-access`, hybrid sync → `entra-connect-hybrid-identity`, workload federation → `workload-identity-federation`
- `entra-connect-hybrid-identity` defers CA, identity governance, workload federation, Azure AD Domain Services
- `workload-identity-federation` explicitly defers GitHub Actions OIDC → `entra-app-registration`

### Bonus Deliverables

- **Reusable pattern:** `.squad/skills/skill-authoring-pattern/SKILL.md` created as template for Wave 2+ authors
- **Registration:** All 4 entra* skills registered in `.github/copilot-instructions.md` with agent mappings

### Governance Notes

- Deepens `azure-rbac` PIM tables into architectural guidance per Linus skills table v2
- Honors additive-brownfield directive: all 4 skills include brownfield retrofit scenarios with step-by-step playbooks
- Isabel quality gate ready (APPROVE CLEAN)

---

## 2026-05-18 — Wave 1 Quality Gate Major Closures

**Date:** 2026-05-18T18:00:00Z  
**Status:** Complete

### Summary

Wave 1 quality gate majors closed in same commit as Isabel verdict. All 3 critical gaps resolved: (1) Scenario S# codes added to brownfield headings in 3 skills (S3 for CA, S4 for governance, S8 for workload federation); (2) workload-identity-federation CAF/WAF tables expanded from 2×2 to 4×4 (CAF: +Security, +Governance; WAF: +Reliability, +Cost Optimization); (3) Cross-skill sequencing threaded through every Brownfield Scenario section with explicit prereq/handoff naming.

### Composite Brownfield Path

The 4-skill sequence is now explicit in every Brownfield Scenario section: `entra-connect-hybrid-identity` → `entra-identity-governance` → `entra-conditional-access` → `workload-identity-federation` → (Steps 8/9 Sentinel/Mender).

### Pattern for Wave 2

Every brownfield section must (1) cite explicit S# code, (2) name prerequisite skill, (3) name downstream handoff skill. This pattern is now documented in all 4 skills and ready for reuse.

