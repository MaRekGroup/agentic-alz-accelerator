# Project Context

- **Owner:** Yeselam Tesfaye
- **Project:** agentic-alz-accelerator
- **Stack:** Azure Landing Zone accelerator, Python, Bicep, Terraform, GitHub Actions, Markdown, YAML, and JSON
- **Description:** Multi-agent Azure Landing Zone accelerator with HVE workflow roles, agent prompts, skills, and deployment automation
- **Created:** 2026-05-08T21:31:32.689+00:00

## Core Context

Basher maps to the HVE design role and owns architecture visuals.

## Recent Updates

📌 Team hired on 2026-05-08T21:31:32.689+00:00 by Yeselam Tesfaye

## Learnings

Day-1 context: design artifacts must follow approved architecture and governance constraints.

### 2026-05-08 — Diagram Positioning & Value Proposition Review

**Architecture Decision:**
- Diagram generation is a **differentiator**, not a feature add-on. The system produces 4 diagram types (Draw.io, PNG, Mermaid) automatically from architecture decisions—no hand-drawing.
- **Credibility gaps identified**:
  - Diagrams don't sync with live Azure state post-deployment (no continuous regeneration)
  - No diagram validation rules → incomplete diagrams can slip through gates
  - Mermaid coverage limited to inline docs; not used for architecture diagrams
  - Export pipeline (SVG/PDF) missing; teams need Draw.io license to view/edit
- **Key proof points**:
  - Design agent (Step 3) produces 4 diagram types + ADRs
  - Documentation agent (Step 7) embeds diagrams in TDDs with resource inventory
  - marekgroup deployment shows 13 diagrams auto-generated (4 estate + 9 per-LZ)
  - Skills exist for all 3 engines: drawio (editable), python-diagrams (PNG), mermaid (markdown)

**Positioning Statement:**
"From Requirements to Deployed Reality — Automatically Visualized at Every Step."  
Diagrams are executable artifacts synchronized with architecture decisions and live deployments, not ornamental add-ons.

**Recommended messaging**:
- Emphasize **automation + consistency** (diagrams regenerate with architecture)
- Position as **"Visual Infrastructure Documentation as Code"**—define architecture, get diagrams
- Elevate in README (currently buried in features list; should be in main narrative)
- Flag 4 gaps to fix before external messaging (live sync, validation rules, Mermaid coverage, SVG/PDF export)

**Skill paths discovered**:
- `.github/skills/azure-diagrams/SKILL.md` — routing skill (decision tree for diagram type selection)
- `.github/skills/drawio/SKILL.md` — editable architecture diagrams via MCP server
- `.github/skills/python-diagrams/SKILL.md` — programmatic PNG generation
- `.github/skills/mermaid/SKILL.md` — inline markdown flowcharts, sequences, state machines

### 2026-05-13 — Cross-Agent Finding: Artifact Naming Contract Failure

**Insight from system review (Basher + Tess + Isabel):**

Basher's Finding 2 ("artifact naming is inconsistent across five documents") was independently confirmed by Tess (Finding 1) and Isabel (Risk 2). All three agents discovered the same structural problem: Artisan's output path and ADR naming differ across `design.md`, `04-design.prompt.md`, and `AGENTS.md`. **Critical**: The prompt does NOT produce `03-design-summary.md`, but Chronicler's prerequisite expects it. This is a silent artifact dependency failure.

**Implication for Basher:** When designing Step 3 visuals and ADRs, ensure the completion artifact is named `03-design-summary.md` and lists all diagram file paths and ADR references. This is now a hard contract between Design and Documentation steps.

**See:** `.squad/orchestration-log/2026-05-13T16-13-48Z-basher-design-audit.md` (full findings) and `.squad/decisions.md` (merged decision record).
- `src/tools/azure_diagram_generator.py` — SVG engine with official Azure colors
- `src/tools/tdd_generator.py` — Word document generation with embedded diagrams
- `src/tools/python_diagram_generator.py` — DiagramEngine class (4 methods: MG hierarchy, hub-spoke, security, full estate)

**Key agent responsibilities**:
- Design agent (Step 3): Generates diagrams from architecture assessment, validates CIDR ranges, outputs Draw.io + PNG + ADRs
- Documentation agent (Step 7): Embeds diagrams in TDDs, references architecture assessment + deployed state
- Challenger agent (Gate 2, 4): Should validate diagrams include required elements (currently no rule set)

### 2026-05-13T18:47:55.170+00:00 — Pass 1 Step 3 Contract Canonicalization

**Architecture decision:**
- Within Basher-owned Step 3 files, the canonical completion artifact is `agent-output/{customer}/03-design-summary.md`.
- Step 3 diagram outputs stay in `agent-output/{customer}/diagrams/` and use `03-design-*.{drawio,png,md}` naming.
- Step 3 ADR outputs stay in `agent-output/{customer}/adr/` and use `03-design-adr-{NNN}-{slug}.md` naming, while document titles remain `ADR-{NNN}: {Title}`.

**Reusable pattern:**
- Route with `.github/skills/azure-diagrams/SKILL.md` before choosing Draw.io, Python diagrams, or Mermaid; do not pick an engine first and back-justify it later.
- Make the handoff file a manifest, not a narrative summary: Step 7 needs exact relative paths for diagrams and ADRs.

**User preference captured:**
- Keep Step 3 fixes scoped to Basher-owned files and avoid touching shared workflow docs or Step 7 files during pass 1.

**Key file paths:**
- `.github/agents/design.md`
- `.github/prompts/04-design.prompt.md`
- `.github/agents/documentation.md`
- `.github/skills/azure-diagrams/SKILL.md`
- `.squad/decisions/inbox/basher-pass1-design-contract.md`

