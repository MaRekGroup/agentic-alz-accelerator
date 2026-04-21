// @ts-check
import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

const SITE_BASE = "/agentic-alz-accelerator";

export default defineConfig({
  site: "https://MaRekGroup.github.io",
  base: SITE_BASE,
  trailingSlash: "always",
  integrations: [
    starlight({
      title: "ALZ Accelerator",
      description:
        "Agentic Azure Landing Zone Accelerator — from requirements to deployed, governed infrastructure",
      favicon: "/images/favicon.svg",
      editLink: {
        baseUrl:
          "https://github.com/MaRekGroup/agentic-alz-accelerator/edit/main/site/",
      },
      lastUpdated: true,
      social: [
        {
          icon: "github",
          label: "GitHub",
          href: "https://github.com/MaRekGroup/agentic-alz-accelerator",
        },
      ],
      sidebar: [
        {
          label: "Getting Started",
          collapsed: false,
          items: [
            { label: "Quickstart", slug: "getting-started/quickstart" },
            {
              label: "Dev Container Setup",
              slug: "getting-started/dev-containers",
            },
          ],
        },
        {
          label: "Concepts",
          collapsed: true,
          items: [
            { label: "How It Works", slug: "concepts/how-it-works" },
            { label: "Agent Workflow", slug: "concepts/workflow" },
            {
              label: "CAF Design Areas",
              slug: "concepts/caf-design-areas",
            },
            {
              label: "Platform Landing Zones",
              slug: "concepts/platform-landing-zones",
            },
          ],
        },
        {
          label: "Guides",
          collapsed: true,
          items: [
            {
              label: "Platform Deployment",
              slug: "guides/platform-deployment",
            },
            {
              label: "Security Baseline",
              slug: "guides/security-baseline",
            },
            { label: "Cost Governance", slug: "guides/cost-governance" },
            { label: "Troubleshooting", slug: "guides/troubleshooting" },
          ],
        },
        {
          label: "Reference",
          collapsed: true,
          items: [
            { label: "CI/CD Pipelines", slug: "reference/pipelines" },
            {
              label: "Repository Variables",
              slug: "reference/repo-variables",
            },
            { label: "Agent Roster", slug: "reference/agents" },
            { label: "MCP Servers", slug: "reference/mcp-servers" },
          ],
        },
        {
          label: "Project",
          collapsed: true,
          items: [
            { label: "Contributing", slug: "project/contributing" },
            { label: "Changelog", slug: "project/changelog" },
          ],
        },
      ],
    }),
  ],
});
