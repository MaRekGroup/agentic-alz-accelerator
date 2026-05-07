<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Profile Management Skill (Minimal)

**3-Tier Inheritance Model** — YAML-based: base-platform → platform-{name} → overrides/{env}/{name}, merged via deep dictionary merge.

**Available Profiles** — Four platform profiles (management, connectivity, identity, security) with Dev/Prod differentiation tables.

**File Locations** — Profiles in `src/config/profiles/` with base, LZ-specific, and environment override tiers.

**Key Configuration Fields** — Shared fields: location, resource_group_name, tags, budget, networking, security, monitoring.

Read `SKILL.md` or `SKILL.digest.md` for full content.
