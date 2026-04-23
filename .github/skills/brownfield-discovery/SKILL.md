---
name: brownfield-discovery
description: "KQL query patterns and inventory collectors for discovering existing Azure environments. USE FOR: brownfield assessment, environment inventory, current-state documentation. DO NOT USE FOR: compliance evaluation (use wara-assessment), security enforcement (use security-baseline)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "1.0"
  category: azure-brownfield
---

# Brownfield Discovery Skill

Domain knowledge for discovering and inventorying existing Azure environments.
All operations are **read-only** — no resources are created, modified, or deleted.

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
| `tenant` | Tenant ID | All MGs, all subscriptions, all resources |
| `management_group` | MG name | MGs under this parent, subscriptions, resources |
| `subscription` | Subscription ID | Resources, policies, RBAC in this subscription |
| `resource_group` | RG name + sub ID | Resources in this resource group |

## Implementation Reference

- **Module:** `src/tools/discovery.py`
- **Class:** `DiscoveryCollector`
- **Data model:** `DiscoveryResult`
- **Output:** `agent-output/assessment/00-discovery.json`

## KQL Query Patterns

### Management Group Hierarchy

```kql
resourcecontainers
| where type == 'microsoft.management/managementgroups'
| project id, name, displayName=properties.displayName,
          parent=properties.details.parent.id,
          tenantId=tenantId
| order by name asc
```

### Subscription Inventory

```kql
resourcecontainers
| where type == 'microsoft.resources/subscriptions'
| project subscriptionId, name, displayName=properties.displayName,
          state=properties.state, tags,
          managementGroup=properties.managementGroupAncestorsChain
| order by name asc
```

### Resource Inventory by Type

```kql
resources
| summarize count=count() by type
| order by count desc
```

### Resource Inventory by Location

```kql
resources
| summarize count=count() by location
| order by count desc
```

### VNet Topology with Peerings

```kql
resources
| where type == 'microsoft.network/virtualnetworks'
| project id, name, location, resourceGroup, subscriptionId,
          addressSpace=properties.addressSpace.addressPrefixes,
          subnets=array_length(properties.subnets),
          peerings=array_length(properties.virtualNetworkPeerings),
          dnsServers=properties.dhcpOptions.dnsServers
```

### VNet Peering Details

```kql
resources
| where type == 'microsoft.network/virtualnetworks'
| mv-expand peering = properties.virtualNetworkPeerings
| project localVnet=name, remoteVnet=peering.properties.remoteVirtualNetwork.id,
          peeringState=peering.properties.peeringState,
          allowForwarding=peering.properties.allowForwardedTraffic
```

### Policy Assignments

```kql
policyresources
| where type == 'microsoft.authorization/policyassignments'
| project id, name, displayName=properties.displayName,
          policyDefinitionId=properties.policyDefinitionId,
          enforcementMode=properties.enforcementMode,
          scope=properties.scope
| order by name asc
```

### RBAC Role Assignments

```kql
authorizationresources
| where type == 'microsoft.authorization/roleassignments'
| project id, name,
          principalId=properties.principalId,
          principalType=properties.principalType,
          roleDefinitionId=properties.roleDefinitionId,
          scope=properties.scope,
          createdOn=properties.createdOn
| order by name asc
```

### Log Analytics Workspaces

```kql
resources
| where type == 'microsoft.operationalinsights/workspaces'
| project id, name, location, resourceGroup,
          sku=properties.sku.name,
          retentionDays=properties.retentionInDays,
          dailyCapGb=properties.workspaceCapping.dailyQuotaGb
```

### Key Vault Security Posture

```kql
resources
| where type == 'microsoft.keyvault/vaults'
| project id, name, location,
          enableSoftDelete=properties.enableSoftDelete,
          enablePurgeProtection=properties.enablePurgeProtection,
          enableRbacAuthorization=properties.enableRbacAuthorization,
          networkAcls=properties.networkAcls.defaultAction
```

### Storage Account Security Posture

```kql
resources
| where type == 'microsoft.storage/storageaccounts'
| project id, name, location,
          httpsOnly=properties.supportsHttpsTrafficOnly,
          minTls=properties.minimumTlsVersion,
          publicBlob=properties.allowBlobPublicAccess,
          networkDefault=properties.networkAcls.defaultAction
```

### Azure Firewall Inventory

```kql
resources
| where type == 'microsoft.network/azurefirewalls'
| project id, name, location, sku=properties.sku,
          threatIntelMode=properties.threatIntelMode
```

### Private DNS Zones

```kql
resources
| where type == 'microsoft.network/privatednszones'
| project id, name, recordSets=properties.numberOfRecordSets
```

## Discovery Output Schema

The `DiscoveryResult` contains:

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
| `errors` | list | Any collector errors (partial results still returned) |

## Usage

### CLI (via orchestrator)

```bash
python -m src.agents.orchestrator \
  --mode assess \
  --scope mrg \
  --scope-type management_group
```

### MCP Tools

| Tool | Description |
|------|-------------|
| `discover_mg_hierarchy` | Management group tree with subscription placement |
| `discover_subscription_inventory` | Subscriptions with resource counts and tags |
| `discover_rbac_snapshot` | Role assignments across scope |
