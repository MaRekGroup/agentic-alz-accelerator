"""
Azure Pricing MCP Server

Exposes Azure pricing operations as MCP tools for the agent workflow.
Supports cost estimation, price comparison across regions/SKUs,
reserved instance pricing analysis, and region recommendations.

Uses the Azure Retail Prices API (no authentication required).
"""

import json
import logging
import sys
from typing import Any
from urllib.parse import quote
from urllib.request import urlopen

logger = logging.getLogger(__name__)

AZURE_PRICING_API = "https://prices.azure.com/api/retail/prices"

TOOLS = [
    {
        "name": "azure_cost_estimate",
        "description": "Estimate costs based on resource types and usage patterns",
        "inputSchema": {
            "type": "object",
            "properties": {
                "service_name": {"type": "string", "description": "Azure service (e.g., 'Virtual Machines')"},
                "sku_name": {"type": "string", "description": "SKU name (e.g., 'Standard_D2s_v5')"},
                "region": {"type": "string", "default": "eastus2"},
                "hours_per_month": {"type": "number", "default": 730},
            },
            "required": ["service_name"],
        },
    },
    {
        "name": "azure_bulk_estimate",
        "description": "Multi-resource cost estimate in one call",
        "inputSchema": {
            "type": "object",
            "properties": {
                "resources": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "service_name": {"type": "string"},
                            "sku_name": {"type": "string"},
                            "region": {"type": "string"},
                            "quantity": {"type": "number"},
                        },
                    },
                    "description": "List of resources to estimate",
                },
            },
            "required": ["resources"],
        },
    },
    {
        "name": "azure_price_compare",
        "description": "Compare prices across regions and SKUs",
        "inputSchema": {
            "type": "object",
            "properties": {
                "service_name": {"type": "string"},
                "sku_name": {"type": "string"},
                "regions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Regions to compare",
                },
            },
            "required": ["service_name", "regions"],
        },
    },
    {
        "name": "azure_ri_pricing",
        "description": "Reserved Instance pricing and savings analysis",
        "inputSchema": {
            "type": "object",
            "properties": {
                "service_name": {"type": "string"},
                "sku_name": {"type": "string"},
                "region": {"type": "string", "default": "eastus2"},
            },
            "required": ["service_name"],
        },
    },
    {
        "name": "azure_region_recommend",
        "description": "Find cheapest regions for a given service",
        "inputSchema": {
            "type": "object",
            "properties": {
                "service_name": {"type": "string"},
                "sku_name": {"type": "string"},
                "top_n": {"type": "integer", "default": 5},
            },
            "required": ["service_name"],
        },
    },
]


def _query_pricing_api(filter_str: str) -> list[dict]:
    """Query the Azure Retail Prices API."""
    encoded_filter = quote(filter_str)
    url = f"{AZURE_PRICING_API}?$filter={encoded_filter}"
    try:
        with urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read())
            return data.get("Items", [])
    except Exception as e:
        logger.error(f"Pricing API error: {e}")
        return []


