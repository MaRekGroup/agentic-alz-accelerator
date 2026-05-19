# Copilot Agent Skills

Domain knowledge modules that GitHub Copilot agents load on demand during workflow
execution. Each subdirectory contains a `SKILL.md` file that the Copilot runtime
auto-discovers — no separate registration step is required.

Skills differ from agents and instructions:

- **Agents** (`.github/agents/`) define personas, goals, and tool permissions
- **Instructions** (`.github/instructions/`) set per-filetype coding rules
- **Skills** (this directory) provide specialized knowledge a running agent can pull in mid-session

## How Skills Are Loaded

When an agent (e.g., Warden, Forge, Oracle) encounters a problem domain it needs
expertise in, the Copilot runtime searches this directory for a matching skill.
Skills are invoked by name in the agent's context — users do not call them directly.

The skill body (`SKILL.md`) follows a standard structure:

1. **YAML frontmatter** — `name`, `description` (≤1024 chars), `category`, `used_by`
2. **Overview** — what the skill covers, CAF/WAF alignment, when to use/not use
3. **Patterns & Guidance** — architecture patterns, decision heuristics, IaC samples
4. **Brownfield Playbook** (if applicable) — assessment and hardening steps
5. **Anti-Patterns** — common mistakes to avoid
6. **Cross-References** — related skills, ADRs, and Learn docs

## Skill Inventory

The catalog spans Azure services, governance, tooling, and assessment domains.
Categories include:

- **Core** — caf-design-areas, security-baseline, cost-governance, profile-management, workflow-engine
- **Azure & IaC** — azure-defaults, azure-bicep-patterns, terraform-patterns, azure-diagnostics, azure-rbac, azure-compliance, azure-cost-optimization, azure-quotas
- **Tooling & Operations** — python-diagrams, drawio, mermaid, azure-adr, github-operations, docs-writer
- **Governance & Context** — golden-principles, context-shredding, azure-validate, azure-governance-discovery
- **Assessment (Brownfield)** — brownfield-discovery, wara-assessment, assessment-report
- **Microsoft Learn (Azure Services)** — Governance, Security, Identity, Networking, Compute, Tenant Architecture, Data Platform, Hybrid, Management, Cost & Reliability

The full inventory with agent→skill mappings lives in
[`.github/copilot-instructions.md`](../copilot-instructions.md).

## Authoring a New Skill

1. Create `.github/skills/<skill-name>/` with a `SKILL.md` file.

2. Add YAML frontmatter at the top:

   ```yaml
   ---
   name: my-new-skill
   description: >
     Brief description (must be ≤1024 characters). Covers X, Y, Z.
   category: azure-service | governance | tooling | assessment
   used_by:
     - Oracle
     - Forge
   ---
   ```

3. Structure the body with standard sections: Overview, Patterns, Brownfield (if
   applicable), Anti-Patterns, Cross-References.

4. Validate the description length: `wc -c` on the description text must be ≤1024.

5. Place skills in category-appropriate locations:
   - Azure service skills: `azure-<service-name>/`
   - Entra ID skills: `entra-<surface>/`
   - Tooling skills: `<tool-name>/`

6. Add a row to the appropriate category table in
   [`.github/copilot-instructions.md`](../copilot-instructions.md).

## Related Documentation

- [`AGENTS.md`](../../AGENTS.md) — Agent roster, workflow steps, and the Skills section
- [`.github/copilot-instructions.md`](../copilot-instructions.md) — Full skill catalog with agent→skill mappings
- [`.github/hooks/README.md`](../hooks/README.md) — Runtime guards (distinct from skills)
