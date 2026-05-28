#!/usr/bin/env python3
"""Generate the Agentic Azure Enterprise ALZ Accelerator L300 dark-theme deck."""
import os, sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)  # pptx_utils.py lives here
from pptx_utils import *

set_theme('dark')
TOTAL = 12

def build():
    prs = create_presentation()
    slide = add_slide(prs)
    add_background(slide)
    
    title_box = slide.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.3), Inches(1.2))
    title_frame = title_box.text_frame
    title_paragraph = title_frame.paragraphs[0]
    title_paragraph.alignment = PP_ALIGN.CENTER
    title_run = title_paragraph.add_run()
    title_run.text = "Agentic Azure Enterprise Landing Zone Accelerator"
    style_run(title_run, 36, color=WHITE, bold=True)
    
    subtitle_box = slide.shapes.add_textbox(Inches(1.2), Inches(3.25), Inches(10.9), Inches(0.6))
    subtitle_frame = subtitle_box.text_frame
    subtitle_paragraph = subtitle_frame.paragraphs[0]
    subtitle_paragraph.alignment = PP_ALIGN.CENTER
    subtitle_run = subtitle_paragraph.add_run()
    subtitle_run.text = "AI Orchestrates - Humans Decide - Azure Executes"
    style_run(subtitle_run, 20, color=SUBTLE_TEXT)
    
    footer_box = slide.shapes.add_textbox(Inches(2.3), Inches(6.55), Inches(8.7), Inches(0.3))
    footer_frame = footer_box.text_frame
    footer_paragraph = footer_frame.paragraphs[0]
    footer_paragraph.alignment = PP_ALIGN.CENTER
    footer_run = footer_paragraph.add_run()
    footer_run.text = "Microsoft | Azure Cloud Solution Architecture"
    style_run(footer_run, 14, color=SUBTLE_TEXT)
    
    add_notes(
        slide,
        "Welcome. Today I will show you how we are using multi-agent AI to transform Azure Landing Zone "
        "deployments from weeks of manual effort into hours of guided, governed automation. This is not a "
        "demo of a single tool - it is an enterprise-grade orchestration system built on the APEX pattern "
        "that covers the full lifecycle from requirements through continuous Day-2 operations.",
    )
    
    slide = add_slide(prs)
    add_background(slide)
    add_title(slide, "About Me + Why This Talk Matters")
    
    left_heading_box = slide.shapes.add_textbox(Inches(0.7), Inches(1.25), Inches(2.5), Inches(0.4))
    left_heading_frame = left_heading_box.text_frame
    left_heading_run = left_heading_frame.paragraphs[0].add_run()
    left_heading_run.text = "About Me"
    style_run(left_heading_run, 20, color=ACCENT_BLUE, bold=True)
    
    right_heading_box = slide.shapes.add_textbox(Inches(6.9), Inches(1.25), Inches(3.0), Inches(0.4))
    right_heading_frame = right_heading_box.text_frame
    right_heading_run = right_heading_frame.paragraphs[0].add_run()
    right_heading_run.text = "Why Attend"
    style_run(right_heading_run, 20, color=ACCENT_BLUE, bold=True)
    
    add_two_column_bullets(
        slide,
        [
            "Senior Cloud Solution Architect, Microsoft",
            "Recently joined Microsoft",
            "Focus: Azure infrastructure automation + AI-driven operations",
        ],
        [
            "Manual ALZ deployments take 4-8 weeks",
            "Governance drift starts on Day 1 after deploy",
            "This accelerator reduces to hours with continuous compliance",
        ],
        top=1.75,
        font_size=18,
    )
    add_notes(
        slide,
        "I am a Senior Cloud Solution Architect who recently joined Microsoft. My focus is on using AI to "
        "transform how we deliver Azure infrastructure at enterprise scale. You should care about this talk "
        "because manual landing zone deployments are slow, error-prone, and create immediate governance drift. "
        "The accelerator we built solves all three problems by using specialized AI agents that enforce "
        "compliance continuously - not just at deployment time.",
    )
    
    slide = add_slide(prs)
    add_background(slide)
    add_title(slide, "The Challenge: Manual ALZ Deployment")
    add_bullet_list(
        slide,
        [
            "4-8 weeks from requirements to production deployment",
            "Inconsistent governance - tribal knowledge, no enforcement",
            "Documentation debt - as-built docs are never written",
            "No Day-2 story - compliance drifts within days",
            "Skills gap - CAF + WAF + IaC + security expertise rarely in one team",
            "Brownfield blind spots - existing environments lack assessment",
        ],
        top=1.55,
        font_size=20,
    )
    add_notes(
        slide,
        "Let me paint the problem. A typical enterprise landing zone deployment takes 4 to 8 weeks. Governance "
        "rules exist in wiki pages nobody reads. Documentation is always planned but never delivered. After "
        "go-live, nobody monitors for drift. And brownfield environments - the ones already in production - "
        "rarely get a proper WAF assessment. The accelerator addresses every one of these pain points with "
        "specialized AI agents.",
    )

    slide = add_slide(prs)
    add_background(slide)
    add_title(slide, "Solution: Multi-Agent APEX Workflow")
    add_card(slide, "15 Agents\nSpecialized roles", left=0.6, top=1.8, width=3.4, height=1.2)
    add_card(slide, "9 Steps\n+ Brownfield Step 0", left=4.8, top=1.8, width=3.4, height=1.2)
    add_card(slide, "6 Gates\nNon-negotiable approval", left=9.0, top=1.8, width=3.4, height=1.2)
    add_bullet_list(
        slide,
        [
            "APEX Pattern: AI Orchestrates, Humans Decide, Azure Executes",
            "Full lifecycle: requirements through continuous Day-2 operations",
            "Supports both greenfield (new) and brownfield (existing) scenarios",
            "AVM-first approach - Azure Verified Modules for Bicep and Terraform",
        ],
        left=0.8,
        top=3.8,
        width=11.6,
        height=2.3,
        font_size=18,
    )
    add_notes(
        slide,
        "The solution follows the APEX pattern - AI Orchestrates, Humans Decide, Azure Executes. "
        "We have 15 specialized agents, each owning a specific step in the workflow. There are 9 workflow "
        "steps plus a Step 0 for brownfield assessment. Six non-negotiable approval gates ensure humans stay "
        "in control. The system supports both greenfield deployments and brownfield environments that already "
        "exist. We use Azure Verified Modules first - falling back to native resources only when no AVM module exists.",
    )
    
    slide = add_slide(prs)
    add_background(slide)
    add_title(slide, "Agent Roster and Workflow")
    add_table(
        slide,
        ["Agent", "Role", "Step"],
        [
            ["Conductor", "Master orchestration + routing", "--"],
            ["Assessor", "Brownfield WAF assessment", "0"],
            ["Scribe", "Requirements capture (8 CAF areas)", "1"],
            ["Oracle", "WAF assessment + cost estimation", "2"],
            ["Warden", "Policy discovery + security baseline", "3.5"],
            ["Strategist", "AVM module selection + planning", "4"],
            ["Forge", "Bicep/Terraform code generation", "5"],
            ["Envoy", "Deploy with what-if preview", "6"],
            ["Sentinel", "Continuous compliance monitoring", "8"],
            ["Mender", "Auto-remediation with rollback", "9"],
            ["Challenger", "Adversarial review at gates", "Gates"],
        ],
        left=0.7,
        top=1.55,
        width=11.9,
        row_height=0.43,
    )
    add_notes(
        slide,
        "Here is the full agent roster. The Conductor orchestrates everything. The Assessor handles brownfield "
        "environments. Scribe captures requirements mapped to all 8 CAF design areas. Oracle does WAF assessment "
        "with cost estimation. Warden enforces governance. Strategist selects AVM modules. Forge generates the IaC "
        "code. Envoy deploys with what-if preview. Then for Day-2: Sentinel monitors continuously and Mender "
        "auto-remediates. The Challenger is our adversarial reviewer - it challenges every output at approval gates "
        "with depth proportional to complexity.",
    )
    
    slide = add_slide(prs)
    add_background(slide)
    add_title(slide, "Layered Architecture")
    
    for top, bg, text in [
        (1.5, ACCENT_BLUE, "Agents Layer: 15 specialized agents (Conductor, Scribe, Oracle, Forge, Sentinel...)"),
        (2.3, CARD_BG, "Skills Layer: 60+ skills (Azure services, CAF, WAF, IaC patterns, security baseline)"),
        (3.1, DARK_BLUE, "Tools Layer: 15 tools (Azure CLI, Resource Graph, Policy, Defender, Cost Management)"),
        (3.9, CARD_BG, "MCP Servers: 3 servers (azure-pricing: 18 tools, azure-platform: 27 tools, drawio)"),
        (4.7, DARK_BLUE, "Hooks Layer: 6 runtime hooks (tool-guardian, secrets-scanner, governance-audit)"),
        (5.5, CARD_BG, "CI/CD Layer: 18 GitHub Actions workflows (bootstrap, deploy, monitor, validate)"),
    ]:
        shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0.6),
            Inches(top),
            Inches(12.1),
            Inches(0.7),
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg
        shape.line.fill.background()
        text_frame = shape.text_frame
        text_frame.clear()
        text_frame.word_wrap = True
        text_frame.margin_left = Pt(14)
        text_frame.margin_right = Pt(14)
        text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        paragraph = text_frame.paragraphs[0]
        paragraph.alignment = PP_ALIGN.LEFT
        run = paragraph.add_run()
        run.text = text
        style_run(run, 18, color=WHITE, bold=True)
    
    add_notes(
        slide,
        "The architecture is layered for separation of concerns. At the top, 15 agents handle high-level workflow "
        "steps. They invoke 60-plus skills - think of these as knowledge modules covering Azure services, CAF, WAF, "
        "and IaC patterns. Skills use 15 tools for actual Azure operations. Three MCP servers provide pricing, "
        "platform operations, and diagramming. Six runtime hooks act as guardrails - the tool-guardian blocks "
        "destructive operations, secrets-scanner prevents credential leaks. At the bottom, 18 GitHub Actions workflows "
        "handle CI/CD.",
    )
    
    slide = add_slide(prs)
    add_background(slide)
    add_title(slide, "Security Baseline + Governance (Non-Negotiable)")
    add_bullet_list(
        slide,
        [
            "6 Security Rules (enforced always):",
            "  TLS 1.2 minimum on all resources",
            "  HTTPS-only traffic",
            "  No public blob access",
            "  Managed Identity preferred",
            "  Azure AD-only SQL authentication",
            "  Public network disabled (prod)",
        ],
        left=0.6,
        top=1.7,
        width=5.8,
        height=4.8,
        font_size=18,
    )
    add_bullet_list(
        slide,
        [
            "Cost Governance:",
            "  Budget alerts at 80% / 100% / 120%",
            "  Parameterized per environment",
            "",
            "Compliance:",
            "  Azure Policy discovery + assignment",
            "  Continuous posture monitoring",
            "  Challenger reviews at 4 gates",
        ],
        left=6.8,
        top=1.7,
        width=5.8,
        height=4.8,
        font_size=18,
    )
    add_notes(
        slide,
        "Security is non-negotiable. Six rules are enforced at code generation, deployment preflight, and continuous "
        "monitoring. TLS 1.2, HTTPS-only, no public blob access, Managed Identity, Azure AD-only SQL auth, and public "
        "network disabled in production. These are not optional - the Forge agent generates code with them baked in, "
        "the Envoy validates at deploy time, and the Sentinel monitors continuously. Cost governance requires budget "
        "alerts at 80, 100, and 120 percent on every deployment. The Challenger agent adversarially reviews outputs at "
        "four gates.",
    )

    slide = add_slide(prs)
    add_background(slide)
    add_title(slide, "CI/CD: 5-Stage Reusable Pipeline")
    add_table(
        slide,
        ["Stage", "Action", "Tools"],
        [
            ["1. Resolve", "Validate Azure access via OIDC", "Workload Identity Federation"],
            [
                "2. Validate",
                "Security baseline + cost governance + lint",
                "Validators, az bicep lint, terraform validate",
            ],
            ["3. Plan", "Bicep what-if / Terraform plan", "ARM deployment, TF state"],
            ["4. Deploy", "Apply with timestamped deployment name", "az deployment, terraform apply"],
            ["5. Verify", "Compliance scan + TDD auto-generation", "Resource Graph, Defender"],
        ],
        top=1.8,
    )
    add_bullet_list(
        slide,
        [
            "18 GitHub Actions workflows total",
            "Supports both Bicep and Terraform tracks",
            "Every PR triggers validate + plan (no surprise deployments)",
        ],
        top=5.2,
        font_size=16,
        height=1.6,
    )
    add_notes(
        slide,
        "The CI/CD pipeline has 5 stages in a reusable workflow. Stage 1 resolves Azure access using Workload Identity Federation - no secrets stored. Stage 2 validates against the security baseline, cost governance rules, and runs linting. Stage 3 runs what-if for Bicep or plan for Terraform - you see exactly what will change. Stage 4 applies with timestamped deployment names for auditability. Stage 5 verifies by running a compliance scan and auto-generating the Technical Design Document. There are 18 total workflows covering bootstrap, platform deploy, app deploy, monitoring, and PR validation.",
    )
    
    slide = add_slide(prs)
    add_background(slide)
    add_title(slide, "Day-2: Continuous Compliance + Auto-Remediation")
    left_items = [
        "Sentinel (Monitor):",
        "  Full scan daily at 06:00 UTC",
        "  Compliance + drift + audit",
        "  Security posture from Defender",
        "  Alert routing by severity",
        "  Critical = immediate action",
    ]
    right_items = [
        "Mender (Remediate):",
        "  8 built-in remediation strategies",
        "  Auto-fix critical + high severity",
        "  Snapshot before every remediation",
        "  Full rollback capability",
        "  Human approval for medium/low",
    ]
    add_two_column_bullets(slide, left_items, right_items, top=1.8, font_size=20)
    add_notes(
        slide,
        "Day-2 is where most landing zone projects fail. The Sentinel agent runs a full compliance, drift detection, and audit scan every day at 6 AM UTC. It checks security posture via Defender for Cloud secure score. Alerts route by severity - critical gets immediate action, high within 15 minutes, medium and low in a daily report. The Mender agent has 8 built-in remediation strategies for common policy violations. It auto-fixes critical and high severity issues but always takes a snapshot first for rollback. Medium and low severity escalate to human approval. This is true continuous compliance, not point-in-time.",
    )
    
    slide = add_slide(prs)
    add_background(slide)
    add_title(slide, "Brownfield: Assess Before You Transform")
    add_bullet_list(
        slide,
        [
            "Step 0: Automated WAF 5-pillar assessment",
            "WARA engine with 221 service-specific checks",
            "Gap analysis mapped to CAF design areas",
            "Current-state architecture documentation (auto-generated)",
            "Target-state architecture with migration roadmap",
            "Discovers: resources, policies, RBAC, networking, security posture",
            "Feeds findings directly into Step 1 requirements",
        ],
        top=1.8,
        font_size=18,
        height=3.8,
    )
    add_subtitle(slide, "Supports: Subscription, Resource Group, or Management Group scope", top=5.5)
    add_notes(
        slide,
        "Most enterprises are not greenfield. They have existing Azure environments that need assessment before transformation. Step 0 runs a full WAF five-pillar assessment using our WARA engine with 221 service-specific checks. It discovers the current state - resources, policies, RBAC assignments, networking topology, and security posture. It generates current-state architecture docs automatically, identifies gaps against CAF design areas, and produces a target-state architecture with a prioritized migration roadmap. The assessment findings feed directly into Step 1 requirements, so the full workflow is informed by reality, not assumptions. You can scope the assessment to a subscription, resource group, or entire management group.",
    )

    slide = add_slide(prs)
    add_background(slide)
    add_title(slide, "By the Numbers")
    
    stats_cards = [
        (0.4, "15", "Agents"),
        (2.9, "60+", "Skills"),
        (5.4, "18", "Workflows"),
        (7.9, "221", "WARA Checks"),
        (10.4, "3", "MCP Servers"),
    ]
    
    for left, number, label in stats_cards:
        card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(left),
            Inches(1.8),
            Inches(2.3),
            Inches(1.45),
        )
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = ACCENT_BLUE
        card.line.width = Pt(1)
    
        text_frame = card.text_frame
        text_frame.clear()
        text_frame.word_wrap = True
        text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    
        number_paragraph = text_frame.paragraphs[0]
        number_paragraph.alignment = PP_ALIGN.CENTER
        number_run = number_paragraph.add_run()
        number_run.text = number
        style_run(number_run, 24, color=WHITE, bold=True)
    
        label_paragraph = text_frame.add_paragraph()
        label_paragraph.alignment = PP_ALIGN.CENTER
        label_run = label_paragraph.add_run()
        label_run.text = label
        style_run(label_run, 14, color=LIGHT_TEXT, bold=True)
    
    add_bullet_list(
        slide,
        [
            "AVM-first: Azure Verified Modules for Bicep and Terraform",
            "CAF-aligned: All 8 design areas covered end-to-end",
            "Full lifecycle: Requirements through continuous Day-2 operations",
            "Auto-documentation: Technical Design Document generated post-deploy",
            "Dual-track IaC: Choose Bicep or Terraform per landing zone",
        ],
        left=0.8,
        top=3.8,
        width=11.8,
        height=2.6,
        font_size=18,
    )
    add_notes(
        slide,
        "Let me give you the numbers. 15 specialized agents, each with a defined role. Over 60 skills covering Azure services, frameworks, and patterns. 18 GitHub Actions workflows for full CI/CD automation. 221 WARA checks for brownfield assessment. 3 MCP servers providing pricing, platform operations, and diagramming. The key differentiators: AVM-first means we always use Azure Verified Modules. CAF-aligned means all 8 design areas are covered. Full lifecycle means we do not stop at deployment - Day-2 operations are built in. Auto-documentation means the Technical Design Document is generated automatically after every deployment. And you can choose Bicep or Terraform per landing zone.",
    )
    
    slide = add_slide(prs)
    add_background(slide, DARK_NAVY)
    
    get_started_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.8))
    title_frame = get_started_title.text_frame
    title_paragraph = title_frame.paragraphs[0]
    title_paragraph.alignment = PP_ALIGN.CENTER
    title_run = title_paragraph.add_run()
    title_run.text = "Get Started"
    style_run(title_run, 40, color=WHITE, bold=True)
    
    content_box = slide.shapes.add_textbox(Inches(1.2), Inches(2.0), Inches(10.9), Inches(3.5))
    content_frame = content_box.text_frame
    content_frame.clear()
    content_frame.word_wrap = True
    content_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    
    content_lines = [
        ("github.com/MaRekGroup/agentic-alz-accelerator", 22, ACCENT_BLUE, True),
        ("", 22, WHITE, False),
        ("Next Steps:", 22, WHITE, True),
        ("1. Clone the repo and explore the interactive guide", 22, LIGHT_TEXT, False),
        ("2. Run a brownfield assessment on a sandbox subscription", 22, LIGHT_TEXT, False),
        ("3. Deploy your first landing zone with agent orchestration", 22, LIGHT_TEXT, False),
    ]
    
    for index, (text, font_size, color, bold) in enumerate(content_lines):
        paragraph = content_frame.paragraphs[0] if index == 0 else content_frame.add_paragraph()
        paragraph.alignment = PP_ALIGN.CENTER
        paragraph.space_after = Pt(10)
        run = paragraph.add_run()
        run.text = text
        style_run(run, font_size, color=color, bold=bold)
    
    questions_box = slide.shapes.add_textbox(Inches(0.8), Inches(6.55), Inches(11.7), Inches(0.3))
    questions_frame = questions_box.text_frame
    questions_paragraph = questions_frame.paragraphs[0]
    questions_paragraph.alignment = PP_ALIGN.CENTER
    questions_run = questions_paragraph.add_run()
    questions_run.text = "Questions?"
    style_run(questions_run, 14, color=SUBTLE_TEXT)
    
    add_notes(
        slide,
        "Here is how to get started. The repo is on GitHub at MaRekGroup/agentic-alz-accelerator. Step one: clone it and open the interactive HTML guide - it walks through every agent, skill, and workflow. Step two: run a brownfield assessment on a sandbox subscription to see the WARA engine in action. Step three: deploy your first landing zone using the full agent orchestration. I am happy to do a deeper dive with your team or help you run a proof of concept. Questions?",
    )

    out = os.path.join(SCRIPT_DIR, '../../docs/agentic-alz-accelerator-l300-10m-dark.pptx')
    save_presentation(prs, out)

if __name__ == '__main__':
    build()
