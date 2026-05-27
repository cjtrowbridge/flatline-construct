# Reference: CVE Research and Remediation Source Map

## Purpose

Provide a strict, reusable source map so agents can research CVEs with low ambiguity and low hallucination risk.

## Lifecycle Backbone

Use this lifecycle for all CVE work:

1. Asset inventory.
2. Automated and targeted discovery/scanning.
3. Risk prioritization.
4. Remediation planning and execution.
5. Verification and closure.

## Homelab Profile (Single Operator)

This framework is optimized for personal homelabs, not enterprise SOC workflows.

Use these defaults unless you intentionally override them:

1. Keep one simple remediation queue (markdown or JSON), not a full ticketing system.
2. Prioritize by exposure and exploitability, not volume of findings.
3. Use short patch windows for edge-facing risk and routine windows for internal-only risk.
4. Prefer actionable fixes and safe mitigations over complex governance artifacts.

Suggested priority bands for homelab operations:

- `P1`: Internet-exposed and KEV-listed, or clear remote-auth-bypass/RCE path.
- `P2`: High-confidence exploitable internal exposure or high-impact misconfiguration.
- `P3`: Hygiene debt, low-confidence findings, or low-impact hardening improvements.

Suggested response windows:

- `P1`: same day when feasible, otherwise within 24-48 hours.
- `P2`: within 7 days.
- `P3`: next maintenance cycle (for example monthly).

## What Is a CVE?

1. CVE is a public identifier system for disclosed vulnerabilities.
2. A CVE ID is the identifier (for example `CVE-2025-12345`).
3. A CVE Record is the vulnerability data attached to that ID.
4. There is one CVE Record per vulnerability in the CVE list.

Primary CVE program sources:

- `https://www.cve.org/About/Overview`
- `https://www.cve.org/about/Process`

## What Is NVD vs CVE vs KEV?

1. CVE Program (`cve.org`) defines and publishes CVE Records.
2. NVD (`nvd.nist.gov`) enriches CVEs with additional analysis such as CVSS, CWE, CPE/configuration data, and tagged references.
3. CISA KEV (`cisa.gov`) identifies CVEs known to be exploited in the wild.

Primary sources:

- CVE: `https://www.cve.org/`
- NVD overview: `https://nvd.nist.gov/vuln`
- NVD detail model: `https://nvd.nist.gov/vuln/vulnerability-detail-pages`
- CISA KEV catalog: `https://www.cisa.gov/known-exploited-vulnerabilities-catalog`

## Term Dictionary (Strict Meanings)

- `affected_range`: exact vulnerable version range stated by vendor/distro advisory.
- `fixed_version`: first version stated as patched by vendor/distro advisory.
- `preconditions`: explicit requirements for exploitation (configuration, auth level, role, exposure).
- `primary_source`: vendor or distro advisory used for affected/fixed truth.
- `secondary_source`: corroborating source such as NVD or KEV.
- `confirmed risk`: target evidence matches affected range and required preconditions.
- `possible risk`: incomplete target evidence or unresolved precondition ambiguity.
- `hygiene finding`: weak posture needing hardening without direct CVE confirmation.

## Blue-Team Default vs Adversarial-Safe Variant

Blue-team default:

1. Coverage-first.
2. Continuously identify exposed assets and vulnerable versions.
3. Prioritize and remediate based on risk and exploitability signals.

Adversarial-safe variant (allowed in this project):

1. Objective-first and path-of-least-resistance focused.
2. Uses deeper reconnaissance and validation to prove exposure pathways.
3. Remains non-exploit and non-destructive.

For personal homelabs, this variant is intended for defensive hardening only:

- discover realistic attacker paths early,
- close high-leverage gaps first,
- avoid any action that could disrupt household services.

Not allowed in this project:

- exploit payload execution,
- persistence,
- lateral movement,
- privilege escalation attempts.

## Source Hierarchy for CVE Assessment

Use this order for every CVE decision:

1. Vendor advisory or vendor security bulletin.
2. OS/distribution advisory for packaged software.
3. NVD CVE detail page (or NVD API) for normalization.
4. CISA KEV status for exploitation prioritization.
5. CERT/CC notes for multi-vendor remediation context when needed.

Source examples:

- NVD CVE detail pattern: `https://nvd.nist.gov/vuln/detail/CVE-YYYY-NNNN`
- NVD API: `https://services.nvd.nist.gov/rest/json/cves/2.0`
- CERT/CC vulnerability notes: `https://www.kb.cert.org/`
- Ubuntu CVE tracker: `https://ubuntu.com/security/cves`
- Debian security tracker: `https://security-tracker.debian.org/`

## Atomic CVE Lookup Procedure (Per CVE ID)

Given `CVE-YYYY-NNNN`, run this exact sequence:

Placeholder rule:

- `CVE-YYYY-NNNN` means a real published CVE ID exactly matching CVE syntax (example: `CVE-2024-6387`).

1. Pull NVD record:

```bash
curl -s "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-YYYY-NNNN" > nvd_CVE-YYYY-NNNN.json
```

2. Pull EPSS score:

```bash
curl -s "https://api.first.org/data/v1/epss?cve=CVE-YYYY-NNNN" > epss_CVE-YYYY-NNNN.json
```

3. Open the KEV catalog page and confirm presence/absence of the CVE:
   - `https://www.cisa.gov/known-exploited-vulnerabilities-catalog`
   - use page search for the CVE ID.
