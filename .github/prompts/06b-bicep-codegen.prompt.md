---
mode: orchestrator
description: "Generate Bicep templates using AVM modules"
---

# Step 5b: Bicep Code Generation

Act as the Forge (⚒️). Generate Bicep templates based on the implementation plan,
using AVM modules where available.

## Process

1. Read `04-implementation-plan.md` and `04-governance-constraints.md`
2. Generate Bicep modules under `infra/bicep/{project}/`
3. Create parameter files per environment under `infra/bicep/parameters/`
4. Enforce security baseline in every module
5. Include budget resource with parameterized alerts

## Mandatory Checks

Every Bicep file must pass:
- Security baseline (6 rules): TLS 1.2, HTTPS-only, no public blob, managed identity, AD-only SQL, no public network (prod)
- Budget resource with 80%/100%/120% forecast thresholds
- Diagnostic settings forwarding to Log Analytics
- CAF naming conventions and required tags
- AVM module references where available

## Validation

```bash
az bicep build --file infra/bicep/{project}/main.bicep
python scripts/validators/validate_security_baseline.py infra/bicep/{project}/
python scripts/validators/validate_cost_governance.py infra/bicep/{project}/
```

## Output

Bicep files in `infra/bicep/{project}/` with parameter files in `parameters/`.
