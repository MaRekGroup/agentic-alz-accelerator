---
applyTo: ".github/instructions/**"
---

# Instructions Authoring

## Format

Every instruction file must have YAML frontmatter with `applyTo` glob:

```yaml
---
applyTo: "**/*.bicep"
---
```

## Glob Patterns

- `**/*.bicep` — all Bicep files
- `**/*.tf` — all Terraform files
- `**/*.py` — all Python files
- `**/*.md` — all Markdown files
- `.github/agents/**` — agent definitions only

## Rules

- Keep instructions concise and actionable
- Focus on patterns specific to this project
- Reference skills for domain knowledge, instructions for coding rules
- Do not duplicate content between instructions and skills