4. Open vendor advisory and extract:
   - affected versions,
   - fixed versions,
   - required preconditions,
   - vendor-recommended workaround (if no patch).
5. If host is distro-packaged, open distro tracker/advisory for same CVE and extract fixed package version.

If any source fetch fails, record `lookup_failed` and do not claim confirmed impact.

## Atomic Field Extraction Rules

Extract these fields exactly once per CVE:

1. `cve_id`
2. `vendor`
3. `affected_range`
4. `fixed_version`
5. `preconditions`
6. `cvss_score`
7. `kev_status` (`listed` | `not_listed`)
8. `epss_probability`
9. `epss_percentile`
10. `primary_fix_url`
11. `secondary_validation_url`

Rules:

1. If two sources disagree, prefer vendor advisory for affected/fixed versions.
2. If version matching is ambiguous, set classification to `possible risk`.
3. Never infer fixed version from CVSS or EPSS values.

## Where to Find How to Test a CVE Safely

1. Vendor advisory first:
   - look for affected scope, preconditions, workaround, detection notes, and validation guidance.
2. NVD references second:
   - follow `Vendor Advisory`, `Patch`, and `Technical Description` links before any other reference types.
3. Product documentation third:
   - use official product docs to derive read-only/protocol-level checks that validate preconditions.
4. Tool documentation fourth:
   - use official docs for each scanner/probe to confirm safety category and behavior before running.

For Nmap-specific checks, verify script category and behavior in official NSE docs:

- NSE categories: `https://nmap.org/nsedoc/categories/`
- Usage and category safety model: `https://nmap.org/nse/nse-usage.html`

Do not treat exploit PoCs as required validation material in this framework.

For exploitability likelihood (prioritization signal only):

- EPSS (FIRST): `https://www.first.org/epss`
- EPSS FAQ: `https://www.first.org/epss/faq`

## Where to Find Proposed Fixes for a CVE

1. Vendor advisory is primary for fixed versions and official mitigation.
2. Distro advisory is primary for package-managed hosts (fixed package version may be backported).
3. NVD reference tags help locate patch and vendor-advisory URLs quickly.
4. KEV provides urgency signal, not patch mechanics.

Fix confirmation order:

1. Confirm target is actually in affected range.
2. Identify official fixed version or vendor-approved mitigation.
3. Map fix to host reality:
   - upstream upgrade path, or
   - distro package update path.
4. Re-run the same benign validation checks used pre-fix.
5. Verify finding state changed from vulnerable/probable to remediated.

Atomic fix selection order:

1. Vendor patch/update.
2. Vendor-approved configuration mitigation.
3. Distro-fixed package update (when package-managed).
4. Temporary exposure reduction (ACL/segmentation/service restriction) until patch.

## Evidence Minimum for Any CVE Claim

Required fields:

- `cve_id`
- `asset`
- `service`
- `detected_version`
- `version_confidence`
- `affected_range`
- `fix_source_url`
- `verification_source_url`
- `preconditions`
- `classification` (`confirmed risk` or `possible risk`)
- `recommended_fix`
- `retest_step`

If `affected_range` or `fix_source_url` is missing, do not mark as `confirmed risk`.

Additional rejection rules:

1. If no reproducible evidence exists on the target asset, classification cannot exceed `possible risk`.
2. If preconditions are unknown, classification cannot exceed `possible risk`.
3. If only third-party blogs mention the issue, do not open a confirmed finding.

## Output Contract (Templates and Field Locks)

Use these templates as canonical output contracts:

1. `templates/homelab_risk_report.md`
2. `templates/homelab_findings.json`
3. `templates/homelab_approvals.md`

Rules:

1. Do not rename required fields from template files.
2. Do not introduce new enum values for `priority`, `classification`, `status`, or `version_confidence`.
3. If evidence is missing, keep the field and set value to `unknown` or `none` as appropriate.
4. Keep all artifact paths relative to the run directory (`artifacts/<run_id>/...`).

Use parser scripts to avoid ad-hoc text parsing:

1. `scripts/extract_nmap_live_hosts.py` for host discovery parsing.
2. `scripts/extract_nmap_open_ports.py` for open-port extraction and host/port maps.

## Prioritization Inputs (Use Together)

1. Asset criticality and exposure.
2. CVSS severity context:
   - FIRST CVSS specification: `https://www.first.org/cvss/specification-document`
   - NVD CVSS notes (`CVSS is not a measure of risk`): `https://nvd.nist.gov/vuln-metrics/cvss`
3. KEV presence (known exploitation evidence).
4. EPSS probability/percentile.
5. Verified preconditions on your environment.

Do not prioritize on CVSS alone.

## Homelab Priority Assignment (Deterministic)

Assign one of three priorities:

1. `P1`:
   - exposed to internet or remote untrusted path, and
   - KEV-listed or strong remote compromise path confirmed.
2. `P2`:
   - internal/VPN reachable with high-confidence vulnerability and meaningful impact.
3. `P3`:
   - low-confidence findings, hygiene issues, or low-impact improvements.

Response window targets:

- `P1`: 24-48 hours.
- `P2`: 7 days.
- `P3`: next maintenance window.

## Hallucination Controls

1. Never claim vulnerability from CVSS score alone.
2. Never claim remediation from a generic "latest available" statement without fixed-version evidence.
3. Never use one secondary database as sole source of truth.
4. Mark uncertainty explicitly when version detection is weak.
5. Prefer `possible risk` over overconfident `confirmed risk` when evidence is incomplete.
