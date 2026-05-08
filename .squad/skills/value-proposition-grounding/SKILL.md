---
name: value-proposition-grounding
description: "Pattern for grounding product value propositions in actual code evidence rather than marketing claims. Maps architectural capabilities to buyer personas and proof points."
version: "1.0"
author: Linus
date: 2026-05-08T22:31:56.807+00:00
---

# Value Proposition Grounding Pattern

Reusable workflow for deriving credible, differentiated value propositions from codebase architecture.

## Core Principle

**Evidence First, Claims Second** — Every proposition must be traceable to actual code, not aspirational messaging.

## Grounding Workflow

1. **Fan Out Across Architecture** — Read agent definitions, skill implementations, validators, IaC modules, CI/CD pipelines
2. **Identify Enforcement Points** — Where/when are non-functional requirements actually enforced? (code-gen, deploy, monitor, remediate)
3. **Map to User Pain Points** — Which teams experience which operational challenges? (security drift, compliance violations, knowledge loss, slow delivery)
4. **Match Capabilities to Personas** — Pair each pain point with a specific agent/skill/validator that addresses it
5. **Craft Propositions** — One primary (broadest audience), two secondary (differentiators)
6. **Attach Proof Points** — Every claim must cite code file paths

## Proposition Types

### Type 1: Problem-Solver (Operational Pain Point)
- **Structure:** "Solve [Problem] Automatically [Where] [How]"
- **Example:** "Enforce ALZ Best Practices Automatically — at code generation, deployment, and continuous monitoring"
- **Evidence:** Three-layer enforcement with validators, approval gates, monitoring agent
- **Personas:** Operations, Security, Compliance teams
- **Strength:** Defensible; addresses post-deploy pain; broadest audience

### Type 2: Knowledge Multiplier (Institutional Knowledge Capture)
- **Structure:** "Accelerate [Knowledge Area] via [Generation Method]"
- **Example:** "Accelerate Knowledge Transfer via Orchestrated Documentation"
- **Evidence:** Generated current/target-state docs, CAF mapping, ADR generation, architectural diagrams
- **Personas:** Architects, Learning/Knowledge teams, Auditors
- **Strength:** Differentiator from IaC-only tools; high-touch use case

### Type 3: Speed / Efficiency (Timeline / Throughput)
- **Structure:** "Deliver [Outcome] in [Timeline] with [Quality Gate]"
- **Example:** "Deploy ALZ in 2–4 Weeks with Approval Gates Intact"
- **Evidence:** Parallelized workflow, AVM-first generation, complexity-scaled gate rules
- **Personas:** Delivery/PMO, MSPs, strategic programs
- **Strength:** Competitive advantage; but only claim credibly for Simple/Standard tiers

## Evidence Mapping Template

For each proposition, create a table:

| Capability | Evidence File(s) | Proof |
|------------|------------------|-------|
| [Feature] | `.github/agents/X.md`, `.github/skills/Y/SKILL.md`, `scripts/Z.py` | [Specific code pattern or behavior] |

## Grounding Checklist

- [ ] Every claim is traceable to ≥1 code file
- [ ] File paths are correct and current
- [ ] Propositions are distinct (no overlap)
- [ ] Propositions map to different personas
- [ ] Primary proposition addresses broadest audience / most defensible pain point
- [ ] Secondary propositions position as differentiators
- [ ] No aspirational claims ("could", "should", "might")
- [ ] No generic marketing ("AI-powered", "modern", "cutting-edge") without code backing

## Example: Enforcement Capability Grounding

**Claim:** "Enforce ALZ Best Practices Automatically at Code Generation"

**Proof Points:**
1. `.github/skills/security-baseline/SKILL.md` — Lists 6 non-negotiable rules + 8 extended checks
2. `scripts/validators/validate_security_baseline.py` — Shows rule 1 (TLS 1.2) as blocker (blocking merge)
3. `.github/instructions/iac-bicep-best-practices.instructions.md` — Code must pass validation
4. `.github/agents/bicep-code.md` (Forge agent) — "All generated code passes security baseline before output"

**Persona Fit:** Security/Compliance teams ("We need enforcement, not guidance")

## Application to ALZ Accelerator

### Prop 1 Evidence Summary
- **Enforcement Layers:** 3 (`security-baseline/SKILL.md` + `monitoring.md` + `remediation.md`)
- **Rules Enforced:** 6 core + 8 extended (from `validate_security_baseline.py`)
- **Cost Governance:** Mandatory budget + parameterized alerts (`cost-governance/SKILL.md`)
- **Gates:** 6 non-negotiable (`AGENTS.md` Approval Gates section)

### Prop 2 Evidence Summary
- **Brownfield Assessment:** Step 0 with WARA evaluation (`assessment.md`)
- **CAF Alignment:** 8 design areas mapped to IaC modules (`caf-design-areas/SKILL.md`)
- **Generated Docs:** Steps 3, 7 produce diagrams, ADRs, TDDs (`design.md`, `documentation.md`)
- **Knowledge Capture:** ADRs with WAF rationale (`azure-adr/SKILL.md`)

### Prop 3 Evidence Summary
- **Parallelization:** Design + Governance run concurrently (`orchestrator.md` workflow)
- **AVM-First:** All code generation uses Azure Verified Modules (`bicep-patterns/`, `terraform-patterns/`)
- **Gate Scaling:** 1/2/3 passes by complexity tier (`AGENTS.md` Complexity Classification)
- **Timeline:** Linear flow with no rework loops (Step 1→2→3→4→5→6→7)

## Anti-Patterns to Avoid

- ❌ "We use AI" (too generic; no code evidence)
- ❌ "Faster than competitors" (relative claim; no proof)
- ❌ "Best-in-class" (subjective; no code)
- ❌ "Fully automated" (misleading; humans approve at gates)
- ✅ "Enforce 6 non-negotiable security rules at code generation" (specific, traceable, verifiable)
- ✅ "Continuous compliance scans every 30 minutes with auto-remediation for critical violations" (specific, measurable, code-backed)

## Review Checklist for Product Teams

When receiving value propositions from architecture:

1. **Verify Each Claim**
   - Open cited code files
   - Confirm capability exists as described
   - Check file paths are current

2. **Assess Persona Fit**
   - Can you name 3 customer types for this proposition?
   - Do they have this pain point?
   - Is this the right solution for them?

3. **Evaluate Competitive Position**
   - Is this unique to ALZ Accelerator?
   - Or is it standard IaC/cloud practice?
   - If standard, what's the differentiator?

4. **Test Credibility**
   - Could a prospect reproduce this by reading the code?
   - Would a security audit validate this claim?
   - Is there demo-able evidence?
