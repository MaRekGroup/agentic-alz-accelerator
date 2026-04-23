# Current-State Architecture — Agentic ALZ Accelerator

> **Date:** 2026-04-23
> **Branch:** `pr1/current-state-architecture-docs`
> **Scope:** Describes the system as it exists today — before brownfield/assessment enhancements.

## Overview

The Agentic ALZ Accelerator is a multi-agent system that turns Azure Landing Zone
requirements into deployed, governed, and continuously monitored infrastructure.
It follows the APEX (Agentic Platform Engineering eXperience) pattern where
**AI orchestrates, humans decide, and Azure executes**.

The system manages:

- **Platform Landing Zones** — Management, Connectivity, Identity, Security
  (deployed sequentially)
- **Application Landing Zones** — Workloads stamped on the platform via
  configurable profiles (online, corp, sandbox, sap)
- **Cross-cutting Governance** — Management group hierarchy, policies, RBAC, budgets
- **Day-2 Operations** — Continuous compliance monitoring and auto-remediation

All Azure operations flow through **GitHub Actions workflows** — never local CLI.
Authentication uses **OIDC (Workload Identity Federation)** with no stored secrets.

## Component Inventory

### Agents

Agents are defined in two layers: agent definitions (Markdown) under
`.github/agents/` and Python implementations under `src/agents/`.

| Agent | Codename | Step | Role |
|-------|----------|------|------|
| Orchestrator | 🧠 Conductor | — | Master coordinator; routes workflow, enforces gates |
| Requirements | 📜 Scribe | 1 | Captures LZ requirements across CAF design areas |
| Governance | 🛡️ Warden | 3.5 | Policy discovery, security baseline enforcement |
| Deployment | 🚀 Envoy | 6 | Profile selection, what-if/plan, deploy, verify |
| Monitoring | 🔭 Sentinel | 8 | Compliance scans, drift detection, security posture |
| Remediation | 🔧 Mender | 9 | Auto-remediation with snapshot/rollback |
| Challenger | ⚔️ Challenger | Gates | Adversarial review at gates 1, 2, 4, 5 |

The Orchestrator delegates to agents either **interactively** (requirements,
planning — needs user input) or **autonomously** (architecture, code gen, deploy).

### Tools

Tools under `src/tools/` provide Azure integration capabilities:

| Tool | Purpose |
|------|---------|
| `resource_graph.py` | Azure Resource Graph queries — inventory, KQL interface |
| `policy_checker.py` | Azure Policy compliance state and violation retrieval |
| `drift_detector.py` | Compares current Azure state vs IaC baseline via change tracking |
| `bicep_deployer.py` | What-if analysis, Bicep compilation, deployment execution |
| `terraform_deployer.py` | Terraform plan/apply/destroy with Azure backend |
| `python_diagram_generator.py` | PNG architecture diagrams via `mingrammer/diagrams` |
| `azure_diagram_generator.py` | SVG diagrams with Azure icon colors (inline) |
| `tdd_generator.py` | Technical Design Documents (.docx + .md + .svg/.png) |

### Skills

Skills under `.github/skills/` provide domain knowledge to agents as structured
Markdown. Categories include:

- **Azure infrastructure** — defaults, naming, tagging, AVM-first policy
- **IaC patterns** — Bicep and Terraform module examples
- **Security & compliance** — baseline rules, compliance framework mapping, RBAC
- **Cost** — governance enforcement, optimization patterns
- **Operations** — diagnostics, session resume, workflow engine
- **Tooling** — Draw.io, Python diagrams, GitHub operations

### MCP Servers

Model Context Protocol servers under `mcp/` expose tools to agents:

| Server | Technology | Capabilities |
|--------|-----------|--------------|
| azure-pricing | Python | Cost estimation, SKU discovery, RI pricing, spot VM analysis |
| azure-platform | Python (MCP SDK) | Resource Graph, Policy, Monitor, Deployment, Security |
| drawio | Deno/TypeScript | Architecture diagram generation with Azure icon library |

### IaC Modules

Infrastructure-as-Code is implemented in both Bicep and Terraform, with Bicep
as the primary framework.

**Bicep modules** (`infra/bicep/modules/`):

| Module | Scope | Description |
|--------|-------|-------------|
| `billing-and-tenant/` | managementGroup | CAF enterprise-scale MG hierarchy |
| `connectivity/` | subscription | Hub-spoke/vWAN networking, Bastion, DNS |
| `governance/` | subscription | Policy initiatives + budget resources |
| `identity/` | subscription | Managed Identities + RBAC |
| `logging/` | resourceGroup | AVM Log Analytics + Automation Account |
| `management/` | subscription | Full management subscription resources |
| `networking/` | resourceGroup | AVM VNet, Subnets, NSGs, DDoS |
| `platform-security/` | subscription | Sentinel, Defender, SOAR, Key Vault |
| `policies/` | subscription | Policy definitions and assignments |
| `security/` | resourceGroup | AVM Key Vault + Defender enablement |

