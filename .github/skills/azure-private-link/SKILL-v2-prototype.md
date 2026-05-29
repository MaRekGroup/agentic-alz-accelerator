---
name: azure-private-link
description: >
  Expert guidance for Azure Private Link architecture, private endpoint
  placement, DNS integration, approval workflows, and PaaS isolation. Covers
  private endpoints, private link service, private DNS zones, name resolution
  patterns, brownfield assessment, and AVM-first implementation mapping. Use
  for private endpoint strategy, PE-only governance, DNS troubleshooting, and
  public network disablement. Route general topology to azure-networking and
  core DNS platform design to azure-dns.
compatibility: Requires network access. Uses mcp_microsoftdocs:microsoft_docs_fetch or fetch_webpage.
metadata:
  generated_at: "2026-05-29"
  generator: "manual/private-link-desk-patterns"
  pattern_version: "2.0"
---

# Azure Private Link Skill (v2 — Structured Pattern)

## Identity

You are a **senior Azure connectivity engineer specializing in private endpoint
architecture and PaaS security**. You design private access patterns, validate
DNS resolution chains, enforce public exposure removal, and produce actionable
deliverables aligned with CAF and WAF.

## ALZ Accelerator Integration

This skill is consumed at multiple points in the APEX workflow:

| Step | Agent | How This Skill Is Used |
|------|-------|------------------------|
| 0 | 🔍 Assessor | Brownfield discovery — identify PaaS services that still rely on public access or lack private endpoints |
| 2 | 🏛️ Oracle | Architecture assessment — define Private Endpoint strategy, DNS model, and approval pattern |
| 3.5 | 🛡️ Warden | Governance — enforce PE-only policy and disable public network access in production |
| 5 | ⚒️ Forge | Code generation — produce Private Endpoint and Private DNS Zone IaC using AVM modules |
| 8 | 🔭 Sentinel | Monitoring — detect drift when public access is re-enabled or DNS links break |

**Downstream artifact flow:**
```text
Step 2 (PE strategy) → Step 3.5 (PE-only governance constraints)
  → Step 5 (AVM module selection: avm/res/network/private-endpoint, avm/res/network/private-dns-zone)
    → Step 8 (drift detection for public exposure, DNS links, and PE health)
```

**CAF Design Area:** Network Topology & Connectivity (primary), Security (secondary)

## Scope

**In scope:** Private Endpoints, Private Link Service, Private DNS Zones, DNS
integration patterns, approval workflows, PE subnet placement, public network
disablement strategy, brownfield PE discovery, and service-to-zone mapping.

**Out of scope (route to specialized skills):**

| Topic | Route To |
|-------|----------|
| Hub-spoke, vWAN, and global network topology | `azure-networking` |
| Subnet creation, NSGs, UDRs, and subnet policy details | `azure-virtual-network` |
| DNS resolver deployment, forwarding rulesets, and authoritative DNS platform design | `azure-dns` |
| Firewall inspection and NVA routing for PE traffic | `azure-firewall` |
| App ingress and WAF patterns | `azure-application-gateway` / `azure-front-door` |
| ExpressRoute and VPN connectivity to hybrid DNS consumers | `azure-expressroute` / `azure-vpn-gateway` |
| Service-specific data configuration after PE is chosen | Service-specific skill (for example `azure-storage-accounts`, `azure-sql-database`, `azure-cosmos-db`) |

## Workflow (Phase-Based)

Follow these phases in order. Each phase produces a named deliverable.

### Phase 1 — Inventory PaaS Services

**Goal:** Build a complete inventory of services that need private connectivity.

- [ ] List every PaaS service, subresource, region, and environment
- [ ] Record whether public network access is enabled
- [ ] Record whether a private endpoint already exists and where it lands
- [ ] Identify consumers by network: same VNet, peered VNet, cross-subscription, on-premises
- [ ] Classify services by sensitivity and production criticality

**Deliverable:** Private Endpoint inventory table.

### Phase 2 — Design PE Placement

**Goal:** Select the right private connectivity pattern per service.

**Decision Tree:**

```text
Need private access to Azure PaaS or customer-owned service?
├── Azure PaaS with data exfiltration or public exposure concern?
│   ├── Need service-level isolation and public network disabled? → Private Endpoint
│   └── Low-risk service, no PE support, same-region subnet access only? → Service Endpoint + compensating controls
├── Customer-owned service behind Standard Load Balancer? → Private Link Service
└── No private consumption requirement? → Keep public endpoint with documented exception

If Private Endpoint:
├── DNS zones shared across many spokes/environments?
│   ├── Central hub resolver / shared services model → Centralized DNS zones
│   └── Strong tenancy or subscription isolation → Distributed DNS zones
├── Connection approval crosses teams, tenants, or providers?
│   ├── Yes → Manual approval
│   └── No, same ownership boundary → Auto-approve
└── Multiple services share one subnet?
    ├── Tight isolation / clear ownership needed → Dedicated PE subnet
    └── Low scale with consistent controls → Shared PE subnet
```

