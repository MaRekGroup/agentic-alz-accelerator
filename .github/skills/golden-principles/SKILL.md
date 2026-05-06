---
name: golden-principles
description: "The 10 agent-first operating principles governing how agents work in this repository. USE FOR: agent behavior rules, operating philosophy, principle lookup, governance invariants. DO NOT USE FOR: Azure infrastructure, code generation, troubleshooting, diagram creation."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "1.0"
  category: governance
---

# Golden Principles

These 10 principles govern how every agent operates in this Enterprise Landing Zone accelerator.
Adapted from Harness Engineering philosophy for agent-driven infrastructure at scale.

---

## The 10 Principles

### 1. Repository Is the System of Record

All context lives in-repo, not in external docs or chat history.
Agent outputs go to `agent-output/`, decisions go to ADRs, conventions go to
skills and instructions. If it isn't committed, it doesn't exist.

**Test**: Can a new agent session reconstruct full project context from repo files alone?

---

### 2. Map, Not Manual

Instructions point to deeper sources; never dump everything into context.
`AGENTS.md` is the table of contents. Skills hold deep knowledge. Instructions
enforce rules. No single file should try to be comprehensive.

**Test**: Does each context-loaded file stay under 200 lines? Does it point to
deeper sources rather than inline them?

---

### 3. Enforce Invariants, Not Implementations

Set strict boundaries but allow autonomous expression within them.
Enforce WHAT must be true (TLS 1.2, AVM-first, managed identity, budget alerts),
not HOW to achieve it. Agents choose their path within the invariant envelope.

**Test**: Are rules expressed as constraints ("MUST use managed identity")
rather than scripts ("first create identity, then assign role...")?

---

### 4. Parse at Boundaries

Validate inputs and outputs at module edges, not in the middle.
Each workflow step validates its prerequisites exist and its outputs
conform to templates. Internal logic is the agent's domain.

**Test**: Does each agent check for required input artifacts before starting?
Does each output pass artifact template validation?

---

### 5. AVM-First, Security Baseline Always

Prefer Azure Verified Modules over hand-rolled Bicep/Terraform.
Apply the security baseline (TLS 1.2, HTTPS-only, managed identity,
no public blob access, Entra-only SQL, no public network in prod) to every
resource without exception. These are non-negotiable invariants.

**Test**: Is every resource checked against AVM availability before coding?
Does every resource include the 6 security baseline properties?

---

### 6. Golden Path Pattern

Prefer shared utilities over hand-rolled helpers.
Use `azure-defaults` as the single source of truth for naming, regions, tags,
and service matrices. Use `alz-recall` as the single source of truth for session
state. Don't reinvent.

**Test**: Are there duplicate conventions across agents? If yes, consolidate
into the appropriate skill.

---

### 7. Human Taste Gets Encoded

Review feedback becomes documentation, linter rules, or skill updates —
not ad-hoc fixes. When a reviewer catches a pattern issue, the fix is
to update the instruction or skill that should have prevented it.

**Test**: After receiving feedback, was the lesson encoded into a rule
(instruction, skill, or validator) rather than just applied once?

---

### 8. Context Is Scarce

Every token in the agent's context window must earn its keep.
Load skills progressively: `golden-principles` → `azure-defaults` →
task-specific skills. Use `context-shredding` tiers when approaching limits.
Use pointers over inline content.

**Test**: Does each agent load ≤ 5 skills? Are skills loaded on-demand?

---

### 9. Progressive Disclosure

Start small, point to deeper docs when needed.
`AGENTS.md` gives the overview. Skills give deep knowledge.
Instructions give enforcement rules. `alz-recall` gives session state.
Each layer adds detail when the agent needs it.

**Test**: Can an agent complete a basic task by reading only `AGENTS.md`
and one skill? Does it only load more when needed?

---

### 10. Mechanical Enforcement Over Documentation

If a rule can be a linter check, CI validation, or pre-commit hook,
make it one. Documentation is for humans; machines enforce rules.
The validators in `scripts/validators/` are more reliable than a
paragraph saying "use the correct security properties."

**Test**: For each documented rule, is there a corresponding validator?

---

## Enterprise Landing Zone Specifics

These principles apply with additional ALZ context:

| Principle | ALZ Application |
|-----------|----------------|
| #1 System of Record | Estate state lives in `alz-recall` + `00-estate-state.json` |
| #3 Invariants | Security baseline (6 rules), cost governance (budget alerts), CAF naming |
| #5 AVM-First | Both Bicep and Terraform tracks use AVM modules when available |
| #6 Golden Path | All platform LZs follow: Validate → Plan → Deploy → Verify |
| #8 Context | Use `context-shredding` tiers; recommend session breaks at Gates 2 & 4 |
| #10 Mechanical | `validate_security_baseline.py`, `validate_cost_governance.py` |

## How to Apply

### For Agents

1. Read this skill FIRST, before task-specific skills
2. Use principles as a decision framework when uncertain
3. When two approaches are equally valid, choose the one that better aligns

### For Contributors

1. When adding an instruction, check if it could be a linter rule (Principle 10)
2. When adding content, check if it exceeds 200 lines (Principle 2)
3. When fixing a bug, encode the lesson into a rule (Principle 7)

### For Code Review

1. Does the change follow the golden path or create a new one? (Principle 6)
2. Does it add context load or reduce it? (Principle 8)
3. Does it enforce invariants or prescribe implementation? (Principle 3)
