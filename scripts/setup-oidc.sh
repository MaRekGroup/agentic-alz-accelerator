#!/usr/bin/env bash
# ============================================================================
# OIDC Federated Identity Setup for GitHub Actions → Azure
# Creates an Entra ID app registration with federated credentials so
# GitHub Actions can authenticate to Azure without storing secrets.
#
# Prerequisites:
#   - az cli authenticated with Global Admin or Application Admin role
#   - GitHub CLI (gh) authenticated
#
# Usage:
#   chmod +x scripts/setup-oidc.sh
#   ./scripts/setup-oidc.sh <github-org> <github-repo> <mg-prefix>
#
# Example:
#   ./scripts/setup-oidc.sh contoso agentic-alz-accelerator alz
# ============================================================================
set -euo pipefail

# ── Args ──
GITHUB_ORG="${1:?Usage: $0 <github-org> <github-repo> <mg-prefix>}"
GITHUB_REPO="${2:?Usage: $0 <github-org> <github-repo> <mg-prefix>}"
MG_PREFIX="${3:-alz}"

APP_NAME="alz-github-actions-oidc"
REPO_FULL="${GITHUB_ORG}/${GITHUB_REPO}"

echo "============================================"
echo "  ALZ OIDC Setup"
echo "  Repo:   ${REPO_FULL}"
echo "  Prefix: ${MG_PREFIX}"
echo "============================================"
echo ""

# ── Step 1: Create Entra ID App Registration ──
echo "1. Creating Entra ID app registration: ${APP_NAME}"
APP_ID=$(az ad app create --display-name "$APP_NAME" --query appId -o tsv)
echo "   App ID: ${APP_ID}"

# Create service principal
echo "   Creating service principal..."
SP_OBJECT_ID=$(az ad sp create --id "$APP_ID" --query id -o tsv 2>/dev/null || \
               az ad sp show --id "$APP_ID" --query id -o tsv)
echo "   SP Object ID: ${SP_OBJECT_ID}"

# ── Step 2: Add Federated Credentials ──
echo ""
echo "2. Adding federated credentials for GitHub Actions"

# Federated credential for main branch
echo "   Adding credential for main branch..."
az ad app federated-credential create --id "$APP_ID" --parameters '{
  "name": "github-main",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:'"${REPO_FULL}"':ref:refs/heads/main",
  "audiences": ["api://AzureADTokenExchange"],
  "description": "GitHub Actions - main branch"
}' --output none

# Federated credential for pull requests (needed for PR validation what-if)
echo "   Adding credential for pull requests..."
az ad app federated-credential create --id "$APP_ID" --parameters '{
  "name": "github-pull-request",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:'"${REPO_FULL}"':pull_request",
  "audiences": ["api://AzureADTokenExchange"],
  "description": "GitHub Actions - pull request validation"
}' --output none

# Federated credential for GitHub environments
for env_name in platform-management platform-connectivity platform-identity \
                platform-security app-prod app-dev remediation; do
  echo "   Adding credential for environment: ${env_name}..."
  az ad app federated-credential create --id "$APP_ID" --parameters '{
    "name": "github-env-'"${env_name}"'",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:'"${REPO_FULL}"':environment:'"${env_name}"'",
    "audiences": ["api://AzureADTokenExchange"],
    "description": "GitHub Actions - '"${env_name}"' environment"
  }' --output none
done

# ── Step 3: Assign RBAC Roles ──
echo ""
echo "3. Assigning RBAC roles"

TENANT_ID=$(az account show --query tenantId -o tsv)
MG_SCOPE="/providers/Microsoft.Management/managementGroups/${MG_PREFIX}"

# Owner on the root management group (covers all child MGs and subscriptions)
echo "   Assigning Owner on management group: ${MG_PREFIX}"
az role assignment create \
  --assignee-object-id "$SP_OBJECT_ID" \
  --assignee-principal-type ServicePrincipal \
  --role "Owner" \
  --scope "$MG_SCOPE" \
  --output none 2>/dev/null || echo "   (role may already exist)"

