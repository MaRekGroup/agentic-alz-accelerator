<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Terraform Test Skill (Minimal)

**Quick Reference** — `.tftest.hcl` files with run blocks, assertions, plan/apply modes, mock providers (TF >= 1.6–1.9).

**File Structure** — `*_unit_test.tftest.hcl` (plan mode, fast) and `*_integration_test.tftest.hcl` (apply mode) in `tests/`.

**ALZ Test Patterns** — Security baseline, required tags, budget, naming convention, validation rules, and mock provider tests.

**Running Tests** — `terraform test` from the module directory; filter with specific file paths or `-verbose`.

**Workflow Integration** — Tests generated at Step 5, validated at Gate 5, and run in CI via `5-pr-validate.yml`.

**Best Practices** — Plan mode first, test security baseline + tags + budgets, use mocks in CI, never hard-code subscription IDs.

Read `SKILL.md` or `SKILL.digest.md` for full content.
