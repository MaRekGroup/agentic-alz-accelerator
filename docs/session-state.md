# Agentic ALZ Accelerator — Session State

## Completed Work
- **MCP Overhaul**: Replaced 5 homegrown MCP servers with 3 (APEX azure-pricing-mcp submodule + consolidated azure-platform + drawio)
- **Python Diagrams Engine**: Added `diagrams` library as Step 3 option (python/svg/drawio), wired into orchestrator
- **Icon Fixes**: Updated imports from `managementgovernance`, `networking` etc. for proper Azure icons (Policy, Bastions, AutomationAccounts)
- **MG Hierarchy**: Added subscriptions under each management group

## Key Files Modified
- `mcp/azure-platform/server.py` — consolidated 27-tool MCP server
- `mcp/azure-pricing-mcp/` — git submodule (APEX v4.0.0)
- `mcp/mcp-config.json` — 3-server config
- `src/tools/python_diagram_generator.py` — DiagramEngine with 7 methods, proper Azure icons
- `src/tools/azure_diagram_generator.py` — added `generate_diagrams()` facade (engine selector)
- `src/agents/orchestrator.py` — `diagram_engine` param, `_run_design_step()`
- `.github/skills/workflow-engine/templates/workflow-graph.json` — Step 3 engine options
- `requirements.txt` — added `mcp>=1.0.0`, `diagrams>=0.24.0`
- `.devcontainer/devcontainer.json` — graphviz, submodule init, pricing deps

## Diagrams Generated (agent-output/{customer}/diagrams/)
- `01-management-group-hierarchy.png` (85KB) — with subscriptions ✅
- `02-hub-spoke-network-topology.png` (135KB) — proper Bastion/Automation icons ✅
- `03-security-governance-monitoring.png` (137KB) — proper Policy icon ✅
- `alz-architecture.png` (195KB) — proper Policy/Automation icons ✅

## Technical Notes
- Python .venv with Python 3.13, all deps installed
- `azure-mgmt-resource` v25 removed PolicyClient — replaced with Resource Graph policyresources queries
- Old MCP dirs removed: azure-deployment/, azure-monitor/, azure-policy/, azure-resource-graph/, azure-pricing/
- `.gitmodules` maps `mcp/azure-pricing-mcp` → `https://github.com/msftnadavbh/AzurePricingMCP.git`

## Diagram Detail Improvements (Round 2)
- **01-MG Hierarchy**: Added policy assignment indicators at each MG level
- **02-Hub-Spoke**: Added CIDRs, named subnets, NSGs, route tables, DDoS, Private DNS Zones, VNet Peering labels
- **03-Security/Gov/Mon**: Added Compliance Dashboard, Identity & Access (PIM/RBAC, Conditional Access), Action Groups, budget alerts, diagnostic settings flow
- **04-ALZ Architecture**: Added Azure Monitor, Bastion, Private DNS, PIM/RBAC, NSGs, Private Endpoints, App GW + WAF, Route Tables, Compliance, CIDRs

## Guide HTML Fixes (Round 3)
- MCP count 5→3 (hero stat, description card, architecture chips, MCP table)
- Added Step 3 Design/Artisan (progress tracker, workflow step card, agent roster row)
- Agent count 10→11→12 (hero stat, sidebar badge, roster header)
- Tools count 7→8 (sidebar badge, added python_diagram_generator.py row)
- MCP architecture layer: 5 chips → 3 (Pricing, Platform consolidated, Draw.io)
- MCP table: 5 rows → 3 rows with module paths
- Removed 3 references to non-existent ALZ_Bootstrap_Settings_Checklist.xlsx, replaced with inline table

## Deployment Status (as of April 16)
- **Management LZ**: Bicep deployment SUCCEEDED via GitHub Actions (Log Analytics, Automation Account, Action Group, Budget deployed). Post-deploy Python verify step failed (pydantic AzureAISettings error — FIXED in commit d9dde2f).
- **Connectivity LZ**: NOT deployed — was blocked by missing bicepparam file (FIXED — platform-connectivity-prod.bicepparam created)
- **Identity LZ**: NOT deployed — was blocked by missing bicepparam file (FIXED — platform-identity-prod.bicepparam created)  
- **Security LZ**: NOT deployed — was blocked by missing bicepparam file (FIXED — platform-security-prod.bicepparam created)
- **Azure CLI**: NOT authenticated locally (device code expired in last session)

## Fixes Applied (commit d9dde2f, pushed to main)
- AzureAISettings: project_connection_string and openai_endpoint default to "" 
- Created 3 missing .bicepparam files (connectivity, identity, security)
- Fixed ResourceGraphClient constructor args in verify step

## Pending / Next Steps
- Re-trigger GitHub Actions pipeline to deploy remaining 3 platform LZs (Connectivity, Identity, Security)
- Or authenticate locally (`az login`) and run verification
- Continue APEX workflow after all 4 platform LZs are deployed
- Test full end-to-end workflow
