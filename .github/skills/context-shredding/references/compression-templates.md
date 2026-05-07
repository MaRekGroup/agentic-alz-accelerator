<!-- ref:compression-templates-v1 -->

# Compression Templates

Per-artifact compression rules at each tier. H2 sections to keep/drop
and character budget targets. Adapted for ALZ accelerator artifacts (Steps 0–9).

## 00-assessment-report.md (Brownfield Only)

| Tier | Keep H2 Sections | Budget |
|------|-------------------|--------|
| full | All | No limit |
| summarized | Executive Summary, WAF Pillar Scores, must_fix findings, Resource Inventory count | ~3000 chars |
| minimal | `score: {n}/100, findings: {n}, must_fix: {n}, resources: {n}` | ~200 chars |

## 00-current-state-architecture.md (Brownfield Only)

| Tier | Keep H2 Sections | Budget |
|------|-------------------|--------|
| full | All | No limit |
| summarized | Management Group Hierarchy, Subscription Summary, Resource Counts by type | ~3000 chars |
| minimal | `mg_count: {n}, sub_count: {n}, resource_count: {n}, topology: {hub-spoke|vwan|flat}` | ~200 chars |

## 00-target-state-architecture.md (Brownfield Only)

| Tier | Keep H2 Sections | Budget |
|------|-------------------|--------|
| full | All | No limit |
| summarized | Remediation Roadmap (critical/high only), Migration Phases table | ~2000 chars |
| minimal | `critical_remediations: {n}, phases: {n}, estimated_effort: {text}` | ~200 chars |

## 00-estate-state.json

| Tier | Keep JSON Fields | Budget |
|------|------------------|--------|
| full | Entire JSON | No limit |
| summarized | `estate` (prefix, region, iac_tool) + `platform_landing_zones` (status fields only) + `application_landing_zones` (names + status) | ~1000 chars |
| minimal | `platform: {mgmt:✅, conn:✅, id:✅, sec:✅}, apps: {count}, iac: {tool}` | ~150 chars |

**Preferred**: Use `alz-recall show {customer} --json` instead of reading the file directly.

## 01-requirements.md

| Tier | Keep H2 Sections | Budget |
|------|-------------------|--------|
| full | All | No limit |
| summarized | Project Overview, CAF Design Area Summary table, Complexity Classification, IaC Tool, Environments | ~3000 chars |
| minimal | `complexity: {tier}, iac_tool: {tool}, regions: [{list}], environments: [{list}], resource_types: {n}` | ~300 chars |

## 02-architecture-assessment.md

| Tier | Keep H2 Sections | Budget |
|------|-------------------|--------|
| full | All | No limit |
| summarized | Architecture Pattern, WAF Pillar Scores, Resource Summary table, Cost Estimate, Key Decisions | ~4000 chars |
| minimal | `waf_score: {n}/100, resources: {n}, cost_monthly: ${n}, pattern: {hub-spoke|vwan}, key_risks: [...]` | ~300 chars |

## 03-design-*.md / 03-design-*.drawio

| Tier | Keep H2 Sections | Budget |
|------|-------------------|--------|
| full | All (including diagram references) | No limit |
| summarized | ADR Decision table, Architecture Diagram file paths only | ~1500 chars |
| minimal | `diagrams: [{file_list}], adr_count: {n}` | ~200 chars |

Design artifacts are among the **first to compress** — diagrams are visual
and don't carry structured data needed by downstream agents.

## 04-governance-constraints.md / .json

| Tier | Keep H2 Sections | Budget |
|------|-------------------|--------|
| full | All | No limit |
| summarized | Deny-effect policies table, Security Baseline Violations, Blocker count, DINE policies summary | ~3000 chars |
| minimal | `blockers: {n}, deny_policies: {n}, audit_policies: {n}, baseline_violations: [...]` | ~300 chars |

**Never skip entirely** — governance constraints contain blockers that
affect all downstream steps (plan, code, deploy).

## 04-implementation-plan.md

| Tier | Keep H2 Sections | Budget |
|------|-------------------|--------|
| full | All | No limit |
| summarized | Module Inventory table (with AVM refs), Deployment Order, Parameter Strategy, Dependencies | ~5000 chars |
| minimal | `modules: [{list}], deploy_order: [...], framework: {bicep|terraform}, avm_count: {n}` | ~400 chars |

## 06-deployment-summary.md

| Tier | Keep H2 Sections | Budget |
|------|-------------------|--------|
| full | All | No limit |
| summarized | Deployment Result, Resources Deployed table, Validation Results, Run IDs | ~3000 chars |
| minimal | `status: {success|failed}, resources: {n}, run_id: {id}, compliance: {n}%` | ~200 chars |

## 07-* (As-Built Documents)

As-built documents are terminal artifacts — no downstream agent loads them.
Compression is only needed when the Documentation agent loads predecessor
artifacts to generate the as-built suite.

| Tier | Keep H2 Sections | Budget |
|------|-------------------|--------|
| full | All | No limit |
| summarized | Architecture Overview, Resource Inventory, Compliance Matrix | ~4000 chars |
| minimal | `resources: {n}, compliance: {n}%, last_updated: {date}` | ~200 chars |

## 08-compliance-report.md

| Tier | Keep H2 Sections | Budget |
|------|-------------------|--------|
| full | All | No limit |
| summarized | Compliance Summary per subscription, Critical/High violations only, Drift count | ~3000 chars |
| minimal | `compliance: {n}%, violations: {critical: {n}, high: {n}}, drift: {n}` | ~200 chars |

## 09-remediation-log.md

| Tier | Keep H2 Sections | Budget |
|------|-------------------|--------|
| full | All | No limit |
| summarized | Remediation Actions table (status + strategy), Rollback inventory | ~2000 chars |
| minimal | `remediated: {n}, failed: {n}, pending: {n}, rollbacks: {n}` | ~200 chars |

## General Rules

- When compressing, preserve all **tables** within kept sections (tables are dense)
- Drop **code blocks** first (they are verbose)
- Keep **decision rationale** over implementation details
- Keep **resource names and SKUs** over configuration details
- Always preserve the document title (H1) and first paragraph
- At the `minimal` tier, prefer reading `alz-recall show {customer} --json`
  over loading full artifact prose for rationale behind prior choices

## ALZ-Specific Loading Priority

1. **Never compress** (always full): Security baseline (6 rules), current step from `alz-recall`
2. **Compress first** (oldest/least critical): Assessment artifacts (Step 0), Design artifacts (Step 3)
3. **Never skip entirely**: Governance constraints (blockers affect all downstream steps)
4. **Use CLI instead**: Estate state and session state — use `alz-recall` commands, not raw JSON files

## Session Break Protocol

At Gates 2 and 4, if estimated context > 70%:
1. Write `00-handoff.md` with all artifact paths and key decisions
2. Recommend starting a fresh chat session
3. New session resumes from `alz-recall show {customer} --json` — zero information loss
