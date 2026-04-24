# Platform Landing Zones

Platform Landing Zones are the shared foundation that all Application Landing
Zones depend on. They must be deployed before any workload subscription.

## Platform Subscription Order

```
[1] platform-management   ← Deploy first (all other LZs log here)
       |
[2] platform-connectivity ← Deploy second (all workloads network here)
       |
[3] platform-identity     ← Deploy third (workloads that need domain join)
       |
[4] platform-security     ← Deploy fourth (SecOps, Sentinel, Defender, SOAR)
       |
[5+] Application LZs      ← corp, online, sandbox, sap ...
```

## Platform Profile Reference

### 1. Management (`platform-management`)

Centralized observability and operations for the entire Azure estate.

| Resource | Details |
|---------|---------|
| Log Analytics Workspace | PerGB2018, 365-day retention (prod), central for all subs |
| Microsoft Sentinel | AAD, Activity, Defender, Office 365 connectors |
| Automation Account | Linked to Log Analytics; start/stop runbooks |
| Update Manager | Weekly critical patches (Sat 02:00), monthly full patches |
| Change Tracking | File and service change detection |
| Recovery Services Vault | Daily + weekly backup policies |

**Key customizations:**
- Log retention (`management.log_analytics.retention_days`)
- Sentinel data connectors (`security.sentinel.data_connectors`)
- Backup policies (`management.backup.policies`)
- Update schedules (`management.update_management.schedules`)

---

### 2. Connectivity (`platform-connectivity`)

Hub networking with selectable topology.

#### Hub-Spoke (default)

```
                    ┌─────────────────────────┐
                    │      Hub VNet            │
                    │  ┌─────────────────────┐ │
                    │  │  Azure Firewall Prem │ │ ← All traffic inspected
                    │  └─────────────────────┘ │
                    │  ┌──────┐ ┌───────────┐  │
                    │  │  ER  │ │ VPN GW    │  │ ← On-prem connectivity
                    │  │  GW  │ │           │  │
                    │  └──────┘ └───────────┘  │
                    │  ┌────────────────────┐  │
                    │  │ Azure Bastion       │  │
                    │  └────────────────────┘  │
                    └───────────┬─────────────┘
                    Peering     │     Peering
              ┌─────────────────┼────────────────┐
              │                 │                 │
        ┌─────▼──────┐  ┌──────▼─────┐  ┌───────▼────┐
        │ Corp Spoke │  │Online Spoke│  │  SAP Spoke │
        └────────────┘  └────────────┘  └────────────┘
```

#### Azure Virtual WAN

```
┌─────────────────────────────────────────────────────┐
│                   Azure Virtual WAN                  │
│  ┌──────────────────────┐  ┌──────────────────────┐ │
│  │  vHub East US 2      │  │  vHub West Europe    │ │
│  │  ┌────────────────┐  │  │  ┌────────────────┐  │ │
│  │  │ Azure Firewall │  │  │  │ Azure Firewall │  │ │
│  │  │ ER/VPN Gateway │  │  │  │ ER/VPN Gateway │  │ │
│  │  └────────────────┘  │  │  └────────────────┘  │ │
│  └──────────────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

**Selecting a topology:**

Set `hub_topology` in your environment override:

```yaml
# src/config/profiles/overrides/prod/platform-connectivity.yaml
networking:
  hub_topology: "hub-spoke"   # or "vwan"
```

Or pass as a parameter at deploy time:

```bash
# Bicep
az deployment sub create \
  --template-file infra/bicep/modules/connectivity/main.bicep \
  --parameters hubTopology=vwan

