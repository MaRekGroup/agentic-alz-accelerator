# Assessment Report Skill

Generates comprehensive assessment reports from WARA evaluation results and
discovery data. Produces multiple artifact types for different audiences.

## Report Types

### Current-State Architecture (`current-state-architecture.md`)
Documents the as-is Azure environment:
- Management group hierarchy table
- Subscription inventory
- Resource counts by type
- Network topology (VNets, peerings)
- Policy assignments
- RBAC assignment counts
- Logging/monitoring configuration
- Security posture (Defender score, plans)

### Target-State Architecture (`target-state-architecture.md`)
Remediation roadmap based on assessment findings:
- Assessment score summary
- Findings grouped by WAF pillar, ordered by severity
- Step-by-step remediation instructions per finding
- Target state alignment goals (CAF, WAF, Security Baseline)

### Assessment Report (`assessment-report.md` + `.json`)
Scored findings report:
- Executive summary (overall score, check counts)
- Pillar score table (score, critical/high/medium/low counts)
- Detailed findings with severity, recommendation, remediation steps, references
- JSON variant for machine consumption / CI integration

### Architecture Diagram (`architecture-diagram.mmd`)
Mermaid graph of the discovered environment:
- Management group hierarchy with parent→child edges
- Subscription nodes
- VNet topology with address spaces
- Peering connections

### ADR (`ADR-assessment-findings.md`)
Architecture Decision Record for critical/high findings:
- Context (scope, score, finding count)
- Each critical/high finding as a decision item
- Decision placeholder (Accept / Modify / Defer)
- Consequences section

## Output Directory

All artifacts are written to:
```
agent-output/{customer}/assessment/<scope-label>/
```

Where `<scope-label>` is derived from the assessment scope, sanitized to be
filesystem-safe (alphanumeric, hyphens, underscores only).

## Usage

```python
from src.tools.report_generator import ReportGenerator

reporter = ReportGenerator(output_dir="agent-output/{customer}/assessment")
outputs = reporter.generate_all(discovery_result, assessment_result)
# Returns: {"current_state": Path, "target_state": Path, ...}
```

## Conventions

- All timestamps in UTC
- Severity badges: 🔴 Critical, 🟠 High, 🟡 Medium, 🔵 Low
- Evidence capped at 10 items in report output
- Policy assignments capped at 20 in current-state doc
- Mermaid node IDs are alphanumeric (special chars replaced with underscore)
