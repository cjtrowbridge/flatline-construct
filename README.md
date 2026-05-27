# flatline-construct

`flatline-construct` is a personal homelab defense framework that continuously maps local attack surface, identifies likely vulnerabilities without exploitation, and delivers prioritized hardening actions.

## What This Project Is

- A focused framework for personal homelab security assessment.
- A safety-first workflow for discovery, vulnerability research, benign validation, and remediation guidance.
- A documentation-and-script driven system designed to be usable by both human operators and LLM agents.

## What This Project Is Not

- Not a general-purpose agent framework.
- Not an exploitation framework.
- Not a persistence, lateral movement, or destructive testing toolkit.

## Why It Exists

Personal attack surface is increasing quickly as offensive AI capabilities improve. Many home labs have mixed-generation hardware/software and stale patch states. This project exists to methodically identify real risk and provide concrete hardening actions without causing harm.

## Intended Audience

- Primary: home operators running personal homelabs with layered legacy tech.
- Secondary: agents assisting those operators under strict safety and approval rules.

## Success Criteria

- Maximize high-confidence identification of real vulnerabilities and misconfigurations.
- Produce actionable fixes with minimal false positives.
- Keep output high signal: clear rationale, clear evidence, concrete remediation steps.

## Start Here

### Human Operator Path

1. Read `playbooks/how_to_assess_local_network_risk_non_destructively.md`.
2. Read `references/cve_research_and_remediation_source_map.md`.
3. Choose run profile: `Observe`, `Validate`, or `Adversarial-safe`.
4. Use report templates in `templates/` and keep all evidence in `artifacts/<run_id>/...`.

### Agent Path

1. Load this README plus:
   - `playbooks/how_to_assess_local_network_risk_non_destructively.md`
   - `references/cve_research_and_remediation_source_map.md`
   - `templates/homelab_risk_report.md`
   - `templates/homelab_findings.json`
   - `templates/homelab_approvals.md`
2. Enforce non-negotiable safety and approval gates before active checks.
3. Follow run artifact layout exactly and never invent schema fields or enum values.
4. Use parser helpers:
   - `scripts/extract_nmap_live_hosts.py`
   - `scripts/extract_nmap_open_ports.py`

## Core Workflow

Use this lifecycle for each run:

1. Asset inventory.
2. Automated and targeted scanning.
3. Risk prioritization.
4. Remediation recommendation.
5. Verification and closure.

## Safety and Autonomy Model

- Default autonomy model is human-in-the-loop.
- Passive discovery and research can run automatically.
- Active probing requires explicit user approval per run or profile.
- Potentially disruptive checks are disabled by default.
- All automation must be auditable with logs and reproducible command traces.

### Autonomy Profiles (Accepted)

- `Observe` (default): passive inventory plus risk enrichment only.
- `Validate`: non-destructive active checks; explicit approval required per run.
- `Adversarial-safe`: deeper non-destructive probing; explicit target allowlist and second confirmation required.

## Outputs and Evidence Contract

- Human-readable output: `report.md`.
- Machine-readable output: `findings.json` (automation/history support).
- Approval trace output: `approvals.md`.

Required per-finding baseline fields:

- `asset`
- `service_or_exposure`
- `evidence`
- `reference` (CVE/CWE when available)
- `confidence`
- `impact`
- `recommended_fix`
- `priority`
- `effort`
- `retest_step`

## Repository Guide

- `playbooks/`: step-by-step operational workflows.
- `references/`: source hierarchies and supporting security methodology.
- `templates/`: report/schema templates used by humans and agents.
- `scripts/`: deterministic parsing/helpers used by playbooks.
- `journal/`: daily work log entries.
- `plans/`: plan lifecycle files (`future`, `current`, `past`).
- `kanban/`: lightweight task board state.

## v1 Scope

- Local asset and service discovery.
- Risk enrichment from known-vulnerability intelligence.
- Non-destructive active checks under explicit user control.
- Prioritized hardening recommendation generation.
- Repeatable markdown reporting with evidence and remediation steps.

## Explicit Non-Goals

- No exploit execution.
- No persistence, lateral movement, or destructive testing.
- No offensive automation beyond safe validation checks.

