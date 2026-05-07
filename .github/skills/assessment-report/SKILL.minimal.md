<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Assessment Report Skill (Minimal)

**Implementation Reference** — Module `src/tools/report_generator.py` with `ReportGenerator` class and CLI via `assess_cli.py`.

**Report Types** — Generates current-state, target-state, assessment report (md+json), architecture diagram (mermaid), ADR, and per-pillar WAF reports.

**Output Directory** — All artifacts written to `agent-output/{customer}/assessment/<scope-label>/`.

**Format Conventions** — Severity badges (🔴🟠🟡🔵), score interpretation (≥90 Excellent to <50 Poor), pillar→CAF area mapping.

**Caps and Limits** — 20 resources per finding, 20 policy assignments, UTC timestamps, alphanumeric Mermaid IDs.

**Integration** — JSON artifact feeds Step 1 requirements; alz-recall marks step complete.

Read `SKILL.md` or `SKILL.digest.md` for full content.
