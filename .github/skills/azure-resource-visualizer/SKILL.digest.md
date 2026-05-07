<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Azure Resource Visualizer Skill (Digest)

Analyze deployed ALZ resources via Resource Graph and generate Mermaid architecture diagrams.

## When to Use

- Post-deployment visualization of platform or application LZs
- Brownfield assessment — visualizing existing estate
- Drift detection — comparing live state to expected architecture
- Step 7 documentation — generating as-built diagrams

## Workflow

| Step | Action |
|------|--------|
| 1. Scope Selection | Full estate, platform LZ, app LZ, or resource group |
| 2. Resource Discovery | Azure Resource Graph KQL queries for cross-subscription inventory |
| 3. Relationship Mapping | Network, peering, diagnostics, private endpoints, identity, Key Vault, LAW |
| 4. Diagram Generation | Mermaid diagrams organized by CAF design area |
| 5. File Output | `agent-output/{customer}/diagrams/{scope}-architecture.md` + inventory |

## Relationship Types

| Type | How to Detect |
|------|---------------|
| Network (VNet→Subnet→NIC) | `properties.subnets`, `properties.ipConfigurations` |
| Peering (VNet↔VNet) | `virtualNetworkPeerings` resources |
| Diagnostic settings | `microsoft.insights/diagnosticSettings` |
| Private endpoints | `privateLinkServiceConnections` |
| Managed Identity | `identity.principalId` |
| Log Analytics | `properties.workspaceId` |

## Diagram Construction Rules

- **Grouping:** Management, Connectivity, Identity, Security subgraphs
- **Arrows:** Solid (`-->`) data flow, dashed (`-.->`) monitoring, thick (`==>`) critical path
- **Node labels:** `ResourceType<br/>name<br/>Key Detail (SKU/Tier)`
- **Required elements:** All RGs with resources, cross-resource relationships, CAF labels, SKU annotations, security indicators

## Integration

| Skill | Integration |
|-------|-------------|
| `brownfield-discovery` | Initial resource inventory |
| `azure-diagnostics` | KQL queries for Resource Graph |
| `mermaid` | Diagram syntax conventions |
| `assessment-report` | Visualization in assessment outputs |

## Constraints

- Read-only — never create/modify/delete resources
- Resource Graph preferred over per-resource ARM queries
- Diagrams must render in GitHub markdown (Mermaid)
- 50+ resources → split by CAF design area

> _See SKILL.md for full KQL queries and Mermaid diagram examples._
