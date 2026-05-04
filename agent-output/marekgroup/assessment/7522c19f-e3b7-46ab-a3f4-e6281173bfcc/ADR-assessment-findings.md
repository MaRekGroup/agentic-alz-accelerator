# ADR — Assessment Findings for 7522c19f-e3b7-46ab-a3f4-e6281173bfcc

**Date**: 2026-05-04
**Status**: Proposed
**Deciders**: Platform team

## Context

A WARA/CAF assessment was performed on `7522c19f-e3b7-46ab-a3f4-e6281173bfcc` scoring **92.6/100** overall.
The assessment identified **5** findings across 221 checks.

## Critical/High Findings Requiring Decision

### 🟠 High — No policy assignments found (`OPE-002`)

**Problem**: Assign Azure Policy initiatives (e.g., ASB, CIS) for governance enforcement.

**Proposed remediation**:
1. Assign Azure Security Benchmark initiative at MG or subscription scope

### 🟠 High — Management group hierarchy not CAF-aligned (`OPE-004`)

**Problem**: Adopt CAF enterprise-scale MG hierarchy: platform, landing zones, sandbox, decommissioned.

**Proposed remediation**:
1. Run bootstrap workflow to create CAF-aligned MG hierarchy
2. Move subscriptions to appropriate MGs

### 🟠 High — No hub VNet or firewall detected (`OPE-006`)

**Problem**: Deploy a hub VNet with Azure Firewall for centralized network governance.

**Proposed remediation**:
1. Deploy connectivity landing zone with hub-spoke topology

## Decision

<!-- TO BE FILLED: Accept / Modify / Defer each finding -->

## Consequences

- Accepted findings will be remediated according to the roadmap in target-state-architecture.md
- Deferred findings will be tracked in the next assessment cycle
