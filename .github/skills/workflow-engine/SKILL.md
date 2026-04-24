---
name: workflow-engine
description: "DAG-based workflow engine for multi-step ALZ accelerator lifecycle. USE FOR: step sequencing, gate enforcement, workflow state transitions, next-step resolution. DO NOT USE FOR: session recovery (use session-resume)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "2.0"
  category: tooling-workflow
---

# Workflow Engine Skill

Manages the DAG-based workflow that drives the ALZ accelerator lifecycle.

## Workflow Graph

The workflow is defined as a directed acyclic graph in
`templates/workflow-graph.json` with **nodes** (steps and gates) and **edges**
(transitions with conditions).

### Node Types

| Type | Purpose |
|------|---------|
| `agent-step` | Work performed by a specific agent (produces an artifact) |
| `gate` | Approval checkpoint — requires explicit user confirmation |
| `subagent-fan-out` | Parallel execution of multiple subagents |
| `validation` | Automated validation step (no user interaction) |

### Edge Conditions

| Condition | Meaning |
|-----------|---------|
| `on_complete` | Source step finished successfully |
| `on_approve` | Gate approved by user |
| `on_fail` | Source step failed |
| `on_skip` | Source step was skipped |
| `on_violation` | Monitoring detected a policy violation |

## Step Sequence

```
Step 0 (brownfield only) → Step 1 → Gate 1 → Step 2 → Gate 2 →
Step 3 / Step 3.5 → Gate 3 → Step 4 → Gate 4 → Step 5 → Gate 5 →
Step 6 → Gate 6 → Step 7 → Step 8 ⇄ Step 9 (continuous)
```

## Usage

The Conductor (orchestrator) uses this skill to:
1. Load the workflow graph from `templates/workflow-graph.json`
2. Determine the next executable step based on current state
3. Enforce gate approvals before advancing
4. Track step status transitions (pending → in_progress → completed/failed)

## Implementation

The Python implementation is in `src/agents/workflow_engine.py`:
- `WorkflowEngine.load_graph()` — parses the DAG
- `WorkflowEngine.get_next_steps()` — resolves ready steps from edges and state
- `WorkflowEngine.advance()` — transitions a step and returns the next steps
