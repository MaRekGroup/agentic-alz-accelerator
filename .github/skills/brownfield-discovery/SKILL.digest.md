<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Brownfield Discovery Skill (Digest)

Read-only discovery and inventory of existing Azure environments using KQL
queries against Azure Resource Graph. No resources are created or modified.

## Required Permissions

| Scope | Role | Purpose |
|-------|------|---------|
| Management Group (root) | Reader | MG hierarchy discovery |
| Subscriptions | Reader | Resource inventory |
| Subscriptions | Policy Reader | Policy compliance state |
| Subscriptions | Security Reader | Defender for Cloud posture |

## Discovery Scope Levels

| Scope | Input | What Is Discovered |
|-------|-------|--------------------|
| `tenant` | Tenant ID | All MGs, subscriptions, resources |
| `management_group` | MG name | MGs under parent, subscriptions, resources |
| `subscription` | Subscription ID | Resources, policies, RBAC |
| `resource_group` | RG name + sub ID | Resources in this RG |

## Implementation Reference

- **Module:** `src/tools/discovery.py` — Class: `DiscoveryCollector`
- **Output:** `agent-output/{customer}/assessment/00-discovery.json`

## Key KQL Query Patterns

- Management group hierarchy, subscription inventory
- Resource counts by type and location
- VNet topology with peerings and DNS
- Policy assignments and RBAC role assignments
- Log Analytics workspaces
- Key Vault and Storage Account security posture
- Azure Firewall inventory, Private DNS zones

> _See SKILL.md for full KQL query listings._

## Discovery Output Schema

| Field | Type | Description |
|-------|------|-------------|
| `scope` | string | Target scope identifier |
| `scope_type` | enum | tenant, management_group, subscription, resource_group |
| `discovered_at` | ISO 8601 | Timestamp of discovery run |
| `management_groups` | list | MG hierarchy with parent relationships |
| `subscriptions` | list | Subscriptions with MG placement and tags |
| `resources` | dict | Counts by type, location, and resource group |
| `policy_assignments` | list | Policy assignments with enforcement mode |
| `policy_compliance` | dict | Per-subscription compliance percentages |
| `rbac_assignments` | list | Role assignments with principal info |
| `network_topology` | dict | VNets, peerings, NSGs, DNS zones, firewalls |
| `logging_config` | dict | LAW, automation accounts, diagnostic settings |
| `security_posture` | dict | Key Vaults, Sentinel, storage security |
| `errors` | list | Collector errors (partial results still returned) |

## MCP Tools

| Tool | Description |
|------|-------------|
| `discover_mg_hierarchy` | Management group tree with subscription placement |
| `discover_subscription_inventory` | Subscriptions with resource counts and tags |
| `discover_rbac_snapshot` | Role assignments across scope |