**Terraform modules** (`infra/terraform/modules/`) mirror the Bicep modules
with equivalent functionality using `azurerm ~>4.0`.

The root orchestrators (`infra/bicep/main.bicep`, `infra/terraform/main.tf`)
compose modules based on landing zone profile configuration.

### Configuration

| File | Purpose |
|------|---------|
| `src/config/settings.py` | Pydantic settings from `.env`: Azure AI, Azure infra, IaC, monitoring, notifications |
| `src/config/agent_config.yaml` | Agent orchestration config: concurrency, models, tools, schedules, thresholds |
| `src/config/landing_zone_profiles.yaml` | Profile registry: platform (4) and application (4) profiles with dependencies |
| `src/config/profile_loader.py` | 3-tier inheritance: environment override → child profile → base |
| `environments/subscriptions.json` | Subscription-to-LZ mapping for app deployments |

### Pipelines

GitHub Actions workflows under `.github/workflows/`:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `1-bootstrap.yml` | Manual | MG hierarchy creation, subscription moves, provider registration |
| `2-platform-deploy.yml` | Manual | Sequential platform LZ deployment with approval gates |
| `3-app-deploy.yml` | Manual + callable | Application LZ deployment from `subscriptions.json` |
| `4-monitor.yml` | Schedule + manual | Compliance (30min), drift (hourly), full audit (daily 6AM) |
| `5-pr-validate.yml` | Pull request | Lint, security validator, cost validator, pytest |
| `reusable-deploy.yml` | Callable | Validate → plan → deploy → verify pipeline |
| `deploy-on-merge.yml` | Push to main | Trunk-based: deploys only changed LZs |
| `generate-diagrams.yml` | Manual | Python architecture diagram generation |
| `deploy-docs.yml` | Push to main | Astro docs site → GitHub Pages |
| `cleanup-old-rg.yml` | Manual | Utility: delete resource groups |
| `assign-role.yml` | Manual | Utility: RBAC role assignment |

Reference copies also exist under `pipelines/github-actions/` and an Azure DevOps
pipeline under `pipelines/azure-devops/`.

### Validators

Pre-merge enforcement scripts under `scripts/validators/`:

| Validator | Rule |
|-----------|------|
| `validate_security_baseline.py` | 6 baseline rules + extended checks (regex-based) |
| `validate_cost_governance.py` | Budget resource required with 80/100/120% forecast alerts |

### Tests

Unit tests under `tests/` cover deployment agent, monitoring agent, and
remediation agent. Tests use mocked Azure SDK clients and Semantic Kernel.

## Data Flows

### Greenfield: Requirements → Deployed Infrastructure

```
User Input → [Scribe] Requirements → [Oracle] Architecture Assessment
  → [Artisan] Design Diagrams → [Warden] Governance Constraints
  → [Strategist] Implementation Plan → [Forge] IaC Code Generation
  → [Envoy] Deploy via GitHub Actions → [Chronicler] As-Built Docs
```

Each step produces artifacts in `agent-output/{lz-name}/` and passes through
approval gates. The Challenger agent reviews at gates 1, 2, 4, and 5.

### Platform Deployment Pipeline

```
gh workflow run 2-platform-deploy.yml
  → reusable-deploy.yml (per subscription)
    → Validate (bicep build / tf validate)
    → Plan (what-if / tf plan)
    → Deploy (az deployment / tf apply)
    → Verify (Resource Graph compliance queries)
```

Sequential order: Management → Connectivity → Identity → Security.
Each LZ has `depends_on` constraints and uses a dedicated GitHub environment
with its own subscription secret.

### Continuous Operations (Day-2)

```
Schedule trigger (4-monitor.yml)
  → [Sentinel] Compliance scan (Policy) every 30 min
  → [Sentinel] Drift detection (Resource Graph) every hour
  → [Sentinel] Full audit (Defender + Policy + Resource Graph) daily 6 AM
  → If violations found:
    → Critical/High → [Mender] Auto-remediate (snapshot → fix → verify)
    → Medium/Low → Report for human review
```

## Security Model

### Authentication

- **OIDC Workload Identity Federation** — the only authentication method
- Entra ID app registration with federated credentials for:
  - `main` branch pushes
  - Pull request events
  - Per-environment deployments (7 GitHub environments)
- **No stored secrets** for Azure authentication

### Secrets in GitHub