# Terraform
terraform apply -var="hub_topology=vwan"
```

**Pre-configured Private DNS Zones (20):**

| Zone | Service |
|------|---------|
| `privatelink.database.windows.net` | Azure SQL |
| `privatelink.blob.core.windows.net` | Blob Storage |
| `privatelink.file.core.windows.net` | File Storage |
| `privatelink.vaultcore.azure.net` | Key Vault |
| `privatelink.azurewebsites.net` | App Service |
| `privatelink.azurecr.io` | Container Registry |
| `privatelink.openai.azure.com` | Azure OpenAI |
| `privatelink.servicebus.windows.net` | Service Bus |
| `privatelink.cognitiveservices.azure.com` | Cognitive Services |
| `privatelink.search.windows.net` | AI Search |
| `privatelink.monitor.azure.com` | Azure Monitor |
| `privatelink.ods.opinsights.azure.com` | Log Analytics |
| + 8 more | Storage queue, table, DFS, Synapse, Event Grid, API Management |

**Key customizations:**
- `hub_topology`: `hub-spoke` or `vwan`
- `hub_spoke.azure_firewall.sku_tier`: `Standard` or `Premium`
- `hub_spoke.expressroute_gateway.enabled`: `true` if you have ER
- `hub_spoke.hub_vnet.address_space`: your IP address plan
- `dns_resolver.forwarding_rules`: on-prem DNS server IPs
- `private_dns_zones`: add any zones not in the default list

---

### 3. Identity (`platform-identity`)

Active Directory Domain Services with three deployment modes.

| Mode | When to Use |
|------|------------|
| `adds` | New Azure-only environment with no existing AD |
| `aadds` | Small deployments, no need for GPO or schema extensions |
| `hybrid` | Existing on-prem AD — extend with replica DCs (recommended) |

**Setting the mode:**

```yaml
# src/config/profiles/overrides/prod/platform-identity.yaml
identity:
  mode: "hybrid"              # adds | aadds | hybrid
  domain_name: "corp.contoso.com"
  netbios_name: "CORP"
```

**Key customizations:**
- `identity.mode`: AD DS deployment mode
- `identity.hybrid.domain_controllers.count`: Number of replica DCs (min 2)
- `identity.hybrid.domain_controllers.vm_size`: DC VM size
- `identity.pim.eligible_roles`: PIM role assignments and durations
- `identity.hybrid.domain_controllers.static_private_ips`: Static IPs for DNS

---

### 4. Security (`platform-security`)

Dedicated security operations subscription — enforces separation of duties between SecOps and platform operations.

| Resource | Details |
|---------|---------|
| Microsoft Sentinel | Dedicated workspace, 90-day retention (configurable), onboarding + solution, TI connector (requires Sentinel Contributor role) |
| Microsoft Defender for Cloud | 11 plans enabled (Api plan excluded — requires subPlan), security contacts with alert notifications |
| SOAR Playbooks (Logic Apps) | Block-SuspiciousIP, Isolate-CompromisedVM, Revoke-EntraIDSession, Enrich-ThreatIntel |
| Security Key Vault | Private endpoint only, purge protection, RBAC-authorized |
| Automation Account | SecurityBaseline-Check runbook, SecurityPosture-Report (weekly) |

> **Note:** The deprecated `autoProvisioningSettings` resource has been removed.
> Security contacts use the `2020-01-01-preview` API version. Defender plans deploy
> with `@batchSize(1)` to avoid concurrent update conflicts.

**Sentinel workspace modes:**

| Mode | When to Use |
|------|------------|
| `dedicated` | Recommended — separate workspace for security data, longer retention, independent access control |
| `linked` | Link to management workspace — simpler but no separation of duties on data access |

**Setting the mode:**

```yaml
# src/config/profiles/overrides/prod/platform-security.yaml
security:
  sentinel:
    workspace_mode: "dedicated"    # dedicated | linked
    retention_days: 90             # configurable per environment
