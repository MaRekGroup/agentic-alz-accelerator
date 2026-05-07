<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Count Registry Skill (Digest)

Single source of truth for project entity counts. Prevents hard-coded numbers
that go stale as agents and skills are added.

## Source of Truth

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
| Golden Principles | Fixed: 10 | Immutable |
| Security Rules | Fixed: 6 | Immutable |
| CAF Design Areas | Fixed: 8 | Immutable |

## Canonical Phrases (Preferred)

| Entity | Canonical Phrase |
|---|---|
| Agents | "specialized agents and subagents" |
| Skills | "the full skill catalog" |
| Instructions | "coding instruction files" |
| Platform LZs | "4 platform Landing Zones" (fixed, safe) |
| Security rules | "6 non-negotiable security rules" (fixed, safe) |
| CAF design areas | "all 8 CAF design areas" (fixed, safe) |

## Fixed vs. Computed

| Type | Rule |
|---|---|
| **Fixed** (Platform LZs=4, Security Rules=6, CAF Areas=8, Principles=10) | Safe to hard-code |
| **Computed** (agents, skills, instructions, workflows) | Never hard-code — compute or use descriptive language |

## Validation

```bash
echo "Agents: $(ls .github/agents/*.md 2>/dev/null | grep -v _subagents | wc -l)"
echo "Skills: $(ls .github/skills/*/SKILL.md 2>/dev/null | wc -l)"
echo "Workflows: $(ls .github/workflows/*.yml 2>/dev/null | wc -l)"
```
