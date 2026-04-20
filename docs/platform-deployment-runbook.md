# Platform Landing Zone Deployment Runbook

> Step-by-step guide documenting the verified process for bootstrapping and deploying
> platform landing zones using the Agentic ALZ Accelerator with GitHub Actions.

## Prerequisites

| Requirement | Details |
|-------------|---------|
| Azure CLI | Authenticated with Global Admin or Application Admin role |
| GitHub CLI (`gh`) | Authenticated to the GitHub org hosting the repo |
| Azure Tenant | 1 tenant with Owner access |
| Subscriptions | Minimum 4 platform subscriptions provisioned |
| GitHub Repo | Private repo with Actions enabled |

### Platform Subscriptions Needed

| # | Purpose | Management Group |
|---|---------|-----------------|
| 1 | Management (logging, Sentinel, Automation) | `mrg-platform-management` |
| 2 | Connectivity (hub VNet, Firewall, DNS) | `mrg-platform-connectivity` |
| 3 | Identity (AD DS, PIM) | `mrg-platform-identity` |
| 4 | Security (Defender, SOAR, SecOps) | `mrg-platform-security` |

---

## Step 1: Install GitHub CLI

If `gh` is not available in your environment:

```bash
# Direct .deb install (works when apt repo has issues)
wget -q https://github.com/cli/cli/releases/download/v2.67.0/gh_2.67.0_linux_amd64.deb -O /tmp/gh.deb
sudo dpkg -i /tmp/gh.deb
```

Verify:
```bash
gh --version
```

---

## Step 2: Authenticate GitHub CLI

```bash
# Option A: Interactive browser auth
gh auth login

# Option B: PAT token (needs repo, workflow, admin:org scopes)
echo "<YOUR_PAT>" | gh auth login --with-token
```

Verify:
```bash
gh auth status
```

> **Note:** If your repo is in a GitHub organization with SSO (e.g., Microsoft enterprise),
> the PAT must be SSO-authorized for that org. Go to GitHub → Settings → Developer settings →
> Personal access tokens → Configure SSO → Authorize.

---

## Step 3: Run OIDC Setup Script

The script creates an Entra ID app registration with federated credentials so
GitHub Actions can authenticate to Azure without storing secrets.

```bash
bash scripts/setup-oidc.sh <github-org> <github-repo> <mg-prefix>
```

Example:
```bash
bash scripts/setup-oidc.sh MaRekGroup agentic-alz-accelerator alz
```

### What the script creates:

| Item | Details |
|------|---------|
| Entra ID App Registration | `alz-github-actions-oidc` |
| Service Principal | Created automatically |
| Federated Credentials (8) | `main` branch + 7 environments |
| RBAC Roles | Owner + User Access Administrator on the MG prefix |
| GitHub Secrets | `AZURE_TENANT_ID`, `AZURE_CLIENT_ID` |

### Environments with federated credentials:
- `platform-management`
- `platform-connectivity`
- `platform-identity`
- `platform-security`
- `app-prod`
- `app-dev`
- `remediation`

> **Known issue:** If the repo doesn't exist yet when running the script, Steps 1-3
> (app reg, federated creds, RBAC) succeed but Step 4 (GitHub secrets) fails with
> HTTP 404. Create the repo first, then run the script — or set secrets manually afterward.

---

## Step 4: Fix Federated Credentials (if repo org differs)

If the OIDC script was run with a different repo path than where the repo actually lives,
update the federated credentials to match:

```bash
APP_ID="<your-app-id>"
REPO="<org>/<repo-name>"

# Update main branch credential
az ad app federated-credential delete --id "$APP_ID" --federated-credential-id "github-main" --output none 2>/dev/null
az ad app federated-credential create --id "$APP_ID" --parameters '{
  "name": "github-main",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:'"${REPO}"':ref:refs/heads/main",
  "audiences": ["api://AzureADTokenExchange"],
  "description": "GitHub Actions - main branch"
}' --output none

# Update all environment credentials
for env_name in platform-management platform-connectivity platform-identity \
                platform-security app-prod app-dev remediation; do
  az ad app federated-credential delete --id "$APP_ID" --federated-credential-id "github-env-${env_name}" --output none 2>/dev/null
  az ad app federated-credential create --id "$APP_ID" --parameters '{
    "name": "github-env-'"${env_name}"'",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:'"${REPO}"':environment:'"${env_name}"'",
    "audiences": ["api://AzureADTokenExchange"],
    "description": "GitHub Actions - '"${env_name}"' environment"
  }' --output none
done
```

