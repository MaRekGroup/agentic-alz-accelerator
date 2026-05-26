"""Tests for scripts/sync_aprl.py."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
import yaml

from scripts.sync_aprl import build_diff_summary, sync_aprl, transform_recommendation, write_yaml

SAMPLE_REC = {
    "aprlGuid": "9ec5b4c8-3dd8-473a-86ee-3273290331b9",
    "recommendationTypeId": None,
    "recommendationMetadataState": "Active",
    "learnMoreLink": [{"name": "Doc", "url": "https://learn.microsoft.com/test"}],
    "recommendationControl": "HighAvailability",
    "longDescription": "Enable Stretched Clusters for multi-AZ availability.",
    "pgVerified": True,
    "description": "Enable Stretched Clusters",
    "potentialBenefits": "99.99% SLA",
    "tags": [],
    "recommendationResourceType": "Microsoft.AVS/privateClouds",
    "recommendationImpact": "Low",
    "automationAvailable": True,
    "query": "resources\n| where ['type'] == \"microsoft.avs/privateclouds\"\n| project id, name",
}


@pytest.fixture
def sample_rec() -> dict[str, Any]:
    return copy.deepcopy(SAMPLE_REC)


@pytest.fixture
def transformed_check(sample_rec: dict[str, Any]) -> dict[str, Any]:
    check = transform_recommendation(sample_rec, 0)
    assert check is not None
    return check


def test_transform_recommendation_valid(sample_rec: dict[str, Any]) -> None:
    check = transform_recommendation(sample_rec, 0)

    assert check is not None
    assert check["id"] == "APRL-REL-9EC5B4C8"
    assert check["title"] == "Enable Stretched Clusters (privateClouds)"
    assert check["pillar"] == "reliability"
    assert check["severity"] == "low"
    assert check["confidence"] == "high"
    assert check["query_type"] == "resource_graph"
    assert check["references"] == ["https://learn.microsoft.com/test"]


def test_transform_recommendation_skips_no_query(sample_rec: dict[str, Any]) -> None:
    sample_rec["query"] = ""

    assert transform_recommendation(sample_rec, 0) is None


def test_transform_recommendation_skips_inactive(sample_rec: dict[str, Any]) -> None:
    sample_rec["recommendationMetadataState"] = "Archived"

    assert transform_recommendation(sample_rec, 0) is None


def test_transform_recommendation_skips_cannot_validate(sample_rec: dict[str, Any]) -> None:
    sample_rec["query"] = "cannot-be-validated-with-arg"

    assert transform_recommendation(sample_rec, 0) is None


def test_sync_aprl_filters_correctly(sample_rec: dict[str, Any]) -> None:
    missing_query = copy.deepcopy(sample_rec)
    missing_query["query"] = ""

    inactive = copy.deepcopy(sample_rec)
    inactive["recommendationMetadataState"] = "Inactive"

    cannot_validate = copy.deepcopy(sample_rec)
    cannot_validate["query"] = "cannot-be-validated-with-arg"

    with patch(
        "scripts.sync_aprl.fetch_aprl_feed",
        return_value=[sample_rec, missing_query, inactive, cannot_validate],
    ) as mock_fetch:
        checks = sync_aprl(url="https://example.com/aprl.json")

    mock_fetch.assert_called_once_with("https://example.com/aprl.json")
    assert len(checks) == 1
    assert checks[0]["id"] == "APRL-REL-9EC5B4C8"


def test_write_yaml_creates_file(tmp_path: Path, transformed_check: dict[str, Any]) -> None:
    output = tmp_path / "_aprl_synced.yaml"

    write_yaml([transformed_check], output)

    assert output.exists()
    content = output.read_text(encoding="utf-8")
    data = yaml.safe_load(content)

    assert content.startswith("# APRL-Synced Check Catalog")
    assert data["checks"][0]["id"] == transformed_check["id"]
    assert data["checks"][0]["mappings"]["aprl_guid"] == SAMPLE_REC["aprlGuid"]


def test_build_diff_summary_counts_changes(transformed_check: dict[str, Any]) -> None:
    removed_check = copy.deepcopy(transformed_check)
    removed_check["id"] = "APRL-REL-REMOVED"

    updated_check = copy.deepcopy(transformed_check)
    updated_check["severity"] = "high"

    new_check = copy.deepcopy(transformed_check)
    new_check["id"] = "APRL-REL-NEWCHECK"

    summary = build_diff_summary([transformed_check, removed_check], [updated_check, new_check])

    assert "New: 1" in summary
    assert "Removed: 1" in summary
    assert "Updated: 1" in summary
