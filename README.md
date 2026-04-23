# Agentic Azure Landing Zone Accelerator

> **AI Orchestrates · Humans Decide · Azure Executes**

A multi-agent workflow that transforms Azure Landing Zone requirements into deployed,
governed, and continuously monitored infrastructure — aligned with the
[Cloud Adoption Framework](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-areas)
design areas and the [APEX](https://github.com/jonathan-vella/azure-agentic-infraops) agentic infrastructure patterns.

Supports both **greenfield** (new environment) and **brownfield** (existing environment)
scenarios. For brownfield, an optional Step 0 runs a WAF-aligned assessment of the
current estate before the standard workflow begins.

## What This Repository Contains

| Component | Description |
|-----------|-------------|
| **Agent Definitions** | 12 specialized agents with Semantic Kernel function calling |
| **Workflow Engine** | DAG-based orchestration with approval gates and artifact handoffs |
| **IaC Modules** | Bicep + Terraform organized by CAF design area |
| **MCP Servers** | Azure Pricing, Azure Platform (consolidated), Draw.io |
| **Validation Scripts** | Security baseline, cost governance, pre-commit hooks |
| **CI/CD Pipelines** | GitHub Actions with OIDC, approval environments, self-hosted runner support |
| **Bootstrap Checklist** | Excel workbook to gather settings from networking, security, identity teams |
| **TDD Generator** | As-built Technical Design Documents with Azure architecture diagrams |
| **Documentation** | Architecture doc (Word), stakeholder deck (PowerPoint), interactive HTML guide |

## CAF Design Area Alignment

Every IaC module maps to an official Azure Landing Zone design area:

| CAF Design Area | Bicep Module | Terraform Module |
|-----------------|-------------|-----------------|
| Billing & Tenant | `billing-and-tenant/` | — |
| Identity & Access | `identity/` | `identity/` |
| Network Topology & Connectivity | `connectivity/`, `networking/` | `connectivity/`, `networking/` |
| Security | `security/`, `platform-security/` | `security/`, `platform-security/` |
| Management | `management/`, `logging/` | `platform-management/`, `logging/` |
| Governance | `governance/`, `policies/` | `policies/` |

## Agent Workflow (APEX-Aligned)

```
� Assessment   (brownfield only — Step 0)
    (Assessor)
       │
       ▼
�📜 Requirements  →  🏛️ Architecture  →  🛡️ Governance  →  📐 Plan
    (Scribe)          (Oracle)           (Warden)        (Strategist)
       🛑                🛑                 🛑               🛑
    GATE 1            GATE 2             GATE 3           GATE 4

⚒️ Code Gen  →  🚀 Deploy  →  📚 Docs  →  🔭 Monitor  ↔  🔧 Remediate
   (Forge)       (Envoy)     (Chronicler)   (Sentinel)      (Mender)
      🛑            🛑
   GATE 5        GATE 6                    Continuous Loop
```

### Agent Roster

| Agent | Codename | Step | Purpose |
|-------|----------|------|---------|
| Orchestrator | 🧠 Conductor | — | Master workflow orchestration |
| Assessment | 🔍 Assessor | 0 | Brownfield discovery + WAF assessment (brownfield only) |
| Requirements | 📜 Scribe | 1 | Gather LZ requirements mapped to CAF |
| Architect | 🏛️ Oracle | 2 | WAF assessment + cost estimation |
| Design | 🎨 Artisan | 3 | Architecture diagrams and ADRs |
| Governance | 🛡️ Warden | 3.5 | Policy discovery + security baseline |
| IaC Planner | 📐 Strategist | 4 | Implementation planning + AVM selection |
| Code Generator | ⚒️ Forge | 5 | Bicep/Terraform generation (AVM-first) |
| Deployer | 🚀 Envoy | 6 | Deployment with what-if/plan preview |
| Documentation | 📚 Chronicler | 7 | Post-deployment docs suite |
| Monitor | 🔭 Sentinel | 8 | Compliance + drift detection (continuous) |
| Remediation | 🔧 Mender | 9 | Auto-remediation with rollback |
| Challenger | ⚔️ Challenger | Gates | Adversarial review at approval gates |

### MCP Server Integration

| MCP Server | Tools | Used By |
|-----------|-------|---------|
| Azure Pricing | Cost estimation, region comparison, SKU pricing (18 tools) | Oracle, Strategist |
| Azure Platform | Resource Graph, Policy, Deployment, Monitor, RBAC, WARA Assessment (27 tools, consolidated) | All agents |
| Draw.io | Architecture diagram generation with Azure icons | Artisan |

## Security Baseline

Non-negotiable rules enforced at code generation, deployment preflight, and monitoring:

| Rule | Bicep | Terraform |
|------|-------|-----------|
| TLS 1.2 minimum | `minimumTlsVersion: 'TLS1_2'` | `min_tls_version = "1.2"` |
| HTTPS-only | `supportsHttpsTrafficOnly: true` | `https_traffic_only_enabled = true` |
| No public blob | `allowBlobPublicAccess: false` | `allow_nested_items_to_be_public = false` |
| Managed Identity | `identity: { type: 'SystemAssigned' }` | `identity { type = "SystemAssigned" }` |
| AD-only SQL | `azureADOnlyAuthentication: true` | `azuread_authentication_only = true` |
| No public network (prod) | `publicNetworkAccess: 'Disabled'` | `public_network_access_enabled = false` |

## Cost Governance

Every deployment includes budget alerts — **no budget, no merge**:

| Threshold | Type | Action |
|-----------|------|--------|
| 80% | Forecast | Email notification |
| 100% | Forecast | Email + action group |
| 120% | Forecast | Email + action group |

## CI/CD Pipelines

7 GitHub Actions workflows orchestrate the full lifecycle:

| Workflow | Trigger | Scope |
|----------|---------|-------|
| `1-bootstrap.yml` | Manual (one-time) | MG hierarchy, subscription placement, provider registration |
| `2-platform-deploy.yml` | Manual | 4 platform LZs (Mgmt → Conn → Ident → Sec) with cascade or targeted deploy |
| `3-app-deploy.yml` | Manual | Config-driven app LZs from `subscriptions.json` (parallel) |
| `monitor.yml` | Cron + Manual | Compliance scan across all 4 platform subscriptions in parallel |
| `5-pr-validate.yml` | PR to main | Lint, security, cost, tests, what-if preview |
| `reusable-deploy.yml` | Called by 2 & 3 | DRY: resolve → validate → plan → deploy → verify |
| `assign-role.yml` | Manual (utility) | Assign/remove RBAC roles on platform subscriptions |
| `assess.yml` | Manual | Brownfield WAF-aligned assessment (discovery + WARA + reports) |

### Self-Hosted Runner Support

All workflows use `vars.RUNNER_LABEL` to select the runner — set it once, all jobs follow:

```bash
# Use a private self-hosted runner
gh variable set RUNNER_LABEL --body "self-hosted"

# Or use a custom label
gh variable set RUNNER_LABEL --body "alz-runner"
```

If `RUNNER_LABEL` is not set, all workflows default to `ubuntu-latest` (GitHub-hosted).

### Platform Landing Zone Deployment

The accelerator deploys 4 platform landing zones in dependency order:

```
Management → Connectivity → Identity → Security
  (LAW, AA)   (Hub, Bastion)  (DC, RBAC)  (Sentinel, Defender, KV, SOAR)
```

Each platform LZ follows the reusable pipeline: **Resolve → Validate → Plan → Deploy → Verify**.

Deploy all or target a single LZ:

```bash
# Deploy all platform LZs in cascade
gh workflow run "2-platform-deploy.yml" -f framework=bicep -f action=deploy \
  -f location=southcentralus -f prefix=mrg

# Deploy only the security LZ
gh workflow run "2-platform-deploy.yml" -f framework=bicep -f action=deploy \
  -f start_from=security -f deploy_only=security \
  -f location=southcentralus -f prefix=mrg
```

### Compliance Monitoring

The monitor workflow scans all deployed subscriptions for policy compliance:

```bash
# Full compliance scan across all 4 platform subscriptions
gh workflow run "monitor.yml" -f scan_type=compliance -f scan_scope=all

# Scan a single LZ
gh workflow run "monitor.yml" -f scan_type=compliance -f scan_scope=security
```

Results include per-subscription compliance percentages and detailed violation listings.

### Bootstrap Settings Checklist

Complete `docs/ALZ_Bootstrap_Settings_Checklist.xlsx` **before** running the bootstrap:

| Tab | What It Gathers |
|-----|-----------------|
| **Bootstrap** | IaC choice, tenant ID, 10 subscription IDs, OIDC, GitHub environments, approval gates |
| **Bicep** | Connectivity topology, Firewall SKU, IP addressing, policies, Defender plans, budgets |
| **Terraform** | Same as Bicep + state backend config, Sovereign LZ |

Share the checklist with your networking, security, and identity teams to gather inputs in parallel.

## Quick Start

### Prerequisites

- Python 3.11+ (3.13 recommended)
- Azure CLI (`az`) authenticated
- Bicep CLI or Terraform CLI
- Azure subscription with Owner role
- Self-hosted runner (optional) or GitHub-hosted runners

### Installation

```bash
git clone https://github.com/your-org/agentic-alz-accelerator.git
cd agentic-alz-accelerator
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your credentials
```

### Run the Full Workflow

```bash
# Full APEX workflow with approval gates
python -m src.agents.orchestrator --mode workflow --project my-landing-zone --iac-tool bicep

# Deploy only (Steps 4-6)
python -m src.agents.orchestrator --mode deploy --profile corp

# Continuous monitoring (Steps 8-9)
python -m src.agents.orchestrator --mode monitor

# Deploy + Monitor
python -m src.agents.orchestrator --mode full --profile corp

# Brownfield assessment (via GitHub Actions)
gh workflow run assess.yml -f scope=/subscriptions/<sub-id> -f scope_type=subscription -f mode=full
```

### Run Validators

```bash
# Security baseline
python scripts/validators/validate_security_baseline.py infra/

# Cost governance
python scripts/validators/validate_cost_governance.py infra/
```

## Project Structure

```
├── AGENTS.md                  # Agent roster, workflow, gates, baseline
├── agent-output/              # Estate state and per-LZ session tracking
│   ├── 00-estate-state.json         # All platform + app LZ statuses
│   └── {lz-name}/                   # Per-LZ artifacts and session state
├── src/
│   ├── agents/                # Agent implementations
│   │   ├── orchestrator.py          # 🧠 Conductor (APEX workflow)
│   │   ├── requirements_agent.py    # 📜 Scribe (CAF requirements)
│   │   ├── assessment_agent.py      # 🔍 Assessor (brownfield discovery + WARA)
│   │   ├── governance_agent.py      # 🛡️ Warden (policy + baseline)
│   │   ├── challenger_agent.py      # ⚔️ Challenger (adversarial review)
│   │   ├── deployment_agent.py      # 🚀 Envoy (deploy)
│   │   ├── monitoring_agent.py      # 🔭 Sentinel (compliance)
│   │   ├── remediation_agent.py     # 🔧 Mender (auto-fix)
│   │   └── workflow_engine.py       # DAG workflow engine
│   ├── tools/                 # Azure SDK integrations
│   │   ├── bicep_deployer.py        # ARM deployment via SDK
│   │   ├── terraform_deployer.py    # Terraform CLI wrapper
│   │   ├── policy_checker.py        # Policy compliance checks
│   │   ├── resource_graph.py        # Azure Resource Graph queries
│   │   ├── drift_detector.py        # Configuration drift detection
│   │   ├── discovery_collector.py   # Brownfield environment discovery
│   │   ├── wara_engine.py           # WAF Reliability Assessment engine
│   │   ├── report_generator.py      # Assessment report generation
│   │   ├── assess_cli.py            # Assessment CLI entry point
│   │   ├── azure_diagram_generator.py # Architecture diagrams (engine selector)
│   │   ├── python_diagram_generator.py # Python diagrams library engine
│   │   └── tdd_generator.py         # Technical Design Documents
│   └── config/                # Agent and profile configs
│       ├── settings.py              # pydantic-settings from .env
│       ├── profile_loader.py        # 3-tier YAML profile inheritance
│       ├── wara_checks.yaml         # 28 WAF reliability assessment checks
│       └── profiles/                # base → child → env overrides
├── infra/
│   ├── bicep/modules/         # Bicep by CAF design area
│   │   ├── billing-and-tenant/
│   │   ├── connectivity/      # hub-spoke, vwan, gateways, private-dns
│   │   ├── governance/
│   │   ├── identity/
│   │   ├── logging/
│   │   ├── management/
│   │   ├── networking/
│   │   ├── platform-security/  # sentinel, defender, soar
│   │   ├── policies/
│   │   └── security/
│   └── terraform/modules/     # Terraform by CAF design area
│       ├── connectivity/
│       ├── identity/
│       ├── logging/
│       ├── networking/
│       ├── platform-management/
│       ├── platform-security/
│       ├── policies/
│       └── security/
├── mcp/                       # MCP servers
│   ├── mcp-config.json        # 3-server configuration
│   ├── azure-platform/        # Consolidated platform server (27 tools, MCP SDK)
│   ├── azure-pricing-mcp/     # APEX pricing submodule (18 tools)
│   └── drawio-mcp-server/     # Diagram generation (Deno/TypeScript)
├── .github/
│   ├── workflows/             # CI/CD (8 workflows)
│   │   ├── 1-bootstrap.yml          # One-time MG hierarchy setup
│   │   ├── 2-platform-deploy.yml    # Platform LZ deployments
│   │   ├── 3-app-deploy.yml         # Application LZ deployments
│   │   ├── assess.yml               # Brownfield WAF-aligned assessment
│   │   ├── 5-pr-validate.yml        # PR validation (lint, security, what-if)
│   │   ├── monitor.yml              # Multi-subscription compliance scanning
│   │   ├── reusable-deploy.yml      # Shared: resolve → validate → plan → deploy → verify
│   │   └── assign-role.yml          # Utility: RBAC role assignments to SPN
│   ├── agents/                # Agent definition files
│   ├── skills/                # 20 skill SKILL.md entry points
│   └── instructions/          # Per-filetype coding instructions
├── pipelines/                 # Legacy / Azure DevOps pipelines
├── docs/                      # Security baseline, cost governance, workflow
│   └── tdd/                   # Generated Technical Design Documents
└── tests/                     # 107 tests (assessment, deployment, monitoring, remediation)
```

## References

- [Azure Landing Zone Design Areas](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-areas) — CAF
- [Azure Agentic InfraOps (APEX)](https://github.com/jonathan-vella/azure-agentic-infraops) — Patterns & workflow
- [Azure Verified Modules](https://aka.ms/AVM) — IaC module standards

## License

MIT License — See [LICENSE](LICENSE) for details.
