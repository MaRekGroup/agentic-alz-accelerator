---
name: docs-writer
description: "Maintains repository documentation accuracy and freshness for the ALZ accelerator. USE FOR: doc updates, agent/skill documentation changes, staleness checks, post-deployment documentation. DO NOT USE FOR: agent-output artifacts (validators handle those), IaC code generation, architecture decisions."
---

# docs-writer — Enterprise Landing Zone Documentation

Expert technical writer for the ALZ Accelerator repository. Maintains all
user-facing documentation to be accurate, current, and consistent with the
deployed estate and agent/skill inventory.

## When to Use

| Trigger | Workflow |
|---|---|
| "Update the docs" | Update existing documentation |
| "Add docs for new agent/skill" | Add entity documentation |
| "Check docs for staleness" | Freshness audit |
| "Explain how this repo works" | Architectural Q&A |
| New skill/agent added | Update copilot-instructions.md + README.md |

## Scope

### In Scope

| Path | Content |
|---|---|
| `docs/` | User-facing guides, runbooks, architecture docs |
| `README.md` | Repo root README |
| `.github/copilot-instructions.md` | Copilot project-level instructions |
| `AGENTS.md` | Agent specification and workflow |
| `docs/accelerator/` | Architecture docs, ADRs |
| `site/src/` | Published documentation site |

### Out of Scope (Governed by Other Agents/Validators)

| Path | Governed By |
|---|---|
| `agent-output/**/*.md` | Step agents (Scribe, Oracle, Chronicler) |
| `.github/agents/*.md` | Agent definitions (manual authoring) |
| `.github/skills/*/SKILL.md` | Skill definitions (manual authoring) |
| `infra/**/*.bicep` | Forge agent + bicep-patterns skill |
| `infra/**/*.tf` | Forge agent + terraform-patterns skill |

---

## Workflow 1: Update Existing Documentation

1. **Identify target files** in `docs/` or repo root
2. **Read current version** — always read before editing
3. **Apply conventions**:
   - Use `#` for title (single H1 per file)
   - Markdown tables for structured data
   - Code blocks with language identifiers
   - Relative links between docs
4. **Verify links** resolve to existing files
5. **Check consistency** with AGENTS.md and copilot-instructions.md

## Workflow 2: Add Documentation for New Entity

When a new agent or skill is added:

1. **Update `.github/copilot-instructions.md`**:
   - Add skill to appropriate table (Core, Azure & IaC, Tooling, Agent Governance)
   - Update skill location and "Used By" columns
2. **Update `AGENTS.md`** if a new agent is added:
   - Add to Agent Roster table
   - Update workflow diagram if step order changes
3. **Update `README.md`** if the addition is user-facing
4. **Use descriptive language** for counts — avoid hard-coding numbers:
   - Good: "the full skill catalog"
   - Bad: "30 skills" (will go stale)

## Workflow 3: Freshness Audit

Check these targets for staleness:

| Target | Validation |
|---|---|
| Agent count in docs | `ls .github/agents/*.md \| wc -l` matches prose |
| Skill count in docs | `ls .github/skills/*/SKILL.md \| wc -l` matches prose |
| Skill tables | Every skill directory has a row in copilot-instructions.md |
| Agent registry | Every agent in registry has a `.md` definition file |
| Platform LZ status | Matches actual deployment state |
| Workflow file references | All referenced `.yml` files exist |
| Link targets | All relative links resolve |

### Auto-Fix Rules

- Missing skill in table → add row with skill name, location, and agent mapping
- Count mismatch → update to descriptive language or correct number
- Dead link → search for moved file, update path
- Stale platform status → update from `alz-recall show {customer} --json`

## Workflow 4: Post-Deployment Documentation (Step 7 Support)

The Chronicler agent produces Step 7 artifacts. This skill supports by ensuring
the `docs/` folder stays aligned:

1. **Platform deployment runbook** (`docs/platform-deployment-runbook.md`) — update with latest deployment sequence
2. **Architecture diagram** (`docs/accelerator/architecture-diagram.mmd`) — regenerate if topology changed
3. **Quickstart** (`docs/quickstart.md`) — verify commands still work

---

## Documentation Standards

### File Naming

| Type | Pattern | Example |
|---|---|---|
| Guide | `{topic}.md` | `quickstart.md` |
| Runbook | `{scope}-{purpose}-runbook.md` | `platform-deployment-runbook.md` |
| Architecture | `architecture.md` or `target-architecture.md` | `docs/accelerator/architecture.md` |
| ADR | `ADR-{NNN}-{title}.md` | `ADR-001-hub-spoke-topology.md` |

### Content Conventions

- **No hardcoded counts** — use descriptive language or reference `agent-registry.json`
- **CAF terminology** — use official Azure CAF terms (Landing Zone, not "landing zone")
- **Prefix placeholder** — use `{prefix}` not actual prefix in example commands
- **Region placeholder** — use `{region}` or note "configurable via AZURE_DEPLOYMENT_REGION"
- **Required tags** documented: Environment, Owner, CostCenter, Project, ManagedBy

### Cross-Reference Pattern

When referencing other docs:
```markdown
See [Platform Landing Zones](docs/platform-landing-zones.md) for deployment order.
See [Security Baseline](docs/security-baseline.md) for the 6 non-negotiable rules.
```

---

## Integration with Agents

| Agent | Documentation Role |
|---|---|
| Chronicler (Step 7) | Produces as-built docs, TDD, runbooks |
| Orchestrator | References docs in handoff documents |
| Requirements (Step 1) | Links to quickstart for setup guidance |
| This skill | Keeps `docs/` folder fresh and consistent |

---

## Guardrails

- **Never modify** files in `agent-output/` (those are step artifacts)
- **Never modify** `.github/agents/*.md` (agent definitions are manually authored)
- **Always read** the latest file version before editing
- **Preserve** existing Mermaid diagrams unless regenerating
- **Match** the existing style of adjacent content when adding new sections