```

**SOAR playbook approval gates:**

| Playbook | Auto in Dev? | Auto in Prod? | Rationale |
|----------|-------------|--------------|-----------|
| Block-SuspiciousIP | Simulation only | ✅ Auto | Low user impact, fast containment |
| Isolate-CompromisedVM | Simulation only | ❌ Human approval | High impact — takes VM offline |
| Revoke-EntraIDSession | Simulation only | ❌ Human approval | Direct user impact |
| Enrich-IncidentWithThreatIntel | ✅ Auto | ✅ Auto | Read-only enrichment |

**Key customizations:**
- `sentinel.workspace_mode`: `dedicated` or `linked`
- `sentinel.retention_days`: 90 (dev) to 730 (prod)
- `sentinel.data_connectors`: enable/disable specific connectors
- `defender_for_cloud.plans`: selectively enable plans (dev may use fewer)
- `soar.playbooks[].requires_approval`: per-playbook approval gates
- `soar.playbooks[].simulation_mode`: log-only mode for dev/test

---

## Profile Inheritance & Customization

All Platform profiles use a 3-tier inheritance model:

```
base-platform.yaml           ← Shared defaults for all platform LZs
       ↓
platform-{name}.yaml         ← Profile-specific settings
       ↓
overrides/{env}/{name}.yaml  ← Environment-specific overrides (prod/dev/staging)
```

### Creating a Custom Platform Profile

```python
from src.config.profile_loader import ProfileLoader

loader = ProfileLoader()

# Extend the connectivity profile with custom firewall rules
loader.create_custom_profile(
    name="financial-connectivity",
    inherits="platform-connectivity",
    description="Connectivity profile for financial services with SWIFT compliance",
    overrides={
        "networking": {
            "hub_spoke": {
                "azure_firewall": {
                    "sku_tier": "Premium",
                    "threat_intel_mode": "Deny",
                    "tls_inspection": True,
                }
            },
            "private_dns_zones": [
                "privatelink.database.windows.net",
                "privatelink.blob.core.windows.net",
                # ... add SWIFT-specific zones
            ]
        },
        "governance": {
            "policy_initiatives": [
                "Azure Security Benchmark",
                "PCI DSS 3.2.1",
                "ISO 27001:2013",
            ]
        }
    }
)
```

Custom profiles are saved to `src/config/profiles/custom/` and picked up
automatically by the profile loader and all agents.

### Per-Environment Overrides

Create override files for any environment-specific settings:

```
src/config/profiles/overrides/
├── dev/
│   ├── platform-connectivity.yaml    ← No ER, cheaper Firewall SKU, no DDoS
│   ├── platform-management.yaml      ← 90-day retention, smaller budgets
│   ├── platform-identity.yaml        ← Single DC, no PAWs
│   └── platform-security.yaml        ← Fewer Defender plans, 90-day retention, SOAR simulation mode
├── staging/
│   └── platform-connectivity.yaml
└── prod/
    ├── platform-connectivity.yaml    ← ER enabled, Firewall Premium, DDoS on
    ├── platform-management.yaml      ← 730-day retention, Sentinel rules
    ├── platform-identity.yaml        ← 2 DCs, PAWs, full PIM
    └── platform-security.yaml        ← All 12 Defender plans, 730-day retention, STIX/TAXII, PCI DSS
