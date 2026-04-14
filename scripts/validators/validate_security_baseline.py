#!/usr/bin/env python3
"""
Security Baseline Validator

Validates IaC files (.bicep, .tf) against the non-negotiable security baseline.
Runs at: pre-commit hook, code generation, and deployment preflight.

Based on APEX validate:iac-security-baseline pattern.
"""

import re
import sys
from pathlib import Path

# Security baseline rules — violations block deployment
BICEP_RULES = [
    {
        "id": "SEC-001",
        "name": "TLS 1.2 minimum",
        "pattern": r"minimumTlsVersion:\s*'(?!TLS1_2)",
        "anti_pattern": True,
        "severity": "blocker",
        "message": "minimumTlsVersion must be 'TLS1_2'",
    },
    {
        "id": "SEC-002",
        "name": "HTTPS-only traffic",
        "pattern": r"supportsHttpsTrafficOnly:\s*false",
        "anti_pattern": True,
        "severity": "blocker",
        "message": "supportsHttpsTrafficOnly must be true",
    },
    {
        "id": "SEC-003",
        "name": "No public blob access",
        "pattern": r"allowBlobPublicAccess:\s*true",
        "anti_pattern": True,
        "severity": "blocker",
        "message": "allowBlobPublicAccess must be false",
    },
    {
        "id": "SEC-005",
        "name": "Azure AD-only SQL auth",
        "pattern": r"azureADOnlyAuthentication:\s*false",
        "anti_pattern": True,
        "severity": "blocker",
        "message": "azureADOnlyAuthentication must be true",
    },
    {
        "id": "SEC-EXT-001",
        "name": "Redis non-SSL port",
        "pattern": r"enableNonSslPort:\s*true",
        "anti_pattern": True,
        "severity": "blocker",
        "message": "enableNonSslPort must be false",
    },
    {
        "id": "SEC-EXT-002",
        "name": "FTPS state",
        "pattern": r"ftpsState:\s*'AllAllowed'",
        "anti_pattern": True,
        "severity": "blocker",
        "message": "ftpsState must not be 'AllAllowed' — use 'FtpsOnly' or 'Disabled'",
    },
    {
        "id": "SEC-EXT-003",
        "name": "Remote debugging",
        "pattern": r"remoteDebuggingEnabled:\s*true",
        "anti_pattern": True,
        "severity": "blocker",
        "message": "remoteDebuggingEnabled must be false in production",
    },
    {
        "id": "SEC-EXT-004",
        "name": "Cosmos DB local auth",
        "pattern": r"disableLocalAuth:\s*false",
        "anti_pattern": True,
        "severity": "blocker",
        "message": "disableLocalAuth must be true — use Entra ID authentication",
    },
    {
        "id": "SEC-EXT-005",
        "name": "Key Vault network open",
        "pattern": r"defaultAction:\s*'Allow'",
        "anti_pattern": True,
        "severity": "warning",
        "message": "Key Vault networkAcls defaultAction should be 'Deny'",
    },
    {
        "id": "SEC-EXT-006",
        "name": "Wildcard CORS",
        "pattern": r"allowedOrigins:\s*\[\s*'\*'\s*\]",
        "anti_pattern": True,
        "severity": "warning",
        "message": "Wildcard CORS origin detected — restrict to specific domains",
    },
]

TERRAFORM_RULES = [
    {
        "id": "SEC-001",
        "name": "TLS 1.2 minimum",
        "pattern": r'min_tls_version\s*=\s*"(?!1\.2")',
        "anti_pattern": True,
        "severity": "blocker",
    },
    {
        "id": "SEC-002",
        "name": "HTTPS-only traffic",
        "pattern": r"https_traffic_only_enabled\s*=\s*false",
        "anti_pattern": True,
        "severity": "blocker",
    },
    {
        "id": "SEC-003",
        "name": "No public blob access",
        "pattern": r"allow_nested_items_to_be_public\s*=\s*true",
        "anti_pattern": True,
        "severity": "blocker",
    },
    {
        "id": "SEC-005",
        "name": "Azure AD-only SQL auth",
        "pattern": r"azuread_authentication_only\s*=\s*false",
        "anti_pattern": True,
        "severity": "blocker",
    },
    {
        "id": "SEC-EXT-001",
        "name": "Redis non-SSL port",
        "pattern": r"enable_non_ssl_port\s*=\s*true",
        "anti_pattern": True,
        "severity": "blocker",
    },
    {
        "id": "SEC-EXT-002",
        "name": "FTPS state",
        "pattern": r'ftps_state\s*=\s*"AllAllowed"',
        "anti_pattern": True,
        "severity": "blocker",
    },
    {
        "id": "SEC-EXT-003",
        "name": "Remote debugging",
        "pattern": r"remote_debugging_enabled\s*=\s*true",
        "anti_pattern": True,
        "severity": "blocker",
    },
]


def validate_file(file_path: Path) -> list[dict]:
    """Validate a single IaC file against security baseline."""
    content = file_path.read_text()
    violations = []

    if file_path.suffix == ".bicep":
        rules = BICEP_RULES
    elif file_path.suffix == ".tf":
        rules = TERRAFORM_RULES
    else:
        return []

    for rule in rules:
        matches = list(re.finditer(rule["pattern"], content))
        if rule.get("anti_pattern") and matches:
            for match in matches:
                line_num = content[:match.start()].count("\n") + 1
                violations.append({
                    "file": str(file_path),
                    "line": line_num,
                    "rule_id": rule["id"],
                    "name": rule["name"],
                    "severity": rule["severity"],
                    "message": rule.get("message", f"Security baseline violation: {rule['name']}"),
                    "match": match.group().strip(),
                })

    return violations


def validate_directory(directory: Path) -> tuple[list[dict], list[dict]]:
    """Validate all IaC files in a directory."""
    blockers = []
    warnings = []

    for pattern in ["**/*.bicep", "**/*.tf"]:
        for file_path in directory.glob(pattern):
            for violation in validate_file(file_path):
                if violation["severity"] == "blocker":
                    blockers.append(violation)
                else:
                    warnings.append(violation)

    return blockers, warnings


def main():
    """CLI entry point."""
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("infra")

    if not target.exists():
        print(f"Target not found: {target}")
        sys.exit(1)

    if target.is_file():
        violations = validate_file(target)
        blockers = [v for v in violations if v["severity"] == "blocker"]
        warnings = [v for v in violations if v["severity"] == "warning"]
    else:
        blockers, warnings = validate_directory(target)

    # Print results
    if warnings:
        print(f"\n⚠️  {len(warnings)} warning(s):")
        for w in warnings:
            print(f"  [{w['rule_id']}] {w['file']}:{w['line']} — {w['message']}")

    if blockers:
        print(f"\n🚫 {len(blockers)} blocking violation(s):")
        for b in blockers:
            print(f"  [{b['rule_id']}] {b['file']}:{b['line']} — {b['message']}")
        print("\n❌ Security baseline validation FAILED — fix blockers before proceeding")
        sys.exit(1)

    print(f"\n✅ Security baseline validation PASSED ({len(warnings)} warnings)")
    sys.exit(0)


if __name__ == "__main__":
    main()
