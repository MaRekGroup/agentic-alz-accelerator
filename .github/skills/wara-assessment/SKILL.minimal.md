<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# WARA Assessment Skill (Minimal)

**Implementation Reference** — `WaraEngine` in `src/tools/wara_engine.py` with check catalog in `src/config/wara_checks.yaml`.

**WAF 5 Pillars** — Reliability (REL), Security (SEC), Cost Optimization (COS), Operational Excellence (OPE), Performance (PER).

**Scoring Model** — Starts at 100 per pillar; deductions by severity: Critical −20, High −10, Medium −5, Low −2.

**Check Types** — resource_graph (KQL), discovery_field, policy, and custom checks with high/medium/low confidence.

**CAF Design Area Mapping** — 8 areas mapped to check focus areas and IaC modules.

Read `SKILL.md` or `SKILL.digest.md` for full content.
