# Copilot Instructions — Agentic ALZ Accelerator

> Project-level instructions auto-loaded by GitHub Copilot for every session.
> For the full AGENTS.md spec, see the repo root.

## Quick Start

This repo implements a multi-agent APEX workflow that turns Azure Landing Zone
requirements into deployed, governed, and continuously monitored infrastructure —
aligned with all 8 CAF design areas.

The accelerator supports both **greenfield** (new environment) and **brownfield**
(existing environment) scenarios. For brownfield, an optional Step 0 runs a
WAF-aligned assessment before the standard workflow begins.

Enable subagents: In VS Code Copilot Chat, prefix with `@workspace` and use
the agent names below (e.g., `@requirements`, `@governance`, `@orchestrator`).

## Multi-Step Workflow

| Step | Agent | Codename | Artifact |
|------|-------|----------|----------|
| 0 | `assessment` | 🔍 Assessor | `00-assessment-*.{md,json,mmd}` (brownfield only) |
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
| `azure-quotas` | `.github/skills/azure-quotas/` | Strategist, Envoy |
| `iac-common` | `.github/skills/iac-common/` | Strategist, Forge |
| `terraform-test` | `.github/skills/terraform-test/` | Forge (Terraform) |
| `terraform-search-import` | `.github/skills/terraform-search-import/` | Forge (Terraform), Assessor |

### Tooling & Operations Skills

| Skill | Location | Used By |
|-------|----------|---------|
| `session-resume` | `.github/skills/session-resume/` | Conductor (Orchestrator) |
| `python-diagrams` | `.github/skills/python-diagrams/` | Artisan |
| `drawio` | `.github/skills/drawio/` | Artisan |
| `mermaid` | `.github/skills/mermaid/` | Artisan, Chronicler |
| `azure-diagrams` | `.github/skills/azure-diagrams/` | Artisan (routing) |
| `azure-resource-visualizer` | `.github/skills/azure-resource-visualizer/` | Artisan, Assessor |
| `azure-adr` | `.github/skills/azure-adr/` | Oracle, Chronicler |
| `github-operations` | `.github/skills/github-operations/` | Envoy, Conductor |
| `docs-writer` | `.github/skills/docs-writer/` | Chronicler |

### Agent Governance & Context Skills

| Skill | Location | Used By |
|-------|----------|---------|
| `golden-principles` | `.github/skills/golden-principles/` | All agents (operating invariants) |
| `context-shredding` | `.github/skills/context-shredding/` | All agents (context compression) |
| `azure-validate` | `.github/skills/azure-validate/` | Envoy, Challenger |
| `azure-governance-discovery` | `.github/skills/azure-governance-discovery/` | Warden |
| `context-optimizer` | `.github/skills/context-optimizer/` | Conductor (audits) |
| `count-registry` | `.github/skills/count-registry/` | All agents (entity counts) |
| `entra-app-registration` | `.github/skills/entra-app-registration/` | Warden, Envoy |

### Assessment Skills (Brownfield)

| Skill | Location | Used By |
|-------|----------|---------|
| `brownfield-discovery` | `.github/skills/brownfield-discovery/` | Assessor |
| `wara-assessment` | `.github/skills/wara-assessment/` | Assessor, Oracle |
| `assessment-report` | `.github/skills/assessment-report/` | Assessor, Chronicler |

### Microsoft Learn Skills (Azure Services)

