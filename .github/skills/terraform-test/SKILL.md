---
name: terraform-test
description: "Write and run Terraform tests (.tftest.hcl) for Enterprise Landing Zone modules. USE FOR: test files, run blocks, assertions, mock providers, plan-mode unit tests, apply-mode integration tests. DO NOT USE FOR: Bicep code, architecture decisions, deployment."
compatibility: Requires Terraform >= 1.6 (test blocks), >= 1.7 (mock providers), >= 1.9 (parallel execution)
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "1.0"
  category: terraform
---

# Terraform Test Skill

Write, organize, and run Terraform's built-in test framework for Enterprise
Landing Zone infrastructure modules.

## Quick Reference

| Concept | Description | Min Version |
|---------|-------------|-------------|
| Test file | `.tftest.hcl` in `tests/` directory | 1.6 |
| Run block | Single test scenario with assertions | 1.6 |
| Assert block | Condition that must be true for test to pass | 1.6 |
| Plan mode | `command = plan` — validates logic, no resources created | 1.6 |
| Apply mode | `command = apply` (default) — creates real infrastructure | 1.6 |
| Mock provider | Simulates provider without real API calls | 1.7 |
| Expect failures | Verify validation rules reject invalid input | 1.6 |

## File Structure

```text
infra/terraform/{customer}/
├── main.tf
├── variables.tf
├── outputs.tf
├── modules/
│   ├── management/
│   ├── connectivity/
│   ├── identity/
│   └── security/
└── tests/
    ├── naming_unit_test.tftest.hcl           # Plan mode — CAF naming
    ├── security_baseline_unit_test.tftest.hcl # Plan mode — 6 security rules
    ├── tags_unit_test.tftest.hcl             # Plan mode — required tags
    ├── budget_unit_test.tftest.hcl           # Plan mode — cost governance
    └── platform_integration_test.tftest.hcl  # Apply mode — deploys resources
```

**Naming convention**: `*_unit_test.tftest.hcl` (plan mode, fast), `*_integration_test.tftest.hcl` (apply mode, creates resources).

## ALZ-Specific Test Patterns

### Security Baseline Test (Plan Mode)

```hcl
# tests/security_baseline_unit_test.tftest.hcl

run "storage_account_tls" {
  command = plan

  assert {
    condition     = azurerm_storage_account.main.min_tls_version == "TLS1_2"
    error_message = "Security baseline rule 1: TLS 1.2 minimum required"
  }

  assert {
    condition     = azurerm_storage_account.main.https_traffic_only_enabled == true
    error_message = "Security baseline rule 2: HTTPS-only traffic required"
  }

  assert {
    condition     = azurerm_storage_account.main.allow_nested_items_to_be_public == false
    error_message = "Security baseline rule 3: No public blob access"
  }
}

run "managed_identity" {
  command = plan

  assert {
    condition     = azurerm_storage_account.main.identity[0].type == "SystemAssigned"
    error_message = "Security baseline rule 4: Managed identity required"
  }
}
```

### Required Tags Test

```hcl
# tests/tags_unit_test.tftest.hcl

variables {
  environment = "prod"
  owner       = "platform-team"
  cost_center = "IT-001"
  project     = "alz-platform"
}

run "required_tags_present" {
  command = plan

  assert {
    condition     = contains(keys(azurerm_resource_group.main.tags), "Environment")
    error_message = "Required tag 'Environment' missing"
  }

  assert {
    condition     = contains(keys(azurerm_resource_group.main.tags), "Owner")
    error_message = "Required tag 'Owner' missing"
  }

  assert {
    condition     = contains(keys(azurerm_resource_group.main.tags), "CostCenter")
    error_message = "Required tag 'CostCenter' missing"
  }

  assert {
    condition     = contains(keys(azurerm_resource_group.main.tags), "Project")
    error_message = "Required tag 'Project' missing"
  }

  assert {
    condition     = contains(keys(azurerm_resource_group.main.tags), "ManagedBy")
    error_message = "Required tag 'ManagedBy' missing"
  }
}
```

