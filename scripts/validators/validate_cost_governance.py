#!/usr/bin/env python3
"""
Cost Governance Validator

Validates that IaC files include budget resources with forecast alerts
at 80%, 100%, and 120% thresholds. Based on APEX cost governance pattern.

Rule: No budget, no merge.
"""

import re
import sys
from pathlib import Path


def validate_bicep_budget(content: str, file_path: str) -> list[dict]:
    """Check Bicep files for budget resource with forecast alerts."""
    findings = []

    # Check for budget resource
    if "Microsoft.Consumption/budgets" not in content:
        findings.append({
            "file": file_path,
            "rule": "COST-001",
            "severity": "blocker",
            "message": "No Azure Budget resource found — every deployment must include cost monitoring",
        })
        return findings

    # Check for forecast thresholds
    for threshold in [80, 100, 120]:
        pattern = rf"threshold:\s*{threshold}"
        if not re.search(pattern, content):
            findings.append({
                "file": file_path,
                "rule": f"COST-002-{threshold}",
                "severity": "blocker",
                "message": f"Missing {threshold}% forecast alert threshold in budget resource",
            })

    # Check thresholdType is Forecasted (not Actual)
    if "thresholdType: 'Actual'" in content and "thresholdType: 'Forecasted'" not in content:
        findings.append({
            "file": file_path,
            "rule": "COST-003",
            "severity": "warning",
            "message": "Budget uses Actual thresholds — prefer Forecasted for early warning",
        })

    # Check for hardcoded budget amount
    budget_match = re.search(r"amount:\s*(\d+)", content)
    if budget_match:
        findings.append({
            "file": file_path,
            "rule": "COST-004",
            "severity": "blocker",
            "message": "Budget amount is hardcoded — must be a parameter",
        })

    return findings


def validate_terraform_budget(content: str, file_path: str) -> list[dict]:
    """Check Terraform files for budget resource with forecast alerts."""
    findings = []

    if "azurerm_consumption_budget" not in content:
        findings.append({
            "file": file_path,
            "rule": "COST-001",
            "severity": "blocker",
            "message": "No Azure Budget resource found — every deployment must include cost monitoring",
        })
        return findings

    # Support both literal thresholds and dynamic blocks with for_each
    has_dynamic_thresholds = re.search(
        r'for_each\s*=\s*\[\s*80\s*,\s*100\s*,\s*120\s*\]', content
    )

    for threshold in [80, 100, 120]:
        pattern = rf"threshold\s*=\s*{threshold}"
        if not re.search(pattern, content) and not has_dynamic_thresholds:
            findings.append({
                "file": file_path,
                "rule": f"COST-002-{threshold}",
                "severity": "blocker",
                "message": f"Missing {threshold}% forecast alert threshold",
            })

    return findings


def validate_directory(directory: Path) -> tuple[list[dict], list[dict]]:
    """Validate cost governance in all IaC files."""
    blockers = []
    warnings = []

    # Sub-modules and non-deploying modules are exempt from individual budget requirements.
    # Budgets are managed by parent/governance entry-point modules.
    exempt_patterns = {
        # Bicep sub-modules consumed by parent modules
        "hub-spoke", "vwan", "gateways", "private-dns",
        "security-workspace", "sentinel", "defender", "soar",
        # Modules that don't deploy billable resources
        "billing-and-tenant", "policies",
    }

    def is_exempt(file_path: Path) -> bool:
        return any(part in exempt_patterns for part in file_path.parts)

    for main_file in directory.glob("**/main.bicep"):
        if is_exempt(main_file):
            continue
        content = main_file.read_text()
        for finding in validate_bicep_budget(content, str(main_file)):
            if finding["severity"] == "blocker":
                blockers.append(finding)
            else:
                warnings.append(finding)

    for main_file in directory.glob("**/main.tf"):
        if is_exempt(main_file):
            continue
        content = main_file.read_text()
        for finding in validate_terraform_budget(content, str(main_file)):
            if finding["severity"] == "blocker":
                blockers.append(finding)
            else:
                warnings.append(finding)

    return blockers, warnings


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("infra")

    if not target.exists():
        print(f"Target not found: {target}")
        sys.exit(1)

    blockers, warnings = validate_directory(target)

    if warnings:
        print(f"\n⚠️  {len(warnings)} cost governance warning(s):")
        for w in warnings:
            print(f"  [{w['rule']}] {w['file']} — {w['message']}")

    if blockers:
        print(f"\n🚫 {len(blockers)} cost governance violation(s):")
        for b in blockers:
            print(f"  [{b['rule']}] {b['file']} — {b['message']}")
        print("\n❌ Cost governance validation FAILED — no budget, no merge")
        sys.exit(1)

    print("\n✅ Cost governance validation PASSED")
    sys.exit(0)


if __name__ == "__main__":
    main()
