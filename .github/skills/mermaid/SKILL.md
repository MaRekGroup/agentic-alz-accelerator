---
name: mermaid
description: "Mermaid diagram generation for inline markdown documentation: flowcharts, sequence diagrams, Gantt charts, state diagrams, and ER diagrams. USE FOR: inline markdown diagrams, workflow visualizations, auth flows, deployment sequences, lifecycle state machines. DO NOT USE FOR: architecture diagrams with Azure icons (use drawio), WAF/cost charts (use python-diagrams), Draw.io diagrams (use drawio)."
compatibility: Works with VS Code Copilot, Claude Code, and any tool that renders Mermaid in markdown.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "1.0"
  category: diagrams
---

# Mermaid Diagrams

Skill for generating Mermaid diagrams embedded in markdown fences. Used for
inline documentation diagrams — flowcharts, sequences, state machines, ER
diagrams, and Gantt charts. For architecture diagrams with Azure service icons,
use the `drawio` skill instead.

## When to Use Mermaid

- Inline diagrams inside markdown documents (`.md`)
- Workflow flowcharts for operational runbooks
- Sequence diagrams for auth flows and API interactions
- Gantt charts for deployment schedules
- State diagrams for landing zone lifecycle
- Management group hierarchy visualizations
- Policy assignment flow diagrams

## When NOT to Use Mermaid

- Architecture diagrams needing Azure service icons → use `drawio`
- WAF score charts, cost donuts → use `python-diagrams`
- Standalone diagram files for external consumption → use `drawio`

## Syntax Reference

### Flowcharts

```mermaid
graph TB
    A["Step 1"] --> B{"Decision"}
    B -->|"Yes"| C["Action"]
    B -->|"No"| D["Skip"]
```

Use `graph TB` (top-to-bottom) for vertical layouts.
Use `graph LR` (left-to-right) for horizontal layouts.
Use subgraphs for logical grouping:

```mermaid
graph TB
    subgraph "Platform Landing Zones"
        MGMT["Management"]
        CONN["Connectivity"]
        IDTY["Identity"]
        SEC["Security"]
    end
    MGMT --> CONN --> IDTY --> SEC
```

### Sequence Diagrams

```mermaid
sequenceDiagram
    participant User
    participant Orchestrator
    participant Forge
    participant GitHub Actions
    User->>Orchestrator: Deploy connectivity
    Orchestrator->>Forge: Generate Bicep
    Forge-->>Orchestrator: Templates ready
    Orchestrator->>GitHub Actions: Trigger workflow
    GitHub Actions-->>Orchestrator: Deployment complete
```

### Gantt Charts

```mermaid
gantt
    title Platform LZ Deployment
    dateFormat YYYY-MM-DD
    section Management
        Deploy LAW        :mgmt1, 2026-01-01, 2d
        Deploy Automation :mgmt2, after mgmt1, 1d
    section Connectivity
        Deploy Hub VNet   :conn1, after mgmt2, 2d
        Deploy Bastion    :conn2, after conn1, 1d
```

### State Diagrams

```mermaid
stateDiagram-v2
    [*] --> pending
    pending --> in_progress: start-step
    in_progress --> completed: complete-step
    in_progress --> blocked: blocker found
    blocked --> in_progress: blocker resolved
    completed --> [*]
```

### ER Diagrams

```mermaid
erDiagram
    MANAGEMENT_GROUP ||--o{ SUBSCRIPTION : contains
    SUBSCRIPTION ||--o{ RESOURCE_GROUP : contains
    RESOURCE_GROUP ||--|{ RESOURCE : deploys
    POLICY_DEFINITION ||--o{ POLICY_ASSIGNMENT : "assigned via"
```

## ALZ-Specific Patterns

### Management Group Hierarchy

```mermaid
graph TB
    ROOT["Tenant Root Group"]
    ROOT --> PLATFORM["mrg-platform"]
    ROOT --> LZ["mrg-landingzones"]
    ROOT --> SANDBOX["mrg-sandbox"]
    ROOT --> DECOMM["mrg-decommissioned"]
    PLATFORM --> MGMT["mrg-platform-management"]
    PLATFORM --> CONN["mrg-platform-connectivity"]
    PLATFORM --> IDTY["mrg-platform-identity"]
    PLATFORM --> SEC["mrg-platform-security"]
    LZ --> CORP["mrg-landingzones-corp"]
    LZ --> ONLINE["mrg-landingzones-online"]
```

### APEX Workflow

```mermaid
graph LR
    REQ["1 Requirements"] --> ARCH["2 Architecture"]
    ARCH --> DES["3 Design"]
    DES --> GOV["3.5 Governance"]
    GOV --> PLAN["4 Plan"]
    PLAN --> CODE["5 Code"]
    CODE --> DEPLOY["6 Deploy"]
    DEPLOY --> DOCS["7 Docs"]
```

### Deployment Pipeline

```mermaid
graph LR
    VALIDATE["Validate"] --> WHATIF["What-If"]
    WHATIF --> APPROVE{"Gate"}
    APPROVE -->|Approved| DEPLOY["Deploy"]
    APPROVE -->|Rejected| FIX["Fix Issues"]
    FIX --> VALIDATE
    DEPLOY --> VERIFY["Verify"]
```

## Theming (Dark Mode Compatible)

Include a neutral theme directive for consistent rendering:

```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#ffffff',
      'primaryTextColor': '#333333',
      'primaryBorderColor': '#e91e63',
      'lineColor': '#475569',
      'fontFamily': 'ui-sans-serif, system-ui, sans-serif'
    }
  }
}%%
graph LR
    A --> B
```

## Node Styling

Use `classDef` for consistent styling:

```mermaid
graph TB
    classDef default fill:#ffffff,stroke:#e91e63,stroke-width:2px,color:#1f2937,rx:8px,ry:8px;
    classDef gate fill:#ffffff,stroke:#3b82f6,stroke-width:2px,color:#1f2937,rx:8px,ry:8px;
    classDef deployed fill:#d1fae5,stroke:#10b981,stroke-width:2px,color:#1f2937,rx:8px,ry:8px;

    S1["Management"]:::deployed
    G1{{"Gate 1"}}:::gate
```

## Guardrails

**DO:** Use fenced code blocks with `mermaid` language tag · Include theme
directives for dark mode · Use `graph TB` for vertical layouts · Use subgraphs
for grouping · Use descriptive connection labels.

**DON'T:** Use Mermaid for WAF/cost charts (use `python-diagrams`) · Use Mermaid
for architecture diagrams needing Azure icons (use `drawio`) · Create diagrams
with >30 nodes (split into multiple diagrams) · Omit theme directives.