### Budget Test (Cost Governance)

```hcl
# tests/budget_unit_test.tftest.hcl

run "budget_exists" {
  command = plan

  assert {
    condition     = length(azurerm_consumption_budget_subscription.main) > 0
    error_message = "Cost governance: budget resource required for every deployment"
  }
}

run "budget_thresholds" {
  command = plan

  assert {
    condition     = length(azurerm_consumption_budget_subscription.main.notification) >= 3
    error_message = "Cost governance: budget must have 80%, 100%, 120% alert thresholds"
  }
}
```

### Naming Convention Test

```hcl
# tests/naming_unit_test.tftest.hcl

variables {
  prefix   = "mrg"
  location = "southcentralus"
}

run "resource_group_naming" {
  command = plan

  assert {
    condition     = can(regex("^mrg-.*-scus-rg$", azurerm_resource_group.main.name))
    error_message = "Resource group name must follow CAF pattern: {prefix}-{workload}-{region}-rg"
  }
}
```

### Validation Rule Test (Expect Failures)

```hcl
# tests/validation_unit_test.tftest.hcl

run "reject_invalid_environment" {
  command = plan

  variables {
    environment = "invalid"
  }

  expect_failures = [
    var.environment
  ]
}

run "reject_empty_prefix" {
  command = plan

  variables {
    prefix = ""
  }

  expect_failures = [
    var.prefix
  ]
}
```

### Mock Provider (Unit Tests Without Azure)

```hcl
# tests/mock_unit_test.tftest.hcl

mock_provider "azurerm" {
  mock_resource "azurerm_resource_group" {
    defaults = {
      id       = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/mock-rg"
      location = "southcentralus"
      tags     = {
        Environment = "prod"
        Owner       = "platform-team"
        CostCenter  = "IT-001"
        Project     = "alz-platform"
        ManagedBy   = "terraform"
      }
    }
  }
}

run "mock_plan" {
  command = plan

  assert {
    condition     = azurerm_resource_group.main.location == "southcentralus"
    error_message = "Default region should be southcentralus"
  }
}
```

## Running Tests

```bash
# All tests (from module directory)
cd infra/terraform/{customer}
terraform test

# Specific test file
terraform test tests/security_baseline_unit_test.tftest.hcl

# Verbose output
terraform test -verbose

# Filter by name
terraform test -filter=storage_account_tls

# Unit tests only (plan mode — no Azure credentials needed with mocks)
terraform test tests/*_unit_test.tftest.hcl
```

## Integration with Workflow

| Step | Agent | Test Type |
|------|-------|-----------|
| Step 5 (Code Gen) | Forge | Generate test files alongside modules |
| Step 5 (Validation) | azure-validate | Run `terraform test` as part of preflight |
| Gate 5 | Challenger | Review test coverage and results |
| CI/CD | PR Validate | Run unit tests in `5-pr-validate.yml` |

## Key Syntax Rules

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `command` | `plan`/`apply` | `apply` | Test mode |
| `variables` | block | — | Override file-level variables |
| `assert` | block (1+) | — | Validation conditions |
| `expect_failures` | list | — | Expected validation failures |
| `module` | block | — | Test alternate module |

## Best Practices

1. **Plan mode first** — use `command = plan` for fast, cost-free validation
2. **Test the 6 security baseline rules** — every module must validate these
3. **Test required tags** — verify all 5 required tags are present
4. **Test budget resources** — verify cost governance compliance
5. **Mock for CI** — use mock providers in PR validation (no Azure credentials)
6. **Negative testing** — use `expect_failures` for validation rule coverage
7. **Naming convention tests** — verify CAF naming patterns

## Guardrails

**DO:** Test security baseline rules · Test required tags · Test naming patterns ·
Use plan mode for unit tests · Use mocks in CI pipelines.

**DON'T:** Skip security baseline tests · Use apply mode without cleanup ·
Hard-code subscription IDs in tests · Test against production subscriptions.