```

Override files use deep-merge semantics — only specify what differs.

## Deploying Platform Landing Zones

### Option A: GitHub CI/CD (Recommended)

The recommended approach uses GitHub Actions workflows with OIDC authentication,
environment approval gates, and automated compliance validation.

**Application Landing Zone names are fully configurable** — edit
`environments/subscriptions.json` to rename, add, or remove app LZs. The workflows
read this file dynamically at runtime, so no workflow YAML changes are needed.

#### Prerequisites

**Before you begin**, complete the **Bootstrap Settings Checklist** (`docs/ALZ_Bootstrap_Settings_Checklist.xlsx`)
to gather all required values — tenant ID, subscription IDs, management group prefix,
IP addressing, connectivity topology, policy decisions, and approval gate reviewers.
The checklist has three tabs:

| Tab | Purpose |
|-----|---------|
| **Accelerator - Bootstrap** | Core settings: IaC choice, subscriptions (10), OIDC config, GitHub environments, approval gates |
| **Accelerator - Bicep** | Bicep-specific: connectivity topology, Firewall SKU, DDoS, DNS, IP addressing, budgets, Defender plans |
| **Accelerator - Terraform** | Terraform-specific: same as Bicep + state management backend, Sovereign LZ option |

#### Self-Hosted Runners (Optional)

All workflows use `vars.RUNNER_LABEL` to determine the runner. By default this
falls back to `ubuntu-latest` (GitHub-hosted). To use a private self-hosted runner:

1. [Register a self-hosted runner](https://docs.github.com/en/actions/hosting-your-own-runners) on your GitHub repo or org
2. Set the **repository variable** `RUNNER_LABEL` to your runner's label:
   - Go to **Settings → Secrets and variables → Actions → Variables**
   - Create variable: **Name** = `RUNNER_LABEL`, **Value** = `self-hosted` (or your custom label like `alz-runner`)
3. All 6 workflows will automatically use your private runner on the next run

> **Note:** The reusable deploy workflow receives the runner label as an input from the
> calling workflow. No workflow YAML changes are needed — just set the repo variable.

1. Run the OIDC setup script to create federated credentials:

```bash
chmod +x scripts/setup-oidc.sh
./scripts/setup-oidc.sh <your-org> agentic-alz-accelerator alz
```

2. Configure your Application Landing Zones in `environments/subscriptions.json`:

```jsonc
// environments/subscriptions.json — "application" section
// Rename keys, change profiles, add or remove entries to match YOUR workloads.
// Each key becomes a deployment target name in the workflow.
{
  "application": {
    "corp-erp": {                                    // ← your name (any kebab-case key)
      "display_name": "Corp ERP",                    // ← shown in workflow UI
      "subscription_id": "<SUB-5-ID>",               // ← Azure subscription
      "profile": "corp",                             // ← security/networking profile
      "management_group": "landingzones-corp",       // ← which MG to place it in
      "environment": "prod",                         // ← prod or dev
      "github_environment": "app-prod",              // ← approval gate
      "github_secret": "APP_CORP_ERP_SUBSCRIPTION_ID" // ← secret name in GitHub
    }
    // ... add as many as you need
  }
}
```

Valid profiles: `corp`, `online`, `sandbox`, `sap`

3. Set GitHub secrets for platform subscriptions (always required):

| Secret | Subscription |
|--------|-------------|
| `PLATFORM_MGMT_SUBSCRIPTION_ID` | Sub 1 — Management |
| `PLATFORM_CONN_SUBSCRIPTION_ID` | Sub 2 — Connectivity |
| `PLATFORM_IDTY_SUBSCRIPTION_ID` | Sub 3 — Identity |
| `PLATFORM_SEC_SUBSCRIPTION_ID` | Sub 4 — Security |

4. Set a GitHub secret for each app LZ using the `github_secret` name from your config:

| Secret (from config) | Subscription |
|--------|-------------|
| `APP_CORP_ERP_SUBSCRIPTION_ID` | Sub 5 — Corp ERP |
| `APP_CORP_CRM_SUBSCRIPTION_ID` | Sub 6 — Corp CRM |
| `APP_ONLINE_WEB_SUBSCRIPTION_ID` | Sub 7 — Online Web |
| `APP_ONLINE_API_SUBSCRIPTION_ID` | Sub 8 — Online API |
| `APP_SAP_SUBSCRIPTION_ID` | Sub 9 — SAP |
| `APP_SANDBOX_SUBSCRIPTION_ID` | Sub 10 — Sandbox |

> **Tip:** When you add a new app LZ to `subscriptions.json`, just add a matching
> GitHub secret — the workflow picks it up automatically.

3. Configure GitHub environment protection rules:

| Environment | Required Reviewers |
|---|---|
| `platform-management` | platform-team |
| `platform-connectivity` | platform-team, network-team |
| `platform-identity` | platform-team, identity-team |
| `platform-security` | platform-team, security-team |
| `app-prod` | platform-team |
| `app-dev` | *(none — auto-approve)* |
| `remediation` | platform-team, security-team |

#### Workflow Pipeline

```
.github/workflows/
├── 1-bootstrap.yml         ← One-time: MG hierarchy + subscription placement + providers
├── 2-platform-deploy.yml   ← Sequential: Management → Connectivity → Identity → Security
├── 3-app-deploy.yml        ← Parallel: all 6 app LZs (or individual)
├── monitor.yml             ← Scheduled: compliance (30 min), drift (hourly), audit (daily)
├── 5-pr-validate.yml       ← Automatic: lint, security, cost, tests, what-if on PRs
└── reusable-deploy.yml     ← Shared: validate → plan → deploy → verify
```

#### Step 1: Bootstrap (one-time)

```bash
gh workflow run "1 · Bootstrap Landing Zone Foundation" \
  -f mg_prefix=mrg \
  -f primary_location=eastus2 \
  -f action=all
