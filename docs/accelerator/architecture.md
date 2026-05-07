# Current-State Architecture — Agentic ALZ Accelerator

> **Date:** 2026-05-07
> **Branch:** `main`
> **Scope:** Describes the system as it exists today — full greenfield + brownfield capability.

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
| Assessment | 🔍 Assessor | 0 | Brownfield discovery + WAF-aligned assessment (brownfield only) |
| Requirements | 📜 Scribe | 1 | Captures LZ requirements across CAF design areas |
| Architect | 🏛️ Oracle | 2 | WAF assessment, CAF mapping, cost estimation |
| Design | 🎨 Artisan | 3 | Architecture diagrams (Python, Draw.io MCP), ADRs |
| Governance | 🛡️ Warden | 3.5 | Policy discovery, security baseline enforcement |
| IaC Planner | 📐 Strategist | 4 | Implementation plan with AVM module selection |
| Code Gen (Bicep) | ⚒️ Forge | 5 | Bicep template generation (AVM-first) |
| Code Gen (Terraform) | ⚒️ Forge | 5 | Terraform configuration generation (AVM-TF) |
| Deployment | 🚀 Envoy | 6 | Profile selection, what-if/plan, deploy, verify |
| Documentation | 📚 Chronicler | 7 | As-built design docs, ops runbooks, resource inventory |
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
| `azure_diagram_generator.py` | Architecture diagram facade — engine selector |
| `drawio_diagram_generator.py` | Draw.io XML diagram generation with Azure icon library |
| `tdd_generator.py` | Technical Design Documents (.docx + .md + .svg/.png) |
| `discovery.py` | Brownfield environment discovery via Resource Graph |
| `wara_engine.py` | WAF Assessment engine with 221-check APRL-synced catalog |
| `report_generator.py` | Assessment report generation (6 artifact types) |
| `assess_cli.py` | Assessment CLI — orchestrates discovery, WARA, and reports |

### Skills

Skills under `.github/skills/` provide domain knowledge to agents as structured
Markdown. 35 skills across these categories:

- **Azure infrastructure** — defaults, naming, tagging, AVM-first policy, quotas
- **IaC patterns** — Bicep and Terraform module examples, testing
- **Security & compliance** — baseline rules, compliance framework mapping, RBAC, Entra ID
- **Cost** — governance enforcement, optimization patterns
- **Operations** — diagnostics, session resume, workflow engine, context optimization
- **Tooling** — Draw.io, Python diagrams, Mermaid, GitHub operations, docs writer
- **Assessment** — brownfield discovery, WARA checks, report generation
- **Governance** — golden principles, context shredding, count registry, resource visualizer

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

**Bicep modules** (`infra/bicep/{customer}/modules/`):

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

**Terraform modules** (`infra/terraform/{customer}/modules/`) mirror the Bicep modules
with equivalent functionality using `azurerm ~>4.0`.

The root orchestrators (`infra/bicep/{customer}/main.bicep`, `infra/terraform/{customer}/main.tf`)
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
| `monitor.yml` | Schedule + manual | Compliance (30min), drift (hourly), full audit (daily 6AM) |
| `5-pr-validate.yml` | Pull request | Lint, security validator, cost validator, pytest |
| `reusable-deploy.yml` | Callable | Validate → plan → deploy → verify pipeline |
| `assess.yml` | Manual | Brownfield WAF-aligned assessment (discover → WARA → reports) |
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

197 tests across 13 test files under `tests/` cover all agents (assessment,
deployment, monitoring, remediation), tools (discovery, WARA engine, report
generator, validators), and the `alz-recall` CLI. Tests use mocked Azure SDK
clients and Semantic Kernel.

### CLI Tools

| Tool | Location | Purpose |
|------|----------|---------|
| `alz-recall` | `tools/apex-recall/` | Session state management CLI (init, show, decide, checkpoint, etc.) |
| Agent Registry | `tools/registry/agent-registry.json` | Agent → definition, skills, scope mapping |
| JSON Schemas | `tools/schemas/` | State file validation schemas |

## Data Flows

### Greenfield: Requirements → Deployed Infrastructure

```
User Input → [Scribe] Requirements → [Oracle] Architecture Assessment
  → [Artisan] Design Diagrams → [Warden] Governance Constraints
  → [Strategist] Implementation Plan → [Forge] IaC Code Generation
  → [Envoy] Deploy via GitHub Actions → [Chronicler] As-Built Docs
```

Each step produces artifacts in `agent-output/{customer}/{lz-name}/` and passes through
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
Schedule trigger (monitor.yml)
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

`agent-output/{customer}/00-estate-state.json` — single source of truth for the entire
landing zone estate:

- Estate metadata (prefix, region, IaC tool)
- Platform LZ statuses (all 4 deployed)
- Application LZ inventory (empty)
- Management group hierarchy (12 MGs under `mrg`)
- Cross-cutting governance status (policies: not started, RBAC: not started, budgets: deployed)
- Day-2 operations status
- Deploy history with run IDs

### Per-LZ Session State

`agent-output/{customer}/{lz-name}/00-session-state.json` — per-landing-zone workflow
progress, gate approvals, and artifact inventory.

### Workflow Engine State

`WorkflowEngine` class (`src/agents/workflow_engine.py`) manages in-memory
DAG-based step execution with `WorkflowState` tracking step status, artifacts,
and gate approvals. Production config specifies Azure Table Storage for persistence.

### Artifacts

| Location | Contents |
|----------|----------|
| `agent-output/{customer}/` | Estate state, per-LZ state, challenger reviews |
| `agent-output/{customer}/tdd/` | Technical Design Documents (.md + .docx + .png) |
| `agent-output/{customer}/diagrams/` | Architecture diagrams (.drawio + .mmd + .png) |
| `infra/bicep/{customer}/parameters/` | Bicep parameter files per platform LZ |
| `infra/terraform/{customer}/environments/` | Terraform variable files per environment |

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

### Resolved (formerly gaps)

The following were previously gaps and are now fully implemented:

- ✅ **Brownfield assessment** — Step 0 with discovery, 221-check WARA engine, and report generation
- ✅ **WAF/Well-Architected scoring** — All 5 pillars scored via APRL-synced catalog
- ✅ **Current-state architecture docs** — Auto-generated from live Azure state
- ✅ **CAF assessment output** — Design area alignment included in assessment reports

### Remaining Gaps

#### Cross-Cutting Governance

- **Policy assignments:** Not started — only budget policies are deployed
- **RBAC assignments:** Not started
- **Tagging enforcement:** Missing required tags (Owner, CostCenter, Project)

#### Security Gaps (from Assessment — 5 must_fix)

- Defender for Cloud not fully enabled across all subscriptions (SEC-010)
- Azure Firewall disabled in connectivity parameter file (OPE-006)
- No budget resources deployed (COS-001)
- Insecure storage defaults (SEC-029)
- Missing diagnostic settings on platform resources

#### Operational Gaps

- Single-region deployment only (no HA/DR)
- Empty SOAR playbooks in security LZ
- Threat Intelligence connector pending permissions

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
