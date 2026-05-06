---
name: entra-app-registration
description: "Guides Entra ID (Azure AD) app registration, workload identity federation, and service principal management for Landing Zone deployments. USE FOR: create app registration, configure OIDC federation, set up GitHub Actions identity, workload identity, service principal. DO NOT USE FOR: Azure RBAC role assignments (use azure-rbac), Key Vault secrets management, general security (use security-baseline)."
---

# Entra App Registration — Enterprise Landing Zone Identity

Manages Microsoft Entra ID app registrations and workload identity federation
for GitHub Actions deployment pipelines and platform service principals.

## When to Use

- Setting up OIDC federation for GitHub Actions → Azure deployment
- Creating service principals for platform LZ deployment pipelines
- Configuring workload identity for application Landing Zones
- Auditing existing app registrations during brownfield assessment

## Core Concepts for ALZ

| Concept | ALZ Usage |
|---|---|
| App Registration | GitHub Actions deployment identity |
| Federated Credential | OIDC trust between GitHub repo and Azure |
| Service Principal | Identity that receives RBAC on management groups/subscriptions |
| Managed Identity | Preferred over app registrations for deployed workloads |
| Client Secret | **Avoid** — use federated credentials instead (security baseline rule #4) |

---

## Platform LZ Identity Architecture

```text
GitHub Actions Pipeline
    │
    ├─ OIDC Token (federated credential)
    │
    ▼
Entra App Registration: "sp-{prefix}-platform-deploy"
    │
    ├─ Contributor on: mrg-platform (MG)
    ├─ User Access Administrator on: mrg-platform (MG)
    └─ Reader on: Tenant Root Group (MG)

Per-App LZ:
Entra App Registration: "sp-{prefix}-{app-name}-deploy"
    │
    ├─ Contributor on: subscription (app LZ)
    └─ Reader on: mrg-landingzones (MG)
```

---

## Workflow: GitHub Actions OIDC Federation

### Step 1: Create App Registration

```bash
# Platform deployment identity
az ad app create \
  --display-name "sp-{prefix}-platform-deploy" \
  --sign-in-audience AzureADMyOrg

# Capture the Application (Client) ID
APP_ID=$(az ad app list --display-name "sp-{prefix}-platform-deploy" --query "[0].appId" -o tsv)
```

### Step 2: Create Service Principal

```bash
az ad sp create --id $APP_ID
SP_OBJECT_ID=$(az ad sp show --id $APP_ID --query "id" -o tsv)
```

### Step 3: Add Federated Credential (OIDC)

```bash
# For main branch deployments
az ad app federated-credential create --id $APP_ID --parameters '{
  "name": "github-actions-main",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:MaRekGroup/agentic-alz-accelerator:ref:refs/heads/main",
  "audiences": ["api://AzureADTokenExchange"]
}'

# For PR validation (environment-scoped)
az ad app federated-credential create --id $APP_ID --parameters '{
  "name": "github-actions-pr-validate",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:MaRekGroup/agentic-alz-accelerator:environment:validate",
  "audiences": ["api://AzureADTokenExchange"]
}'
```

### Step 4: Assign RBAC Roles

```bash
# Contributor on platform management group
az role assignment create \
  --assignee $SP_OBJECT_ID \
  --role "Contributor" \
  --scope "/providers/Microsoft.Management/managementGroups/mrg-platform"

# User Access Administrator (for RBAC assignments in IaC)
az role assignment create \
  --assignee $SP_OBJECT_ID \
  --role "User Access Administrator" \
  --scope "/providers/Microsoft.Management/managementGroups/mrg-platform"
```

### Step 5: Configure GitHub Actions Secrets

```bash
# Set as GitHub repository variables (not secrets — OIDC uses no secret)
gh variable set AZURE_CLIENT_ID --body "$APP_ID"
gh variable set AZURE_TENANT_ID --body "$(az account show --query tenantId -o tsv)"
gh variable set AZURE_SUBSCRIPTION_ID --body "$(az account show --query id -o tsv)"
```

---

## IaC: Bicep App Registration

```bicep
// For IaC-managed app registrations (requires Microsoft.Graph provider)
resource appRegistration 'Microsoft.Graph/applications@v1.0' = {
  displayName: 'sp-${prefix}-${appName}-deploy'
  signInAudience: 'AzureADMyOrg'

  web: {
    implicitGrantSettings: {
      enableAccessTokenIssuance: false
      enableIdTokenIssuance: false
    }
  }
}

resource federatedCredential 'Microsoft.Graph/applications/{id}/federatedIdentityCredentials@v1.0' = {
  name: 'github-actions-main'
  issuer: 'https://token.actions.githubusercontent.com'
  subject: 'repo:${githubOrg}/${githubRepo}:ref:refs/heads/main'
  audiences: ['api://AzureADTokenExchange']
}
```

---

## Naming Convention

| Entity | Pattern | Example |
|---|---|---|
| Platform deploy SP | `sp-{prefix}-platform-deploy` | `sp-mrg-platform-deploy` |
| App LZ deploy SP | `sp-{prefix}-{app}-deploy` | `sp-mrg-webapp-deploy` |
| Federated credential | `github-actions-{branch/env}` | `github-actions-main` |
| Managed Identity | `id-{prefix}-{purpose}-{region}` | `id-mrg-deploy-scus` |

---

## Security Best Practices (ALZ-Specific)

| Rule | Rationale |
|---|---|
| **No client secrets** — use federated credentials only | Security baseline rule #4: Managed Identity preferred |
| **Least privilege RBAC** | Contributor + UAA only at required scope |
| **Environment-scoped federation** | Separate credentials for prod vs. validate |
| **No wildcard subjects** | Always scope to specific branch or environment |
| **Audit regularly** | Check `az ad app list --filter "startswith(displayName, 'sp-{prefix}')"` |
| **Use Managed Identity for workloads** | App registrations only for CI/CD pipelines |

---

## Brownfield Assessment: App Registration Audit

When assessing existing environments, check for:

```bash
# List all app registrations with expired credentials
az ad app list --all --query "[?passwordCredentials[?endDateTime<'$(date -u +%Y-%m-%dT%H:%M:%SZ)']].{name:displayName,appId:appId}" -o table

# List app registrations with client secrets (should migrate to federated)
az ad app list --all --query "[?passwordCredentials[0]].{name:displayName,appId:appId,expires:passwordCredentials[0].endDateTime}" -o table

# Check for overprivileged service principals
az role assignment list --all --query "[?principalType=='ServicePrincipal' && roleDefinitionName=='Owner']" -o table
```

---

## Integration with Accelerator Workflow

| Step | Integration |
|---|---|
| Bootstrap (scripts/setup-oidc.sh) | Creates initial platform deployment identity |
| Step 3.5 Governance | Audits existing app registrations for compliance |
| Step 5 Code Gen | Generates Bicep/Terraform for workload identities |
| Step 6 Deploy | Uses OIDC federation for GitHub Actions authentication |

---

## Constraints

- **Never create client secrets** — always use federated credentials for CI/CD
- **Never grant Owner role** to service principals
- **Always scope** federation subjects to specific branches or environments
- App registration changes via `scripts/setup-oidc.sh` or IaC — not manual portal
- Document all app registrations in `environments/subscriptions.json`