## Integration Boundaries

- Cloud API integrations are deferred by default.
- Ticketing integrations are deferred by default.
- Both remain optional v2 capabilities.

## Initial Spec Assertions (Normative)

1. The project exists to defend personal networks in an era of rapidly advancing AI-enabled attack capability.
2. The primary user is a home operator with a long-lived homelab and mixed-generation hardware/software.
3. The framework will discover and inventory local-network devices, services, and exposed interfaces.
4. The framework will build and maintain a risk profile for each observed asset and for the network as a whole.
5. The core output is a concrete, prioritized list of hardening recommendations and risk warnings the user may not already know.
6. The framework will proactively research known vulnerabilities and risks relevant to detected versions, configurations, and exposures.
7. Active validation is allowed only when it is non-destructive and does not execute exploit payloads.
8. A user-optional adversarial "red-team mode" will increase depth of vulnerability discovery but will remain non-destructive.
9. Exploitation is out of scope for all modes, including red-team mode.
10. The framework is focused specifically on local networks and homelabs, including environments with VPNs, offsite backups, and limited cloud-connected infrastructure.
11. The project is not a general-purpose security agent framework.
12. The implementation format will be markdown specs/playbooks plus scripts and tool wrappers (for example, Nmap).
13. The default autonomy model will be human-in-the-loop.
14. Passive discovery and research can run automatically.
15. Active probing requires explicit user approval per run or profile.
16. Potentially disruptive checks are disabled by default.
17. Every automated action must be auditable through logs and reproducible command traces.
18. Findings will use a standard evidence format with both human-readable and machine-readable outputs.
19. The default human-readable output will be markdown reports; optional JSON output will support automation and future integrations.
20. Each finding record will include asset identifier, observed service or exposure, supporting evidence, mapped CVE or CWE when available, confidence score, impact summary, recommended remediation, and remediation priority plus effort estimate.
21. Cloud APIs and ticketing integrations are not required for v1; they are optional later for users who run hybrid homelabs or want workflow export.
22. Success for the first major milestone is maximizing high-confidence identification of real vulnerabilities and misconfigurations with actionable fixes.
23. Quality is defined by signal over noise: fewer false positives, clear rationale, and recommendations that can be applied by a homelab operator.

## Initial Decision Records

### DR-001: Autonomy Profiles

- Status: Accepted
- Decision:
  - `Observe` (default): passive inventory plus risk enrichment only.
  - `Validate`: non-destructive active checks; explicit approval required per run.
  - `Adversarial-safe`: deeper non-destructive probing; explicit target allowlist and second confirmation required.
- Rationale:
  - Maximizes safety for home environments.
  - Preserves user control over noisy or sensitive checks.
  - Enables progressive depth without enabling exploitation.

### DR-002: Findings Evidence Format

- Status: Accepted
- Decision:
  - Produce `report.md` for human actionability.
  - Produce `findings.json` for structured automation/history.
  - Required per-finding fields: `asset`, `service_or_exposure`, `evidence`, `reference` (CVE/CWE when available), `confidence`, `impact`, `recommended_fix`, `priority`, `effort`, `retest_step`.
- Rationale:
  - Markdown keeps output readable for homelab operators.
  - JSON enables reproducibility, diffing, and future integrations.
  - Required fields enforce consistent quality and remediation clarity.

### DR-003: v1 Integration Boundaries

- Status: Accepted
- Decision:
  - Cloud API integrations: deferred by default.
  - Ticketing integrations: deferred by default.
  - Both remain optional v2 capabilities.
- Rationale:
  - Keeps v1 focused on local-network risk discovery and hardening.
  - Reduces implementation complexity and dependency surface.
  - Avoids workflow overhead for solo users.

### DR-004: Mission Statement

- Status: Accepted
- Decision:
  - `flatline-construct is a personal homelab defense framework that discovers attack surface, identifies likely vulnerabilities without exploitation, and produces prioritized hardening actions.`
- Rationale:
  - Anchors scope around defense and remediation.
  - Explicitly excludes exploit-driven goals.
  - Matches primary user and expected output.
