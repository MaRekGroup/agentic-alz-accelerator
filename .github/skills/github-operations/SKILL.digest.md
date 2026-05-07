<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# GitHub Operations Skill (Digest)

Git and GitHub conventions for the ALZ Accelerator.

## Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feat/{description}` | `feat/add-connectivity-module` |
| Fix | `fix/{description}` | `fix/nsg-rules-missing` |
| Docs | `docs/{description}` | `docs/update-runbook` |
| Chore | `chore/{description}` | `chore/update-dependencies` |

## Conventional Commits

```text
<type>(<scope>): <short description>
```

Types: `feat`, `fix`, `refactor`, `docs`, `chore`, `ci`, `test`

Scopes: `agents`, `skills`, `bicep`, `terraform`, `mcp`, `tools`, `docs`, `pipelines`

## Key CLI Commands

```bash
gh pr create --title "feat(bicep): ..." --body "..." --base main
gh pr status
gh issue list --label "landing-zone"
```

## OIDC Setup

```bash
./scripts/setup-oidc.sh
```

Creates federated credentials for main branch, PR validation, and environment-specific deployments.
