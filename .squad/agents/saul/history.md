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

---

## 2026-05-18 (Wave 2): Compute & Containers — 3 parallel SKILL.md drafts

Authored 3 SKILL.md files in parallel under Wave 2 (Compute & Containers theme):
- azure-kubernetes-service (saul-4, 338 lines, 6 CAF / 5 WAF rows — exceeds floor)
- azure-virtual-machines (saul-5, 301 lines, 4 CAF / 4 WAF — Identity & Access added per Isabel M1)
- azure-container-apps (saul-6, 307 lines, 4 CAF / 4 WAF — ADR-anchored at 3 reference points)

All 3 pre-emptively passed Isabel compliance baseline: Scenario S# code in brownfield headline (S8/S3/S8), ≥4 CAF / ≥4 WAF rows, cross-skill sequencing sentence (verbatim per plan), Prerequisites subsection covering 5 hidden assumptions. Boundary discipline: each defers to ADR `docs/decisions/compute-tier-selection.md` for tier selection rather than redefining inline.

Lesson: Pre-emptive compliance baking eliminates the post-draft major-closure cycle. The Wave 1 pattern was "draft → Isabel finds 3 majors → surgical close." Wave 2 pattern is "plan codifies compliance → drafts pass first-time." Will validate at Isabel Wave 2 quality gate next.


## 2026-05-18 — Wave 3 Skill: management-group-architecture

**Date:** 2026-05-18T00:00:00Z
**Status:** Complete
**Requested by:** Coordinator (Wave 3 parallel authoring)

### Deliverable

- **File:** `.github/skills/management-group-architecture/SKILL.md`
- **Line count:** 280 lines
- **Sections:** 13 H2 sections + 11 H3 subsections (27 headers total)

### Isabel W2 Checklist Self-Grade (9 items)

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Skill ID and Domain in header table | ✅ PASS | Header table row 1-2: `management-group-architecture`, `Azure Governance / Resource Organization` |
| 2 | Brownfield Scenario in header table (S4) | ✅ PASS | Header table: `S4 — Brownfield M&A Integration` |
| 3 | Hard + Soft prereqs in header table | ✅ PASS | Hard: `azure-policy`; Soft: `azure-rbac`, `caf-design-areas` |
| 4 | CAF Design Area Mapping table ≥4 rows including Identity & Access | ✅ PASS | 5 rows: Resource Organization, Governance, Security, Identity & Access, Platform Automation & DevOps |
| 5 | WAF Pillar Coverage table ≥4 rows including Operational Excellence | ✅ PASS | 4 rows: Security, Operational Excellence, Reliability, Cost Optimization |
| 6 | Boundaries explicitly cross-references ADR + sibling Wave 3 skill | ✅ PASS | First two bullets: ADR link + `subscription-vending` SKILL.md |
| 7 | H2 format for `## Brownfield Scenario (Scenario S4: ...)` | ✅ PASS | Line is `## Brownfield Scenario (Scenario S4: Brownfield M&A Integration)` |
| 8 | Cross-skill sequencing INLINE in brownfield intro paragraph, NOT in trailing H3 | ✅ PASS | Second sentence of intro paragraph, before the playbook H3 |
| 9 | Step 3 uses `⛔ HARD GATE` prefix; Steps 4-8 use "Soft rollback" annotation | ✅ PASS | Step 3 verbatim per plan; Steps 4-8 all annotated `*Soft rollback: ...*` |

### ADR Cross-References Audit

- Overview boundary sentence: ✅ references ADR (relative path)
- Boundaries DO NOT USE FOR: ✅ first bullet with link
- Brownfield intro paragraph: ✅ references ADR for salvageable-vs-rebuild criteria
- References table: ✅ first row with relative path link

### Key Architectural Decisions

