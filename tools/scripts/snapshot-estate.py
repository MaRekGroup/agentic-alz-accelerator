#!/usr/bin/env python3
"""Quick estate status snapshot for debugging and session context.

Reads agent-output/{customer}/00-estate-state.json and prints a summary
of all landing zones, their deployment status, and key metadata.

Usage:
    python tools/scripts/snapshot-estate.py [customer]
    python tools/scripts/snapshot-estate.py marekgroup --json
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
AGENT_OUTPUT = REPO_ROOT / "agent-output"


def _find_customers() -> list[str]:
    """List customer directories that have estate-state files."""
    customers = []
    if AGENT_OUTPUT.is_dir():
        for d in sorted(AGENT_OUTPUT.iterdir()):
            if d.is_dir() and (d / "00-estate-state.json").exists():
                customers.append(d.name)
    return customers


def _load_estate(customer: str) -> dict | None:
    path = AGENT_OUTPUT / customer / "00-estate-state.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def _print_text(estate: dict, customer: str) -> None:
    e = estate.get("estate", {})
    print(f"Customer:  {customer}")
    print(f"Prefix:    {e.get('prefix', '?')}")
    print(f"Region:    {e.get('primary_region', '?')}")
    print(f"IaC:       {e.get('iac_tool', '?')}")
    print(f"Updated:   {e.get('updated', '?')}")
    print()

    # Platform LZs
    plz = estate.get("platform_landing_zones", {})
    if plz:
        print("Platform Landing Zones:")
        for name, info in plz.items():
            status = info.get("status", "unknown")
            marker = "✓" if status == "deployed" else "✗" if status == "failed" else "○"
            run_id = info.get("last_deploy_run", "")
            print(f"  {marker} {name:<20} {status:<12} run={run_id}")
        print()

    # App LZs
    alz = estate.get("application_landing_zones", {})
    if alz:
        print("Application Landing Zones:")
        for name, info in alz.items():
            status = info.get("status", "unknown")
            marker = "✓" if status == "deployed" else "○"
            print(f"  {marker} {name:<20} {status}")
        print()
    else:
        print("Application Landing Zones: (none)\n")

    # Cross-cutting
    cc = estate.get("cross_cutting", {})
    mgh = cc.get("management_group_hierarchy", {})
    if mgh:
        print(f"MG Hierarchy:  {mgh.get('status', '?')} ({mgh.get('design', '?')})")
        mg_list = mgh.get("management_groups", [])
        if mg_list:
            print(f"  Groups: {', '.join(mg_list[:6])}", end="")
            if len(mg_list) > 6:
                print(f" (+{len(mg_list) - 6} more)")
            else:
                print()

    # Day-2
    d2 = estate.get("day2_operations", {})
    mon = d2.get("monitoring", {})
    rem = d2.get("remediation", {})
    print(f"\nDay-2 Ops:")
    print(f"  Monitoring:   {mon.get('status', '?')}")
    print(f"  Remediation:  {rem.get('status', '?')}")


def main() -> int:
    as_json = "--json" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if args:
        customer = args[0]
    else:
        customers = _find_customers()
        if not customers:
            print("No estate-state files found in agent-output/")
            return 1
        if len(customers) == 1:
            customer = customers[0]
        else:
            print(f"Multiple customers found: {', '.join(customers)}")
            print("Specify one: python tools/scripts/snapshot-estate.py <customer>")
            return 1

    estate = _load_estate(customer)
    if estate is None:
        print(f"No estate-state found for customer: {customer}")
        return 1

    if as_json:
        print(json.dumps(estate, indent=2))
    else:
        _print_text(estate, customer)

    return 0


if __name__ == "__main__":
    sys.exit(main())