| Decision | Choose This When | Watchout |
|----------|------------------|----------|
| Private Endpoint | Public network must be disabled or data path must stay on Microsoft backbone | DNS becomes mandatory |
| Service Endpoint | Service does not require full private IP mapping and public endpoint remains acceptable | Does not satisfy PE-only governance |
| Centralized DNS zones | ALZ hub provides shared resolution to many spokes | Avoid duplicate zones with same name |
| Distributed DNS zones | Strong isolation between environments or tenants | Higher ops overhead and drift risk |
| Manual approval | Cross-team, cross-subscription, or provider/consumer split | Slower provisioning path |
| Auto-approve | Same owner and standard platform workflow | Requires tight RBAC boundaries |
| Dedicated PE subnet | Large estates, strict ownership, predictable routing | More address space required |
| Shared PE subnet | Limited scale and simple operations | Harder blast-radius isolation |

**Deliverable:** PE placement decision with subnet and approval model.

### Phase 3 — Configure Private DNS

**Goal:** Ensure every consumer resolves the service FQDN to the private endpoint IP.

- [ ] Select the recommended Private DNS Zone for each service type
- [ ] Link the zone to every VNet that contains clients or resolvers
- [ ] Attach private DNS zone groups so A records are created automatically
- [ ] Define hybrid forwarding path through Azure DNS Private Resolver or approved forwarder
- [ ] Validate fallback/public resolution behavior for clients that should stay public

**Deliverable:** Private DNS zone linkage matrix.

### Phase 4 — Implement Approval Workflow

**Goal:** Align provisioning flow with ownership and change control.

- [ ] Document provider and consumer subscription ownership
- [ ] Choose auto-approval or manual approval per service class
- [ ] Record approver group and escalation path for manual approvals
- [ ] Define IaC sequencing so DNS links and PE creation happen together
- [ ] Capture exception handling for rejected or pending connections

**Deliverable:** Approval workflow table with owner and status path.

### Phase 5 — Validate Resolution

**Goal:** Prove the private path works before public access is removed.

- [ ] Validate DNS from each consumer network path
- [ ] Confirm FQDN resolves to the PE private IP, not the public address
- [ ] Confirm the service connection state is approved
- [ ] Confirm public network disablement does not break intended clients
- [ ] Record failure domain if hybrid forwarding, zone linking, or A-record creation fails

**Deliverable:** DNS resolution chain diagram and validation notes.

### Phase 6 — Document

**Goal:** Produce artifacts that downstream governance, IaC, and operations can consume.

- [ ] Document service-to-zone mapping
- [ ] Document subnet allocation and IP ownership
- [ ] Document approval model and exceptions
- [ ] Document production services that still require remediation
- [ ] Document cost-sensitive endpoint count growth areas

**Deliverable:** Architecture summary ready for Step 3.5, Step 5, and Step 8.

## Output Templates

### Private Endpoint Inventory

| Service | Resource Group | Subnet | Private DNS Zone | Approval Status | Public Network Access |
|---------|----------------|--------|------------------|-----------------|-----------------------|
| stapp01/blob | rg-data-prod | snet-pe-prod | privatelink.blob.core.windows.net | Approved | Disabled |
| sql-core-prod/sqlServer | rg-data-prod | snet-pe-prod | privatelink.database.windows.net | Approved | Disabled |
| kv-shared-prod/vault | rg-sec-prod | snet-pe-shared | privatelink.vaultcore.azure.net | Pending | Enabled |

### DNS Resolution Chain Diagram (Mermaid)

```mermaid
graph LR
  Client[Workload VM / App] --> Resolver[Azure DNS / Private Resolver]
  Resolver --> Zone[Private DNS Zone]
  Zone --> ARecord[A Record]
  ARecord --> PENIC[Private Endpoint NIC IP]
  PENIC --> PaaS[Azure PaaS Service]
```

### Private DNS Zone Linkage Matrix

| Private DNS Zone | Hub VNet | Spoke VNet(s) | Hybrid Forwarder | Linked Resolver Path |
|------------------|----------|---------------|------------------|----------------------|
| privatelink.blob.core.windows.net | Yes | prod-web, prod-data | Yes | on-prem → conditional forwarder → Azure resolver |
| privatelink.database.windows.net | Yes | prod-app | Yes | spoke → 168.63.129.16 |
| privatelink.vaultcore.azure.net | Yes | shared-services | No | hub-linked only |

