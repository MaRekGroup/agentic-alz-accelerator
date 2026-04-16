# Copilot Instructions — Agentic ALZ Accelerator

> Project-level instructions auto-loaded by GitHub Copilot for every session.
> For the full AGENTS.md spec, see the repo root.

## Quick Start

This repo implements a multi-agent APEX workflow that turns Azure Landing Zone
requirements into deployed, governed, and continuously monitored infrastructure —
aligned with all 8 CAF design areas.

Enable subagents: In VS Code Copilot Chat, prefix with `@workspace` and use
the agent names below (e.g., `@requirements`, `@governance`, `@orchestrator`).

## Multi-Step Workflow

| Step | Agent | Codename | Artifact |
|------|-------|----------|----------|
| 1 | `requirements` | 📜 Scribe | `01-requirements.md` |
| 2 | `architect` | 🏛️ Oracle | `02-architecture-assessment.md` |
| 3 | `design` | 🎨 Artisan | `03-design-*.{drawio,png,md}` |
| 3.5 | `governance` | 🛡️ Warden | `04-governance-constraints.md/.json` |
| 4 | `iac-planner` | 📐 Strategist | `04-implementation-plan.md` |
| 5 | `bicep-code` / `terraform-code` | ⚒️ Forge | `infra/{bicep,terraform}/{project}/` |
| 6 | `deploy` | 🚀 Envoy | `06-deployment-summary.md` |
| 7 | `documentation` | 📚 Chronicler | `07-*.md` |
| 8 | `monitor` | 🔭 Sentinel | `08-compliance-report.md` |
| 9 | `remediate` | 🔧 Mender | `09-remediation-log.md` |
| Gates | `challenger` | ⚔️ Challenger | Gate reviews at 1, 2, 4, 5 |

## Skills (Auto-Invoked by Agents)

### Core Skills

| Skill | Location | Used By |
|-------|----------|---------|
| `caf-design-areas` | `.github/skills/caf-design-areas/` | Scribe, Oracle, Warden |
| `security-baseline` | `.github/skills/security-baseline/` | Warden, Forge, Challenger |
| `cost-governance` | `.github/skills/cost-governance/` | Oracle, Forge, Sentinel |
| `profile-management` | `.github/skills/profile-management/` | Envoy, Strategist |
| `workflow-engine` | `.github/skills/workflow-engine/` | Conductor (Orchestrator) |

### Azure & IaC Skills

| Skill | Location | Used By |
|-------|----------|---------|
| `azure-defaults` | `.github/skills/azure-defaults/` | All agents (naming, tags, AVM, WAF) |
| `azure-bicep-patterns` | `.github/skills/azure-bicep-patterns/` | Forge (Bicep), Strategist |
| `terraform-patterns` | `.github/skills/terraform-patterns/` | Forge (Terraform), Strategist |
| `azure-diagnostics` | `.github/skills/azure-diagnostics/` | Sentinel, Chronicler |
| `azure-rbac` | `.github/skills/azure-rbac/` | Warden, Forge |
| `azure-compliance` | `.github/skills/azure-compliance/` | Warden, Sentinel, Challenger |
| `azure-cost-optimization` | `.github/skills/azure-cost-optimization/` | Oracle, Sentinel |
| `iac-common` | `.github/skills/iac-common/` | Strategist, Forge |

### Tooling & Operations Skills

| Skill | Location | Used By |
|-------|----------|---------|
| `session-resume` | `.github/skills/session-resume/` | Conductor (Orchestrator) |
| `python-diagrams` | `.github/skills/python-diagrams/` | Artisan |
| `drawio` | `.github/skills/drawio/` | Artisan |
| `github-operations` | `.github/skills/github-operations/` | Envoy, Conductor |

## Approval Gates

6 non-negotiable gates (1, 2, 3, 4, 5, 6). Challenger reviews at gates 1, 2, 4, 5.
Passes scale with complexity: Simple = 1×, Standard = 2×, Complex = 3×.
**Never skip gates.**

## Key Conventions

### AVM-First
Always use Azure Verified Modules (AVM) when available for both Bicep and Terraform.
Fall back to native `resource` / `module` blocks only when no AVM module exists.

### Security Baseline (Non-Negotiable)
6 mandatory rules enforced at code gen, deploy preflight, and continuous monitoring:
1. TLS 1.2 minimum
2. HTTPS-only traffic
3. No public blob access
4. Managed Identity preferred
5. Azure AD-only SQL authentication
6. Public network disabled (prod)

### Cost Governance
Every deployment **must** include a budget resource with alerts at 80%, 100%, 120%
forecast thresholds. Budget amounts are parameterized per environment — never hardcoded.

### Naming & Tagging
Follow CAF naming conventions. Required tags on all resource groups:
`Environment`, `Owner`, `CostCenter`, `Project`, `ManagedBy`.

### IaC Defaults
- Default region: `southcentralus` (configurable via `AZURE_DEPLOYMENT_REGION`)
- IaC framework: Bicep or Terraform (configurable via `IAC_FRAMEWORK`)
- Management group prefix: `alz` (configurable via `AZURE_MANAGEMENT_GROUP_PREFIX`)

## Key Files

| File/Dir | Purpose |
|----------|---------|
| `AGENTS.md` | Full agent spec, workflow diagram, security rules |
| `.github/agents/` | Agent definition files (7 agents) |
| `.github/skills/` | Skill SKILL.md entry points (17 skills) |
| `.github/workflows/` | CI/CD pipelines (6 workflows) |
| `src/agents/` | Agent Python implementations |
| `src/tools/` | Tool implementations (8 tools) |
| `src/config/` | Settings, profiles, agent config |
| `infra/bicep/` | Bicep modules and parameters |
| `infra/terraform/` | Terraform modules and environments |
| `mcp/` | MCP servers (3: azure-pricing, azure-platform, drawio) |
| `docs/` | Architecture docs, diagrams, runbooks |
| `scripts/validators/` | Security baseline and cost governance validators |

## Validation Commands

```bash
# Security baseline validation
python scripts/validators/validate_security_baseline.py infra/bicep/

# Cost governance validation
python scripts/validators/validate_cost_governance.py infra/bicep/

# Bicep lint
az bicep build --file infra/bicep/main.bicep

# Terraform validate
cd infra/terraform && terraform init && terraform validate

# Python tests
python -m pytest tests/ -v
```

## MCP Servers

3 MCP servers configured in `mcp/mcp-config.json`:
1. **azure-pricing** — Cost estimation and pricing lookups
2. **azure-platform** — Consolidated 22-tool Azure platform server
3. **drawio** — Architecture diagram generation

## CAF Design Areas → IaC Module Mapping

| Design Area | IaC Module | Agent(s) |
|-------------|-----------|----------|
| Billing & Tenant | `billing-and-tenant/` | Scribe, Oracle |
| Identity & Access | `identity-and-access/` | Warden, Forge |
| Resource Organization | `resource-organization/` | Oracle, Strategist |
| Network Topology | `network-topology/` | Oracle, Forge |
| Security | `security/` | Warden, Sentinel |
| Management | `management/` | Chronicler, Sentinel |
| Governance | `governance/` | Warden, Sentinel |
| Platform Automation | `platform-automation/` | Envoy, Forge |

## Day-2 Operations

Beyond deployment (Steps 1–7), continuous operations run in Steps 8–9:
- **Sentinel** scans compliance every 30 min, drift every hour, full audit daily at 6 AM
- **Mender** auto-remediates critical/high violations with snapshot/rollback
- Alert thresholds: Critical → immediate, High → 15 min, Medium/Low → daily report
