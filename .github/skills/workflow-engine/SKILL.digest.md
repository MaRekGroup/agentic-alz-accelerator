<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Workflow Engine Skill (Digest)

Manages the DAG-based workflow that drives the ALZ accelerator lifecycle.

## Node Types

| Type | Purpose |
|------|---------|
| `agent-step` | Work performed by a specific agent (produces an artifact) |
| `gate` | Approval checkpoint — requires explicit user confirmation |
| `subagent-fan-out` | Parallel execution of multiple subagents |
| `validation` | Automated validation step (no user interaction) |

## Edge Conditions

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

## Implementation

`src/agents/workflow_engine.py`:
- `WorkflowEngine.load_graph()` — parses the DAG from `templates/workflow-graph.json`
- `WorkflowEngine.get_next_steps()` — resolves ready steps from edges and state
- `WorkflowEngine.advance()` — transitions a step and returns the next steps

> _See SKILL.md for full usage details._
