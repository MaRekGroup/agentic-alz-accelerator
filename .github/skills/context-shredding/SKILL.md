---
name: context-shredding
description: "Runtime context compression for agents approaching model context limits. Defines 3 compression tiers (full/summarized/minimal) with per-artifact templates. USE FOR: reducing artifact loading size at runtime, context budget management. DO NOT USE FOR: diagnostic context auditing (use context-optimizer), Azure infrastructure."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "1.0"
  category: context-management
---

# Context Shredding Skill

Runtime compression system that actively reduces context when agents approach
model limits. Agents check approximate context usage before loading artifact
files and select the appropriate compression tier.

## When to Use

- Before loading a predecessor artifact file (00 through 09)
- When conversation length suggests >60% of model context is used
- When an agent needs to load multiple large artifacts
- At Gates 2 and 4 when orchestrator recommends session breaks

## Compression Tiers

| Tier | Context Usage | Strategy |
|------|---------------|----------|
| `full` | < 60% | Load entire artifact — no compression |
| `summarized` | 60-80% | Load key H2 sections only |
| `minimal` | > 80% | Load decision summaries only (< 500 chars) |

## Action Rules

Before loading any artifact file:

1. **Estimate context usage** — count approximate conversation tokens
2. **Select tier** based on the thresholds above
3. **Apply compression template** from the tables below
4. If loading multiple artifacts, compress the older/less-critical ones first

## Tier Selection Protocol

```text
1. Estimate current context usage (rough: 1 token ≈ 4 chars)
2. Check model limit (Claude Opus: 200K, GPT-4.1: 128K)
3. Calculate usage percentage
4. Select tier:
   < 60%  → full (no compression needed)
   60-80% → summarized (key sections only)
   > 80%  → minimal (decision summaries only)
5. Load artifact/skill using the appropriate variant
```

## Skill Loading Tiers

Skills also have compression tiers (digest and minimal variants):

| Context Usage | Skill Variant | Path Pattern | Approx Tokens |
|---------------|---------------|--------------|---------------|
| < 60% | Full | `SKILL.md` | 400-800 |
| 60-80% | Digest | `SKILL.digest.md` | 150-320 |
| > 80% | Minimal | `SKILL.minimal.md` | 40-100 |

## Artifact Compression Templates

### 01-requirements.md

| Tier | Load These Sections |
|------|---------------------|
| full | Entire document |
| summarized | Overview, CAF Design Area Summary table, Complexity, IaC Tool |
| minimal | `complexity: {tier}, iac_tool: {tool}, regions: {list}, environments: {list}` |

### 02-architecture-assessment.md

| Tier | Load These Sections |
|------|---------------------|
| full | Entire document |
| summarized | WAF Scores table, Resource List, Cost Estimate, Key Decisions |
| minimal | `waf_score: {n}/100, resources: {count}, cost_monthly: ${n}, key_risks: [...]` |

### 04-governance-constraints.md/.json

| Tier | Load These Sections |
|------|---------------------|
| full | Entire document |
| summarized | Deny-effect policies, Security baseline violations, Blocker count |
| minimal | `blockers: {n}, deny_policies: {n}, baseline_violations: [...]` |

### 04-implementation-plan.md

| Tier | Load These Sections |
|------|---------------------|
| full | Entire document |
| summarized | Module List with AVM refs, Deployment Order, Parameter Strategy |
| minimal | `modules: {list}, deploy_order: [...], framework: {bicep|terraform}` |

### 00-assessment-report.md (Brownfield)

| Tier | Load These Sections |
|------|---------------------|
| full | Entire document |
| summarized | Executive Summary, WAF Scores, must_fix findings only |
| minimal | `score: {n}/100, findings: {n}, must_fix: {n}, resource_count: {n}` |

### 00-estate-state.json

| Tier | Load These Sections |
|------|---------------------|
| full | Entire JSON |
| summarized | `estate` + `platform_landing_zones` status fields only |
| minimal | `platform: {mgmt:✅, conn:✅, id:✅, sec:✅}, apps: {count}` |

## Session State via alz-recall

Instead of loading full JSON state, use `alz-recall show {customer} --json`
and extract only what's needed:

| Need | Command |
|------|---------|
| Current step | `alz-recall show {customer} --json \| jq '.session_state.current_step'` |
| Decisions only | `alz-recall show {customer} --json \| jq '.session_state.decisions'` |
| Full state | `alz-recall show {customer} --json` |

## Enterprise Landing Zone Specifics

For ALZ workflows, prioritize loading order:

1. **Always load** (never compress): Security baseline (6 rules), current step from `alz-recall`
2. **Compress first** (oldest/least critical): Assessment artifacts (Step 0), Design artifacts (Step 3)
3. **Never skip entirely**: Governance constraints (blockers affect all downstream steps)

## Session Break Recommendation

At Gates 2 and 4, if estimated context > 70%:
- Write `00-handoff.md` with all artifact paths and key decisions
- Recommend starting a fresh chat session
- New session resumes from `alz-recall show {customer} --json` — zero information loss

## Guardrails

**DO:** Check context usage before loading artifacts · Compress older artifacts first ·
Use `alz-recall` for state instead of re-reading JSON · Write handoff docs at gates.

**DON'T:** Load all 9 step artifacts at once · Skip security baseline compression ·
Compress the current step's input artifact · Ignore session break recommendations.
