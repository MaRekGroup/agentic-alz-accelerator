<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Context Shredding Skill (Minimal)

**Compression Tiers** — Full (<60% context), Summarized (60-80%), Minimal (>80%) — applied to both artifacts and skills.

**Skill Variants** — `SKILL.md` (400-800 tokens), `SKILL.digest.md` (150-320), `SKILL.minimal.md` (40-100).

**Artifact Compression** — Each artifact (00–09) has defined summarized/minimal templates with key fields to retain.

**Loading Priority** — Always load security baseline; compress oldest artifacts first; never skip governance constraints.

**Session Breaks** — At Gates 2/4, if context >70%, write handoff doc and start fresh session.

Read `SKILL.md` or `SKILL.digest.md` for full content.
