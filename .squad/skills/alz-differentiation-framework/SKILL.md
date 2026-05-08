---
name: alz-differentiation-framework
description: "Framework for evaluating Azure Landing Zone accelerators: distinguish true differentiators (new capabilities) from repackaging (existing ALZ patterns applied differently)."
compatibility: Works with architects, positioning teams, product managers evaluating ALZ solutions
license: MIT
metadata:
  author: linus
  version: "1.0"
  category: architecture-assessment
---

# ALZ Differentiation Framework

A decision framework for evaluating whether a claimed ALZ innovation is a true differentiator or repackaging.

## The Three-Question Test

For each proposed capability, ask:

### 1. **Does Official ALZ Provide This?**

| Answer | Next | Examples |
|--------|------|----------|
| No (entirely new) | → See Q2 | Brownfield assessment, continuous monitoring, auto-remediation |
| Yes (same capability) | → See Q2 | IaC templates, management groups, policy frameworks |

### 2. **Is the *Approach* Novel?**

| Approach | Verdict | Example |
|----------|---------|---------|
| New algorithm/automation not in ALZ | Differentiator ✓ | Algorithmic brownfield assessment (discovery → WARA eval → roadmap generation) |
| Guided selection of ALZ patterns | Repackaging ✗ | Asking "hub-spoke or vWAN?" then implementing same ALZ topologies |
| Continuous enforcement (code→deploy→monitor) | Differentiator ✓ | Official ALZ: you own Day-2. We: enforce continuously + auto-fix |
| Discovering existing ALZ policies | Repackaging ✗ | ALZ defines policies; we read them, not redefine |

### 3. **Who Benefits & Why?**

| Benefit | Addressable TAM | Verdict |
|--------|-----------------|---------|
| "Faster deployment via parallelization" | Delivery teams under timeline pressure | Differentiator if truly parallel (not just sequential agents) |
| "We follow ALZ best practices" | Everyone who cares about ALZ | Repackaging (ALZ already prescribes this) |
| "We enforce security at code-gen time" | Compliance/security teams with post-deploy drift pain | Differentiator if enforcement is continuous + auto-remediation |
| "We assess existing environments" | Brownfield/migration orgs | Differentiator if assessment is scored (WAF pillars) + roadmap generated |

## Apply to Your Solution

### True Differentiator Template

```
**Claim:** [Feature]
**Question 1 Answer:** Official ALZ does NOT [capability] — or does but only at [narrow scope]
**Question 2 Answer:** Our [approach] is novel because [algorithm/automation/continuous process]
**Question 3 Answer:** This solves [specific pain point] for [persona] (addressable TAM: [estimate])
**Evidence Files:** [Specific code/agent/skill proof points]
**Positioning Language:** "[Feature] solves [pain] by [approach]. Official ALZ [comparison]."
```

### Repackaging Red Flags

- "We implement [official ALZ pattern]" — You're not inventing; you're following
- "We discover and apply [ALZ standard]" — Automation of existing guidance, not new guidance
- "We use the same [ALZ component]" — Not different, just wrapped in orchestration

## Agentic ALZ Accelerator Applied

**True Differentiators:**
- Three-tier enforcement + continuous monitoring (ALZ has code-level best practices; we enforce post-deploy + auto-fix)
- Brownfield assessment (ALZ is greenfield; we evaluate existing estates with scored roadmaps)
- Agentic orchestration (ALZ is reference architecture; we automate the workflow end-to-end)

**Repackaging (OK to Mention, Not to Lead With):**
- IaC templates (we use AVM modules, same as ALZ)
- Policy discovery (we read ALZ policies, don't redefine)
- Management group hierarchy (we guide users to ALZ structure)

---

## Decision Record: When to Claim a Differentiator

✅ **Claim if:**
- Solves a pain point official ALZ doesn't address
- Introduces new automation or continuous enforcement ALZ lacks
- Extends ALZ to scenarios (brownfield) or personas (ops teams) official ALZ doesn't cover

❌ **Don't claim if:**
- Just implementing ALZ recommendations
- Just automating ALZ selection without new logic
- Repackaging ALZ patterns under new names
- No evidence of novel algorithm or enforcement mechanism

---

## See Also

- `.squad/decisions/inbox/linus-alz-comparison-2026-05-08.md` — Full ALZ comparison with evidence
- `AGENTS.md` → `Day-2 Operations` — Continuous monitoring/remediation uniqueness
- `.github/agents/assessment.md` → Brownfield discovery pattern
- `.github/skills/caf-design-areas/SKILL.md` → CAF alignment (repackaging, not differentiator)
