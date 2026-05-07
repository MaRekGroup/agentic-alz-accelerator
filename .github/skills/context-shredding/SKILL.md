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

Detailed per-artifact compression rules with H2 sections to keep/drop and
character budget targets are in the reference doc:

| Reference | File | Content |
|-----------|------|---------|
| Compression Templates | `references/compression-templates.md` | Per-artifact H2 sections per tier for all 10 ALZ artifacts (00–09) |

### Quick Reference (Inline)

| Artifact | Summarized (60-80%) | Minimal (>80%) |
|----------|---------------------|----------------|
| `00-assessment-*` | Executive Summary, WAF Scores, must_fix findings | `score: {n}/100, must_fix: {n}` |
| `00-estate-state.json` | `estate` + LZ statuses | `platform: {status×4}, apps: {n}` |
| `01-requirements.md` | Overview, CAF table, Complexity, IaC Tool | `complexity: {tier}, iac_tool: {tool}` |
| `02-architecture-assessment.md` | WAF Scores, Resources, Cost, Decisions | `waf: {n}/100, cost: ${n}` |
| `03-design-*` | ADR table, diagram paths | `diagrams: [{paths}]` |
| `04-governance-constraints.*` | Deny policies, Baseline violations, Blockers | `blockers: {n}, deny: {n}` |
| `04-implementation-plan.md` | Modules, Deploy Order, Parameters | `modules: [{list}], framework: {tool}` |
| `06-deployment-summary.md` | Result, Resources, Validation | `status: {ok}, resources: {n}` |
| `08-compliance-report.md` | Summary, Critical/High violations | `compliance: {n}%, violations: {n}` |
| `09-remediation-log.md` | Actions table, Rollbacks | `remediated: {n}, failed: {n}` |

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