```

Creates the CAF management group hierarchy and moves subscriptions:

```
mrg (root)
├── Platform
│   ├── Management    ← Sub 1
│   ├── Connectivity  ← Sub 2
│   ├── Identity      ← Sub 3
│   └── Security      ← Sub 4
├── Landing Zones
│   ├── Corp          ← Sub 5, Sub 6
│   ├── Online        ← Sub 7, Sub 8
│   └── SAP           ← Sub 9
├── Sandbox           ← Sub 10
└── Decommissioned
```

#### Step 2: Deploy Platform LZs (strict order with approval gates)

```bash
# Plan first (preview what-if output)
gh workflow run "2 · Deploy Platform Landing Zones" \
  -f framework=bicep -f action=plan \
  -f start_from=management -f location=eastus2

# Deploy (each LZ gets its own approval gate)
gh workflow run "2 · Deploy Platform Landing Zones" \
  -f framework=bicep -f action=deploy \
  -f start_from=management -f location=eastus2
```

Pipeline flow:

```
Management ──[approve]──→ Connectivity ──[approve]──→ Identity ──[approve]──→ Security
   (Sub 1)                   (Sub 2)                   (Sub 3)                (Sub 4)
```

Use `start_from` to resume from any point without re-deploying earlier LZs.

#### Step 3: Deploy Application LZs (config-driven, parallel)

The workflow reads `environments/subscriptions.json` and builds a dynamic matrix.
Use the key names from your config file as targets:

```bash
# Deploy all app LZs defined in subscriptions.json
gh workflow run "3 · Deploy Application Landing Zones" \
  -f target=all -f framework=bicep -f action=deploy -f location=eastus2

# Deploy a single app LZ by its config key
gh workflow run "3 · Deploy Application Landing Zones" \
  -f target=corp-erp -f framework=bicep -f action=deploy

# Deploy multiple (comma-separated)
gh workflow run "3 · Deploy Application Landing Zones" \
  -f target=corp-erp,web-portal -f framework=bicep -f action=deploy
```

**To add a new app LZ:** Add an entry to `subscriptions.json`, create the matching
GitHub secret, and run the workflow — no YAML changes required.

#### Step 4: Continuous Monitoring (automatic)

The `monitor.yml` workflow runs on schedule:

| Schedule | Scan Type |
|---|---|
| Every 30 min | Compliance scan across all 10 subscriptions |
| Every hour | Drift detection (compares to baseline) |
| Daily 6 AM | Full audit report |

Violations trigger Teams notifications and auto-remediation (with approval gate).

#### Reusable Deploy Workflow

Every deployment — platform or application — calls `reusable-deploy.yml`:

| Stage | What Happens |
|---|---|
| **Validate** | Profile config, security baseline, cost governance, IaC template lint |
| **Plan** | Bicep what-if or Terraform plan (saved as artifact) |
| **Deploy** | GitHub Environment approval gate → apply changes |
| **Verify** | Capture drift baseline, compliance scan, **generate As-Built TDD**, Teams notification |

#### PR Validation (automatic on every PR)

| Check | Details |
|---|---|
| Lint | Python (ruff), YAML, Bicep, Terraform format |
| Security | `validate_security_baseline.py` on all IaC |
| Cost | `validate_cost_governance.py` (budget alerts required) |
| Tests | Full pytest suite |
| What-If | Bicep what-if on changed profiles, posted as PR comment |

#### As-Built Technical Design Document (TDD)

After every successful deployment, the pipeline automatically generates an as-built
TDD for the deployed landing zone. Each TDD includes:

- **Cover page** with deployment metadata (subscription, profile, timestamp, deployment ID)
- **Architecture diagram** with official Azure icons (SVG → PNG, profile-specific)
- **Resource inventory** from Azure Resource Graph
- **Network topology** (VNet CIDRs, subnets, peering, DNS)
- **Security posture** (6 non-negotiable rules, Defender plans, policy assignments)
- **Compliance status** (live scan results from post-deploy verification)
- **Cost governance** (budgets, alerts, tag requirements)
- **Operational model** (monitoring schedules, change management process, DR)
- **Full estate overview diagram** showing all landing zones

TDDs are uploaded as pipeline artifacts (90-day retention) and saved to `agent-output/{customer}/tdd/`.

```bash
# Generate TDDs manually for all landing zones
python -m src.tools.tdd_generator --all \
  --config environments/subscriptions.json \
  --output-dir docs/tdd --framework bicep

