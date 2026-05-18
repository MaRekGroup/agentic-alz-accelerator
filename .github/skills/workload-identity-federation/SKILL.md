---
name: workload-identity-federation
description: "Managed identity and workload federation patterns for Azure-hosted workloads. USE FOR: AKS Workload Identity, federated identity credentials for non-GitHub workloads, cross-cloud federation to AWS/GCP, Service Connector managed identity connections, token exchange and refresh patterns, and migration from service principal secrets to managed identity. DO NOT USE FOR: GitHub Actions OIDC or deployment app registrations (use entra-app-registration), basic Azure RBAC role assignment design (use azure-rbac), Conditional Access (use entra-conditional-access), PIM or human identity governance (use entra-identity-governance), or hybrid identity sync/federation migration (use entra-connect-hybrid-identity)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "1.0"
  category: azure-identity
---

# Workload Identity Federation Skill

## Overview

This skill covers workload-to-cloud authentication patterns that remove long-lived secrets from running workloads: AKS Workload Identity, federated identity credentials (FIC) on user-assigned managed identities or app registrations, Service Connector managed identity flows, and cross-cloud federation to AWS IAM roles or GCP service accounts.

For this accelerator, **Security Baseline rule #4 — Managed Identity preferred** is the default. Prefer system-assigned managed identity for single Azure resources, prefer user-assigned managed identity when identity must survive replacement or be shared, and use federated credentials when an external token must be exchanged without storing secrets. GitHub Actions OIDC stays in `entra-app-registration`; this skill only covers **FIC for non-GitHub workloads**.

## CAF Design Area Mapping

| CAF Design Area | How this skill applies |
|-----------------|------------------------|
| Identity & Access | Selects managed identity type, defines trust boundaries for FIC, and removes service principal secrets from workloads |
| Security | Eliminates stored client secrets, certificates, and connection strings as a primary credential attack surface across the workload estate |
| Governance | Enables policy enforcement against secret-based service principal usage (e.g., Azure Policy "deny secret-based auth" at MG scope) and supports credential-lifecycle compliance |
| Platform Automation & DevOps | Standardizes secretless runtime auth for AKS, PaaS connectors, and cross-cloud service integrations |

## WAF Pillar Mapping

| WAF Pillar | Contribution |
|------------|--------------|
| Security | Primary pillar. Eliminates client secrets, constrains issuer/subject/audience, and reduces credential theft blast radius |
| Reliability | Token exchange depends on OIDC issuer availability; design issuer redundancy, token refresh resilience, and explicit failure-mode handling in SDKs |
| Operational Excellence | Removes credential rotation runbooks, simplifies brownfield retrofit, and benefits runtime efficiency through token caching |
| Cost Optimization | Eliminates certificate renewal toil, secret rotation runbooks, and the operational cost of credential-incident response |

## Identity Selection Decision Tree

| Workload type | Recommended identity | Why |
|---------------|----------------------|-----|
| AKS pod or controller | Kubernetes service account + user-assigned managed identity + federated identity credential | Best fit for pod-to-Azure auth without pod-managed identity v1 or Kubernetes secrets |
| Azure-hosted workload calling AWS or GCP | Federated workload token to external cloud trust target | Keeps cross-cloud access on short-lived tokens instead of exporting Azure secrets |
| Single Azure resource | System-assigned managed identity | Lowest operational overhead and lifecycle stays bound to one resource |
| Shared identity across resources or redeployments | User-assigned managed identity | Identity survives resource replacement and can be reused by a bounded workload set |
| App Service / Functions / Container Apps connecting to supported PaaS | Service Connector with managed identity | Fastest path to secretless auth when the source/target pair is supported |

## Architecture Patterns

| Pattern | Core flow | Guardrail |
|---------|-----------|-----------|
| AKS Workload Identity Pattern | AKS OIDC issuer → projected service account token → FIC on user-assigned managed identity → Azure Identity/MSAL | Prefer user-assigned managed identity over app registration for Azure-hosted runtimes |
| Cross-Cloud Federation Pattern | Azure workload token → AWS IAM OIDC provider or GCP Workload Identity Pool → short-lived external credentials | Never export Azure client secrets; scope trust per environment and bounded app |
| Service Connector Pattern | Source PaaS → Service Connector → managed identity auth to supported target service | Review generated RBAC and network path; Connector doesn't replace `azure-rbac` |
| System-Assigned vs User-Assigned Selection Pattern | Single resource → system-assigned; shared lifecycle, blue/green, or FIC → user-assigned | FIC isn't supported on system-assigned managed identities |
| Federated Identity Credential Lifecycle Pattern | Issuer → identity object → FIC → workload binding → audit lifecycle | Pin issuer, subject, and audience; namespace or service account rename is an identity change |
| Token Exchange and Refresh Pattern | Short-lived source token → trust validation → short-lived access token → SDK cache and refresh | Rotate trust, not secrets, and never copy tokens into files or images |