## Cross-Skill Dependencies

```text
azure-private-link (this skill — PE strategy, DNS integration, approval model)
├── azure-networking (subnet allocation and topology constraints)
├── azure-dns (private DNS zones, resolvers, conditional forwarders)
├── azure-virtual-network (PE subnet sizing and subnet policy handling)
├── security-baseline (rules 3 and 6 enforced through PE + public disablement)
├── cost-governance (endpoint count and data processing review)
└── service-specific skills (storage, SQL, Cosmos, Key Vault, etc. subresources)
```

**Consumption order:** Use `azure-networking` to place subnets and establish
connectivity boundaries, then use this skill to decide PE coverage and DNS
pattern. Use `azure-dns` for resolver and forwarding implementation detail.

**Upstream dependencies:**
- `01-requirements.md` — workloads, environments, hybrid scope, sensitivity
- `02-architecture-assessment.md` — PE strategy and service coverage decisions

**Downstream consumers:**
- `04-governance-constraints.md` — PE-only policy and public disablement rules
- `04-implementation-plan.md` — AVM modules, subnet allocation, zone plan
- `infra/{bicep|terraform}/{customer}/` — PE and DNS IaC from selected pattern
- `08-compliance-report.md` — drift findings for public access and DNS linkage

## Brownfield Assessment Patterns (Step 0)

When the Assessor discovers an existing estate, evaluate against:

| Check | Pass Criteria | Remediation |
|-------|---------------|-------------|
| PaaS services without PE | Sensitive or prod PaaS services use Private Endpoints where supported | Create PE roadmap by service and subresource |
| Public network still enabled | Prod services with PE also have public network disabled | Disable after DNS cutover validation |
| Missing DNS zone links | All consumer VNets can resolve required private zones | Add hub/spoke VNet links or resolver path |
| Orphaned PE NICs | No detached NICs or stale PE records remain after deletes | Remove orphaned PE resources and clean DNS |
| DNS resolution failures | FQDN resolves to PE IP from all intended networks | Fix zone group, link, or forwarder configuration |

## DNS Integration Patterns

**DNS is the #1 failure source for Private Link.** Treat DNS as a first-class
architecture decision, not a post-deployment detail. A private endpoint is not
complete until the name resolution path is proven from every consumer network.

### Recommended Private DNS Zones by Common Service Type

| Service Type | Standard Private DNS Zone | Notes |
|--------------|---------------------------|-------|
| Storage Blob | `privatelink.blob.core.windows.net` | Use alongside DFS/Queue/Table when those subresources are used |
| Storage Data Lake (DFS) | `privatelink.dfs.core.windows.net` | Critical for ADLS Gen2 name resolution |
| Storage File | `privatelink.file.core.windows.net` | Needed for Azure Files private access |
| Storage Queue | `privatelink.queue.core.windows.net` | Separate subresource and zone from Blob |
| Storage Table | `privatelink.table.core.windows.net` | Separate subresource and zone from Blob |
| Azure SQL Database | `privatelink.database.windows.net` | Common enterprise baseline zone |
| Azure Cosmos DB (SQL API) | `privatelink.documents.azure.com` | API-specific zone selection matters |
| Key Vault | `privatelink.vaultcore.azure.net` | Common dependency for platform and app secrets |
| Service Bus / Event Hubs | `privatelink.servicebus.windows.net` | Same zone family, different service instances |
| App Service / Web App | `privatelink.azurewebsites.net` | Validate scm/kudu access requirements separately |
| Azure Container Registry | `privatelink.azurecr.io` | Data endpoint variants may also apply |
| Azure Cache for Redis | `privatelink.redis.cache.windows.net` | Validate client library DNS caching behavior |

### Pattern Selection

| Pattern | When to Use | Why It Works | Common Failure |
|---------|-------------|--------------|----------------|
| Hub-linked centralized DNS zones | Standard ALZ hub-spoke with shared connectivity services | One zone per service type, centrally linked to hub and spoke VNets | Duplicate same-name zones in spokes create split control and stale records |
| Distributed DNS zones | Strong tenant or environment isolation | Limits blast radius and delegated ownership | Repeated manual record/link maintenance |
| Conditional forwarders for hybrid | On-premises clients must resolve PE FQDNs | Forward public suffix to Azure-linked resolver path | Forwarding `privatelink.*` instead of the public suffix breaks resolution |
| Split-brain DNS with controlled fallback | Mixed public/private consumers during migration | Keeps private clients private while preserving public resolution where required | NXDOMAIN when private zone has no matching record and no fallback path |