# User Access Administrator for RBAC operations
echo "   Assigning User Access Administrator on management group: ${MG_PREFIX}"
az role assignment create \
  --assignee-object-id "$SP_OBJECT_ID" \
  --assignee-principal-type ServicePrincipal \
  --role "User Access Administrator" \
  --scope "$MG_SCOPE" \
  --output none 2>/dev/null || echo "   (role may already exist)"

# ── Step 4: Set GitHub Secrets ──
echo ""
echo "4. Setting GitHub repository secrets"

gh secret set AZURE_TENANT_ID --repo "$REPO_FULL" --body "$TENANT_ID"
gh secret set AZURE_CLIENT_ID --repo "$REPO_FULL" --body "$APP_ID"

echo "   AZURE_TENANT_ID set"
echo "   AZURE_CLIENT_ID set"

# ── Step 5: Prompt for subscription IDs ──
echo ""
echo "5. Subscription IDs"
echo "   You need to set these secrets in your GitHub repository."
echo "   Run the commands below with your actual subscription IDs:"
echo ""
echo "   # Platform subscriptions"
echo "   gh secret set PLATFORM_MGMT_SUBSCRIPTION_ID --repo ${REPO_FULL} --body '<Sub-1-ID>'"
echo "   gh secret set PLATFORM_CONN_SUBSCRIPTION_ID --repo ${REPO_FULL} --body '<Sub-2-ID>'"
echo "   gh secret set PLATFORM_IDTY_SUBSCRIPTION_ID --repo ${REPO_FULL} --body '<Sub-3-ID>'"
echo "   gh secret set PLATFORM_SEC_SUBSCRIPTION_ID  --repo ${REPO_FULL} --body '<Sub-4-ID>'"
echo ""
echo "   # Application subscriptions"
echo "   gh secret set APP_CORP_ERP_SUBSCRIPTION_ID   --repo ${REPO_FULL} --body '<Sub-5-ID>'"
echo "   gh secret set APP_CORP_CRM_SUBSCRIPTION_ID   --repo ${REPO_FULL} --body '<Sub-6-ID>'"
echo "   gh secret set APP_ONLINE_WEB_SUBSCRIPTION_ID --repo ${REPO_FULL} --body '<Sub-7-ID>'"
echo "   gh secret set APP_ONLINE_API_SUBSCRIPTION_ID --repo ${REPO_FULL} --body '<Sub-8-ID>'"
echo "   gh secret set APP_SAP_SUBSCRIPTION_ID        --repo ${REPO_FULL} --body '<Sub-9-ID>'"
echo "   gh secret set APP_SANDBOX_SUBSCRIPTION_ID    --repo ${REPO_FULL} --body '<Sub-10-ID>'"
echo ""
echo "   # Optional: Terraform state storage"
echo "   gh secret set TF_STATE_STORAGE_ACCOUNT --repo ${REPO_FULL} --body '<storage-account-name>'"
echo ""
echo "   # Optional: Teams webhook for notifications"
echo "   gh secret set TEAMS_WEBHOOK_URL --repo ${REPO_FULL} --body '<webhook-url>'"

# ── Step 6: Create GitHub Environments ──
echo ""
echo "6. Creating GitHub environments"
echo "   (requires GitHub API — set protection rules in repo Settings > Environments)"
echo ""

for env_name in platform-management platform-connectivity platform-identity \
                platform-security app-prod app-dev remediation; do
  echo "   Creating environment: ${env_name}"
  gh api --method PUT "repos/${REPO_FULL}/environments/${env_name}" \
    --silent 2>/dev/null || echo "   (may require admin access)"
done

echo ""
echo "============================================"
echo "  Setup Complete!"
echo "============================================"
echo ""
echo "  App Registration: ${APP_NAME}"
echo "  App (Client) ID:  ${APP_ID}"
echo "  Tenant ID:        ${TENANT_ID}"
echo ""
echo "  Next steps:"
echo "  1. Set the subscription ID secrets (see commands above)"
echo "  2. Configure environment protection rules in GitHub:"
echo "     Settings > Environments > Add required reviewers"
echo "     - platform-*: platform-team + domain team"
echo "     - app-prod:   platform-team"
echo "     - app-dev:    no reviewers (auto-approve)"
echo "     - remediation: platform-team + security-team"
echo "  3. Run workflow: '1 · Bootstrap Landing Zone Foundation'"
echo ""
