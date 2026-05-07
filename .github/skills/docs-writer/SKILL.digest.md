<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Docs Writer Skill (Digest)

Expert technical writer for the ALZ Accelerator. Maintains user-facing
documentation to be accurate, current, and consistent.

## When to Use

| Trigger | Workflow |
|---|---|
| "Update the docs" | Update existing documentation |
| "Add docs for new agent/skill" | Add entity documentation |
| "Check docs for staleness" | Freshness audit |
| New skill/agent added | Update copilot-instructions.md + README.md |

## Scope

| In Scope | Out of Scope |
|---|---|
| `docs/`, `README.md`, `.github/copilot-instructions.md`, `AGENTS.md`, `site/src/` | `agent-output/**` (step agents), `.github/agents/*.md` (manual), `infra/**` (Forge) |

## Workflows

1. **Update Docs** — Read current version, apply conventions, verify links, check consistency with AGENTS.md
2. **Add Entity Docs** — Update copilot-instructions.md skill table, AGENTS.md agent roster, README.md
3. **Freshness Audit** — Validate agent/skill counts, skill tables, link targets, platform LZ status
4. **Post-Deployment** (Step 7 support) — Update runbook, architecture diagram, quickstart

## Freshness Audit Checklist

| Target | Validation |
|---|---|
| Agent/skill count in docs | Matches filesystem count |
| Skill tables | Every skill directory has a row in copilot-instructions.md |
| Workflow file references | All referenced `.yml` files exist |
| Link targets | All relative links resolve |

## Documentation Standards

| Convention | Rule |
|---|---|
| Counts | Use descriptive language, never hard-code computed counts |
| Naming | CAF terminology, `{prefix}` and `{region}` placeholders |
| Required tags | Environment, Owner, CostCenter, Project, ManagedBy |
| File naming | `{topic}.md`, `{scope}-{purpose}-runbook.md`, `ADR-{NNN}-{title}.md` |

## Guardrails

**DO:** Always read before editing · Use descriptive language for counts · Match adjacent style.

**DON'T:** Modify `agent-output/` · Modify `.github/agents/*.md` · Hard-code computed counts.
