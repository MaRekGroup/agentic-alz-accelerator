# Terraform Infrastructure

Terraform configurations for Landing Zone deployments, organized per customer/project.

## Structure

```text
infra/terraform/
├── README.md                   ← You are here (template docs)
├── {customer}/                 ← Per-customer project folder
│   ├── main.tf                 # Root module — providers, module calls
│   ├── modules/                # Customer-specific modules
│   │   ├── logging/
│   │   ├── networking/
│   │   ├── security/
│   │   ├── identity/
│   │   └── ...
│   └── environments/           # Variable files per environment
│       ├── dev/terraform.tfvars
│       └── prod/terraform.tfvars
```

Each customer folder is self-contained. Different customers can have different
module configurations, providers, and backend settings.

## Setup

Run `scripts/init-project.sh` to scaffold a new customer:

```bash
./scripts/init-project.sh --customer acme --prefix acm --region eastus2
```

## Validation

```bash
cd infra/terraform/{customer}
terraform init -backend=false
terraform validate
terraform fmt -check -recursive
```

## Conventions

- **AVM-first**: Use AVM-TF modules from `registry.terraform.io/Azure/avm-res-{provider}-{resource}/azurerm`
- **Provider pin**: `~> 4.0` for AzureRM
- **Backend**: Azure Storage Account (configured via `-backend-config` at init)
- **Tags**: Every resource gets required tags (`Environment`, `ManagedBy`, `Project`, `Owner`)
- **Security**: TLS 1.2, HTTPS-only, managed identity, no public blob access

## Deployment

Deployments run through GitHub Actions — not local CLI:

```bash
gh workflow run 2-platform-deploy.yml -f framework=terraform -f action=deploy -f customer={customer}
```
