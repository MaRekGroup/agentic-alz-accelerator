<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Context Shredding Skill (Digest)

Runtime compression system that reduces context when agents approach model
limits. Select a compression tier before loading artifacts or skills.

## Compression Tiers

| Tier | Context Usage | Strategy |
|------|---------------|----------|
| `full` | < 60% | Load entire artifact — no compression |
| `summarized` | 60-80% | Load key H2 sections only |
| `minimal` | > 80% | Load decision summaries only (< 500 chars) |

## Skill Loading Tiers

| Context Usage | Skill Variant | Path Pattern | Approx Tokens |
|---------------|---------------|--------------|---------------|
| < 60% | Full | `SKILL.md` | 400-800 |
| 60-80% | Digest | `SKILL.digest.md` | 150-320 |
| > 80% | Minimal | `SKILL.minimal.md` | 40-100 |

## Artifact Quick Reference

| Artifact | Summarized (60-80%) | Minimal (>80%) |
|----------|---------------------|----------------|
| `00-assessment-*` | Executive Summary, WAF Scores, must_fix | `score: {n}/100, must_fix: {n}` |
| `00-estate-state.json` | `estate` + LZ statuses | `platform: {status×4}, apps: {n}` |
| `01-requirements.md` | Overview, CAF table, Complexity, IaC Tool | `complexity: {tier}, iac_tool: {tool}` |
| `02-architecture-assessment.md` | WAF Scores, Resources, Cost, Decisions | `waf: {n}/100, cost: ${n}` |
| `03-design-*` | ADR table, diagram paths | `diagrams: [{paths}]` |
| `04-governance-constraints.*` | Deny policies, Baseline violations, Blockers | `blockers: {n}, deny: {n}` |
| `04-implementation-plan.md` | Modules, Deploy Order, Parameters | `modules: [{list}], framework: {tool}` |
| `06-deployment-summary.md` | Result, Resources, Validation | `status: {ok}, resources: {n}` |
| `08-compliance-report.md` | Summary, Critical/High violations | `compliance: {n}%, violations: {n}` |
| `09-remediation-log.md` | Actions table, Rollbacks | `remediated: {n}, failed: {n}` |

## ALZ Loading Priority

1. **Always load** (never compress): Security baseline (6 rules), current step from `alz-recall`
2. **Compress first**: Assessment (Step 0), Design (Step 3) artifacts
3. **Never skip entirely**: Governance constraints (blockers affect downstream)

## Session Break

At Gates 2 and 4, if context > 70%: write `00-handoff.md` with artifact paths
and key decisions, then recommend a fresh chat session. Resume via `alz-recall`.

## Guardrails

**DO:** Check context before loading · Compress oldest artifacts first · Use `alz-recall` for state · Write handoff docs at gates.

**DON'T:** Load all 9 step artifacts at once · Skip security baseline · Compress current step's input · Ignore session break recommendations.