---

## Step 5: Grant Service Principal Access

The SP needs access to subscriptions **before** the bootstrap workflow can log in.
Assign Owner on the **tenant root management group** (not the `alz` prefix MG, which
doesn't exist yet):

```bash
SP_OBJECT_ID="<sp-object-id>"
TENANT_ROOT_MG="<your-tenant-id>"

az role assignment create \
  --assignee-object-id "$SP_OBJECT_ID" \
  --assignee-principal-type ServicePrincipal \
  --role "Owner" \
  --scope "/providers/Microsoft.Management/managementGroups/${TENANT_ROOT_MG}" \
  --output none
```

Verify:
```bash
az role assignment list --assignee "$SP_OBJECT_ID" --all \
  --query "[].{role:roleDefinitionName, scope:scope}" -o table
```

> **Lesson learned:** Assigning Owner on the `alz` MG prefix doesn't work for bootstrap
> because that MG doesn't exist yet. The SP gets "No subscriptions found" on login.
> Assign on the tenant root MG instead.

---

## Step 6: Set GitHub Secrets

```bash
REPO="<org>/<repo-name>"

# OIDC auth (if not set by the script)
gh secret set AZURE_TENANT_ID --repo "$REPO" --body "<tenant-id>"
gh secret set AZURE_CLIENT_ID --repo "$REPO" --body "<app-client-id>"

# Platform subscription IDs
gh secret set PLATFORM_MGMT_SUBSCRIPTION_ID --repo "$REPO" --body "<sub-1-id>"
gh secret set PLATFORM_CONN_SUBSCRIPTION_ID --repo "$REPO" --body "<sub-2-id>"
gh secret set PLATFORM_IDTY_SUBSCRIPTION_ID --repo "$REPO" --body "<sub-3-id>"
gh secret set PLATFORM_SEC_SUBSCRIPTION_ID  --repo "$REPO" --body "<sub-4-id>"
```

---

## Step 7: Create GitHub Environments

```bash
REPO="<org>/<repo-name>"

for env_name in platform-management platform-connectivity platform-identity \
                platform-security app-prod app-dev remediation; do
  gh api --method PUT "repos/${REPO}/environments/${env_name}" --silent
done
```

---

## Step 8: Set Runner Label

```bash
# GitHub-hosted runner (default)
gh variable set RUNNER_LABEL --repo "$REPO" --body "ubuntu-latest"

# Or self-hosted runner
gh variable set RUNNER_LABEL --repo "$REPO" --body "self-hosted"
```

---

## Step 9: Run Bootstrap Workflow

The bootstrap creates the management group hierarchy and moves subscriptions.

### Verify access first:
```bash
gh workflow run "1-bootstrap.yml" --repo "$REPO" \
  -f mg_prefix=mrg \
  -f primary_location=southcentralus \
  -f action=verify-only
```

### Run full bootstrap:
```bash
gh workflow run "1-bootstrap.yml" --repo "$REPO" \
  -f mg_prefix=mrg \
  -f primary_location=southcentralus \
  -f action=all
```

### Monitor progress:
```bash
# Watch the run
gh run list --workflow=1-bootstrap.yml --repo "$REPO" --limit 1

# Check individual job status
RUN_ID=$(gh run list --workflow=1-bootstrap.yml --repo "$REPO" --limit 1 \
  --json databaseId -q '.[0].databaseId')
gh api "repos/${REPO}/actions/runs/${RUN_ID}/jobs" \
  --jq '.jobs[] | "\(.name) | \(.status) | \(.conclusion)"'
```

### Expected results (platform-only):

| Job | Expected |
|-----|----------|
| Verify Azure Access | ✅ Success |
| Create Management Group Hierarchy | ✅ Success |
| Move Subscriptions (Platform) | ✅ All 4 moved |
| Move Subscriptions (App) | ❌ Expected failure if app secrets not set |
| Verify Bootstrap | ✅ Success |
| Register Resource Providers | ⏭️ Skipped if app subs failed upstream |

### Management group hierarchy created:

```
Tenant Root
└── mrg
    ├── mrg-platform
    │   ├── mrg-platform-management       (Sub 1)
    │   ├── mrg-platform-connectivity     (Sub 2)
    │   ├── mrg-platform-identity         (Sub 3)
    │   └── mrg-platform-security         (Sub 4)
    ├── mrg-landing-zones
    │   ├── mrg-landing-zones-corp
    │   ├── mrg-landing-zones-online
    │   └── mrg-landing-zones-sap
    ├── mrg-sandbox
    └── mrg-decommissioned
```

---

## Step 10: Register Resource Providers (if skipped)

If the bootstrap skipped provider registration due to the app subscription failure:

```bash
gh workflow run "1-bootstrap.yml" --repo "$REPO" \
  -f mg_prefix=mrg \
  -f primary_location=southcentralus \
  -f action=register-providers-only
```

---

## Next Steps

After bootstrap completes:

1. **Register resource providers** — run with `register-providers-only` if skipped
2. **Deploy platform landing zones** — trigger `2-platform-deploy.yml`
3. **Grant Sentinel Contributor role** — the Security LZ requires `Microsoft Sentinel Contributor` on the security subscription for Sentinel onboarding. Use the utility workflow:
   ```bash
   gh workflow run "assign-role.yml" \
     -f subscription_secret=PLATFORM_SEC_SUBSCRIPTION_ID \
     -f role_name="Microsoft Sentinel Contributor" \
     -f action=assign
   ```
   Or assign manually via the Azure portal. Allow 10-15 minutes for RBAC propagation.
4. **Set app subscription secrets** — when ready to deploy application landing zones
5. **Re-run bootstrap** with `move-subscriptions-only` to place app subs
6. **Run compliance scan** — `gh workflow run "monitor.yml" -f scan_type=compliance -f scan_scope=all`

---

## Troubleshooting

### "No subscriptions found" on OIDC login

**Cause:** The service principal doesn't have RBAC on any subscription or MG that
contains subscriptions.

**Fix:** Assign Owner on the tenant root management group (see Step 5).

### HTTP 404 when setting GitHub secrets

**Cause:** The repo doesn't exist or the PAT doesn't have access.

**Fix:** Ensure the repo exists and the PAT has `repo` scope. For SSO-protected
orgs, authorize the PAT for the org.

### "Unexpected inputs" when triggering workflow

**Cause:** The local workflow file and the remote (`.github/workflows/`) have
different input names.

**Fix:** Push local changes first (`git push github main`), or check the remote
workflow inputs:

```bash
gh api "repos/${REPO}/contents/.github/workflows/1-bootstrap.yml" \
  --jq '.content' | base64 -d | head -40
```

### Federated credential subject mismatch

**Cause:** The federated credential was created for a different repo path than
where the workflow runs.

**Fix:** Update the federated credentials (see Step 4). The subject claim must
match `repo:<org>/<repo>:ref:refs/heads/main` exactly.

### Sentinel "Unauthorized" / "Access denied" during Security LZ deploy

**Cause:** The OIDC service principal has `Contributor` but Sentinel onboarding
and data connector operations require `Microsoft Sentinel Contributor`.

**Fix:** Assign the role via the portal or the utility workflow:

```bash
gh workflow run "assign-role.yml" \
  -f subscription_secret=PLATFORM_SEC_SUBSCRIPTION_ID \
  -f role_name="Microsoft Sentinel Contributor" \
  -f action=assign
```

Wait 10-15 minutes for RBAC propagation before re-deploying.

### Defender plans "Another update operation is in progress"

**Cause:** Multiple Defender plan resources deploying concurrently hit Azure's
serial update requirement.

**Fix:** The `defender/main.bicep` module uses `@batchSize(1)` on the pricing
loop to serialize plan deployments. If you see this error after a cancelled run,
wait a few minutes for the orphaned operations to complete.

### Deprecated autoProvisioningSettings error

**Cause:** The `Microsoft.Security/autoProvisioningSettings@2017-08-01-preview`
resource with `autoProvision: 'On'` is deprecated and can no longer be enabled.

**Fix:** This resource has been removed from `defender/main.bicep`. If using a
custom Defender module, remove any `autoProvisioningSettings` resources.

### Subscription ID empty in reusable workflow jobs (secret masking)

**Cause:** The original `reusable-deploy.yml` used a `resolve` job to pass
subscription IDs via job outputs (`needs.resolve.outputs.sub_id`). GitHub
Actions automatically masks job outputs whose values match known repository
secrets, replacing the value with an empty string. This caused all downstream
jobs (validate, plan, deploy, verify) to receive an empty `subscription-id`.

**Symptoms:**
- Resolve job shows `success` but logs contain:
  `##[warning]Skip output 'sub_id' since it may contain secret.`
- Azure Login fails with:
  `Ensure 'subscription-id' is supplied or 'allow-no-subscriptions' is 'true'`

**Fix (applied 2026-04-15):**
1. Removed the `resolve` job from `reusable-deploy.yml`
2. Added `SUBSCRIPTION_ID` as a secret input to the reusable workflow
3. Each job now references `secrets.SUBSCRIPTION_ID` directly
4. Platform-deploy passes subscription IDs via `secrets:` block (not `with:`)

### Azure CLI not found on self-hosted runner

**Cause:** Self-hosted runners don't come with Azure CLI pre-installed (unlike
GitHub-hosted `ubuntu-latest` runners).

