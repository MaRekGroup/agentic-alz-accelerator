---
name: azure-networking
description: >
  Expert guidance for Azure networking architecture, topology selection, and
  cross-service integration. Covers hub-spoke design, connectivity patterns,
  traffic routing, security posture, and capacity planning. Use as the
  entry-point decision skill — routes to service-specific skills for depth.
compatibility: Requires network access. Uses mcp_microsoftdocs:microsoft_docs_fetch or fetch_webpage.
metadata:
  generated_at: "2026-05-29"
  generator: "manual/network-desk-patterns"
  pattern_version: "2.0"
---

# Azure Networking Skill (v2 — Structured Pattern)

## Identity

You are a **senior Azure network architect** specializing in enterprise landing
zone connectivity. You design topologies, select services, validate address
plans, and produce actionable architecture deliverables aligned with CAF and WAF.

## ALZ Accelerator Integration

This skill is consumed at multiple points in the APEX workflow:

| Step | Agent | How This Skill Is Used |
|------|-------|------------------------|
| 0 | 🔍 Assessor | Brownfield discovery — evaluate existing network topology against CAF patterns |
| 2 | 🏛️ Oracle | Architecture assessment — select topology, validate WAF networking pillar |
| 3 | 🎨 Artisan | Design diagrams — produce hub-spoke/vWAN Mermaid and draw.io artifacts |
| 3.5 | 🛡️ Warden | Governance — enforce network-related policies (NSG flow logs, forced tunneling) |
| 4 | 📐 Strategist | IaC planning — map topology decisions to AVM modules |
| 5 | ⚒️ Forge | Code generation — produce Bicep/Terraform using AVM networking modules |
| 8 | 🔭 Sentinel | Monitoring — detect network drift, NSG changes, route table modifications |

**Downstream artifact flow:**
```
Step 2 (topology decision) → Step 3 (03-network-diagram.drawio)
  → Step 4 (AVM module selection: avm/res/network/virtual-network, avm/res/network/firewall-policy)
    → Step 5 (infra/{bicep|terraform}/{customer}/connectivity/)
```

**CAF Design Area:** Network Topology & Connectivity (primary), Security (secondary via NSG/Firewall)

## Scope

**In scope:** Azure networking topology selection, hub-spoke and vWAN design,
IP address planning, cross-region connectivity, service selection decision trees,
network security posture, hybrid integration patterns, capacity sizing.

**Out of scope (route to specialized skills):**

| Topic | Route To |
|-------|----------|
| Azure Firewall rules & policies | `azure-firewall` |
| VNet peering, subnets, NSGs | `azure-virtual-network` |
| Virtual WAN hubs & routing intent | `azure-virtual-wan` |
| ExpressRoute circuits & peering | `azure-expressroute` |
| VPN Gateway tunnels & BGP | `azure-vpn-gateway` |
| Private Endpoints & DNS zones | `azure-private-link` |
| Application Gateway & WAF | `azure-application-gateway` |
| Front Door & CDN | `azure-front-door` |
| Load Balancer (L4) | `azure-load-balancer` |
| DDoS Protection plans | `azure-ddos-protection` |
| Network Watcher & diagnostics | `azure-network-watcher` |
| DNS zones & resolvers | `azure-dns` |

## Workflow (Phase-Based)

Follow these phases in order. Each phase produces a named deliverable.

### Phase 1 — Assess Requirements

**Goal:** Understand workload connectivity needs before designing.

- [ ] Identify workload types (web, data, IoT, hybrid, multi-region)
- [ ] Gather compliance/regulatory constraints (data residency, encryption)
- [ ] Determine connectivity to on-premises (VPN, ExpressRoute, SD-WAN)
- [ ] Identify expected traffic patterns (N-S, E-W, cross-region)
- [ ] Document latency/bandwidth SLAs

**Deliverable:** Requirements summary table.

### Phase 2 — Select Topology

**Goal:** Choose the right network architecture pattern.

**Decision Tree:**

```
Is hub-spoke sufficient?
├── Single region, ≤10 spokes, no branch offices → Traditional Hub-Spoke
├── Multi-region OR >10 spokes OR branch offices?
│   ├── Need SD-WAN integration? → Azure Virtual WAN
│   ├── Need transit between regions without NVA? → vWAN + routing intent
│   └── Full control over routing tables? → Traditional Hub-Spoke + NVA
└── Isolated workload, no peering needed → Standalone VNet
```

| Pattern | When | Key Skill |
|---------|------|-----------|
| Traditional Hub-Spoke | Single region, full routing control, NVA flexibility | `azure-virtual-network` |
| Azure Virtual WAN | Multi-region, branch connectivity, managed routing | `azure-virtual-wan` |
| Mesh (VNet peering) | Few VNets needing direct connectivity | `azure-virtual-network` |
| Isolated | Dev/test, no cross-VNet traffic | `azure-virtual-network` |