class AzurePricingServer:
    """MCP server exposing Azure pricing capabilities."""

    def handle_tool_call(self, tool_name: str, arguments: dict) -> Any:
        """Route MCP tool calls to the appropriate handler."""
        if tool_name == "azure_cost_estimate":
            return self._cost_estimate(arguments)
        elif tool_name == "azure_bulk_estimate":
            return self._bulk_estimate(arguments)
        elif tool_name == "azure_price_compare":
            return self._price_compare(arguments)
        elif tool_name == "azure_ri_pricing":
            return self._ri_pricing(arguments)
        elif tool_name == "azure_region_recommend":
            return self._region_recommend(arguments)
        return {"error": f"Unknown tool: {tool_name}"}

    def _cost_estimate(self, arguments: dict) -> dict:
        """Estimate cost for a single resource."""
        service = arguments["service_name"]
        sku = arguments.get("sku_name", "")
        region = arguments.get("region", "eastus2")
        hours = arguments.get("hours_per_month", 730)

        filter_parts = [
            f"serviceName eq '{service}'",
            f"armRegionName eq '{region}'",
            "priceType eq 'Consumption'",
        ]
        if sku:
            filter_parts.append(f"contains(skuName, '{sku}')")

        items = _query_pricing_api(" and ".join(filter_parts))
        if not items:
            return {"error": f"No pricing data found for {service} in {region}"}

        item = items[0]
        unit_price = item.get("unitPrice", 0)
        return {
            "service": service,
            "sku": item.get("skuName", sku),
            "region": region,
            "unit_price": unit_price,
            "unit_of_measure": item.get("unitOfMeasure", ""),
            "estimated_monthly_cost": round(unit_price * hours, 2),
            "currency": item.get("currencyCode", "USD"),
            "meter_name": item.get("meterName", ""),
        }

    def _bulk_estimate(self, arguments: dict) -> dict:
        """Estimate costs for multiple resources."""
        resources = arguments.get("resources", [])
        estimates = []
        total = 0.0

        for res in resources:
            est = self._cost_estimate({
                "service_name": res.get("service_name", ""),
                "sku_name": res.get("sku_name", ""),
                "region": res.get("region", "eastus2"),
                "hours_per_month": res.get("quantity", 730),
            })
            estimates.append(est)
            total += est.get("estimated_monthly_cost", 0)

        return {
            "estimates": estimates,
            "total_monthly_cost": round(total, 2),
            "currency": "USD",
        }

    def _price_compare(self, arguments: dict) -> dict:
        """Compare prices across regions."""
        service = arguments["service_name"]
        sku = arguments.get("sku_name", "")
        regions = arguments.get("regions", ["eastus2", "westus2", "westeurope"])

        comparisons = []
        for region in regions:
            est = self._cost_estimate({
                "service_name": service,
                "sku_name": sku,
                "region": region,
            })
            comparisons.append({
                "region": region,
                "unit_price": est.get("unit_price", 0),
                "monthly_cost": est.get("estimated_monthly_cost", 0),
            })

        comparisons.sort(key=lambda x: x["unit_price"])
        cheapest = comparisons[0]["region"] if comparisons else "unknown"

        return {
            "service": service,
            "sku": sku,
            "comparisons": comparisons,
            "cheapest_region": cheapest,
        }

    def _ri_pricing(self, arguments: dict) -> dict:
        """Get reserved instance pricing and calculate savings."""
        service = arguments["service_name"]
        sku = arguments.get("sku_name", "")
        region = arguments.get("region", "eastus2")

        # Get pay-as-you-go price
        payg = self._cost_estimate({"service_name": service, "sku_name": sku, "region": region})
        payg_monthly = payg.get("estimated_monthly_cost", 0)

        # Get 1-year RI pricing
        filter_parts = [
            f"serviceName eq '{service}'",
            f"armRegionName eq '{region}'",
            "priceType eq 'Reservation'",
            "reservationTerm eq '1 Year'",
        ]
        if sku:
            filter_parts.append(f"contains(skuName, '{sku}')")

        ri_1yr = _query_pricing_api(" and ".join(filter_parts))
        ri_1yr_monthly = ri_1yr[0].get("unitPrice", 0) / 12 if ri_1yr else 0

        # Get 3-year RI pricing
        filter_parts[-2] = "reservationTerm eq '3 Years'"
        ri_3yr = _query_pricing_api(" and ".join(filter_parts))
        ri_3yr_monthly = ri_3yr[0].get("unitPrice", 0) / 36 if ri_3yr else 0

        return {
            "service": service,
            "sku": sku,
            "region": region,
            "pay_as_you_go_monthly": round(payg_monthly, 2),
            "ri_1year_monthly": round(ri_1yr_monthly, 2),
            "ri_3year_monthly": round(ri_3yr_monthly, 2),
            "savings_1year_pct": round((1 - ri_1yr_monthly / max(payg_monthly, 0.01)) * 100, 1) if ri_1yr_monthly else 0,
            "savings_3year_pct": round((1 - ri_3yr_monthly / max(payg_monthly, 0.01)) * 100, 1) if ri_3yr_monthly else 0,
        }

    def _region_recommend(self, arguments: dict) -> dict:
        """Find cheapest regions for a service."""
        service = arguments["service_name"]
        sku = arguments.get("sku_name", "")
        top_n = arguments.get("top_n", 5)

        common_regions = [
            "eastus", "eastus2", "westus2", "westus3", "centralus",
            "northeurope", "westeurope", "uksouth", "southeastasia",
            "australiaeast", "japaneast",
        ]

        region_prices = []
        for region in common_regions:
            est = self._cost_estimate({"service_name": service, "sku_name": sku, "region": region})
            if "error" not in est:
                region_prices.append({
                    "region": region,
                    "unit_price": est.get("unit_price", 0),
                    "monthly_cost": est.get("estimated_monthly_cost", 0),
                })

        region_prices.sort(key=lambda x: x["unit_price"])
        return {
            "service": service,
            "sku": sku,
            "recommended_regions": region_prices[:top_n],
        }


def main():
    """MCP server entry point — reads JSON-RPC from stdin, writes to stdout."""
    server = AzurePricingServer()
    logger.info("Azure Pricing MCP Server started")

    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            method = request.get("method", "")
            if method == "tools/list":
                response = {"tools": TOOLS}
            elif method == "tools/call":
                params = request.get("params", {})
                result = server.handle_tool_call(params["name"], params.get("arguments", {}))
                response = {"content": [{"type": "text", "text": json.dumps(result, default=str)}]}
            else:
                response = {"error": f"Unknown method: {method}"}
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except Exception as e:
            error_response = {"error": str(e)}
            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
