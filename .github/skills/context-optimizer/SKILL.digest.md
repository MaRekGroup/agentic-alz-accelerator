<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Context Optimizer Skill (Digest)

Audits agent context window usage via debug logs, token profiling, and
redundancy detection. Produces prioritized optimization reports.

## Quick Reference

| Capability | Description |
|------------|-------------|
| Log Parsing | Extract structured data from Copilot Chat debug logs |
| Turn-Cost Profiling | Estimate token spend per turn |
| Redundancy Detection | Find duplicate file reads, overlapping instructions |
| Hand-Off Gap Analysis | Identify agents that should delegate to subagents |
| Instruction Audit | Flag overly broad globs and oversized instruction files |
| Report Generation | Structured markdown report with prioritized recommendations |

## Agent Definition Audit Checklist

| Check | Pass Criteria |
|-------|---------------|
| Skills count | ≤ 5 skills per agent |
| Instruction files | ≤ 5 auto-loaded instructions |
| File reads | No duplicate reads of same file |
| Skill overlap | No two agents load identical skill sets |
| Definition size | Agent .md file < 400 lines |

## Context Growth by Step

| Step | Est. Tokens | Notes |
|------|------------|-------|
| Step 1 (Requirements) | ~15K | requirements agent + azure-defaults |
| Step 2 (Architecture) | ~25K | + 01-requirements + caf-design-areas |
| Step 3 (Design) | ~20K | + drawio/mermaid skill |
| Step 3.5 (Governance) | ~30K | + governance discovery output |
| Step 4 (Plan) | ~35K | + 02-architecture + 04-governance |
| Step 5 (Code Gen) | ~50K | + implementation plan + AVM patterns |
| Step 6 (Deploy) | ~20K | fresh context, only deploy artifacts |
| Step 7 (Docs) | ~30K | + multiple predecessor artifacts |

Session break recommendations: Gates 2 and 4.

## Common Optimization Patterns

1. **Subagent Extraction** — Extract when single-turn context > 40K tokens
2. **Instruction Narrowing** — Replace `**/*.md` with `agent-output/**/*.md`
3. **Progressive Skill Loading** — golden-principles → azure-defaults → task-specific
4. **Skill Digest Variants** — Create `SKILL.digest.md` (150-320 tokens) for heavy skills
5. **Artifact Compression** — Use `context-shredding` tiers for predecessor artifacts

> _See SKILL.md for report template and full methodology._

## Guardrails

**DO:** Audit after adding agents/skills · Create digest variants · Use context-shredding tiers · Recommend session breaks at Gates 2 and 4.

**DON'T:** Load this skill during normal workflow · Over-optimize below 40% context · Remove skills without checking agent dependencies.