- S4 (M&A Integration) confirmed as primary brownfield scenario
- Transitional MG branch pattern (`LZ-Acquired-{Name}`) as operational bridge during integration
- ⛔ HARD GATE at blast-radius >5% aligns with ADR Brownfield Assessment Lens criteria
- Diagnostic KQL queries added for: root-parked subscriptions, subscription-scope policy overrides, hierarchy depth per subscription

---

## 2026-05-18 — Wave 3 Skill: subscription-vending

**File created:** `.github/skills/subscription-vending/SKILL.md`
**Line count:** 308
**Total sections:** 16 (Overview, When to Use, CAF Mapping, WAF Coverage, Boundaries, Architecture Patterns, Security Baseline Reinforcement, Decision Heuristics, Brownfield Scenario, Prerequisites & Caveats, Hidden Assumptions, Anti-Patterns, Diagnostic Queries, References, Revision History)

### W2 9-Item Checklist Self-Grade

| # | Item | Status | Notes |
|---|------|--------|-------|
| 1 | Skill ID and Domain in header table | ✅ PASS | `subscription-vending` / `Azure Landing Zone — Platform Automation & Billing` |
| 2 | Brownfield Scenario in header table | ✅ PASS | `S5 — ISV Multi-Tenant SaaS` |
| 3 | Hard + Soft prereqs in header table | ✅ PASS | Hard: `azure-resource-manager`, `azure-policy` / Soft: `management-group-architecture`, `workload-identity-federation` |
| 4 | CAF table ≥4 rows, Billing & Tenant Primary | ✅ PASS | 5 rows; Billing & Tenant marked `**Primary**` |
| 5 | WAF table ≥4 rows, Operational Excellence Primary | ✅ PASS | 4 rows; Operational Excellence marked `**Primary**` |
| 6 | Boundaries cross-refs ADR + sibling skill | ✅ PASS | First DO NOT USE FOR bullet → ADR link; second bullet → `management-group-architecture` SKILL.md |
| 7 | H2 format for Brownfield Scenario heading | ✅ PASS | `## Brownfield Scenario (Scenario S5: ISV Multi-Tenant SaaS)` — not bold |
| 8 | Cross-skill sequencing INLINE in brownfield intro | ✅ PASS | Sentence embedded in same paragraph as scenario description, no trailing H3 |
| 9 | 5 concrete hidden assumptions | ✅ PASS | EA owner model, 202 eventual consistency, 2000-subscription limit, RP registration timing, cancellation ≠ deletion |

**Overall: 9/9 — CLEAN PASS**

### Key Decisions

- EA→MCA migration explicitly DEFERRED per Yeselam Q2 — mentioned only in Boundaries and Prerequisites as prerequisite caveat
- S5 (ISV Multi-Tenant SaaS) as primary brownfield scenario — 8-step playbook with rollback gates per each step
- Security Baseline Reinforcement table added showing how all 6 rules are enforced at subscription creation
- Diagnostic Queries section added (4 KQL queries): root-parked subscriptions, missing mandatory tags, missing budget resources, cancelled-but-not-deleted subscriptions
- Prerequisites & Caveats table added (separate from Hidden Assumptions) covering EA/MCA, billing scope perms, Global Admin elevation, AVM version pinning, Blueprint deprecation

## 2026-05-18 — Wave 3 (Tenant Architecture)
- Saul-7 (sonnet-4.6): Authored `.github/skills/management-group-architecture/SKILL.md` (280 lines, 9/9 PASS on Isabel W2 checklist). S4 Brownfield M&A Integration; 8-step playbook with ⛔ HARD GATE at Step 3, Soft rollback on Steps 4-8.
- Saul-8 (sonnet-4.6): Authored `.github/skills/subscription-vending/SKILL.md` (308 lines, 9/9 PASS on Isabel W2 checklist). S5 ISV Multi-Tenant SaaS; 8-step playbook; Billing & Tenant CAF Primary; Operational Excellence WAF Primary.

## Learnings

### 2026-05-18 — Wave 4: azure-sql-database SKILL.md

