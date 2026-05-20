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
| **Agent Definitions** | 14 specialized agents + 6 subagents with Semantic Kernel function calling |
| **Workflow Engine** | DAG-based orchestration with approval gates and artifact handoffs |
| **IaC Modules** | Bicep + Terraform organized by CAF design area |
| **MCP Servers** | Azure Pricing, Azure Platform (consolidated), Draw.io |
| **Validation Scripts** | Security baseline, cost governance, pre-commit hooks |
| **CI/CD Pipelines** | GitHub Actions with OIDC, approval environments, self-hosted runner support |
| **Bootstrap Checklist** | Inline checklist (root README + interactive HTML guide) covering networking, security, and identity inputs |
| **TDD Generator** | As-built Technical Design Documents with Azure architecture diagrams |
| **Documentation** | Architecture doc (Word), stakeholder deck (PowerPoint), interactive HTML guide |
| **Squad Integration** | Copilot Squad AI team with persistent roster, work routing, sprint ceremonies, and issue automation |

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

## Skills

Agents load specialized domain knowledge from **skills** during workflow execution.
Each skill is a `SKILL.md` file in `.github/skills/` that the Copilot runtime
auto-discovers — users do not invoke skills directly.

Skills cover six categories:

- **Core** — CAF design areas, security baseline, cost governance, profile management, workflow engine
- **Azure & IaC** — Naming/tagging defaults, Bicep patterns, Terraform patterns, diagnostics, RBAC, compliance mapping
- **Tooling & Operations** — Diagram generation (Python, Draw.io, Mermaid), ADRs, GitHub operations, documentation
- **Governance & Context** — Golden principles, context optimization, governance discovery, workload identity federation
- **Assessment (Brownfield)** — Brownfield discovery, WAF-aligned assessment, report generation
- **Microsoft Learn (Azure Services)** — Identity (W1), Compute (W2), Tenant Architecture (W3), Data Platform (W4), Hybrid (W5), plus Governance, Security, Networking, Management, and Cost & Reliability

The full agent→skill catalog is in [`.github/copilot-instructions.md`](.github/copilot-instructions.md).
For skill structure and authoring guidance, see [`.github/skills/README.md`](.github/skills/README.md).

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

Primary GitHub Actions workflows for the deployment + Day-2 ops lifecycle:

| Workflow | Trigger | Scope |
|----------|---------|-------|
| `1-bootstrap.yml` | Manual (one-time) | MG hierarchy, subscription placement, provider registration |
| `2-platform-deploy.yml` | Manual | 4 platform LZs (Mgmt → Conn → Ident → Sec) with cascade or targeted deploy |
| `3-app-deploy.yml` | Manual | Config-driven app LZs from `subscriptions.json` (parallel) |
| `4-monitor.yml` | Cron (30 min / 1 h / daily 06:00 UTC) + Manual | Canonical Day-2 ops: compliance scan, drift detection, auto-remediation (`environment: remediation` gate), Teams alerts, GH issue creation. Covers 4 platform + 6 app subscriptions via `MonitoringAgent` + `RemediationAgent`. |
| `monitor.yml` | Daily 04:00 UTC + Manual | Lightweight diagnostic: direct Azure Policy Insights SDK scan across 4 platform subscriptions in parallel. No agent dependencies — useful as a baseline check independent of the agent framework. |
| `5-pr-validate.yml` | PR to main | Lint, security, cost, tests, what-if preview |
| `reusable-deploy.yml` | Called by 2 & 3 | DRY: resolve → validate → plan → deploy → verify |
| `assign-role.yml` | Manual (utility) | Assign/remove RBAC roles on platform subscriptions |
| `assess.yml` | Manual | Brownfield WAF-aligned assessment (discovery + WARA + reports) |

