<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Entra App Registration Skill (Digest)

Manages Entra ID app registrations and workload identity federation for
GitHub Actions deployment pipelines and platform service principals.

## Core Concepts

| Concept | ALZ Usage |
|---|---|
| App Registration | GitHub Actions deployment identity |
| Federated Credential | OIDC trust between GitHub repo and Azure |
| Service Principal | Receives RBAC on management groups/subscriptions |
| Managed Identity | Preferred over app registrations for deployed workloads |
| Client Secret | **Avoid** — use federated credentials (security baseline rule #4) |

## Platform LZ Identity Architecture

```text
GitHub Actions → OIDC Token → Entra App "sp-{prefix}-platform-deploy"
  ├─ Contributor on: mrg-platform (MG)
  ├─ User Access Administrator on: mrg-platform (MG)
  └─ Reader on: Tenant Root Group (MG)
```

## OIDC Federation Workflow

1. Create app registration: `az ad app create --display-name "sp-{prefix}-platform-deploy"`
2. Create service principal: `az ad sp create --id $APP_ID`
3. Add federated credential (branch-scoped subject)
4. Assign RBAC roles (Contributor + UAA at required scope)
5. Set GitHub variables: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`

> _See SKILL.md for full CLI commands and Bicep implementation._

## Naming Convention

| Entity | Pattern | Example |
|---|---|---|
| Platform deploy SP | `sp-{prefix}-platform-deploy` | `sp-mrg-platform-deploy` |
| App LZ deploy SP | `sp-{prefix}-{app}-deploy` | `sp-mrg-webapp-deploy` |
| Federated credential | `github-actions-{branch/env}` | `github-actions-main` |
| Managed Identity | `id-{prefix}-{purpose}-{region}` | `id-mrg-deploy-scus` |

## Security Best Practices

| Rule | Rationale |
|---|---|
| No client secrets | Security baseline rule #4 |
| Least privilege RBAC | Contributor + UAA only at required scope |
| Environment-scoped federation | Separate credentials for prod vs. validate |
| No wildcard subjects | Always scope to specific branch or environment |
| Use Managed Identity for workloads | App registrations only for CI/CD pipelines |

## Workflow Integration

| Step | Integration |
|---|---|
| Bootstrap (`scripts/setup-oidc.sh`) | Creates initial platform deployment identity |
| Step 3.5 Governance | Audits existing app registrations |
| Step 5 Code Gen | Generates Bicep/Terraform for workload identities |
| Step 6 Deploy | Uses OIDC federation for GitHub Actions auth |

## Constraints

- Never create client secrets — always federated credentials for CI/CD
- Never grant Owner role to service principals
- Always scope federation subjects to specific branches/environments
- Document all app registrations in `environments/subscriptions.json`