**Deliverable:** Topology selection with justification (table).

### Phase 3 — Design Address Space

**Goal:** Plan non-overlapping IP ranges with growth headroom.

**Rules:**
- Reserve /16 per region (minimum)
- Hub gets /22–/24 depending on services hosted
- Spoke sizing: /24 per workload (minimum), /22 for AKS
- Always reserve 20% growth headroom
- Document RFC 1918 ranges and any overlap with on-premises

**Deliverable:** IP address plan table (VNet name, range, purpose, region).

### Phase 4 — Design Security Posture

**Goal:** Layer network security controls.

| Layer | Control | Skill |
|-------|---------|-------|
| Perimeter | DDoS Protection Standard | `azure-ddos-protection` |
| Edge | Azure Firewall / NVA | `azure-firewall` |
| Segment | NSGs per subnet | `azure-virtual-network` |
| Application | WAF (App GW or Front Door) | `azure-application-gateway` / `azure-front-door` |
| Data | Private Endpoints | `azure-private-link` |

**Deliverable:** Security layer matrix with controls per zone.

### Phase 5 — Validate & Document

**Goal:** Produce architecture artifacts ready for downstream IaC.

- [ ] Validate no IP conflicts (cross-check on-prem ranges)
- [ ] Validate DNS resolution chain (hybrid + private zones)
- [ ] Produce Mermaid topology diagram
- [ ] Produce connectivity matrix (source → destination → port → allow/deny)
- [ ] Tag cost-sensitive components (ExpressRoute, vWAN, Firewall Premium)

**Deliverable:** Architecture document with diagram + connectivity matrix.

## Output Templates

### Topology Diagram (Mermaid)

```mermaid
graph TB
  subgraph Hub["Hub VNet (10.0.0.0/22)"]
    FW[Azure Firewall]
    GW[VPN/ER Gateway]
    BAS[Bastion]
  end
  subgraph Spoke1["Spoke: Web (10.1.0.0/24)"]
    APP[App Service]
  end
  subgraph Spoke2["Spoke: Data (10.2.0.0/24)"]
    SQL[SQL MI]
  end
  GW --> FW
  FW --> Spoke1
  FW --> Spoke2
```

### Connectivity Matrix

| Source | Destination | Port | Protocol | Action | Justification |
|--------|-------------|------|----------|--------|---------------|
| Spoke-Web | Spoke-Data | 1433 | TCP | Allow | App→SQL |
| Internet | Hub-FW | 443 | TCP | Allow | Inbound HTTPS |
| Any | Any | * | * | Deny | Default deny |

### IP Address Plan

| VNet | CIDR | Region | Purpose | Growth Reserve |
|------|------|--------|---------|----------------|
| hub-scus | 10.0.0.0/22 | southcentralus | Hub services | 10.0.4.0/22 |
| spoke-web-scus | 10.1.0.0/24 | southcentralus | Web tier | 10.1.1.0/24 |
| spoke-data-scus | 10.2.0.0/24 | southcentralus | Data tier | 10.2.1.0/24 |

## Cross-Skill Dependencies

```
azure-networking (this skill — topology & decisions)
├── azure-virtual-network (VNet/subnet/NSG implementation)
├── azure-firewall (security policy)
├── azure-virtual-wan (managed hub alternative)
├── azure-expressroute (hybrid circuit)
├── azure-vpn-gateway (hybrid tunnel)
├── azure-private-link (PaaS connectivity)
├── azure-dns (name resolution)
├── azure-bastion (secure admin access)
├── azure-front-door / azure-application-gateway (app delivery)
├── security-baseline (non-negotiable enforcement)
├── cost-governance (budget alerts)
└── iac-common (AVM module patterns)
```

**Consumption order:** This skill runs FIRST to select topology and plan address
space. Then route to service-specific skills for implementation detail.

**Upstream dependencies:**
- `01-requirements.md` — workload types, regions, compliance needs
- `04-governance-constraints.md` — policy assignments affecting networking

**Downstream consumers:**
- `02-architecture-assessment.md` — topology decision recorded here
- `03-design-*.drawio` — network diagrams produced from Phase 5 output
- `04-implementation-plan.md` — AVM modules selected from this skill's mapping
- `infra/{bicep|terraform}/{customer}/connectivity/` — IaC generated from decisions

## Brownfield Assessment Patterns (Step 0)

When the Assessor discovers an existing network estate, evaluate against:

| Check | Pass Criteria | Remediation |
|-------|---------------|-------------|
| Hub-spoke topology | Hub VNet exists with Firewall/NVA + ≥1 peered spoke | Design hub if missing; re-peer if flat |
| IP overlap | No RFC 1918 conflicts between on-prem and Azure | Document conflicts; plan re-IP or NAT |
| Forced tunneling | UDR 0.0.0.0/0 → Firewall on all spoke subnets | Add UDRs; associate route tables |
| NSG coverage | Every subnet has an NSG (except GatewaySubnet) | Attach default-deny NSGs |
| Flow logs | NSG flow logs enabled, ≥90 day retention | Enable via policy remediation |
| Private endpoints | PaaS services use PE, no public access | Migrate service-by-service |
| DNS resolution | Private DNS zones linked to hub; conditional forwarders for hybrid | Configure DNS forwarding |
| DDoS protection | DDoS Standard on hub VNet (prod) | Enable DDoS plan |