**Symptoms:**
- Azure Login step fails with:
  `Unable to locate executable file: az`
- Login cleanup also fails with the same message

**Fix (applied 2026-04-15):** Added an `Install Azure CLI` step before each
`Azure Login (OIDC)` step in `reusable-deploy.yml`:

```yaml
- name: Install Azure CLI
  run: |
    if ! command -v az &>/dev/null; then
      curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
    fi
```

### Secrets not allowed in `with:` for reusable workflows

**Cause:** GitHub Actions does not allow `${{ secrets.* }}` in the `with:` block
of reusable workflow calls. This causes a workflow parse error:
`Unrecognized named-value: 'secrets'`.

**Fix (applied 2026-04-15):** Moved `subscription_id` from `with:` to `secrets:`
in `2-platform-deploy.yml` for all 4 platform jobs.

### Secrets not allowed in `if:` conditions

**Cause:** GitHub Actions does not allow `secrets.*` in job/step `if:` conditions.
The `reusable-deploy.yml` had `if: always() && secrets.TEAMS_WEBHOOK_URL != ''`.

**Fix (applied 2026-04-15):** Replaced with an env var + runtime check:

```yaml
- name: Notify Teams on completion
  if: always()
  env:
    TEAMS_WEBHOOK: ${{ secrets.TEAMS_WEBHOOK_URL }}
  run: |
    if [ -z "$TEAMS_WEBHOOK" ]; then
      echo "No Teams webhook configured, skipping notification."
      exit 0
    fi
    # ... rest of curl command
```

---

## Change Log

### 2026-04-15 — Workflow Fixes for Platform Deployment

| Change | File | Description |
|--------|------|-------------|
| Comment out Sentinel | `infra/bicep/modules/management/main.bicep` | Sentinel disabled for initial LAW-only deployment |
| Create param file | `infra/bicep/parameters/platform-management-prod.bicepparam` | Bicep parameters: prefix=mrg, retention=90d, budget=$500 |
| Fix secrets in `with:` | `.github/workflows/2-platform-deploy.yml` | Moved subscription IDs from `with:` to `secrets:` block |
| Remove resolve job | `.github/workflows/reusable-deploy.yml` | Replaced masked job outputs with direct `secrets.SUBSCRIPTION_ID` |
| Fix Teams webhook | `.github/workflows/reusable-deploy.yml` | Moved from `if:` condition to env var + runtime check |
| Add Azure CLI install | `.github/workflows/reusable-deploy.yml` | Added install step for self-hosted runners without `az` |
| Switch to self-hosted | `RUNNER_LABEL` variable | Changed from `ubuntu-latest` to `self-hosted` |
