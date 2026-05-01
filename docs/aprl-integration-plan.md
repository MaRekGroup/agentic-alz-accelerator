# APRL Integration Plan — WARA Assessment Enhancement

> Status: Planning | Date: 2026-04-30

## Context

Our current `wara_checks.yaml` has **20 checks** (9 SEC, 6 OPE, 2 REL, 2 COS, 1 PER).
Microsoft's Azure Proactive Resiliency Library (APRL) publishes **393 recommendations**
(372 with ARG queries) across 83 resource types via a public JSON feed.

- Feed URL: `https://azure.github.io/WARA-Build/objects/recommendations.json`
- Source repo: `Azure/Well-Architected-Reliability-Assessment`
- Module: PowerShell `WARA` (PSGallery), v1.0.6

## APRL Feed Analysis

| Metric | Value |
|--------|-------|
| Total recommendations | 393 |
| With ARG queries | 372 |
| Unique resource types | 83 |
| Impact: High | 210 |
| Impact: Medium | 143 |
| Impact: Low | 40 |

### Control Distribution (APRL is reliability-focused)

| Control | Count |
|---------|-------|
| HighAvailability | 153 |
| DisasterRecovery | 71 |
| MonitoringAndAlerting | 62 |
| Scalability | 45 |
| OtherBestPractices | 43 |
| BusinessContinuity | 9 |
| ServiceUpgradeAndRetirement | 7 |
| Personalized | 2 |
| Security | 1 |

### APRL Recommendation Schema

```json
{
  "aprlGuid": "e6c7e1cc-2f47-264d-aa50-1da421314472",
  "recommendationTypeId": null,
  "recommendationMetadataState": "Active",
  "learnMoreLink": [{"name": "...", "url": "..."}],
  "recommendationControl": "HighAvailability",
  "longDescription": "...",
  "pgVerified": true,
  "description": "Ensure that storage accounts are zone or region redundant",
  "potentialBenefits": "...",
  "tags": [...],
  "recommendationResourceType": "Microsoft.Storage/storageAccounts",
  "recommendationImpact": "High",
  "automationAvailable": true,
  "query": "// ARG KQL query..."
}
```

## Decision: Architecture

**One assessment engine + per-pillar check catalogs** (not per-pillar subagents).

Rationale:
- All checks run the same KQL queries against the same Resource Graph
- Splitting into 5 subagents = 5× auth, 5× ARG clients, 5× partial merges
- APRL is reliability-heavy — no balanced pillar split available
- Per-pillar remediation subagents deferred to later phase

## Implementation Plan

### Task 1: APRL Sync Tool

Script to fetch `recommendations.json`, transform to our YAML schema, cache locally.

- Location: `scripts/sync_aprl.py`
- Schedule: Weekly in CI (or manual)
- Output: `src/config/wara_checks/_aprl_synced.yaml`
- Mapping:
  - `recommendationControl` → `pillar` (HighAvailability/DR/BC → reliability, etc.)
  - `recommendationImpact` → `severity` (High → high, Medium → medium, Low → low)
  - `query` → `query` (ARG KQL, already compatible)
  - `recommendationResourceType` → used for scoping
  - `aprlGuid` → `id` prefix `APRL-`
  - `description` → `title`
  - `longDescription` → `recommendation`
  - `learnMoreLink` → `references`

### Task 2: Split Check Catalog

Break `src/config/wara_checks.yaml` into per-pillar files:

```
src/config/wara_checks/
├── reliability.yaml              ← APRL-synced + custom REL-*
├── security.yaml                 ← Existing SEC-001..009 + security baseline
├── cost_optimization.yaml        ← COS-* checks
├── operational_excellence.yaml   ← OPE-* checks
├── performance.yaml              ← PER-* checks
└── _aprl_synced.yaml             ← Raw synced APRL (generated, do not edit)
```

### Task 3: Update Engine Loader

Modify `WaraEngine._load_checks()` to glob `src/config/wara_checks/*.yaml`
instead of loading a single file. Deduplicate by ID.

### Task 4: APRL → Our Schema Mapping

| APRL `recommendationControl` | Our `pillar` |
|------------------------------|--------------|
| HighAvailability | reliability |
| DisasterRecovery | reliability |
| BusinessContinuity | reliability |
| Scalability | performance |
| MonitoringAndAlerting | operational_excellence |
| OtherBestPractices | operational_excellence |
| ServiceUpgradeAndRetirement | operational_excellence |
| Security | security |
| Personalized | (skip or map by resource type) |

### Task 5: Update Assessment Agent

Point assessment agent at enriched catalog (20 → 390+ checks).
Update test expectations.

## Deferred (Future Phase)

- Per-pillar remediation subagents (invoked by Mender agent)
- Custom check authoring UI/workflow
- APRL feed diffing (detect new/removed recommendations)

## References

- APRL v2: https://azure.github.io/Azure-Proactive-Resiliency-Library-v2/
- WARA repo: https://github.com/Azure/Well-Architected-Reliability-Assessment
- Our engine: `src/tools/wara_engine.py`
- Our checks: `src/config/wara_checks.yaml`
- Our assessment CLI: `src/tools/assess_cli.py`
