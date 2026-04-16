---
name: github-operations
description: "Git branching, PR workflows, and GitHub CLI conventions for the ALZ Accelerator. USE FOR: branch naming, commit messages, PR creation, GitHub Actions workflows. DO NOT USE FOR: Azure deployments (use deployment agent)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "2.0"
  category: tooling-devops
---

# GitHub Operations Skill

Git and GitHub conventions for the ALZ Accelerator.

## Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feat/{description}` | `feat/add-connectivity-module` |
| Fix | `fix/{description}` | `fix/nsg-rules-missing` |
| Docs | `docs/{description}` | `docs/update-runbook` |
| Chore | `chore/{description}` | `chore/update-dependencies` |

## Conventional Commits

```
<type>(<scope>): <short description>

<body — what changed and why>
```

Types: `feat`, `fix`, `refactor`, `docs`, `chore`, `ci`, `test`

Scopes: `agents`, `skills`, `bicep`, `terraform`, `mcp`, `tools`, `docs`, `pipelines`

Examples:
- `feat(bicep): add connectivity module with hub-spoke topology`
- `fix(agents): correct governance agent policy effect classification`
- `docs(guide): update MCP server count from 5 to 3`

## GitHub CLI Commands

```bash
# Create a PR
gh pr create --title "feat(bicep): add connectivity module" --body "..." --base main

# Check PR status
gh pr status

# View issues
gh issue list --label "landing-zone"

# Create an issue from template
gh issue create --template landing-zone-request.yml
```

## OIDC Setup for GitHub Actions

```bash
# Run the OIDC setup script
./scripts/setup-oidc.sh
```

This creates federated credentials for:
- `main` branch deployments
- PR validation (plan/what-if only)
- Environment-specific deployments (dev, staging, prod)
