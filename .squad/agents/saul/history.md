# Saul — History

## Historical Summary (W1 through W3 — entries through 2026-05-18)

**Wave 1 (Identity, 2026-05-18):** Authored 4 SKILL.md files in parallel: entra-conditional-access (335 lines), entra-identity-governance (214 lines), entra-connect-hybrid-identity (249 lines), workload-identity-federation (240 lines). All followed azure-rbac template with YAML frontmatter, CAF/WAF tables, brownfield scenario, diagnostics, anti-patterns. Isabel quality gate: APPROVE WITH CONDITIONS (3 majors: S# codes, CAF/WAF expansion, cross-skill sequencing) → surgical closures → composite W1 brownfield path explicit in all skills.

**Wave 2 (Compute & Containers, 2026-05-18):** Authored 3 SKILL.md files: azure-kubernetes-service (338 lines, saul-4), azure-virtual-machines (301 lines, saul-5), azure-container-apps (307 lines, saul-6). All pre-emptively passed Isabel W1 compliance baseline (S# codes, ≥4 CAF/WAF rows, inline cross-skill sequencing, Prerequisites). Isabel-4 APPROVE WITH CONDITIONS (2 majors) → M1 added OpsEx WAF row to VMs, M2 added inline sequencing sentence to ACA brownfield intro.

**Wave 3 (Tenant Architecture, 2026-05-18):** Authored 2 SKILL.md files: management-group-architecture (280 lines, saul-7, S4 M&A Integration, ⛔ HARD GATE Step 3 blast-radius), subscription-vending (308 lines, saul-8, S5 ISV Multi-Tenant SaaS, 8-step playbook). Both achieved 9/9 on Isabel W2 checklist. Billing & Tenant CAF Primary for vending; Operational Excellence WAF Primary for both.

*(Earlier entries summarized 2026-05-19 by Scribe-8.)*

---

## 2026-05-18 — Wave 4 (Data Platform)

### azure-sql-database

Authored `.github/skills/azure-sql-database/SKILL.md` (306 lines, Wave 4, S3 Regulated Financial Services). 5-row CAF table (Security + Identity & Access primary); 5-row WAF table (Reliability + Security primary, OpsEx row present); Security Baseline Reinforcement table (Rules 1-6 for SQL); 5 Architecture Patterns (Failover Group, Hyperscale, Entra-Only Migration, CMK/BYOK, Managed Instance); Brownfield S3 8-step playbook with ⛔ HARD GATE Step 6 (Entra-only auth — irrevocable) + soft rollback Steps 3/4/5/7/8; 5 Hidden Assumptions; 4 Anti-Patterns; 4 KQL Diagnostic Queries; ADR cross-referenced at 4 required locations. 9/9 W2/W3 compliance self-grade.

### azure-cosmos-db

Authored `.github/skills/azure-cosmos-db/SKILL.md` (287 lines, Wave 4, S2 Multi-Region AI Platform). 5-row CAF table; 5-row WAF table (Reliability + OpsEx primary); Security Baseline Reinforcement (Rules 4/5/6); 5 Architecture Patterns (multi-region active-active writes, bounded staleness vs session, partition key design, RU provisioning, PITR backup); ⛔ HARD GATE Step 4 (consistency level change — time-windowed) and ⛔ HARD GATE Step 7 (key-based auth disable — irrevocable); 3 KQL Diagnostic Queries; ADR cross-referenced at 4 locations. 9/9 self-grade.

### azure-storage-accounts

Authored `.github/skills/azure-storage-accounts/SKILL.md` (291 lines, Wave 4, S5 ISV Multi-Tenant SaaS). 5-row CAF table; 5-row WAF table; Security Baseline Reinforcement table (all 6 rules); 9-row Decision Heuristics table; 5 Architecture Patterns with detailed gotchas (5k RBAC limit, minimum storage days, append blob incompatibility, DNS zone group, Storage Blob Delegator); ⛔ HARD GATE Steps 5 (public access — time-windowed) and 7 (shared key — irrevocable); 4 KQL Diagnostic Queries; 6 Hidden Assumptions; ADR cross-referenced at 4 locations. 9/9 self-grade.

**2026-05-18 — Saul — W4 session close** — 3 SKILL.md files authored for data tier (SQL, Cosmos, Storage) with 9 total HARD GATEs. Merged to main via PR #69. Capacity 12/14 complete.

---

## 2026-05-19 — Wave 5 (Hybrid)

### azure-arc-servers (Saul-12)

Authored `.github/skills/azure-arc-servers/SKILL.md` (323 lines, Wave 5, S6 Hybrid Estate Governance). YAML description 944 chars (≤1024 ✅); category `azure-hybrid`; wave `5`. 10-field metadata table. 5-row CAF (Management primary; Governance, Security); 4-row WAF (OpsEx primary; Security, Reliability). Security Baseline Reinforcement table. Greenfield Patterns section (4 patterns: MI-first HRW, day-0 policy, IaC AVM extension, RG tagging) given equal weight per Yeselam balanced weighting decision. Brownfield S6 8-step playbook with ⛔ HARD GATE Step 3 (credential scope — irrevocable) and ⛔ HARD GATE Step 7 (MDE extension removal — irrevocable coverage gap); Soft rollback Steps 4/5/6/8. MI-first credential default cited to ADR §5. Arc data services explicitly out of scope. ADR cross-referenced at 9 locations. 7 Learn URLs; 8 cross-skill references; 4 KQL queries; 5 hidden assumptions; 4 anti-patterns. 9/9 W4 compliance self-grade.

### azure-arc-kubernetes (Saul-13)

Authored `.github/skills/azure-arc-kubernetes/SKILL.md` (447 lines, Wave 5, S8 Brownfield K8s Fleet). YAML description 985 chars (≤1024 ✅). 6-row CAF (Platform Automation & DevOps primary + Management, Governance, Security, Identity, Network); 5-row WAF (OpsEx + Security + Reliability primary); Security Baseline Alignment table (all 6 rules); 8-step brownfield playbook with ⛔ HARD GATE Step 3 (Arc agent helm install — partially automated rollback via `az connectedk8s delete` + manual namespace/CRD cleanup) and ⛔ HARD GATE Step 7 (OIDC issuer enablement — irrevocable, pre-mutation gate); Greenfield Patterns section with Extension Sequencing table and AVM-first Bicep/Terraform code blocks; 5 Anti-Patterns; Cross-Skill References table (7 entries); 13 Learn URLs. ADR cross-referenced at 5 locations. Isabel quality gate pending (Isabel-9).

**Isabel-9 verdict (post-draft):** APPROVE WITH CONDITIONS — 2 majors (M1: arc-servers WAF missing Performance Efficiency row; M2: arc-kubernetes missing Security Baseline Alignment table in greenfield), 3 should-fixes, 2 considers. Surgical edits applied — all conditions closed. Catalog closed at 14/14.

