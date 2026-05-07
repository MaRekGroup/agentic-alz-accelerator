<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Terraform Test Skill (Digest)

Write, organize, and run Terraform's built-in test framework (`.tftest.hcl`) for Enterprise Landing Zone modules.

## Quick Reference

| Concept | Description | Min Version |
|---------|-------------|-------------|
| Test file | `.tftest.hcl` in `tests/` directory | 1.6 |
| Run block | Single test scenario with assertions | 1.6 |
| Plan mode | `command = plan` — validates logic, no resources created | 1.6 |
| Apply mode | `command = apply` (default) — creates real infrastructure | 1.6 |
| Mock provider | Simulates provider without real API calls | 1.7 |
| Expect failures | Verify validation rules reject invalid input | 1.6 |

## File Structure & Naming

```
infra/terraform/{customer}/tests/
  *_unit_test.tftest.hcl            # Plan mode (fast, no Azure creds with mocks)
  *_integration_test.tftest.hcl     # Apply mode (creates resources)
```

## ALZ-Specific Test Patterns

| Test | What It Validates |
|------|-------------------|
| Security baseline | 6 non-negotiable rules (TLS, HTTPS, blob, MI, AD auth, public network) |
| Required tags | 5 required tags (Environment, Owner, CostCenter, Project, ManagedBy) |
| Budget | Budget resource exists with 80/100/120% alert thresholds |
| Naming convention | CAF naming pattern: `{prefix}-{workload}-{region}-{type}` |
| Validation rules | `expect_failures` for invalid inputs (bad environment, empty prefix) |
| Mock provider | Unit tests without Azure credentials using mock resources |

## Running Tests

```bash
cd infra/terraform/{customer}
terraform test                                        # All tests
terraform test tests/security_baseline_unit_test.tftest.hcl  # Specific file
terraform test -verbose                                # Verbose output
terraform test tests/*_unit_test.tftest.hcl            # Unit tests only
```

## Key Syntax Rules

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `command` | `plan`/`apply` | `apply` | Test mode |
| `variables` | block | — | Override file-level variables |
| `assert` | block (1+) | — | Validation conditions |
| `expect_failures` | list | — | Expected validation failures |
| `module` | block | — | Test alternate module |

## Workflow Integration

| Step | Agent | Test Type |
|------|-------|-----------|
| Step 5 (Code Gen) | Forge | Generate test files alongside modules |
| Step 5 (Validation) | azure-validate | Run `terraform test` as preflight |
| Gate 5 | Challenger | Review test coverage and results |
| CI/CD | PR Validate | Run unit tests in `5-pr-validate.yml` |

## Best Practices

1. Plan mode first for fast, cost-free validation
2. Test all 6 security baseline rules in every module
3. Test all 5 required tags
4. Use mock providers in CI (no Azure credentials needed)
5. Use `expect_failures` for validation rule coverage
6. Never hard-code subscription IDs in tests

> _See SKILL.md for full HCL code examples for each test pattern._
