---
name: context-optimizer
description: "Audits agent context window usage via debug logs, token profiling, and redundancy detection. USE FOR: context optimization, token waste analysis, debug log parsing, hand-off gap analysis. DO NOT USE FOR: Azure infrastructure, Bicep/Terraform code, architecture design, deployments."
compatibility: Requires Python 3.10+ for log parser. Works with VS Code Copilot debug logs.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "1.0"
  category: optimization
---

# Context Window Optimization Skill

Structured methodology for auditing how agents in the Enterprise Landing Zone
accelerator consume their context window. Identifies waste, recommends hand-off
points, and produces prioritized optimization reports.

## When to Use This Skill

- Auditing context window efficiency across the agent roster
- Identifying where to introduce subagent hand-offs
- Reducing redundant file reads and skill loads
- Optimizing instruction file `applyTo` glob patterns
- Profiling per-turn token cost from debug logs
- After adding new skills or agents (verify context budget)

## Quick Reference

| Capability | Description |
|------------|-------------|
| Log Parsing | Extract structured data from Copilot Chat debug logs |
| Turn-Cost Profiling | Estimate token spend per turn from timing and model metadata |
| Redundancy Detection | Find duplicate file reads, overlapping instructions |
| Hand-Off Gap Analysis | Identify agents that should delegate to subagents |
| Instruction Audit | Flag overly broad globs and oversized instruction files |
| Report Generation | Structured markdown report with prioritized recommendations |

## Prerequisites

- Python 3.10+
- Access to VS Code Copilot Chat debug logs
- Agent definitions in `.github/agents/*.md`

### Locating Debug Logs

```bash
# Find latest Copilot Chat logs
find ~/.vscode-server*/data/logs/ -name "GitHub Copilot Chat.log" -newer /tmp/marker 2>/dev/null \
  | sort | tail -5

# Or use the session log path from the environment variable
echo $VSCODE_TARGET_SESSION_LOG
```

## Analysis Methodology

### Step 1: Parse Debug Logs

Extract structured data from Copilot Chat debug logs:

```bash
# Parse log entries into structured JSON
python3 tools/scripts/parse-chat-logs.py \
  --log-dir ~/.vscode-server*/data/logs/ \
  --output context-audit.json
```

Key metrics to extract:
- Files read per turn (count and sizes)
- Skills loaded per agent session
- Instructions auto-loaded via `applyTo` globs
- Total context tokens per turn

### Step 2: Turn-Cost Profiling

Estimate token cost per turn:

```text
Token estimation heuristic:
  1 token ≈ 4 characters (English text)
  1 token ≈ 3 characters (code/JSON)
  Model limits: Claude Opus = 200K, GPT-4.1 = 128K
```

Flag turns that exceed 60% of model context (threshold for `context-shredding`).

### Step 3: Agent Definition Audit

For each agent in `.github/agents/*.md`:

| Check | Pass Criteria |
|-------|---------------|
| Skills count | ≤ 5 skills per agent |
| Instruction files | ≤ 5 auto-loaded instructions |
| File reads | No duplicate reads of same file |
| Skill overlap | No two agents load identical skill sets |
| Definition size | Agent .md file < 400 lines |

### Step 4: Context Growth Mapping

Track how context grows across workflow steps:

```text
Step 1 (Requirements):  ~15K tokens (requirements agent + azure-defaults)
Step 2 (Architecture):  ~25K tokens (+ 01-requirements.md + caf-design-areas)
Step 3 (Design):        ~20K tokens (+ drawio/mermaid skill)
Step 3.5 (Governance):  ~30K tokens (+ governance discovery output)
Step 4 (Plan):          ~35K tokens (+ 02-architecture + 04-governance)
Step 5 (Code Gen):      ~50K tokens (+ implementation plan + AVM patterns)
Step 6 (Deploy):        ~20K tokens (fresh context, only deploy artifacts)
Step 7 (Documentation): ~30K tokens (+ multiple predecessor artifacts)
```

**Session break recommendations**: Gates 2 and 4 (orchestrator protocol).

### Step 5: Generate Optimization Report

Produce a report with:

1. **Per-agent token budget** — estimated context per agent session
2. **Redundancy findings** — duplicate reads, overlapping instructions
3. **Hand-off recommendations** — agents that should use subagents
4. **Instruction narrowing** — overly broad `applyTo` globs
5. **Skill compression** — skills that need `SKILL.digest.md` variants

## Common Optimization Patterns

### 1. Subagent Extraction

If an agent's single-turn context exceeds 40K tokens, consider extracting
a subagent for the heavy-computation phase.

**ALZ example**: The Forge agent (Step 5) loads AVM patterns, security baseline,
governance constraints, AND generates code. Extract validation into
`bicep-validate-subagent` (already done) and `bicep-whatif-subagent`.

### 2. Instruction Narrowing

```yaml
# Too broad — loads for ALL .md files
applyTo: "**/*.md"

# Better — only loads for agent output markdown
applyTo: "agent-output/**/*.md"
```

### 3. Progressive Skill Loading

```text
Turn 1: Load golden-principles + azure-defaults (always needed)
Turn 2: Load task-specific skill (e.g., azure-bicep-patterns)
Turn 3: Load context-shredding if approaching limits
```

### 4. Skill Digest Variants

Create `SKILL.digest.md` (150-320 tokens) for skills loaded at >60% context:

```text
.github/skills/azure-defaults/
├── SKILL.md           # Full version (400-800 tokens)
├── SKILL.digest.md    # Key facts only (150-320 tokens)
└── SKILL.minimal.md   # Decision summaries (40-100 tokens)
```

### 5. Artifact Compression

Use `context-shredding` tiers when loading predecessor artifacts:

| Artifact | Full | Summarized | Minimal |
|----------|------|------------|---------|
| 01-requirements.md | ~3K tokens | ~800 tokens | ~200 tokens |
| 02-architecture.md | ~5K tokens | ~1.5K tokens | ~300 tokens |
| 04-governance.json | ~4K tokens | ~1K tokens | ~200 tokens |

## Report Template

```markdown
# Context Optimization Report — {date}

## Summary
- Agents audited: {N}
- Total redundant reads: {N}
- Agents exceeding 60% context: {list}
- Recommended session breaks: {gates}

## Per-Agent Analysis

### {Agent Name} ({codename})
- Estimated context: {N}K tokens ({pct}% of model limit)
- Skills loaded: {list}
- Instructions auto-loaded: {list}
- Redundant reads: {list}
- **Recommendation**: {action}

## Prioritized Recommendations

1. {High priority action}
2. {Medium priority action}
3. {Low priority action}
```

## Integration with ALZ Workflow

| Agent | Invokes This Skill |
|-------|-------------------|
| Orchestrator (Conductor) | Periodic audits after adding agents/skills |
| Challenger | Can request context audit at any gate |

## Guardrails

**DO:** Audit after adding new agents or skills · Create digest variants for
frequently-loaded skills · Use context-shredding tiers · Recommend session breaks
at Gates 2 and 4.

**DON'T:** Load this skill during normal workflow execution · Over-optimize
(diminishing returns below 40% context usage) · Remove skills without checking
agent dependencies in `agent-registry.json`.
