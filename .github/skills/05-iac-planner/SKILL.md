---
name: 05-iac-planner
description: "Create IaC implementation plan with AVM module selection"
disable-model-invocation: true
---

Read and follow the role, tool restrictions, required skills, and safety rules in [the iac-planner agent definition](../../agents/iac-planner.md) before executing this workflow.

This replaces the original prompt's `agent: iac-planner` routing with explicit context loading; it does not switch agents or grant additional tools.

# Step 4: IaC Planning

Act as the Strategist (📐). Create an implementation plan selecting Azure Verified
Modules (AVM) and mapping requirements to IaC resources.

## Process

1. Read requirements, architecture, and governance constraints
2. Select AVM modules for each resource (Bicep or Terraform based on `IAC_FRAMEWORK`)
3. Map each CAF design area to specific IaC modules
4. Define parameter files / tfvars per environment
5. Plan deployment order (dependencies)

## AVM-First Rule

Always prefer Azure Verified Modules when available:
- Bicep: `br/public:avm/res/{provider}/{type}:{version}`
- Terraform: `Azure/avm-res-{provider}-{type}/azurerm`

Only fall back to native resources when no AVM module exists.

## Output

Produce `04-implementation-plan.md` with:
- Module inventory (AVM vs native)
- Resource → module mapping per CAF design area
- Parameter strategy per environment
- Deployment order with dependency graph
- Estimated effort

## Skill to reference

Read `.github/skills/profile-management/SKILL.md` for profile inheritance.
