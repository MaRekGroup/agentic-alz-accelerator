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

Draw.io files go to `docs/diagrams/`:
- `01-management-group-hierarchy.drawio`
- `02-hub-spoke-network-topology.drawio`
- `03-security-governance-monitoring.drawio`
- `alz-architecture.drawio`

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
