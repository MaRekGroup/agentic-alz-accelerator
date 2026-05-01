"""
Sync APRL (Azure Proactive Resiliency Library) recommendations into local YAML checks.

Fetches the public APRL recommendations feed and transforms it into the
wara_checks YAML format used by src/tools/wara_engine.py.

Usage:
    python scripts/sync_aprl.py [--output src/config/wara_checks/_aprl_synced.yaml]
    python scripts/sync_aprl.py --dry-run  # Preview without writing

Requires network access. Intended for local dev or CI (weekly schedule).
"""

import argparse
import json
import logging
import sys
import textwrap
import urllib.request
from pathlib import Path
from typing import Any

import yaml

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

APRL_FEED_URL = "https://azure.github.io/WARA-Build/objects/recommendations.json"

DEFAULT_OUTPUT = Path(__file__).parent.parent / "src" / "config" / "wara_checks" / "_aprl_synced.yaml"

# Map APRL recommendationControl → our pillar enum
CONTROL_TO_PILLAR: dict[str, str] = {
    "HighAvailability": "reliability",
    "DisasterRecovery": "reliability",
    "BusinessContinuity": "reliability",
    "Scalability": "performance",
    "MonitoringAndAlerting": "operational_excellence",
    "OtherBestPractices": "operational_excellence",
    "ServiceUpgradeAndRetirement": "operational_excellence",
    "Security": "security",
}

# Map APRL recommendationImpact → our severity enum
IMPACT_TO_SEVERITY: dict[str, str] = {
    "High": "high",
    "Medium": "medium",
    "Low": "low",
}

# Map pillar → default CAF area (best-effort; APRL doesn't provide this)
PILLAR_TO_CAF_AREA: dict[str, str] = {
    "reliability": "management",
    "security": "security",
    "performance": "management",
    "operational_excellence": "management",
    "cost_optimization": "governance",
}

# Map pillar → default ALZ area
PILLAR_TO_ALZ_AREA: dict[str, str] = {
    "reliability": "logging",
    "security": "security",
    "performance": "logging",
    "operational_excellence": "logging",
    "cost_optimization": "policy",
}


