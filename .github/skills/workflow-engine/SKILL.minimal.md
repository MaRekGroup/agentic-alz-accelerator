<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Workflow Engine Skill (Minimal)

**Workflow Graph** — DAG defined in `templates/workflow-graph.json` with agent-step, gate, fan-out, and validation node types.

**Edge Conditions** — Transitions via on_complete, on_approve, on_fail, on_skip, and on_violation.

**Step Sequence** — Steps 0–9 with 6 gates; Steps 8–9 form a continuous monitoring loop.

**Implementation** — `WorkflowEngine` in `src/agents/workflow_engine.py` with load_graph, get_next_steps, and advance methods.

Read `SKILL.md` or `SKILL.digest.md` for full content.