| Secret | Scope | Purpose |
|--------|-------|---------|
| `AZURE_CLIENT_ID` | Repository | OIDC app registration |
| `AZURE_TENANT_ID` | Repository | Azure AD tenant |
| `PLATFORM_*_SUBSCRIPTION_ID` | Repository | Per-platform-LZ subscription |
| `SUBSCRIPTION_ID` | Per-environment | App LZ subscription |

### Enforcement Points

1. **Pre-commit** — Security baseline + cost governance validators (lefthook)
2. **CI (PR)** — Lint, validators, pytest
3. **Agent (code gen)** — Governance agent enforces 6 baseline rules
4. **Challenger (gates)** — Adversarial review at gates 1, 2, 4, 5
5. **Deploy (preflight)** — What-if / plan before apply
6. **Runtime (Day-2)** — Compliance scans, drift detection, auto-remediation

### Security Baseline (6 Non-Negotiable Rules)

1. TLS 1.2 minimum
2. HTTPS-only traffic
3. No public blob access
4. Managed Identity preferred
5. Azure AD-only SQL authentication
6. Public network disabled (prod)

## State and Storage

### Estate State

`agent-output/00-estate-state.json` — single source of truth for the entire
landing zone estate:

- Estate metadata (prefix, region, IaC tool)
- Platform LZ statuses (all 4 deployed)
- Application LZ inventory (empty)
- Management group hierarchy (12 MGs under `mrg`)
- Cross-cutting governance status (policies: not started, RBAC: not started, budgets: deployed)
- Day-2 operations status
- Deploy history with run IDs

### Per-LZ Session State

`agent-output/{lz-name}/00-session-state.json` — per-landing-zone workflow
progress, gate approvals, and artifact inventory.

### Workflow Engine State

`WorkflowEngine` class (`src/agents/workflow_engine.py`) manages in-memory
DAG-based step execution with `WorkflowState` tracking step status, artifacts,
and gate approvals. Production config specifies Azure Table Storage for persistence.

### Artifacts

| Location | Contents |
|----------|----------|
| `agent-output/` | Estate state, per-LZ state, challenger reviews |
| `docs/tdd/` | Technical Design Documents (.md + .docx + .png) |
| `docs/diagrams/` | Architecture diagrams (.drawio + .mmd + .png) |
| `infra/bicep/parameters/` | Bicep parameter files per platform LZ |
| `infra/terraform/environments/` | Terraform variable files per environment |

## Current Deployment State

| Platform LZ | Status | Subscription | Key Resources |
|-------------|--------|-------------|---------------|
| Management | ✅ Deployed | `PLATFORM_MGMT_SUBSCRIPTION_ID` | LAW (`mrg-law`), Automation Account |
| Connectivity | ✅ Deployed | `PLATFORM_CONN_SUBSCRIPTION_ID` | Hub VNet, Bastion, Private DNS zones |
| Identity | ✅ Deployed | `PLATFORM_IDTY_SUBSCRIPTION_ID` | Managed Identities, RBAC |
| Security | ✅ Deployed | `PLATFORM_SEC_SUBSCRIPTION_ID` | Sentinel, Defender (11 plans), Key Vault |

**Management Group Hierarchy:** 12 MGs under `mrg` prefix (migrated from `alz-*`).

**Application LZs:** None deployed yet.

## Known Constraints and Gaps

### Greenfield-Only Limitation

The current workflow assumes a **greenfield** environment. There is no mechanism to:

1. Discover existing Azure resources, policies, or RBAC in a tenant
2. Assess an existing environment against WAF pillars or CAF areas
3. Generate a current-state architecture document from live Azure state
4. Onboard an existing environment into the accelerator workflow
5. Handle coexistence with non-ALZ management group hierarchies

### Incomplete Cross-Cutting Governance

- **Policy assignments:** Not started — only budget policies are deployed
- **RBAC assignments:** Not started
- **Tagging enforcement:** Missing required tags (Owner, CostCenter, Project)

### Security Gaps (from Challenger Review)

- LAW public network access enabled (`logging/main.bicep`)
- Azure Firewall disabled in connectivity parameter file
- Empty SOAR playbooks in security LZ
- Threat Intelligence connector pending permissions

### Operational Gaps

- No brownfield discovery or assessment capability
- No WARA/Well-Architected scoring
- No CAF assessment output
- No current-state architecture documentation from live state
- Single-region deployment only (no HA/DR)

## Assumptions and Non-Goals

### Assumptions

- Azure tenant with Entra ID is available
- GitHub repository with Actions enabled
- Self-hosted runner (`vm-github-runner-01`) with Azure CLI access
- OIDC federated identity configured per `scripts/setup-oidc.sh`
- Separate subscriptions for each platform LZ

### Non-Goals (Current State)

- Multi-cloud support (Azure-only)
- Direct Azure CLI operations from developer machines
- GUI-based deployment (CLI/agent-based only)
- Real-time streaming dashboards (batch reporting only)