Authored `.github/skills/azure-sql-database/SKILL.md` (306 lines, Wave 4, S3 Regulated Financial Services). Key structural choices: frontmatter + H1 + metadata table pattern from W3 gold standard; 5-row CAF table (Security ✅ + Identity & Access ✅ primary); 5-row WAF table (Reliability ✅ + Security ✅ primary); Operational Excellence WAF row present (W2 M1); Security Baseline Reinforcement table covering Rules 1-6 for SQL; Decision Heuristics table for tier/tier decision routing; 5 Architecture Patterns (Failover Group, Hyperscale, Entra-Only Migration, CMK/BYOK, Managed Instance); Brownfield S3 8-step playbook with ⛔ HARD GATE Step 6 + soft rollback on Steps 3/4/5/7/8 (W3 M2); Pre-Step-6 Verification Checklist; Prerequisites and Caveats table (7 rows); 5 Hidden Assumptions; 4 Anti-Patterns (### headers + Corrective action subparagraphs, W3 pattern); 4 KQL Diagnostic Queries; References with ADR cross-reference in 4 required locations (Overview, Boundaries, Brownfield intro, References). 9/9 W2/W3 compliance checklist passed. Sibling files authored concurrently by parallel Saul instances: azure-cosmos-db and azure-storage-accounts (no file conflicts).

### 2026-07-14 — Wave 4: azure-storage-accounts SKILL.md

Authored `.github/skills/azure-storage-accounts/SKILL.md` (291 lines, Wave 4, S5 ISV Multi-Tenant SaaS). Key structural choices: 5-row CAF table (Security ✅ + Identity & Access ✅ primary); 5-row WAF table (Reliability ✅ + Security ✅ primary, Operational Excellence present but NOT marked primary per plan spec); Security Baseline Reinforcement table covering all 6 rules for storage; Decision Heuristics table (9 rows); 5 Architecture Patterns (multi-tenant blob isolation, lifecycle management, immutability, private endpoint topology, shared-key-to-Entra-RBAC migration) with detailed gotchas (5k RBAC limit, minimum storage days, append blob incompatibility, DNS zone group requirement, Storage Blob Delegator role, Storage Explorer lockout); Brownfield S5 8-step playbook with ⛔ HARD GATE Steps 5 (public access disable — time-windowed rollback) and 7 (shared key disable — irrevocable), Soft rollback Steps 3/4/6/8; Pre-HARD-GATE checklist inline; 4 KQL Diagnostic Queries (public access violations, shared key enabled, missing private endpoints, HNS/SFTP/NFS feature lock-in inventory); 6 Hidden Assumptions (incl. HNS/SFTP/NFS W4 feature-gating hook); 4 Anti-Patterns (paragraph form, no ### headers); shared ADR `data-tier-selection.md` cross-referenced in exactly 4 locations (Overview, Boundaries, Brownfield intro, References). 9/9 W2/W3 compliance checklist passed.

### 2026-05-18 — Wave 4: azure-cosmos-db SKILL.md

Authored `.github/skills/azure-cosmos-db/SKILL.md` (287 lines, Wave 4, S2 Multi-Region AI Platform). Key structural choices: YAML frontmatter + H1 + metadata table (W3 pattern); 5-row CAF table (Security ✅ + Identity & Access ✅ present, W2 M1); 5-row WAF table (Reliability ✅ + Operational Excellence ✅ present, W2 M1); Security Baseline Reinforcement section (Rules 4/5/6 — managed identity, Entra-only auth, public network disable); 5 Architecture Patterns (multi-region active-active writes, bounded staleness vs session, partition key design, RU provisioning with W4 hook for database-shared vs container-dedicated, PITR continuous backup); 3 KQL Diagnostic Queries (multi-region write disabled, RU throttling by partition, autoscale cost optimization); Brownfield S2 8-step playbook with ⛔ HARD GATE Step 4 (consistency level change — Time-windowed) and ⛔ HARD GATE Step 7 (key-based auth disable — Irrevocable), Soft rollback on Steps 3/5/6/8; Prerequisites & Caveats table (6 rows); 5 Hidden Assumptions; 4 Anti-Patterns (paragraph form); shared ADR `docs/decisions/data-tier-selection.md` cross-referenced in 4 locations (Overview, When to Use, Boundaries, References + brownfield intro). 9/9 W2/W3 compliance checklist passed. Sibling files authored concurrently: azure-sql-database (Saul-7) and azure-storage-accounts (Saul-9).

**2026-05-18 — Saul — W4 session close** — 3 SKILL.md files authored for data tier (SQL, Cosmos, Storage) with comprehensive brownfield scenarios S3/S2/S5, CAF/WAF tables, prerequisites, and 9 total HARD GATEs. Merged to main via PR #69. W4 capacity 12/14 complete.

## 2026-05-19 — Wave 5 (Hybrid): azure-arc-servers SKILL.md

Authored `.github/skills/azure-arc-servers/SKILL.md` (323 lines, Wave 5, S6 Hybrid Estate Governance) as Saul-12. YAML description 944 chars (≤1024 hard limit ✅); category `azure-hybrid`; wave `5`. 10-field metadata table: Skill ID, Domain, Wave, Hard Prereqs (`azure-policy`), Soft Prereqs (`azure-monitor`, `azure-defender-for-cloud`, `workload-identity-federation`), Shared ADR (`hybrid-onboarding-strategy.md`), Primary CAF Area (Management primary; Governance, Security), Primary WAF Pillar (Operational Excellence primary; Security, Reliability), Brownfield Scenario S6, Authored. Brownfield 8-step playbook with ⛔ HARD GATE Step 3 (credential scope — irrevocable) and ⛔ HARD GATE Step 7 (MDE extension removal — irrevocable coverage gap); Soft rollback Steps 4/5/6/8. Greenfield section (4 patterns: MI-first HRW, day-0 policy, IaC AVM extension, RG tagging) given equal weight per Yeselam's balanced weighting decision. MI-first credential default cited to ADR §5 (not independently defined). Arc data services explicitly out of scope per ADR §1. ADR cross-referenced at 9 locations (exceeds 4-location minimum). 7 Microsoft Learn URLs, 8 cross-skill references, 5 CAF rows, 4 WAF rows, 4 KQL diagnostic queries, 6 prerequisites, 5 hidden assumptions, 4 anti-pattern paragraphs. 9/9 W4 compliance self-grade. Sister dispatch Saul-13 authors azure-arc-kubernetes concurrently.

**2026-05-19 — Saul-13 — W5 azure-arc-kubernetes SKILL.md** — Authored `.github/skills/azure-arc-kubernetes/SKILL.md` (447 lines, Wave 5, S8 Brownfield K8s Fleet). YAML description 985 chars (≤1024 ✅). 6-row CAF table (Platform Automation & DevOps ✅ primary + Management, Governance, Security, Identity, Network); 5-row WAF table (Operational Excellence ✅ + Security ✅ + Reliability ✅ primary); Security Baseline Alignment table (all 6 rules); 8-step brownfield playbook with ⛔ HARD GATE Step 3 (Arc agent helm install — partially automated rollback via `az connectedk8s delete` + manual namespace/CRD cleanup) and ⛔ HARD GATE Step 7 (OIDC issuer enablement — irrevocable, positioned as pre-mutation gate with rollback = full cluster re-enrollment); Greenfield Patterns section with Extension Sequencing table and AVM-first native Bicep/Terraform code blocks; 5 Anti-Patterns (paragraph form per W4 convention); Cross-Skill References table (7 entries including ADR); 13 Microsoft Learn URLs. Linus-8 ADR (`docs/decisions/hybrid-onboarding-strategy.md`) cross-referenced in 5 locations (Overview, When to Use, brownfield intro, Security Baseline Rule 4, Cross-Skill References). Awaits Isabel quality gate; not committed.