# Generate TDD for a single landing zone
python -m src.tools.tdd_generator \
  --project platform-management \
  --profile platform-management \
  --subscription-id <SUB-1-ID> \
  --subscription-name mrg-platform-management \
  --location eastus2
```

---

### Option B: CLI — Conversational Workflow

```bash
# Step 1: Management (deploy first)
python -m src.agents.orchestrator \
  --mode deploy \
  --profile platform-management \
  --environment prod

# Step 2: Connectivity (hub-spoke, default)
python -m src.agents.orchestrator \
  --mode deploy \
  --profile platform-connectivity \
  --environment prod

# Step 2 (alt): Connectivity with vWAN
python -m src.agents.orchestrator \
  --mode deploy \
  --profile platform-connectivity \
  --environment prod \
  --hub-topology vwan

# Step 3: Identity (hybrid mode)
python -m src.agents.orchestrator \
  --mode deploy \
  --profile platform-identity \
  --environment prod

# Step 4: Security (dedicated Sentinel workspace)
python -m src.agents.orchestrator \
  --mode deploy \
  --profile platform-security \
  --environment prod

# Step 4 (alt): Security with linked workspace (shares management LAW)
python -m src.agents.orchestrator \
  --mode deploy \
  --profile platform-security \
  --environment prod \
  --sentinel-workspace-mode linked
```

### Option C: Bicep Direct

```bash
# Connectivity
az deployment sub create \
  --location eastus2 \
  --template-file infra/bicep/modules/connectivity/main.bicep \
  --parameters \
      prefix=contoso \
      environment=prod \
      hubTopology=hub-spoke \
      deployAzureFirewall=true \
      firewallSkuTier=Premium \
      deployExpressRouteGateway=true \
      budgetAmountUsd=15000

# Security
az deployment sub create \
  --location eastus2 \
  --template-file infra/bicep/modules/platform-security/main.bicep \
  --parameters \
      prefix=contoso \
      environment=prod \
      sentinelWorkspaceMode=dedicated \
      retentionDays=730 \
      securityContactEmail=secops@contoso.com \
      budgetAmountUsd=8000
```

### Option D: Terraform Direct

```bash
cd infra/terraform

# Connectivity
terraform init
terraform apply \
  -var="subscription_id=$AZURE_SUBSCRIPTION_ID" \
  -var="prefix=contoso" \
  -var="environment=prod" \
  -var="hub_topology=hub-spoke" \
  -var="deploy_azure_firewall=true" \
  -var="firewall_sku_tier=Premium" \
  -var="budget_amount_usd=15000"

# Security
terraform apply \
  -var="subscription_id=$AZURE_SEC_SUBSCRIPTION_ID" \
  -var="prefix=contoso" \
  -var="environment=prod" \
  -var="sentinel_workspace_mode=dedicated" \
  -var="retention_days=730" \
  -var="security_contact_email=secops@contoso.com" \
  -var="budget_amount_usd=8000"
```