The repo also ships operational automation workflows (`deploy-on-merge`, `cleanup-old-rg`, `generate-diagrams`, `deploy-docs`) and [Squad automation workflows](#github-automation-workflows) (`squad-triage`, `squad-issue-assign`, `squad-heartbeat`).

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

The canonical Day-2 ops workflow (`4-monitor.yml`) scans all deployed subscriptions for policy compliance, detects drift, and routes critical violations through auto-remediation:

```bash
# Full Day-2 ops scan across all 10 subscriptions (platform + app)
gh workflow run "4-monitor.yml" -f scan_type=compliance -f scope=all-subscriptions

# Scan only the 4 platform subscriptions
gh workflow run "4-monitor.yml" -f scan_type=compliance -f scope=platform-only
```

Results include per-subscription compliance percentages, drift detection, detailed violation listings, Teams alerts, and auto-created GitHub issues for critical violations. For a lightweight daily diagnostic baseline that bypasses the agent framework, see `monitor.yml` (runs at 04:00 UTC).

### Bootstrap Settings Checklist

Gather the following inputs **before** running the bootstrap. Coordinate with
your networking, security, and identity teams to collect values in parallel.
The full interactive checklist with tooltips lives in
[`docs/guide.html`](docs/guide.html) under **Prerequisites → Bootstrap Settings
Checklist**.

| Area | Required Inputs |
|------|-----------------|
| **Bootstrap** | IaC choice (Bicep/Terraform), tenant ID, 10 subscription IDs, OIDC app registration, GitHub environments, MG prefix, primary region, approval gate reviewers |
| **Bicep** | Connectivity topology (hub-spoke/vWAN), Firewall SKU, DDoS plan, IP addressing (CIDRs), policy initiatives, Defender plans, budget amounts per env |
| **Terraform** | Same as Bicep + state storage account, resource group, container name; Sovereign LZ option |

> The OIDC setup script (`scripts/setup-oidc.sh`) and
> `environments/subscriptions.json` capture most of these values
> programmatically once gathered.

## Quick Start

### Prerequisites

- Python 3.11+ (Python 3.13 used in CI; the devcontainer ships Python 3.14 for early-version testing)
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

### Local Development Guardrails

The repository enforces quality gates at commit, push, and CI via `lefthook.yml` and GitHub Actions:

| Hook | Checks |
|------|--------|
| **pre-commit** | Security baseline (Bicep/TF), cost governance (Bicep/TF), `terraform fmt`, `terraform validate`, `ruff` (Python lint), `yamllint` |
| **commit-msg** | Conventional Commits format via `commitlint` |
| **pre-push** | Full security + cost scans, `pytest` |

**Setup:** The devcontainer runs `npx --yes lefthook install` automatically in `postCreateCommand`. Outside the devcontainer, run `npx --yes lefthook install` after cloning.

**Bypass:** The pre-push `pytest` job currently has pre-existing collection errors unrelated to most contributions. Use `git push --no-verify` to bypass pre-push hooks when needed; CI re-runs the same validators on every PR.

> **Note:** These are git-level hooks managed by Lefthook. For Copilot runtime guards (tool-guardian, secrets-scanner, etc.), see [`.github/hooks/README.md`](.github/hooks/README.md).

## Project Structure

```
├── AGENTS.md                  # Agent roster, workflow, gates, baseline
├── agent-output/              # Per-customer generated content
│   ├── README.md                    # Structure guide
│   └── {customer}/                  # Customer engagement folder
│       ├── 00-estate-state.json     # All platform + app LZ statuses
│       ├── tdd/                     # Technical Design Documents
│       ├── diagrams/                # Architecture diagrams
│       ├── architecture/            # Current/target state docs
│       ├── adr/                     # Architecture Decision Records
│       ├── assessment/              # Brownfield assessment output
│       └── deliverables/            # Generated .xlsx, .docx, .pptx
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
│       ├── wara_checks/              # 221 WAF assessment checks (APRL-synced, per-pillar)
│       ├── wara_checks.yaml         # Legacy single-file checks (superseded by wara_checks/)
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
│   ├── workflows/             # CI/CD — primary deployment workflows + operational automation
│   │   ├── 1-bootstrap.yml          # One-time MG hierarchy setup
│   │   ├── 2-platform-deploy.yml    # Platform LZ deployments
│   │   ├── 3-app-deploy.yml         # Application LZ deployments
│   │   ├── 4-monitor.yml            # Day-2 compliance + drift scanning (Sentinel)
│   │   ├── 5-pr-validate.yml        # PR validation (lint, security, what-if)
│   │   ├── assess.yml               # Brownfield WAF-aligned assessment
│   │   ├── deploy-on-merge.yml      # Auto-deploy changed LZs on merge to main
│   │   ├── reusable-deploy.yml      # Shared: resolve → validate → plan → deploy → verify
│   │   ├── assign-role.yml          # Utility: RBAC role assignments to SPN
│   │   └── squad-*.yml              # Squad automation (heartbeat, triage, label sync)
│   ├── agents/                # Agent definition files
│   ├── skills/                # Skill SKILL.md entry points
│   └── instructions/          # Per-filetype coding instructions
├── .squad/                    # Squad AI team state (roster, routing, decisions, skills)
│   ├── team.md                      # Authoritative agent roster
│   ├── routing.md                   # Work routing and handoff rules
│   ├── ceremonies.md                # Design reviews and retrospectives
│   ├── agents/                      # Per-agent charters and history
│   ├── skills/                      # Squad-authored skill patterns
│   ├── decisions/                   # Decision log and inbox drop-boxes
│   ├── identity/                    # Current team focus (now.md)
│   └── orchestration-log/           # Session orchestration history
├── pipelines/                 # Legacy / Azure DevOps pipelines
├── docs/                      # Security baseline, cost governance, workflow
│   └── tdd/                   # Generated Technical Design Documents
├── tools/                     # CLI tools and registries
│   ├── apex-recall/           # alz-recall CLI (session state management)
│   ├── registry/              # Agent registry (agent-registry.json)
│   ├── schemas/               # JSON schemas for state files
│   └── scripts/               # Utility scripts
└── tests/                     # 197 tests across 13 test files
```

## Squad — AI Team Collaboration

The accelerator integrates [Copilot Squad](https://docs.github.com/en/copilot/using-github-copilot/using-copilot-coding-agent/about-assigning-tasks-to-copilot#about-copilot-squad) for multi-agent team collaboration. Squad provides a persistent roster of AI agents — each mapped to an APEX workflow step — with structured routing, handoff protocols, sprint ceremonies, and issue-driven automation.

### What Squad Does

Squad wraps the APEX agent workflow with team-level coordination:

- **Persistent roster** — agents retain charters, history, and decision context across sessions
- **Work routing** — incoming requests are triaged and routed to the correct agent(s) via a decision tree
- **Handoff protocols** — structured messages flow between agents with scope, artifacts, blockers, and next actions
- **Sprint ceremonies** — design reviews before multi-agent work and retrospectives after failures
- **Approval gate enforcement** — the Challenger agent reviews outputs at gates with adversarial depth scaled by complexity
- **Issue automation** — GitHub workflows auto-triage `squad`-labeled issues and assign to the right agent

### Agent Roster (Ocean's Eleven Casting)

Each Squad agent maps to an APEX workflow step:

| Squad Agent | Role | APEX Step | Codename |
|-------------|------|-----------|----------|
| Danny | Orchestrator | Workflow routing | Conductor |
| Benedict | Scrum Master | Sprint planning | — |
| Rusty | Requirements | Step 1 | Scribe |
| Linus | Architect | Step 2 | Oracle |
| Basher | Design | Step 3 | Artisan |
| Saul | Governance | Step 3.5 | Warden |
| Reuben | IaC Planner | Step 4 | Strategist |
| Livingston | Bicep Code | Step 5b | Forge |
| Yen | Terraform Code | Step 5t | Forge |
| Frank | Deployment | Step 6 | Envoy |
| Tess | Documentation | Step 7 | Chronicler |
| Turk | Monitoring | Step 8 | Sentinel |
| Virgil | Remediation | Step 9 | Mender |
| Isabel | Challenger | Gates 1,2,4,5 | Challenger |
| Terry | Assessment | Step 0 | Assessor |
| Scribe | Session Logger | Background | — |
| Ralph | Work Monitor | Background | — |

### `.squad/` Directory Structure

| Path | Purpose |
|------|---------|
| `team.md` | Authoritative roster with roles, charters, and status |
| `routing.md` | Work routing decision tree, handoff rules, fan-out/merge patterns |
| `ceremonies.md` | Design review and retrospective triggers and agendas |
| `agents/{name}/` | Per-agent charter, history, and session context |
| `skills/` | Squad-authored skill patterns (e.g., skill authoring, diagram generation) |
| `decisions/` | Decision log with inbox drop-boxes for concurrent writes |
| `identity/now.md` | Current team focus, status, and deferred items |
| `orchestration-log/` | Session-level orchestration history |

### GitHub Automation Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `squad-triage.yml` | `squad` label added | Auto-classify and route issues to agents |
| `squad-issue-assign.yml` | `squad:{agent}` label | Assign ownership to the named agent |
| `squad-heartbeat.yml` | Scheduled | Keep-alive monitoring and backlog motion |

### How Squad and APEX Interact

```
User Request
    │
    ▼
Danny (Orchestrator) ── classifies ──▶ Route to HVE step owner(s)
    │                                       │
    ├── Single step ──────────────────▶ Direct route (e.g., Rusty for requirements)
    ├── Multi-step ───────────────────▶ Fan-out to parallel agents
    ├── Major request ────────────────▶ Benedict + Danny for sprint framing
    └── Approval gate ────────────────▶ Isabel for adversarial review
                                            │
                                     Gate pass/fail
                                            │
                                     Next APEX step
```

Squad agents produce the same artifacts as the APEX workflow agents — the roster adds coordination, history, and team governance on top of the core workflow.

## References

- [Azure Landing Zone Design Areas](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-areas) — CAF
- [Azure Agentic InfraOps (APEX)](https://github.com/jonathan-vella/azure-agentic-infraops) — Patterns & workflow
- [Azure Verified Modules](https://aka.ms/AVM) — IaC module standards

## License

MIT License — See [LICENSE](LICENSE) for details.
