<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Azure Governance Discovery Skill (Minimal)

**Usage** — Run `discover.py` with `--scope`, `--customer`, and `--out` flags to enumerate Azure Policy assignments.

**Effect Classification** — Deny=Blocker, DeployIfNotExists/Modify=Auto-remediate, Audit=Advisory, Disabled=Ignore.

**Output Schema** — `governance-constraints-v1` JSON envelope with blockers, auto-remediation, audit findings, and security baseline alignment.

**Defender Filtering** — Defender auto-assignments excluded by default; use `--include-defender` to include.

**Integration** — Feeds Strategist (Step 4), Forge (Step 5), Challenger (gates), and Sentinel (Step 8).

Read `SKILL.md` or `SKILL.digest.md` for full content.
