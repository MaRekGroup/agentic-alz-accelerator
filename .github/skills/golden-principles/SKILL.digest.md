<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Golden Principles Skill (Digest)

The 10 operating principles governing every agent in the ALZ Accelerator.

## The 10 Principles

| # | Principle | Core Rule |
|---|-----------|-----------|
| 1 | Repository Is the System of Record | All context lives in-repo; if it isn't committed, it doesn't exist |
| 2 | Map, Not Manual | Instructions point to deeper sources; no single file tries to be comprehensive; stay under 200 lines |
| 3 | Enforce Invariants, Not Implementations | Set strict boundaries (WHAT) but allow autonomous expression (HOW) |
| 4 | Parse at Boundaries | Validate inputs and outputs at module edges, not in the middle |
| 5 | AVM-First, Security Baseline Always | Prefer Azure Verified Modules; apply 6 security baseline rules to every resource |
| 6 | Golden Path Pattern | Use shared utilities (`azure-defaults`, `alz-recall`) over hand-rolled helpers |
| 7 | Human Taste Gets Encoded | Review feedback becomes documentation, linter rules, or skill updates — not ad-hoc fixes |
| 8 | Context Is Scarce | Every token must earn its keep; load ≤ 5 skills per agent; use context-shredding |
| 9 | Progressive Disclosure | Start small, point to deeper docs when needed; AGENTS.md → Skills → Instructions |
| 10 | Mechanical Enforcement Over Documentation | If a rule can be a linter, CI check, or pre-commit hook, make it one |

## ALZ-Specific Application

| Principle | ALZ Application |
|-----------|----------------|
| #1 System of Record | Estate state in `alz-recall` + `00-estate-state.json` |
| #3 Invariants | Security baseline (6 rules), cost governance, CAF naming |
| #5 AVM-First | Both Bicep and Terraform tracks use AVM modules |
| #6 Golden Path | All platform LZs follow: Validate → Plan → Deploy → Verify |
| #8 Context | Use `context-shredding` tiers; session breaks at Gates 2 & 4 |
| #10 Mechanical | `validate_security_baseline.py`, `validate_cost_governance.py` |

## How to Apply

- **Agents**: Read this skill first; use principles as decision framework
- **Contributors**: Check if instructions could be linter rules (#10); keep files under 200 lines (#2); encode lessons into rules (#7)
- **Code Review**: Does the change follow the golden path or create a new one? (#6) Does it add or reduce context load? (#8)
