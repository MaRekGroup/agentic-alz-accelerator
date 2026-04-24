# Bicep Infrastructure Templates

Azure Bicep templates for Landing Zone deployments, organized per customer/project.

## Structure

```text
infra/bicep/
├── README.md                   ← You are here (template docs)
├── {customer}/                 ← Per-customer project folder
│   ├── main.bicep              # Root deployment template
│   ├── modules/                # Customer-specific modules
│   │   ├── management/
│   │   ├── connectivity/
│   │   ├── identity/
│   │   ├── security/
│   │   └── ...
│   └── parameters/             # Parameter files per platform LZ
│       ├── platform-management-prod.bicepparam
│       ├── platform-connectivity-prod.bicepparam
│       ├── platform-identity-prod.bicepparam
│       └── platform-security-prod.bicepparam
```

Each customer folder is self-contained — modules, parameters, and root template
are all co-located. Different customers can have different module configurations.

## Setup

Run `scripts/init-project.sh` to scaffold a new customer:

```bash
./scripts/init-project.sh --customer acme --prefix acm --region eastus2
```

## Validation

```bash
# Build (syntax check)
az bicep build --file infra/bicep/{customer}/main.bicep

# Security baseline
python scripts/validators/validate_security_baseline.py infra/bicep/{customer}/

# Cost governance
python scripts/validators/validate_cost_governance.py infra/bicep/{customer}/
```

## Deployment

Deployments run through GitHub Actions — not local CLI:

```bash
gh workflow run 2-platform-deploy.yml -f framework=bicep -f action=deploy -f customer={customer}
```