## 2026-05-08 — Scrum Master Initialization
- Scribe merged inbox decisions (4 files)
- Sprint planning system initialized
- Ready for Scrum Master coordination


---

## 2026-05-13T16:13:48Z: Step 3 Design Flow Audit Completed

**Context:** Fan-out request from Yeselam Tesfaye to review Step 3 design/documentation
flow for gaps, inconsistencies, and partial specifications.

**8 Findings (severity ranked):**
- [HIGH] Step 3 optionality has no defined skip criteria (complexity tier never referenced)
- [HIGH] Artifact naming conflicts across 5 documents — single biggest source of agent confusion
- [HIGH] No Challenger gate review covers design artifacts
- [MEDIUM] `04-design.prompt.md` is ~30 lines; `design.md` is 200+ lines — prompt is not a faithful trigger
- [MEDIUM] `azure-diagrams` routing skill and `azure-adr` skill missing from Artisan's required skill list
- [MEDIUM] "Use both methods" instruction conflicts with `azure-diagrams` decision tree routing
- [MEDIUM] No diagram completeness enforcement — no validator, no gate checklist
- [LOW] Step 7 handoff from Step 3 underspecified — no `03-design-summary.md` schema defined

**Key contradictions discovered:**
- ADR paths: `03-design-adr-*.md` (prompt) vs `adr/ADR-*.md` (agent) — direct file path contradiction
- Single vs multiple diagram files: AGENTS.md/markdown.instructions say `03-design-diagram.drawio`; agent uses `diagrams/*.drawio` subdirectory
- `azure-adr` skill: listed for Oracle+Chronicler in copilot-instructions.md but NOT for Artisan, who actually writes ADRs at Step 3

**Recommended target-state:** Complexity-gated skip → route skills in order (azure-diagrams first) → dual-format output → self-validate checklist → structured 03-design-summary.md schema for Chronicler consumption.

**Decision filed:** `.squad/decisions/inbox/basher-design-flow-review.md`

**Key files audited:**
- `.github/agents/design.md`
- `.github/prompts/04-design.prompt.md`
- `docs/workflow.md`
- `AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/markdown.instructions.md`
- `.github/skills/azure-diagrams/SKILL.md`
- `.github/skills/drawio/SKILL.md`
- `.github/skills/python-diagrams/SKILL.md`
- `.github/skills/mermaid/SKILL.md`
- `.squad/skills/diagram-generation-patterns/SKILL.md`
- `.github/agents/documentation.md` (for Step 7 handoff expectations)

---

## 2026-05-08T22:31:56Z: Architecture Diagram Positioning Analysis Completed

**Context:** Repository positioning sprint to position diagram generation as core differentiator and identify gaps in diagram lifecycle coverage.

**Your Contribution:** Analyzed architecture diagram generation capabilities across Steps 3 (Design) and 7 (Documentation). Positioned diagrams as "executable artifacts synchronized throughout entire infrastructure lifecycle" — not ornamental.

**Positioning Statement:** "From Requirements to Deployed Reality — Automatically Visualized at Every Step"

**4 Standard Diagram Types:**
1. Management group hierarchy (Mermaid + Draw.io)
2. Hub-spoke network topology with CIDRs (Draw.io + PNG)
3. Security & governance architecture with policies (Draw.io + PNG)
4. Full ALZ estate overview (Draw.io + PNG)

**Multi-Engine Routing:** Draw.io (interactive, editable), Python diagrams (programmatic), Mermaid (markdown)

**6-Gap Roadmap (Prioritized):**
- **MUST:** Diagram validation rules (Gate 3), Live state sync (Step 8)
- **SHOULD:** SVG/PDF export, Mermaid MG hierarchy
- **NICE:** Custom topology templates, Icon inventory publishing

**Immediate Wins (Next Sprint):**
- Mermaid MG hierarchy output (2 hrs)
- Diagram validation at Phase 2 gate (4 hrs)
- Draw.io MCP documentation (3 hrs)

**Team Coordination:**
- Linus included diagram generation in Proposition 2 (knowledge capture)
- Tess positioned diagrams as embedded in TDDs (operational asset)
- Terry documented diagram gap as underexploited differentiator

**Team Outcome:** Diagram generation positioned as credible, differentiating capability with honest roadmap for gaps. Multi-engine approach explains flexibility; execution plan shows near-term wins.

**Next Phase:** Sprint S1 will prioritize diagram-related enhancements and finalize messaging with examples.

### 2026-05-13T18:47:55.170+00:00 — Pass 1 Step 3 design contract

**Task:** Audit and canonicalize Step 3 (Design / Artisan) workflow contract without editing shared docs.

**Key Decisions:**
1. Canonical completion artifact: `agent-output/{customer}/03-design-summary.md`
2. Diagram storage: `agent-output/{customer}/diagrams/` with `03-design-<topic>.{drawio|png|md}` naming
3. ADR storage: `agent-output/{customer}/adr/` with `03-design-adr-{NNN}-{slug}.md` naming
4. Skill routing: `azure-diagrams` routes before engine selection; Draw.io/PNG for architecture; Mermaid for inline

**Key Findings from Audit:**
- 8 findings identified (HIGH: 3, MEDIUM: 4, LOW: 1)
- Artifact naming inconsistent across 5 sources (AGENTS.md, markdown.instructions.md, design.md, prompt, copilot-instructions.md)
- Skip criteria undefined (no link to complexity tier)
- No Challenger review slot for design artifacts
- Diagram completeness has no enforcement mechanism

**Key Files Updated:**
- `.github/agents/design.md`
- `.github/prompts/04-design.prompt.md`

**Pattern:** When audit reveals artifact contract mismatches, canonicalize in specialist-owned files first; shared-doc updates come in next pass after team alignment.

