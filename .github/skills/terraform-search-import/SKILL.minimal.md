<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Terraform Search & Import Skill (Minimal)

**When to Use** — Brownfield scenarios requiring existing Azure resources to come under Terraform IaC management.

**Manual Discovery Workflow** — Discover via `az resource list`, create paired `import {}` + `resource {}` blocks, plan, and apply.

**Resource Type Mapping** — Maps platform LZ resource types (Management, Connectivity, Identity, Security) to Terraform resources and import patterns.

**Post-Import** — Refactor to AVM modules using `moved {}` blocks, then validate security baseline compliance.

**Constraints** — Never run apply locally; always use GitHub Actions; import blocks in separate `imports.tf`.

Read `SKILL.md` or `SKILL.digest.md` for full content.