def fetch_aprl_feed(url: str = APRL_FEED_URL) -> list[dict[str, Any]]:
    """Fetch the APRL recommendations JSON feed."""
    logger.info("Fetching APRL feed from %s", url)
    req = urllib.request.Request(url, headers={"User-Agent": "alz-accelerator-sync/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
        data = json.loads(resp.read())
    logger.info("Fetched %d recommendations", len(data))
    return data


def transform_recommendation(rec: dict[str, Any], index: int) -> dict[str, Any] | None:
    """Transform a single APRL recommendation into our check format.

    Returns None if the recommendation should be skipped (no query, personalized, etc).
    """
    control = rec.get("recommendationControl", "")
    pillar = CONTROL_TO_PILLAR.get(control)
    if pillar is None:
        # Skip Personalized or unknown controls
        return None

    query = rec.get("query") or ""
    if not query.strip():
        # Skip recommendations without ARG queries
        return None

    # Skip pseudo-queries that can't be validated with ARG
    if "cannot-be-validated-with-arg" in query:
        return None

    # Skip inactive recommendations
    if rec.get("recommendationMetadataState") != "Active":
        return None

    impact = rec.get("recommendationImpact", "Medium")
    severity = IMPACT_TO_SEVERITY.get(impact, "medium")

    # Build ID from APRL GUID (first 8 chars for readability)
    guid = rec.get("aprlGuid", f"unknown-{index}")
    short_id = guid[:8].upper().replace("-", "")
    pillar_prefix = {
        "reliability": "REL",
        "security": "SEC",
        "performance": "PER",
        "operational_excellence": "OPE",
        "cost_optimization": "COS",
    }[pillar]
    check_id = f"APRL-{pillar_prefix}-{short_id}"

    # Extract resource type for context
    resource_type = rec.get("recommendationResourceType", "")

    # Clean up query - strip leading comment-only lines
    query_lines = query.strip().split("\n")
    cleaned_lines = []
    for line in query_lines:
        stripped = line.strip()
        if stripped.startswith("//") and not cleaned_lines:
            continue  # Skip leading comment lines
        cleaned_lines.append(line)
    clean_query = "\n".join(cleaned_lines).strip()

    # If stripping comments left nothing, skip this check
    if not clean_query:
        return None

    # Build references from learnMoreLink
    references = []
    for link in rec.get("learnMoreLink", []):
        url = link.get("url", "")
        if url:
            references.append(url)

    # Build the check
    title = rec.get("description", "").strip()
    if resource_type:
        # Add resource type context to title if not already present
        short_type = resource_type.split("/")[-1]
        if short_type.lower() not in title.lower():
            title = f"{title} ({short_type})"

    recommendation = rec.get("longDescription", "").strip()
    if not recommendation:
        recommendation = title

    # Truncate overly long recommendations
    if len(recommendation) > 300:
        recommendation = recommendation[:297] + "..."

    check: dict[str, Any] = {
        "id": check_id,
        "title": title,
        "pillar": pillar,
        "caf_area": PILLAR_TO_CAF_AREA[pillar],
        "alz_area": PILLAR_TO_ALZ_AREA[pillar],
        "severity": severity,
        "confidence": "high" if rec.get("pgVerified") else "medium",
        "scope": "subscription",
        "query_type": "resource_graph",
        "query": clean_query,
        "match": "any",
        "recommendation": recommendation,
        "references": references,
        "mappings": {
            "waf_pillar": [pillar],
            "caf_lifecycle": ["govern", "manage"],
            "aprl_guid": guid,
            "resource_type": resource_type,
        },
    }

    return check


def sync_aprl(url: str = APRL_FEED_URL) -> list[dict[str, Any]]:
    """Fetch and transform all APRL recommendations."""
    raw = fetch_aprl_feed(url)

    checks = []
    skipped = 0
    for i, rec in enumerate(raw):
        check = transform_recommendation(rec, i)
        if check is None:
            skipped += 1
            continue
        checks.append(check)

    logger.info(
        "Transformed %d checks, skipped %d (no query, inactive, or personalized)",
        len(checks),
        skipped,
    )
    return checks


def write_yaml(checks: list[dict[str, Any]], output: Path) -> None:
    """Write checks to YAML file in our catalog format."""
    output.parent.mkdir(parents=True, exist_ok=True)

    header = textwrap.dedent("""\
        # APRL-Synced Check Catalog (AUTO-GENERATED — DO NOT EDIT)
        #
        # Source: https://azure.github.io/WARA-Build/objects/recommendations.json
        # Repo: https://github.com/Azure/Well-Architected-Reliability-Assessment
        # Synced by: scripts/sync_aprl.py
        #
        # To refresh: python scripts/sync_aprl.py
        # Schedule: weekly in CI

    """)

    content = {"checks": checks}

    class IndentedDumper(yaml.Dumper):
        """Dumper that indents list items inside mappings (yamllint-compliant)."""

        def increase_indent(self, flow=False, indentless=False):
            return yaml.Dumper.increase_indent(self, flow, False)

    with open(output, "w") as f:
        f.write(header)
        yaml.dump(
            content,
            f,
            Dumper=IndentedDumper,
            default_flow_style=False,
            sort_keys=False,
            width=120,
            allow_unicode=True,
        )

    logger.info("Wrote %d checks to %s", len(checks), output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync APRL recommendations to local YAML")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output YAML file (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--url",
        default=APRL_FEED_URL,
        help="APRL feed URL",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview transformation without writing",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Print statistics only",
    )
    args = parser.parse_args()

    checks = sync_aprl(url=args.url)

    if args.stats or args.dry_run:
        from collections import Counter

        pillar_counts = Counter(c["pillar"] for c in checks)
        severity_counts = Counter(c["severity"] for c in checks)
        confidence_counts = Counter(c["confidence"] for c in checks)

        print(f"\n{'='*50}")
        print(f"APRL Sync Summary")
        print(f"{'='*50}")
        print(f"Total checks: {len(checks)}")
        print(f"\nBy pillar:")
        for p, cnt in pillar_counts.most_common():
            print(f"  {p}: {cnt}")
        print(f"\nBy severity:")
        for s, cnt in severity_counts.most_common():
            print(f"  {s}: {cnt}")
        print(f"\nBy confidence:")
        for c, cnt in confidence_counts.most_common():
            print(f"  {c}: {cnt}")

        if args.dry_run:
            print(f"\nDry run — would write to: {args.output}")
            # Print first 2 checks as sample
            print(f"\nSample checks (first 2):")
            print(yaml.dump({"checks": checks[:2]}, default_flow_style=False, sort_keys=False))
        return

    write_yaml(checks, args.output)
    print(f"✓ Synced {len(checks)} APRL checks to {args.output}")


if __name__ == "__main__":
    main()
