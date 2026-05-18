---
name: skill-authoring-pattern
description: "Reusable pattern for drafting Wave 1 skill files with explicit boundaries, additive framing, brownfield coverage, and operational guidance."
category: documentation-workflow
author: saul
version: "1.0"
---

# Skill Authoring Pattern

## Pattern

Author new Wave 1 skill files as additive depth, not greenfield replacements.

| Element | Pattern |
|---------|---------|
| Frontmatter | Include name, USE FOR, DO NOT USE FOR, compatibility, license, and metadata |
| Framing | State which existing skill is extended and what remains out of scope |
| Architecture depth | Add CAF and WAF tables, then pattern tables that downstream agents can act on |
| Brownfield | Include a named `Brownfield Scenario` subsection with a retrofit, migration, or audit playbook |
| Implementation | Include Bicep, Terraform, CLI, Graph, or equivalent programmatic examples when the platform is automatable |
| Operations | Include rollout, monitoring, anti-patterns, and references |

## Why It Works

- Gives Warden policy language, Forge automation direction, and Challenger review hooks in one artifact.
- Preserves the additive-brownfield directive by making retrofit guidance mandatory.
- Prevents sibling skills from overlapping by forcing explicit DO NOT USE FOR clauses.