> Source: [MicrosoftDocs/Agent-Skills](https://github.com/MicrosoftDocs/Agent-Skills). Provide Learn doc links fetched via `mcp_microsoftdocs:microsoft_docs_fetch`.

#### Governance & Architecture

| Skill | Location | Used By |
|-------|----------|---------|
| `azure-policy` | `.github/skills/azure-policy/` | Warden, Sentinel, Challenger |
| `azure-cloud-adoption-framework` | `.github/skills/azure-cloud-adoption-framework/` | Scribe, Oracle, Conductor |
| `azure-well-architected` | `.github/skills/azure-well-architected/` | Oracle, Challenger, Assessor |
| `azure-architecture` | `.github/skills/azure-architecture/` | Oracle, Artisan |
| `azure-resource-manager` | `.github/skills/azure-resource-manager/` | Forge, Strategist, Envoy |
| `azure-resource-graph` | `.github/skills/azure-resource-graph/` | Assessor, Sentinel, Warden |

#### Security

| Skill | Location | Used By |
|-------|----------|---------|
| `azure-security` | `.github/skills/azure-security/` | Warden, Challenger, Sentinel |
| `azure-defender-for-cloud` | `.github/skills/azure-defender-for-cloud/` | Warden, Sentinel, Mender |
| `azure-sentinel` | `.github/skills/azure-sentinel/` | Sentinel, Chronicler |
| `azure-key-vault` | `.github/skills/azure-key-vault/` | Warden, Forge |

#### Networking

| Skill | Location | Used By |
|-------|----------|---------|
| `azure-virtual-network` | `.github/skills/azure-virtual-network/` | Oracle, Forge |
| `azure-networking` | `.github/skills/azure-networking/` | Oracle, Forge, Strategist |
| `azure-firewall` | `.github/skills/azure-firewall/` | Forge, Warden |
| `azure-firewall-manager` | `.github/skills/azure-firewall-manager/` | Warden, Forge |
| `azure-bastion` | `.github/skills/azure-bastion/` | Forge, Strategist |
| `azure-dns` | `.github/skills/azure-dns/` | Forge, Oracle |
| `azure-expressroute` | `.github/skills/azure-expressroute/` | Oracle, Forge |
| `azure-vpn-gateway` | `.github/skills/azure-vpn-gateway/` | Oracle, Forge |
| `azure-virtual-wan` | `.github/skills/azure-virtual-wan/` | Oracle, Forge |
| `azure-virtual-network-manager` | `.github/skills/azure-virtual-network-manager/` | Warden, Forge |
| `azure-private-link` | `.github/skills/azure-private-link/` | Forge, Warden |
| `azure-application-gateway` | `.github/skills/azure-application-gateway/` | Forge, Oracle |
| `azure-web-application-firewall` | `.github/skills/azure-web-application-firewall/` | Warden, Forge |
| `azure-ddos-protection` | `.github/skills/azure-ddos-protection/` | Warden, Forge |
| `azure-nat-gateway` | `.github/skills/azure-nat-gateway/` | Forge |
| `azure-network-watcher` | `.github/skills/azure-network-watcher/` | Sentinel, Chronicler |
| `azure-front-door` | `.github/skills/azure-front-door/` | Oracle, Forge |
| `azure-load-balancer` | `.github/skills/azure-load-balancer/` | Forge, Oracle |
| `azure-route-server` | `.github/skills/azure-route-server/` | Forge |

#### Management & Operations

| Skill | Location | Used By |
|-------|----------|---------|
| `azure-monitor` | `.github/skills/azure-monitor/` | Sentinel, Chronicler |
| `azure-automation` | `.github/skills/azure-automation/` | Forge, Mender |
| `azure-backup` | `.github/skills/azure-backup/` | Forge, Oracle |
| `azure-update-manager` | `.github/skills/azure-update-manager/` | Sentinel, Mender |
| `azure-service-health` | `.github/skills/azure-service-health/` | Sentinel |
| `azure-advisor` | `.github/skills/azure-advisor/` | Oracle, Sentinel |
| `azure-site-recovery` | `.github/skills/azure-site-recovery/` | Forge, Oracle |

#### Cost & Reliability

| Skill | Location | Used By |
|-------|----------|---------|
| `azure-cost-management` | `.github/skills/azure-cost-management/` | Oracle, Sentinel |
| `azure-reliability` | `.github/skills/azure-reliability/` | Oracle, Challenger |
| `azure-resiliency` | `.github/skills/azure-resiliency/` | Oracle, Challenger |

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
- Management group prefix: `mrg` (configurable via `AZURE_MANAGEMENT_GROUP_PREFIX`)

## Key Files

| File/Dir | Purpose |
|----------|---------|
| `AGENTS.md` | Full agent spec, workflow diagram, security rules |
| `.github/agents/` | Agent definition files (8 agents) |
| `.github/skills/` | Skill SKILL.md entry points (20 skills) |
| `.github/workflows/` | CI/CD pipelines (8 workflows) |
| `src/agents/` | Agent Python implementations |
| `src/tools/` | Tool implementations (11 tools) |
| `src/config/` | Settings, profiles, agent config |
| `infra/bicep/{customer}/` | Bicep modules and parameters |
| `infra/terraform/{customer}/` | Terraform modules and environments |
| `mcp/` | MCP servers (3: azure-pricing, azure-platform, drawio) |
| `docs/` | Architecture docs, diagrams, runbooks |
| `scripts/validators/` | Security baseline and cost governance validators |

## Validation Commands

```bash
# Security baseline validation
python scripts/validators/validate_security_baseline.py infra/bicep/{customer}/

# Cost governance validation
python scripts/validators/validate_cost_governance.py infra/bicep/{customer}/

# Bicep lint
az bicep build --file infra/bicep/{customer}/main.bicep

# Terraform validate
cd infra/terraform/{customer} && terraform init && terraform validate

# Python tests
python -m pytest tests/ -v

# Brownfield assessment (via GitHub Actions)
gh workflow run assess.yml -f scope=/subscriptions/<sub-id> -f scope_type=subscription -f mode=full
```

## MCP Servers

3 MCP servers configured in `mcp/mcp-config.json`:
1. **azure-pricing** — Cost estimation and pricing lookups
2. **azure-platform** — Consolidated 27-tool Azure platform server
3. **drawio** — Architecture diagram generation

## CAF Design Areas → IaC Module Mapping

| Design Area | IaC Module | Agent(s) |
|-------------|-----------|----------|
| Billing & Tenant | `billing-and-tenant/` | Scribe, Oracle |
| Identity & Access | `identity/` | Warden, Forge |
| Resource Organization | `governance/`, `policies/` | Oracle, Strategist |
| Network Topology | `connectivity/`, `networking/` | Oracle, Forge |
| Security | `security/`, `platform-security/` | Warden, Sentinel |
| Management | `management/`, `logging/` | Chronicler, Sentinel |
| Governance | `governance/`, `policies/` | Warden, Sentinel |
| Platform Automation | — (CI/CD pipelines) | Envoy, Forge |

## Day-2 Operations

Beyond deployment (Steps 1–7), continuous operations run in Steps 8–9:
- **Sentinel** scans compliance every 30 min, drift every hour, full audit daily at 6 AM
- **Mender** auto-remediates critical/high violations with snapshot/rollback
- Alert thresholds: Critical → immediate, High → 15 min, Medium/Low → daily report