## Security Baseline Reinforcement

| Scenario | How rule #4 is operationalized | Governance expectation |
|----------|--------------------------------|------------------------|
| AKS pod-to-Azure | Service account token + FIC + managed identity replaces Kubernetes secret or client secret env vars | No secret-based Azure auth in pod specs or namespaces where workload identity is enabled |
| Single Azure workload | System-assigned managed identity replaces service principal secrets on the resource | No app setting, Key Vault secret, or pipeline variable should hold runtime Azure credentials |
| Shared application tier | User-assigned managed identity replaces duplicated secrets across replicas or slots | Reuse only within a bounded app or platform function; permissions must stay least privilege |
| Cross-cloud workload | Federated short-lived tokens replace stored AWS keys, GCP keys, or exported Azure secrets | Trust must be issuer/subject scoped and monitored through sign-in logs and audit logs |
| PaaS-to-PaaS connection | Service Connector provisions managed identity instead of connection strings where supported | Generated access must still be reviewed for overbroad roles or public network paths |

## Brownfield Scenario

**Cross-skill sequencing:** Run after `entra-conditional-access` has established baseline CA and `entra-identity-governance` has cleaned up human privileged paths — workload identity is the final layer that closes secret-based authentication estate-wide. No downstream Wave 1 skill follows this; ongoing operations transition to Sentinel monitoring (Step 8) and Mender remediation (Step 9).

### Scenario S8 (Cloud-Native Modernization): Migrating an existing AKS cluster from secret-based service principals (deployed before workload identity GA) to workload identity federation without downtime

Use this retrofit when an existing cluster still relies on `aad-pod-identity`, service principal secrets, or mounted client credentials.

| Step | Action | Zero-downtime / v1 → v2 consideration |
|------|--------|----------------------------------------|
| 1 | Inventory every namespace, service account, secret, and Azure dependency currently using service principal auth | Build a one-to-one map from workload to target managed identity before touching runtime credentials |
| 2 | Enable the AKS OIDC issuer and workload identity features, then verify the issuer URL resolves and matches cluster state | `aad-pod-identity` v1 and workload identity v2 can coexist during migration at cluster level; migrate workload by workload |
| 3 | Create target user-assigned managed identities and least-privilege RBAC assignments for each bounded workload | Avoid one giant shared identity; keep rollback simple by aligning one workload to one target identity or bounded app group |
| 4 | Add federated identity credentials for each service account subject and update manifests with `azure.workload.identity/client-id` annotations | Namespace and service account names become trust inputs; rename only as part of a deliberate cutover |
| 5 | Update application code or SDK configuration to use Azure Identity / MSAL instead of secret-based credentials | Validate library support before rollout; older SDKs often need upgrade or explicit workload identity credential enablement |
| 6 | Canary deploy one workload slice at a time, keep legacy secret auth available only as rollback, and monitor sign-in success plus latency | Do not cut the whole cluster at once; scale up new pods before draining old pods to avoid downtime |
| 7 | After steady-state validation, remove service principal secrets, retire `aad-pod-identity` bindings and exception docs, and add alerts for secret-based regression | The migration is not complete until legacy secrets are deleted and governance prevents reintroduction |

## Bicep Snippets

Use AVM modules in production when available. Raw resources are shown here to make the pattern explicit.

### AKS cluster with OIDC issuer and workload identity enabled

```bicep
resource aks 'Microsoft.ContainerService/managedClusters@2024-10-01' = {
  name: 'aks-wif-scus'
  location: resourceGroup().location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    dnsPrefix: 'aks-wif-scus'
    enableRBAC: true
    servicePrincipalProfile: {
      clientId: 'msi'
    }
    agentPoolProfiles: [
      {
        name: 'system'
        mode: 'System'
        count: 3
        vmSize: 'Standard_D4ds_v5'
        osType: 'Linux'
        type: 'VirtualMachineScaleSets'
      }
    ]
    oidcIssuerProfile: {
      enabled: true
    }
    securityProfile: {
      workloadIdentity: {
        enabled: true
      }
    }
  }
}
```

### User-assigned managed identity with federated identity credential

