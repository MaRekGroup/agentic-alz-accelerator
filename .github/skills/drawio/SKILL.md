---
name: drawio
description: "Architecture diagram generation using the Draw.io MCP server with Azure icon support. USE FOR: creating .drawio architecture diagrams, Azure topology visualizations. DO NOT USE FOR: Python-based diagram generation (use python-diagrams)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "2.0"
  category: tooling-diagrams
---

# DrawIO Skill

Generate architecture diagrams using the Draw.io MCP server.

## MCP Server

The Draw.io MCP server is configured in `mcp/mcp-config.json` and provides
tools for creating Azure architecture diagrams with official Azure icon libraries.

## When to Use Draw.io vs Python Diagrams

| Use Case | Tool |
|----------|------|
| Quick overview diagrams | Python diagrams (`src/tools/python_diagram_generator.py`) |
| Detailed, editable architecture diagrams | Draw.io MCP |
| Diagrams for documentation/PRs | Draw.io MCP |
| CI/CD generated diagrams | Python diagrams |

## Output Location

Draw.io files go to `agent-output/{customer}/diagrams/`:
- `01-management-group-hierarchy.drawio`
- `02-hub-spoke-network-topology.drawio`
- `03-security-governance-monitoring.drawio`
- `alz-architecture.drawio`

## ALZ Diagram Schema (Zone-Based)

The Artisan generates a **structured JSON intermediate** before rendering to Draw.io.
This schema uses nested zones to represent the ALZ hierarchy and enables consistent,
machine-parseable diagram definitions.

- **Schema definition**: `alz-diagram-schema.json` (JSON Schema draft-07)
- **Few-shot example**: `examples/hub-spoke-topology.json`

### Zone Hierarchy (nesting via `parent` field)

```
tenant → mg → subscription → rg → vnet → subnet
                                        → onprem (peer)
                                        → external (internet)
```

### Zone Kinds

| Kind | Represents | Color |
|------|-----------|-------|
| `tenant` | Entra ID tenant root | Grey |
| `mg` | Management Group | Blue (platform) / Green (landing-zone) |
| `subscription` | Azure Subscription | Light blue |
| `rg` | Resource Group | White with border |
| `vnet` | Virtual Network (include CIDR) | Cyan |
| `subnet` | Subnet (include CIDR) | Light cyan |
| `onprem` | On-premises network | Orange |
| `external` | Internet / external actors | Red outline |

### Edge Types

| Type | Represents | Style |
|------|-----------|-------|
| `network-flow` | Traffic path | Solid |
| `peering` | VNet peering | Solid, bidirectional |
| `private-endpoint` | Private Link connection | Dashed |
| `policy-assignment` | Policy inheritance | Dotted |
| `identity-flow` | Authentication/RBAC | Dashed, pink |
| `monitoring-flow` | Diagnostics/telemetry | Dotted, grey |
| `vpn` | VPN tunnel | Dashed, orange |
| `expressroute` | ExpressRoute circuit | Solid, purple |

### CrossCutting Strip

Platform services rendered as a horizontal bar spanning the diagram:
`Entra ID`, `Azure Policy`, `Defender for Cloud`, `Microsoft Sentinel`, `Cost Management`

### Foundation Strip

Connectivity resources rendered as a bottom bar:
`Hub VNet`, `Azure Firewall`, `VPN/ER Gateway`, `Azure Bastion`, `Private DNS Zones`

### Workflow

Numbered steps (1–N) describing traffic/data flow with `step` badges on edges.

## Diagram Standards

### ALZ Diagrams Must Include

1. **Management Group Hierarchy** — Root → Platform/Landing Zones/Sandbox/Decommissioned
2. **Hub-Spoke Topology** — Hub VNet with Firewall, Bastion, Gateway + spoke peerings
3. **Security Architecture** — Defender, Sentinel, Key Vault, policy flow
4. **Full Estate** — Combined view of all components

### Labeling Rules

- Include CIDR ranges on all VNets and subnets
- Show NSG and route table associations
- Label policy assignments at management group level
- Show identity flow (Entra ID → PIM → RBAC)
- Include budget/cost governance indicators

### Layout Rules (Tier Placement)

- **Top strip**: CrossCutting platform services (Entra ID, Policy, Defender)
- **Middle band**: Primary data-plane workload path (compute → data)
- **Bottom strip**: Foundation connectivity (Hub VNet, Firewall, Gateways)
- **Left**: Ingress / external / on-premises
- **Right**: Data stores / analytics
- Hub at center (radial) or left (flow-LR) depending on diagram type
- Monitoring flows FROM resources TO Log Analytics (never reverse)
- Identity flows FROM Entra ID → PIM → role assignment (top-down)
