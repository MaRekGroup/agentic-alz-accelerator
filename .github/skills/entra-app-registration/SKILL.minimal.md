<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Entra App Registration Skill (Minimal)

**Core Concepts** — App registrations for CI/CD identity; federated credentials (OIDC) over client secrets; Managed Identity for workloads.

**OIDC Workflow** — Create app → service principal → federated credential → RBAC assignment → GitHub variables.

**Naming** — `sp-{prefix}-platform-deploy` for platform, `sp-{prefix}-{app}-deploy` for app LZs.

**Security** — No client secrets, no Owner role, environment-scoped federation, no wildcard subjects.

**Integration** — Bootstrap, Step 3.5 audit, Step 5 code gen, Step 6 deployment.

Read `SKILL.md` or `SKILL.digest.md` for full content.