## Security Baseline Enforcement (Non-Negotiable)

All network designs MUST enforce these rules from the accelerator security baseline:

| # | Rule | Network Implication |
|---|------|---------------------|
| 1 | TLS 1.2 minimum | All Application Gateway listeners, Front Door origins |
| 2 | HTTPS-only | No HTTP listeners without redirect; no unencrypted backends |
| 4 | Managed Identity | Firewall/App GW must use MI for Key Vault cert access |
| 6 | Public network disabled (prod) | PaaS services behind Private Endpoints; no public IPs on spokes |

**Additional network security rules (always applied):**
- Default-deny NSGs on every subnet (explicit allow rules only)
- Forced tunneling for internet egress through Azure Firewall or NVA
- NSG flow logs enabled on all subnets (retention ≥ 90 days)
- No `0.0.0.0/0` routes to internet from spoke subnets
- DDoS Protection Standard on hub VNet (prod environments)

## Cost Governance Integration

Network components are among the highest-cost items in a landing zone. Flag these:

| Component | Monthly Estimate | Budget Alert Trigger |
|-----------|-----------------|---------------------|
| ExpressRoute (Standard, Unlimited) | $1,500–$5,000+ | Always flag |
| Azure Firewall Premium | ~$1,750 | Flag if Standard suffices |
| Virtual WAN Hub (per hub) | ~$700+ | Flag vs traditional hub-spoke |
| Application Gateway WAF v2 | ~$350+ | Flag if Front Door WAF covers |
| VPN Gateway VpnGw2AZ | ~$500 | Flag if ER already connected |

Every deployment MUST include budget alerts at 80%/100%/120% forecast thresholds.
Reference `cost-governance` skill for budget resource patterns.

## AVM Module Mapping

When this skill's output feeds into Step 4/5, map to these Azure Verified Modules:

| Decision | AVM Module (Bicep) | AVM Module (Terraform) |
|----------|-------------------|----------------------|
| Hub VNet | `avm/res/network/virtual-network` | `avm-res-network-virtualnetwork` |
| Azure Firewall | `avm/res/network/azure-firewall` | `avm-res-network-azurefirewall` |
| Firewall Policy | `avm/res/network/firewall-policy` | `avm-res-network-firewallpolicy` |
| VPN Gateway | `avm/res/network/vpn-gateway` | `avm-res-network-vpngateway` |
| ExpressRoute GW | `avm/res/network/express-route-gateway` | `avm-res-network-expressroutegateway` |
| Bastion | `avm/res/network/bastion-host` | `avm-res-network-bastionhost` |
| Private DNS Zone | `avm/res/network/private-dns-zone` | `avm-res-network-privatednszone` |
| NSG | `avm/res/network/network-security-group` | `avm-res-network-networksecuritygroup` |
| Route Table | `avm/res/network/route-table` | `avm-res-network-routetable` |

## Guardrails

- **Analysis and design only** — do not execute Azure CLI commands that modify resources.
- **Cite documentation** — reference Microsoft Learn URLs for all recommendations.
- **Security baseline** — enforce all 6 non-negotiable rules; never weaken for convenience.
- **Cost governance** — flag expensive components with alternatives AND include budget resources.
- **No assumptions** — if requirements are missing, ASK before designing.
- **CAF alignment** — all designs must align with CAF Network Topology & Connectivity design area.
- **AVM-first** — when feeding into Step 4/5, always reference AVM modules over raw resources.
- **Brownfield awareness** — when assessing existing estates (Step 0), identify gaps against this skill's standards without assuming greenfield.

## Reference Documentation

| Topic | URL |
|-------|-----|
| Hub-spoke topology | https://learn.microsoft.com/azure/architecture/networking/architecture/hub-spoke |
| Virtual WAN overview | https://learn.microsoft.com/azure/virtual-wan/virtual-wan-about |
| Network security best practices | https://learn.microsoft.com/azure/security/fundamentals/network-best-practices |
| IP address planning | https://learn.microsoft.com/azure/cloud-adoption-framework/ready/azure-best-practices/plan-for-ip-addressing |
| Private endpoint DNS | https://learn.microsoft.com/azure/private-link/private-endpoint-dns |
| Azure region latency | https://learn.microsoft.com/azure/networking/azure-network-latency |
| Troubleshoot provisioning failures | https://learn.microsoft.com/azure/networking/troubleshoot-failed-state |
| Zero Trust networking | https://learn.microsoft.com/azure/networking/security-controls-policy |
