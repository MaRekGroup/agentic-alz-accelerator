#!/usr/bin/env python3
# ruff: noqa: E501
"""Deterministic Azure Policy discovery for Enterprise Landing Zone governance.

Lists effective policy assignments at management group or subscription scope
(including inherited), pulls definitions, classifies effects, filters Defender
auto-assignments, and writes a governance-constraints-v1 JSON envelope.

Stdout line 1 is always a one-line JSON status object for agent consumption.
Stderr carries warnings and filter notes.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# --------------------------------------------------------------------------- #
# Constants                                                                     #
# --------------------------------------------------------------------------- #

API_ASSIGNMENTS = "2022-06-01"
API_DEFINITIONS = "2021-06-01"
API_EXEMPTIONS = "2022-07-01-preview"
ARM = "https://management.azure.com"

BLOCKER_EFFECTS = {"Deny"}
AUTO_REMEDIATE_EFFECTS = {"DeployIfNotExists", "Modify"}
RELEVANT_EFFECTS = BLOCKER_EFFECTS | AUTO_REMEDIATE_EFFECTS | {"Audit", "AuditIfNotExists"}

DEFENDER_ASSIGNED_BY_VALUES = {
    "Security Center",
    "Microsoft Defender for Cloud",
}

# Security baseline policy display name fragments for alignment detection
SECURITY_BASELINE_MARKERS = {
    "tls_enforcement": ["TLS", "tls", "minimum TLS version"],
    "https_only": ["HTTPS", "https", "secure transfer"],
    "no_public_blob": ["public access", "blob public", "anonymous access"],
    "managed_identity": ["managed identity", "system-assigned"],
    "entra_only_sql": ["Azure Active Directory", "Entra", "AD-only", "AAD"],
    "no_public_network": ["public network access", "public endpoint"],
}

_PARALLEL_WORKERS = 8
_TOKEN_CACHE: dict[str, Any] = {"token": None, "expires_at": 0.0}


# --------------------------------------------------------------------------- #
# Azure CLI / ARM token                                                         #
# --------------------------------------------------------------------------- #


def _get_arm_token() -> str:
    """Return a cached ARM bearer token, refreshing when near expiry."""
    now = time.time()
    if _TOKEN_CACHE["token"] and _TOKEN_CACHE["expires_at"] > now + 60:
        return _TOKEN_CACHE["token"]

    result = subprocess.run(
        ["az", "account", "get-access-token", "--resource", ARM, "-o", "json"],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    _TOKEN_CACHE["token"] = data["accessToken"]
    # Parse expiry — az CLI returns expiresOn in local time string
    _TOKEN_CACHE["expires_at"] = now + 3000  # ~50 min safe window
    return _TOKEN_CACHE["token"]


def _arm_get(path: str, api_version: str) -> dict[str, Any]:
    """GET from ARM with bearer token auth."""
    token = _get_arm_token()
    sep = "&" if "?" in path else "?"
    url = f"{ARM}{path}{sep}api-version={api_version}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"WARN: ARM {e.code} for {path}: {body[:200]}", file=sys.stderr)
        return {"value": []}


# --------------------------------------------------------------------------- #
# Discovery logic                                                               #
# --------------------------------------------------------------------------- #


def _list_assignments(scope: str) -> list[dict]:
    """List all policy assignments at the given scope (includes inherited)."""
    assignments: list[dict] = []
    path = f"{scope}/providers/Microsoft.Authorization/policyAssignments"
    data = _arm_get(path, API_ASSIGNMENTS)
    assignments.extend(data.get("value", []))

    # Handle pagination
    next_link = data.get("nextLink")
    while next_link:
        # nextLink is a full URL — strip the ARM prefix
        rel_path = next_link.replace(ARM, "")
        data = _arm_get(rel_path, API_ASSIGNMENTS)
        assignments.extend(data.get("value", []))
        next_link = data.get("nextLink")

    return assignments


def _get_definition(definition_id: str) -> dict:
    """Fetch a single policy or policy set definition."""
    return _arm_get(definition_id, API_DEFINITIONS)


def _list_exemptions(scope: str) -> list[dict]:
    """List policy exemptions at the given scope."""
    path = f"{scope}/providers/Microsoft.Authorization/policyExemptions"
    data = _arm_get(path, API_EXEMPTIONS)
    return data.get("value", [])


def _classify_effect(assignment: dict, definition: dict | None) -> str:
    """Determine the effective policy effect."""
    # Check parameters for explicit effect override
    params = assignment.get("properties", {}).get("parameters", {})
    if "effect" in params:
        val = params["effect"].get("value", "")
        if val:
            return val

    # Fall back to definition default
    if definition:
        def_params = definition.get("properties", {}).get("parameters", {})
        effect_param = def_params.get("effect", {})
        default = effect_param.get("defaultValue", "")
        if default:
            return default

    # Check if policyRule has a hardcoded effect
    if definition:
        rule = definition.get("properties", {}).get("policyRule", {})
        then = rule.get("then", {})
        if "effect" in then:
            return then["effect"]

    return "Unknown"


def _is_defender_assigned(assignment: dict) -> bool:
    """Check if assignment was auto-created by Defender for Cloud."""
    metadata = assignment.get("properties", {}).get("metadata", {})
    assigned_by = metadata.get("assignedBy", "")
    return assigned_by in DEFENDER_ASSIGNED_BY_VALUES


def _detect_security_baseline_alignment(assignments: list[dict], effects_map: dict[str, str]) -> dict[str, bool]:
    """Detect which security baseline rules have policy enforcement."""
    alignment: dict[str, bool] = {}
    all_display_names = " ".join(
        a.get("properties", {}).get("displayName", "") for a in assignments
    ).lower()

    for rule, markers in SECURITY_BASELINE_MARKERS.items():
        alignment[rule] = any(m.lower() in all_display_names for m in markers)

    return alignment


def _extract_resource_types(definition: dict | None) -> list[str]:
    """Extract resource types affected by a policy from its rule."""
    if not definition:
        return []
    rule = definition.get("properties", {}).get("policyRule", {})
    if_block = rule.get("if", {})

    # Look for field == type conditions
    types: list[str] = []
    _walk_conditions(if_block, types)
    return types[:5]  # Cap at 5 for readability


def _walk_conditions(block: dict | list, types: list[str]) -> None:
    """Recursively walk policy conditions to find type references."""
    if isinstance(block, dict):
        field = block.get("field", "")
        if field == "type":
            for key in ("equals", "in", "like"):
                val = block.get(key)
                if isinstance(val, str):
                    types.append(val)
                elif isinstance(val, list):
                    types.extend(v for v in val if isinstance(v, str))
        # Recurse into logical operators
        for op in ("allOf", "anyOf", "not"):
            if op in block:
                _walk_conditions(block[op], types)
    elif isinstance(block, list):
        for item in block:
            _walk_conditions(item, types)


# --------------------------------------------------------------------------- #
# Main orchestration                                                            #
# --------------------------------------------------------------------------- #


def discover(
    scope: str,
    customer: str,
    out_path: str,
    include_defender: bool = False,
    effects_filter: set[str] | None = None,
) -> dict[str, Any]:
    """Run full governance discovery and write JSON envelope."""
    if effects_filter is None:
        effects_filter = RELEVANT_EFFECTS

    # 1. List assignments
    assignments = _list_assignments(scope)
    print(f"INFO: Found {len(assignments)} policy assignments at scope", file=sys.stderr)

    # 2. Filter Defender auto-assignments
    defender_count = 0
    filtered_assignments = []
    for a in assignments:
        if not include_defender and _is_defender_assigned(a):
            defender_count += 1
            continue
        filtered_assignments.append(a)

    if defender_count:
        print(f"INFO: Filtered {defender_count} Defender auto-assignments", file=sys.stderr)

    # 3. Fetch definitions in parallel
    definition_ids = set()
    for a in filtered_assignments:
        def_id = a.get("properties", {}).get("policyDefinitionId", "")
        if def_id:
            definition_ids.add(def_id)

    definitions: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=_PARALLEL_WORKERS) as pool:
        futures = {pool.submit(_get_definition, did): did for did in definition_ids}
        for fut in futures:
            did = futures[fut]
            try:
                definitions[did] = fut.result()
            except Exception as e:
                print(f"WARN: Failed to fetch definition {did}: {e}", file=sys.stderr)

    # 4. Classify effects
    blockers: list[dict] = []
    auto_remediation: list[dict] = []
    audit_only: list[dict] = []

    for a in filtered_assignments:
        props = a.get("properties", {})
        def_id = props.get("policyDefinitionId", "")
        definition = definitions.get(def_id)
        effect = _classify_effect(a, definition)

        entry = {
            "assignment_id": a.get("id", ""),
            "display_name": props.get("displayName", ""),
            "effect": effect,
            "scope": props.get("scope", a.get("id", "").rsplit("/providers/Microsoft.Authorization", 1)[0]),
            "resource_types": _extract_resource_types(definition),
            "description": props.get("description", "")[:200],
        }

        if effect in BLOCKER_EFFECTS:
            entry["iac_impact"] = f"Cannot deploy resources matching this policy in scope {entry['scope']}"
            blockers.append(entry)
        elif effect in AUTO_REMEDIATE_EFFECTS:
            auto_remediation.append(entry)
        elif effect in {"Audit", "AuditIfNotExists"}:
            audit_only.append(entry)

    # 5. Fetch exemptions
    exemptions_raw = _list_exemptions(scope)
    exemptions = [
        {
            "exemption_id": e.get("id", ""),
            "display_name": e.get("properties", {}).get("displayName", ""),
            "category": e.get("properties", {}).get("exemptionCategory", ""),
            "policy_assignment_id": e.get("properties", {}).get("policyAssignmentId", ""),
        }
        for e in exemptions_raw
    ]

    # 6. Security baseline alignment
    effects_map = {
        a.get("id", ""): _classify_effect(a, definitions.get(a.get("properties", {}).get("policyDefinitionId", "")))
        for a in filtered_assignments
    }
    baseline_alignment = _detect_security_baseline_alignment(filtered_assignments, effects_map)

    # 7. Build envelope
    envelope = {
        "$schema": "governance-constraints/v1",
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": scope,
        "customer": customer,
        "summary": {
            "total_assignments": len(filtered_assignments),
            "deny_count": len(blockers),
            "deploy_if_not_exists_count": sum(1 for a in auto_remediation if a["effect"] == "DeployIfNotExists"),
            "modify_count": sum(1 for a in auto_remediation if a["effect"] == "Modify"),
            "audit_count": len(audit_only),
            "exempt_count": len(exemptions),
            "defender_filtered": defender_count,
        },
        "blockers": blockers,
        "auto_remediation": auto_remediation,
        "audit_only": audit_only,
        "exemptions": exemptions,
        "security_baseline_alignment": baseline_alignment,
    }

    # 8. Write output
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(envelope, indent=2) + "\n")

    # 9. Status line for agent consumption (stdout line 1)
    status = {
        "status": "ok",
        "blockers": len(blockers),
        "total": len(filtered_assignments),
        "defender_filtered": defender_count,
        "output": str(out),
    }
    return status


def main() -> None:
    parser = argparse.ArgumentParser(description="Azure Policy discovery for ALZ governance")
    parser.add_argument("--scope", required=True, help="ARM scope (subscription or management group)")
    parser.add_argument("--customer", required=True, help="Customer name")
    parser.add_argument("--out", required=True, help="Output JSON file path")
    parser.add_argument("--include-defender", action="store_true", help="Include Defender auto-assignments")
    parser.add_argument("--effects", default=None, help="Comma-separated effects to include")
    args = parser.parse_args()

    effects_filter = None
    if args.effects:
        effects_filter = set(args.effects.split(","))

    try:
        status = discover(
            scope=args.scope,
            customer=args.customer,
            out_path=args.out,
            include_defender=args.include_defender,
            effects_filter=effects_filter,
        )
        print(json.dumps(status))
    except subprocess.CalledProcessError as e:
        error_status = {"status": "error", "message": f"Azure CLI failed: {e.stderr or str(e)}"}
        print(json.dumps(error_status))
        sys.exit(1)
    except Exception as e:
        error_status = {"status": "error", "message": str(e)}
        print(json.dumps(error_status))
        sys.exit(1)


if __name__ == "__main__":
    main()
