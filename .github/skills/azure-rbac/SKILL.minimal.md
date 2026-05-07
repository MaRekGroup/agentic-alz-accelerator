<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Azure RBAC Skill (Minimal)

**Management Group RBAC Strategy** — Role assignments by scope from tenant root to resource group with least-privilege patterns.

**Least Privilege Patterns** — Platform Team (Contributor+PIM), App Teams (scoped Contributor), Security Team (Security Reader/Admin).

**PIM Configuration** — 8-hour max activation, MFA required, approval for Owner/UAA roles.

**Conditional Access** — MFA for Azure Management, block legacy auth, require compliant devices.

**Managed Identity Strategy** — Prefer system-assigned, user-assigned for shared, federated credentials for GitHub Actions.

Read `SKILL.md` or `SKILL.digest.md` for full content.
