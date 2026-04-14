# Agentic Azure Landing Zone Accelerator

> **AI Orchestrates · Humans Decide · Azure Executes**

A multi-agent workflow that transforms Azure Landing Zone requirements into deployed,
governed, and continuously monitored infrastructure — aligned with the
[Cloud Adoption Framework](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-areas)
design areas and the [APEX](https://github.com/jonathan-vella/azure-agentic-infraops) agentic infrastructure patterns.

## What This Repository Contains

| Component | Description |
|-----------|-------------|
| **Agent Definitions** | 10 specialized agents with Semantic Kernel function calling |
| **Workflow Engine** | DAG-based orchestration with approval gates and artifact handoffs |
| **IaC Modules** | Bicep + Terraform organized by CAF design area |
| **MCP Servers** | Azure Pricing, Resource Graph, Policy, Deployment, Monitor |
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
📜 Requirements  →  🏛️ Architecture  →  🛡️ Governance  →  📐 Plan
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
| Requirements | 📜 Scribe | 1 | Gather LZ requirements mapped to CAF |
| Architect | 🏛️ Oracle | 2 | WAF assessment + cost estimation |
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
| Azure Pricing | Cost estimation, region comparison | Oracle, Strategist |
| Azure Resource Graph | Resource queries, drift detection | Sentinel, Mender, Warden |
| Azure Policy | Policy discovery, compliance | Warden, Sentinel, Challenger |
| Azure Deployment | Bicep/TF deploy, what-if | Envoy, Mender |
| Azure Monitor | Secure score, activity log | Sentinel, Chronicler |

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

6 GitHub Actions workflows orchestrate the full lifecycle:

| Workflow | Trigger | Scope |
|----------|---------|-------|
| `1-bootstrap.yml` | Manual (one-time) | MG hierarchy, subscription placement, provider registration |
| `2-platform-deploy.yml` | Manual | 4 platform LZs in strict order with approval gates |
| `3-app-deploy.yml` | Manual | Config-driven app LZs from `subscriptions.json` (parallel) |
| `monitor.yml` | Cron + Manual | Compliance, drift detection, auto-remediation (24/7) |
| `5-pr-validate.yml` | PR to main | Lint, security, cost, tests, what-if preview |
| `reusable-deploy.yml` | Called by 2 & 3 | DRY: validate → plan → deploy → verify → TDD |

### Self-Hosted Runner Support

All workflows use `vars.RUNNER_LABEL` to select the runner — set it once, all 23 jobs follow:

```bash
# Use a private self-hosted runner
gh variable set RUNNER_LABEL --body "self-hosted"

# Or use a custom label
gh variable set RUNNER_LABEL --body "alz-runner"
```

If `RUNNER_LABEL` is not set, all workflows default to `ubuntu-latest` (GitHub-hosted).

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
├── src/
│   ├── agents/                # Agent implementations
│   │   ├── orchestrator.py          # 🧠 Conductor (APEX workflow)
│   │   ├── requirements_agent.py    # 📜 Scribe (CAF requirements)
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
│   │   ├── azure_diagram_generator.py # Architecture diagrams
│   │   └── tdd_generator.py         # Technical Design Documents
│   └── config/                # Agent and profile configs
│       ├── settings.py              # pydantic-settings from .env
│       ├── profile_loader.py        # 3-tier YAML profile inheritance
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
├── mcp/                       # MCP servers (Python)
│   ├── mcp-config.json
│   ├── azure-resource-graph/
│   ├── azure-policy/
│   ├── azure-deployment/
│   ├── azure-monitor/
│   └── azure-pricing/
├── .github/skills/            # Workflow engine DAG
├── scripts/validators/        # Security + cost validators
├── pipelines/                 # CI/CD (GitHub Actions + ADO)
├── docs/                      # Security baseline, cost governance, workflow
│   └── tdd/                   # Generated Technical Design Documents
└── tests/                     # 18 tests (deployment, monitoring, remediation)
```

## References

- [Azure Landing Zone Design Areas](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-areas) — CAF
- [Azure Agentic InfraOps (APEX)](https://github.com/jonathan-vella/azure-agentic-infraops) — Patterns & workflow
- [Azure Verified Modules](https://aka.ms/AVM) — IaC module standards

## License

MIT License — See [LICENSE](LICENSE) for details.