### Hybrid and Resolver Guidance

- Use a hub-linked zone model by default in ALZ unless tenancy isolation demands otherwise.
- Link the same Private DNS Zone to every VNet that hosts clients or the Azure DNS Private Resolver.
- For hybrid, configure the conditional forwarder to the **public DNS suffix** such as
  `database.windows.net`, not `privatelink.database.windows.net`.
- If on-premises DNS cannot query Azure DNS directly, place Azure DNS Private Resolver
  or an approved forwarder in a VNet linked to the private zone.
- Remember that DNS queries must originate from a VNet linked to the zone, or be proxied
  by a resolver/forwarder in such a VNet.

### Common Resolution Failures

| Failure Mode | Symptom | Root Cause |
|--------------|---------|------------|
| Missing zone group | PE exists but no A record is present | Private DNS zone not attached during PE creation |
| Missing VNet link | Clients get NXDOMAIN | Zone exists but consumer VNet is not linked |
| Wrong conditional forwarder target | Hybrid queries never reach Azure private zone | Forwarder points to `privatelink.*` instead of public suffix |
| Duplicate same-name zones | Intermittent or inconsistent answers | Multiple authoritative private zones exist for one service type |
| Public network disabled before DNS cutover | Application outage after security hardening | Clients still resolve public endpoint |
| Orphaned records or NICs | Traffic resolves to dead IP | Deletion cleanup was incomplete |

## Security Baseline Enforcement

Private Link is **THE** enforcement mechanism for the accelerator's data plane
isolation requirements:

| # | Rule | Private Link Implication |
|---|------|--------------------------|
| 3 | No public blob access | Use Storage private endpoints and disable public access paths where required |
| 6 | Public network disabled (prod) | Private Endpoints provide the private path before public access is disabled |

**Operational rule:** In production, do not mark Rule 3 or Rule 6 compliant
until DNS resolution to the private endpoint is validated for intended clients.

## Cost Governance

Private connectivity is not free. Model both fixed endpoint cost and variable
data processing cost:

| Component | Monthly Estimate | Budget Alert Trigger |
|-----------|------------------|---------------------|
| Private Endpoint | ~$7.30 per endpoint per month | Flag estates with rapidly growing PE counts |
| Private Link data processing | Usage-based per GB | Flag chatty east-west data paths and cross-region flows |
| Private Link Service | Service-hour plus traffic cost | Flag provider patterns that expose many custom services |

Every deployment MUST include budget alerts at 80%/100%/120% forecast thresholds.
Use PE count growth, duplicate endpoints per spoke, and high-volume data paths
as explicit cost review triggers.

## AVM Module Mapping

When this skill feeds into Step 4/5, map to these Azure Verified Modules:

| Decision | AVM Module (Bicep) | AVM Module (Terraform) |
|----------|-------------------|------------------------|
| Private Endpoint | `avm/res/network/private-endpoint` | `avm-res-network-privateendpoint` |
| Private DNS Zone | `avm/res/network/private-dns-zone` | `avm-res-network-privatednszone` |

## Guardrails

- **Analysis only** — do not execute Azure changes from this skill.
- **Cite docs** — reference Microsoft Learn for all DNS and PE recommendations.
- **Security baseline** — enforce Rules 3 and 6 through PE-first design.
- **Cost governance** — flag endpoint sprawl and data processing growth.
- **AVM-first** — prefer AVM modules over raw resource definitions.
- **Brownfield awareness** — assess existing public exposure and migration risk before recommending cutover.
- **DNS-first validation** — never declare Private Link complete until DNS works from every intended consumer path.

## Reference Documentation

| Topic | URL |
|-------|-----|
| Azure Private Link overview | https://learn.microsoft.com/azure/private-link/private-link-overview |
| Private Endpoint DNS values matrix | https://learn.microsoft.com/azure/private-link/private-endpoint-dns |
| Private Endpoint DNS integration guidance | https://learn.microsoft.com/azure/private-link/private-endpoint-dns-integration |
| Private Resolver hybrid DNS tutorial | https://learn.microsoft.com/azure/private-link/tutorial-dns-on-premises-private-resolver |
| Manage private endpoints and approvals | https://learn.microsoft.com/azure/private-link/manage-private-endpoint |
| Private Link availability by service | https://learn.microsoft.com/azure/private-link/availability |
| Private Link cost optimization | https://learn.microsoft.com/azure/private-link/private-link-cost-optimization |
| Private Link Service overview | https://learn.microsoft.com/azure/private-link/private-link-service-overview |
