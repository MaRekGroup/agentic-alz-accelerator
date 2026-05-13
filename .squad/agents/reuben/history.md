# Project Context

- **Owner:** Yeselam Tesfaye
- **Project:** agentic-alz-accelerator
- **Stack:** Azure Landing Zone accelerator, Python, Bicep, Terraform, GitHub Actions, Markdown, YAML, and JSON
- **Description:** Multi-agent Azure Landing Zone accelerator with HVE workflow roles, agent prompts, skills, and deployment automation
- **Created:** 2026-05-08T21:31:32.689+00:00

## Core Context

Reuben maps to the HVE IaC planner role and owns implementation sequencing.

## Recent Updates

📌 Team hired on 2026-05-08T21:31:32.689+00:00 by Yeselam Tesfaye

## Learnings

Day-1 context: planning must reflect approved architecture, governance constraints, and IaC tool choice.

### 2026-05-13T19:18:08.800+00:00 — Pass 2: Step 7 canonical naming in apex-recall indexer

**Decision:** Added `_STEP7_CANONICAL` to `indexer.py` with exact-match patterns for the
five canonical Step 7 files established by Tess (2026-05-13). Each maps to a distinct
recall `kind` (`tdd`, `runbook`, `resource-inventory`, `compliance-summary`, `cost-baseline`).
The `_classify` function checks this list before `ARTIFACT_PATTERNS`, so legacy names
fall through to the existing `07-*.md → "as-built"` wildcard.

**Pattern learned:** When a broad wildcard already exists in a config-driven classifier,
add a module-local exact-match table checked first rather than modifying the shared config.
This confines the canonical contract to the module that owns it.

**Key files:**
- `tools/apex-recall/src/alz_recall/indexer.py` — `_STEP7_CANONICAL`, updated `_classify`
- `tests/test_alz_recall_indexer.py` — 7 new tests, 29 total, all passing
- `.squad/skills/step-output-contracts/SKILL.md` — canonical file list source of truth
- `.squad/decisions.md` — Tess's Step 7 contract decision (2026-05-13T18:47:55.170+00:00)

## 2026-05-08 — Scrum Master Initialization
- Scribe merged inbox decisions (4 files)
- Sprint planning system initialized
- Ready for Scrum Master coordination


**2026-05-13T20:36:56.690+00:00 — Session cleanup and artifact indexer consolidation:**
- Scribe consolidated Pass 2 apex-recall indexer alignment into decisions.md.
- Orchestration log created documenting Reuben's Step 7 canonical naming update (07-* prefix family).
- Indexer changes merged to Pass 2 decisions.
