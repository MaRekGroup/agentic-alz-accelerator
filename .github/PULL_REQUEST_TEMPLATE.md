## Description

<!-- Brief summary of what this PR does -->

## Related Issue

Fixes #

## Type of Change

- [ ] 🏗️ New infrastructure module (Bicep/Terraform)
- [ ] 🤖 Agent definition update (`.github/agents/`)
- [ ] 🛡️ Governance/policy change
- [ ] 📝 Documentation update
- [ ] 🐛 Bug fix
- [ ] 🔧 Refactoring (no functional changes)
- [ ] ⚙️ Configuration/workflow change
- [ ] 💰 MCP server enhancement

## Workflow Used

- [ ] Multi-step workflow: `@requirements` → `architect` → `iac-planner` → `bicep-code`/`terraform-code`
- [ ] Direct implementation (simple change)
- [ ] Copilot Coding Agent (autonomous)
- [ ] Manual implementation

## Changes Made

**Files added:**
-

**Files modified:**
-

## Testing Performed

### Infrastructure (if applicable)

- [ ] `az bicep build` succeeds for all `.bicep` files
- [ ] `az bicep lint` passes with no errors
- [ ] `terraform init && terraform validate` passes
- [ ] Deployed to Azure subscription (region: **____**)
- [ ] All resources pass Azure Policy compliance
- [ ] Resources cleaned up after testing

### Validators

- [ ] Security baseline: `python scripts/validators/validate_security_baseline.py infra/bicep/`
- [ ] Cost governance: `python scripts/validators/validate_cost_governance.py infra/bicep/`
- [ ] Python tests: `python -m pytest tests/ -v`

## Well-Architected Framework Alignment

- [ ] 🛡️ **Security** — Private endpoints, managed identity, TLS 1.2+, no public blob access
- [ ] 🔄 **Reliability** — Zone redundancy, backups, monitoring
- [ ] 💰 **Cost Optimization** — Right-sizing, auto-scaling, budget alerts (80%/100%/120%)
- [ ] ⚡ **Performance Efficiency** — Caching, CDN, scaling
- [ ] 🔧 **Operational Excellence** — IaC, monitoring, alerts, diagnostics

## CAF Design Areas Impacted

- [ ] Billing & Tenant
- [ ] Identity & Access
- [ ] Resource Organization
- [ ] Network Topology & Connectivity
- [ ] Security
- [ ] Management
- [ ] Governance
- [ ] Platform Automation & DevOps

## Pre-Submission Checklist

### Security Baseline (Non-Negotiable)

- [ ] TLS 1.2 minimum on all applicable resources
- [ ] HTTPS-only traffic enforced
- [ ] No public blob access
- [ ] Managed Identity used (no service principal secrets)
- [ ] Azure AD-only SQL authentication
- [ ] Public network disabled for production environments

### Cost Governance

- [ ] Budget resource included with 80%/100%/120% forecast alerts
- [ ] Budget amounts parameterized per environment (no hardcoded values)

### Code Standards

- [ ] Region defaults to `southcentralus` (or configurable via parameter)
- [ ] Resource names follow CAF naming conventions
- [ ] Required tags: `Environment`, `Owner`, `CostCenter`, `Project`, `ManagedBy`
- [ ] Uses Azure Verified Modules (AVM) where available
- [ ] No hardcoded secrets, subscription IDs, or sensitive data

### PR Hygiene

- [ ] PR touches < 50 files (split larger changes into stacked PRs)
- [ ] Commit messages follow conventional commits format
- [ ] Architecture diagram included (for significant infrastructure changes)

## Screenshots / Architecture Diagram

<!-- If applicable, add diagrams or screenshots -->

## Additional Notes

<!-- Any deployment instructions, breaking changes, or special considerations -->