```bicep
param aksOidcIssuer string

resource workloadIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-orders-api-scus'
  location: resourceGroup().location
}

resource workloadFic 'Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials@2023-01-31' = {
  name: 'aks-orders-orders-api'
  parent: workloadIdentity
  properties: {
    audiences: [
      'api://AzureADTokenExchange'
    ]
    issuer: aksOidcIssuer
    subject: 'system:serviceaccount:orders:orders-api'
  }
}
```

## Terraform Snippets

### AKS cluster with OIDC issuer and workload identity enabled

```terraform
resource "azurerm_kubernetes_cluster" "aks" {
  name                = "aks-wif-scus"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = "aks-wif-scus"
  oidc_issuer_enabled       = true
  workload_identity_enabled = true

  identity {
    type = "SystemAssigned"
  }

  default_node_pool {
    name       = "system"
    node_count = 3
    vm_size    = "Standard_D4ds_v5"
  }
}
```

### User-assigned managed identity with federated identity credential

```terraform
resource "azurerm_user_assigned_identity" "workload" {
  name                = "id-orders-api-scus"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_federated_identity_credential" "orders_api" {
  name                = "fic-orders-api"
  resource_group_name = azurerm_resource_group.rg.name
  parent_id           = azurerm_user_assigned_identity.workload.id
  audience            = ["api://AzureADTokenExchange"]
  issuer              = azurerm_kubernetes_cluster.aks.oidc_issuer_url
  subject             = "system:serviceaccount:orders:orders-api"
}
```

## Diagnostic & Monitoring

| Signal | Source | What to watch |
|--------|--------|---------------|
| FIC create/update/delete | Entra audit logs | Unauthorized trust expansion, stale credentials left after migration |
| Federated service principal sign-ins | `AADServicePrincipalSignInLogs` | Empty or unexpected `FederatedCredentialId`, repeated auth failures, wrong target resource |
| Managed identity sign-ins | `AADManagedIdentitySignInLogs` | Whether workloads actually moved off secrets after cutover |
| AKS admission/runtime issues | Kubernetes events, workload logs, Azure Identity logs | Missing service account annotation, wrong client ID, issuer mismatch |

### KQL Examples

```kql
AuditLogs
| where TimeGenerated > ago(7d)
| where OperationName has "federated" or tostring(TargetResources) has "federatedIdentityCredentials"
| project TimeGenerated, OperationName, Result, InitiatedBy, TargetResources
| order by TimeGenerated desc
```

```kql
AADServicePrincipalSignInLogs
| where TimeGenerated > ago(24h)
| where federatedCredentialId != ""
| project TimeGenerated, appDisplayName, federatedCredentialId, resourceDisplayName, resultType
| order by TimeGenerated desc
```

## Anti-Patterns

| Anti-pattern | Why it fails |
|--------------|--------------|
| Keeping service principal secrets after managed identity is available | Creates permanent rollback debt and preserves the original credential theft path |
| Reusing one user-assigned managed identity across unrelated apps, environments, or subscriptions | Turns a convenience identity into a shared blast-radius multiplier |
| Using app registrations for Azure-native workloads that could use managed identity | Reintroduces secret or certificate lifecycle where the platform can avoid it |
| Missing or over-broad FIC subject scoping | Trust drifts away from a single workload boundary and becomes hard to audit |
| Creating FIC before the issuer is stable or verified | Leads to token exchange failures that appear as intermittent runtime auth bugs |
| Letting Service Connector create access without reviewing role scope and network path | Easy to end up with over-entitled access or public routing that violates governance intent |

## References

| Topic | URL |
|-------|-----|
| AKS workload identity overview | https://learn.microsoft.com/en-us/azure/aks/workload-identity-overview |
| Migrate from pod identity to workload identity | https://learn.microsoft.com/en-us/azure/aks/workload-identity-migrate-from-pod-identity |
| Workload identity federation overview | https://learn.microsoft.com/en-us/entra/workload-id/workload-identity-federation |
| Create trust on a user-assigned managed identity | https://learn.microsoft.com/en-us/entra/workload-id/workload-identity-federation-create-trust-user-assigned-managed-identity |
| Managed identities overview | https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview |
| Managed identity best practice recommendations | https://learn.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/how-to-best-practices |
| Manage authentication in Service Connector | https://learn.microsoft.com/en-us/azure/service-connector/how-to-manage-authentication |
| `AADServicePrincipalSignInLogs` table reference | https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/aadserviceprincipalsigninlogs |
| `AADManagedIdentitySignInLogs` table reference | https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/aadmanagedidentitysigninlogs |
| Bicep reference: managed clusters | https://learn.microsoft.com/en-us/azure/templates/microsoft.containerservice/managedclusters?pivots=deployment-language-bicep |
