---
name: count-registry
description: "Provides canonical entity counts from filesystem globs. Prevents hard-coded counts in documentation. USE FOR: agent count, skill count, entity inventory, project statistics. DO NOT USE FOR: Azure resource counts (use azure-resource-visualizer), cost data."
---

# Count Registry — Entity Count Source of Truth

Single source of truth for project entity counts in the ALZ Accelerator.
Prevents hard-coded numbers that go stale as agents and skills are added.

## Source of Truth

Counts are computed from filesystem globs — never hard-coded in prose.

| Entity | Glob Pattern | How to Count |
|---|---|---|
| Agents | `.github/agents/*.md` | `ls .github/agents/*.md \| grep -v _subagents \| wc -l` |
| Subagents | `.github/agents/_subagents/*.md` | `ls .github/agents/_subagents/*.md \| wc -l` |
| Skills | `.github/skills/*/SKILL.md` | `ls .github/skills/*/SKILL.md \| wc -l` |
| Instructions | `.github/instructions/*.md` | `ls .github/instructions/*.md \| wc -l` |
| Workflows | `.github/workflows/*.yml` | `ls .github/workflows/*.yml \| wc -l` |
| MCP Servers | `mcp/*/server.py` or `mcp/*/src/` | Count directories with server entry points |
| Validators | `scripts/validators/*.py` | `ls scripts/validators/*.py \| wc -l` |
| Platform LZs | Fixed: 4 | management, connectivity, identity, security |
| Golden Principles | Fixed: 10 | Immutable (defined in golden-principles skill) |
| Security Rules | Fixed: 6 | Immutable (defined in security-baseline skill) |
| CAF Design Areas | Fixed: 8 | Immutable (Azure CAF standard) |

## How to Reference Counts

### Preferred: Descriptive Language

When generating documentation or artifacts that mention entity quantities:

| Entity | Canonical Phrase |
|---|---|
| Agents | "specialized agents and subagents" |
| Skills | "the full skill catalog" |
| Instructions | "coding instruction files" |
| Validators | "the validation suite" |
| Workflow steps | "the multi-step workflow" (Step 3.5 makes counting ambiguous) |
| Platform LZs | "4 platform Landing Zones" (fixed, safe to state) |
| Security rules | "6 non-negotiable security rules" (fixed, safe to state) |
| CAF design areas | "all 8 CAF design areas" (fixed, safe to state) |

### When Exact Numbers Are Needed

If exact numbers are required (e.g., in a compliance report):

1. Compute from filesystem: `ls .github/skills/*/SKILL.md | wc -l`
2. State with source: "35 skills (per `.github/skills/` directory)"
3. Never hard-code into committed prose without a mechanism to update

### Fixed vs. Computed

| Type | Rule |
|---|---|
| **Fixed** (Platform LZs=4, Security Rules=6, CAF Areas=8, Golden Principles=10) | Safe to hard-code — these are architectural constants |
| **Computed** (agents, skills, instructions, workflows) | Never hard-code — always compute or use descriptive language |

## Validation

To check if documentation counts match reality:

```bash
# Quick count audit
echo "Agents: $(ls .github/agents/*.md 2>/dev/null | grep -v _subagents | wc -l)"
echo "Subagents: $(ls .github/agents/_subagents/*.md 2>/dev/null | wc -l)"
echo "Skills: $(ls .github/skills/*/SKILL.md 2>/dev/null | wc -l)"
echo "Instructions: $(ls .github/instructions/*.md 2>/dev/null | wc -l)"
echo "Workflows: $(ls .github/workflows/*.yml 2>/dev/null | wc -l)"
echo "Validators: $(ls scripts/validators/*.py 2>/dev/null | wc -l)"
```

If any documentation file references an incorrect count, update it using
the `docs-writer` skill's freshness audit workflow.

## Integration

| Skill | How It Uses count-registry |
|---|---|
| `docs-writer` | References canonical phrases when updating documentation |
| `context-optimizer` | Uses entity counts for context budget allocation |
| `golden-principles` | Principle #9: "Counts are computed, never hard-coded" |

## Constraints

- **Never** commit a file with a hard-coded computed count without automation to keep it fresh
- **Always** use descriptive language in agent definitions and skill docs
- **Fixed constants** (4 platform LZs, 6 security rules, 8 CAF areas, 10 principles) are safe
- When in doubt, use the canonical phrase from the table above
