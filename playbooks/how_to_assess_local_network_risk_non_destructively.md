# Playbook: How to Assess Local Network Risk Non-Destructively

*Status: Draft*

## Objective

Define a repeatable, safety-first workflow for exploring a personal homelab network, identifying exposed services and likely vulnerabilities, and producing actionable hardening recommendations without exploitation or service disruption.

## Lifecycle Backbone

Use this sequence for every assessment run:

1. Asset inventory.
2. Automated and targeted scanning.
3. Risk prioritization.
4. Remediation recommendation.
5. Verification and closure.

## Operating Perspectives

Blue-team default (coverage-first):

1. Broadly identify assets and services in authorized scope.
2. Correlate observed versions/configurations to CVE intelligence.
3. Prioritize and remediate with evidence-backed recommendations.

Adversarial-safe variant (objective-first, still non-exploit):

1. Focus on realistic attack paths and high-value exposure chains.
2. Use deeper read-only validation to reduce false positives.
3. Do not execute exploits or post-exploitation steps.

## Homelab Execution Model

This playbook assumes a single operator (or small household team), not a full enterprise security function.

Practical defaults:

1. Maintain one lightweight vulnerability queue (`report.md` + `findings.json` is enough).
2. Use three priority bands:
   - `P1`: edge-facing and likely exploitable,
   - `P2`: important internal risk needing near-term fixes,
   - `P3`: hygiene improvements.
3. Use simple response windows:
   - `P1` within 24-48 hours when possible,
   - `P2` within 7 days,
   - `P3` in the next regular maintenance window.
4. Prefer mitigations that preserve homelab availability:
   - configuration hardening,
   - access restriction,
   - segmentation,
   - controlled service disablement when necessary.

## Safety Invariants (Non-Negotiable)

1. No exploit payloads.
2. No brute force or credential stuffing.
3. No fuzzing, denial-of-service, or crash-oriented testing.
4. No persistence, lateral movement, or destructive changes.
5. Only authorized targets in the user's own homelab scope.
6. Active tests require explicit user approval before execution.

## Prerequisites

- User-provided network scope (CIDRs, hosts, VLANs, or named assets).
- One assessment shell selected for the run (`bash` or `powershell`) and used consistently.
- User-selected run profile:
  - `Observe` (passive + research only)
  - `Validate` (approved non-destructive probes)
  - `Adversarial-safe` (deeper approved probes, still non-destructive)
- Tool availability (for example `nmap`, `smbclient`, `openssl`, `curl`) where applicable.
- CVE source-map reference loaded:
  - `references/cve_research_and_remediation_source_map.md`

### 0.1 Tool Contract (No Substitution Guessing)

Required tools:

- `nmap`
- `curl`
- `openssl`
- `python`

Recommended tools:

- `jq` (JSON parsing)
- `dig` or `nslookup` (DNS checks)

Optional service-specific tools:

- `smbclient`
- `ssh`
- `snmpwalk`

Tool verification step (run before assessment):

```bash
command -v nmap curl openssl python
command -v jq dig nslookup smbclient ssh snmpwalk
```

```powershell
Get-Command nmap,curl,openssl,python -ErrorAction SilentlyContinue
Get-Command jq,dig,nslookup,smbclient,ssh,snmpwalk -ErrorAction SilentlyContinue
```

Rules:

1. If a required tool is missing, stop and report `blocked_missing_required_tool`.
2. If an optional tool is missing, mark related checks as `skipped_missing_tool`.
3. Do not replace missing tools with unfamiliar alternatives.

### 0.2 Run Artifacts Layout (Mandatory)

Create a unique run id and keep all evidence under one directory:

```bash
run_id="$(date +%Y-%m-%d-%H-%M-%S)"
mkdir -p "artifacts/$run_id/raw" "artifacts/$run_id/parsed" "artifacts/$run_id/reports"
```

PowerShell equivalent:

```powershell
$run_id = Get-Date -Format "yyyy-MM-dd-HH-mm-ss"
New-Item -ItemType Directory -Force -Path "artifacts/$run_id/raw","artifacts/$run_id/parsed","artifacts/$run_id/reports" | Out-Null
```

Command logging setup:

```bash
exec > >(tee -a "artifacts/$run_id/raw/commands.log") 2>&1
set -x
```

```powershell
Start-Transcript -Path "artifacts/$run_id/raw/commands.log" -Append
```

Minimum required files:

- `artifacts/<run_id>/raw/commands.log`
- `artifacts/<run_id>/raw/host_discovery.nmap`
- `artifacts/<run_id>/raw/host_discovery.xml`
- `artifacts/<run_id>/raw/host_discovery.gnmap`
- `artifacts/<run_id>/raw/top1000.nmap`
- `artifacts/<run_id>/raw/top1000.xml`
- `artifacts/<run_id>/raw/top1000.gnmap`
- `artifacts/<run_id>/parsed/live_hosts.txt`
- `artifacts/<run_id>/parsed/open_ports_by_host.csv`
- `artifacts/<run_id>/parsed/host_to_open_ports.txt`
- `artifacts/<run_id>/reports/report.md`
- `artifacts/<run_id>/reports/findings.json`
- `artifacts/<run_id>/reports/approvals.md`

### 0.3 Placeholder Replacement Rules

When command templates use placeholders, substitute exactly as follows:

- `<host>`: one IP or hostname from `artifacts/<run_id>/parsed/live_hosts.txt`.
- `<asset>`: same as `<host>` unless a named asset alias is used in the inventory.
- `<hostname_or_host>`: DNS name if known, otherwise same value as `<host>`.
- `<tls_port>`: a port already observed as open and speaking TLS.
- `<port>`: one open service port for the target host.
- `<comma_separated_open_ports>`: open ports for that host from `artifacts/<run_id>/parsed/host_to_open_ports.txt` (example: `22,80,443`).
- `<relevant_ports>`: specific ports in scope for the check being run.
- `<approved_safe_script_list>`: explicit NSE script names that are documented as safe/discovery.

Never use wildcards for script execution in this workflow (no `*`, no category-wide vuln scans).

### 0.4 Report Template Bootstrap (Mandatory)

Copy canonical templates before writing findings:

```bash
cp templates/homelab_risk_report.md "artifacts/$run_id/reports/report.md"
cp templates/homelab_findings.json "artifacts/$run_id/reports/findings.json"
cp templates/homelab_approvals.md "artifacts/$run_id/reports/approvals.md"
```

```powershell
Copy-Item "templates/homelab_risk_report.md" "artifacts/$run_id/reports/report.md" -Force
Copy-Item "templates/homelab_findings.json" "artifacts/$run_id/reports/findings.json" -Force
Copy-Item "templates/homelab_approvals.md" "artifacts/$run_id/reports/approvals.md" -Force
```

If any template is missing, stop and report `blocked_missing_template`.

### 0.5 Execution Status Vocabulary (Use Only These Values)

- `completed`
- `blocked_missing_required_tool`
- `blocked_missing_template`
- `blocked_no_live_hosts`
- `skipped_missing_tool`
- `skipped_no_approval`
- `failed_command`
- `not_applicable`

## Phase 1: Look Around (Discovery)

Goal: identify what exists, what is reachable, and what appears exposed.

- Build an asset inventory:
  - IP address / hostname / MAC / vendor fingerprint.
  - Device role guess (router, NAS, VM host, camera, printer, IoT, etc.).
- Build an exposure inventory:
  - Open ports and transport protocols.
  - Externally reachable services if the user has edge exposure.
- Record evidence for each observation:
  - command used,
  - timestamp,
  - raw output reference.
- Capture host context for remediation:
  - operating system/distribution,
  - patch/update channel,
  - ownership/criticality tag.

### 1.1 Atomic Discovery Steps

1. Normalize authorized scope into a target list file:
   - `targets.txt` containing one CIDR/host per line.
2. Run host discovery only:

```bash
nmap -sn -n -iL targets.txt -oN "artifacts/$run_id/raw/host_discovery.nmap" -oX "artifacts/$run_id/raw/host_discovery.xml" -oG "artifacts/$run_id/raw/host_discovery.gnmap"
```

3. Build `live_hosts.txt` from host discovery output:

```bash
python scripts/extract_nmap_live_hosts.py "artifacts/$run_id/raw/host_discovery.gnmap" "artifacts/$run_id/parsed/live_hosts.txt"
```

```powershell
python scripts/extract_nmap_live_hosts.py "artifacts/$run_id/raw/host_discovery.gnmap" "artifacts/$run_id/parsed/live_hosts.txt"
```

4. If `artifacts/<run_id>/parsed/live_hosts.txt` is empty, stop and report `blocked_no_live_hosts`.
5. Run baseline TCP exposure scan on live hosts:

```bash
nmap -Pn -n --top-ports 1000 --open -iL "artifacts/$run_id/parsed/live_hosts.txt" -oN "artifacts/$run_id/raw/top1000.nmap" -oX "artifacts/$run_id/raw/top1000.xml" -oG "artifacts/$run_id/raw/top1000.gnmap"
```

6. Build port maps used by later phases:

```bash
python scripts/extract_nmap_open_ports.py "artifacts/$run_id/raw/top1000.xml" "artifacts/$run_id/parsed/open_ports_by_host.csv" "artifacts/$run_id/parsed/host_to_open_ports.txt"
```

```powershell
python scripts/extract_nmap_open_ports.py "artifacts/$run_id/raw/top1000.xml" "artifacts/$run_id/parsed/open_ports_by_host.csv" "artifacts/$run_id/parsed/host_to_open_ports.txt"
```

7. Optional deeper scan (requires explicit approval):

```bash
nmap -Pn -n -p- --open -iL "artifacts/$run_id/parsed/live_hosts.txt" -oN "artifacts/$run_id/raw/full_tcp.nmap" -oX "artifacts/$run_id/raw/full_tcp.xml"
```

8. Record asset inventory table with required columns:
   - `asset_id`, `ip`, `hostname`, `mac_or_unknown`, `role_guess`, `exposure_scope`.

Allowed `exposure_scope` values:

- `internet_exposed`
- `vpn_reachable`
- `internal_only`
- `unknown`

## Phase 2: Identify What You Found

Goal: map each open service to a probable product and version.

- Perform non-destructive service fingerprinting and banner/version collection.
- Capture certainty level:
  - `high` = clear version string from service response.
  - `medium` = inferred from fingerprints/signatures.
  - `low` = only port-level guess.
- Normalize findings into a service record:
  - asset,
  - service/protocol,
  - detected version/build (or unknown),
  - confidence,
  - evidence reference.

### 2.1 Atomic Service Identification Steps

1. Read `artifacts/<run_id>/parsed/host_to_open_ports.txt`.
2. For each line in format `<host>|<comma_separated_open_ports>`, run version detection:

```bash
nmap -Pn -n -sV --version-light -p <comma_separated_open_ports> <host> -oN "artifacts/$run_id/raw/sv_<host>.nmap" -oX "artifacts/$run_id/raw/sv_<host>.xml"
```

3. If TLS is present on a port, collect handshake metadata:

```bash
openssl s_client -connect <host>:<tls_port> -servername <hostname_or_host> -brief < /dev/null > "artifacts/$run_id/raw/tls_<host>_<tls_port>.txt"
```

4. Optional HTTP metadata collection for web services:

```bash
curl -k -I --max-time 10 "https://<host>:<port>/" > "artifacts/$run_id/raw/http_head_https_<host>_<port>.txt"
curl -I --max-time 10 "http://<host>:<port>/" > "artifacts/$run_id/raw/http_head_http_<host>_<port>.txt"
```

5. Set `version_confidence` using strict rules:
   - `high`: explicit version string from banner/protocol response.
   - `medium`: version inferred from fingerprint without explicit version string.
   - `low`: service guessed by port/protocol only.
   - `unknown`: no reliable signal.

6. Never invent a version. Use `unknown` when not explicit.

### 2.2 Automated and Targeted Detection Methods

1. Network/service scanning:
   - version/banner detection,
   - protocol capability checks,
   - configuration posture checks.
2. Authenticated host checks where available:
   - installed package versions,
   - service configuration state relevant to CVE preconditions.
3. Software composition analysis (when local code/repositories are in scope):
   - third-party dependency vulnerability matching for known CVEs.
4. Continuous monitoring inputs:
   - recurring scan cadence,
   - CVE feed/watchlist updates for detected software families.
5. Optional passive external reconnaissance for owned public assets:
   - certificate transparency, DNS exposure, and search-indexed service metadata.

Minimum cadence recommendation:

- `edge-facing assets`: daily quick scan + weekly deep scan.
- `internal assets`: weekly quick scan + monthly deep scan.

## Phase 3: Research Known Risks

Goal: determine whether observed service/version/configuration likely maps to known vulnerabilities or weak security posture.

Use the CVE source map reference as the default rulebook for all CVE research:

- `references/cve_research_and_remediation_source_map.md`

### 3.1 Source Order (Use in This Exact Order)

1. Vendor advisory first (primary truth for affected/fixed versions).
2. OS/distribution security advisory for package-specific patch status.
3. NVD CVE detail for normalization and enrichment.
4. CISA KEV for known exploitation prioritization.
5. Secondary sources only as supplemental context, never as primary proof.

Reference URLs and patterns:

- CVE program overview and process: `https://www.cve.org/About/Overview` and `https://www.cve.org/about/Process`
- NVD CVE detail pattern: `https://nvd.nist.gov/vuln/detail/CVE-YYYY-NNNN`
- CISA KEV catalog: `https://www.cisa.gov/known-exploited-vulnerabilities-catalog`
- NVD API endpoint (optional automation): `https://services.nvd.nist.gov/rest/json/cves/2.0`
- CERT/CC vulnerability notes: `https://www.kb.cert.org/`
- Example distro trackers: `https://ubuntu.com/security/cves` and `https://security-tracker.debian.org/`

### 3.2 Atomic Research Workflow (Per Service)

1. Create a research tuple:
   - `asset`, `service`, `port`, `detected_version`, `version_confidence`, `exposure_scope`.
2. Collect candidate CVEs from vendor advisory pages first.
3. For each candidate CVE, extract and store:
   - affected version range,
   - fixed version(s),
   - exploitation preconditions,
   - impact class (C/I/A),
   - source URL and date accessed.
4. Cross-check the same CVE in NVD:
   - confirm ID consistency,
   - capture CVSS and CWE,
   - capture any affected-product mismatch notes.
5. Check CISA KEV:
   - if present, raise remediation priority.
6. If the host runs distro-packaged software, check distro advisory status:
   - package version backport status may differ from upstream version strings.

Command templates for enrichment:

```bash
# NVD CVE lookup by ID
curl -s "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-YYYY-NNNN" > "artifacts/$run_id/raw/nvd_CVE-YYYY-NNNN.json"

# EPSS lookup by ID
curl -s "https://api.first.org/data/v1/epss?cve=CVE-YYYY-NNNN" > "artifacts/$run_id/raw/epss_CVE-YYYY-NNNN.json"
```

If `jq` is available, parse core fields:

```bash
jq '.' "artifacts/$run_id/raw/nvd_CVE-YYYY-NNNN.json" > /dev/null
jq '.' "artifacts/$run_id/raw/epss_CVE-YYYY-NNNN.json" > /dev/null
```

### 3.3 Exploitability and Risk Prioritization

Use multiple signals together:

1. Exposure context:
   - internet-exposed, VPN-reachable, or internal-only.
2. Vulnerability severity context:
   - CVSS from NVD/FIRST as severity input, not full risk.
3. Exploitation evidence:
   - KEV inclusion (known exploited in the wild).
4. Exploitation likelihood estimate:
   - EPSS probability/percentile as prioritization input.
5. Environment-specific precondition match:
   - only elevate when preconditions are met on the target.

Homelab priority mapping rules:

1. Set `P1` when:
   - `internet_exposed` and KEV-listed, or
   - strong remote compromise path with matched preconditions.
2. Set `P2` when:
   - internal or VPN-reachable with high-confidence vulnerability and meaningful impact.
3. Set `P3` when:
   - low-confidence findings, weak hygiene, or non-urgent hardening.

Response windows:

- `P1`: 24-48 hours.
- `P2`: 7 days.
- `P3`: next maintenance cycle.

### 3.4 Verification Rules (Prevent Hallucination)

1. Never mark a risk as `confirmed` without version/config evidence tied to affected criteria.
2. If version is unknown or weakly inferred, classify as `possible risk`.
3. If advisory requires specific preconditions (for example AD DC role, authentication, specific module), verify those preconditions before confirmation.
4. Do not use blogs, forums, or vulnerability databases as sole evidence.
5. Every finding must cite at least:
   - one primary source (vendor advisory or distro advisory),
   - one secondary corroboration source (NVD or KEV when applicable).

### 3.5 Risk Classification Rules

- `confirmed risk`: service/version/config matches affected criteria and preconditions.
- `possible risk`: partial evidence, missing version certainty, or unverified preconditions.
- `hygiene finding`: weak/legacy config or outdated software without direct CVE confirmation.

### 3.6 Service-Specific Research Guardrails

1. Do not infer vulnerability class from port alone.
2. Confirm service identity and version confidence before CVE matching.
3. Validate vulnerability preconditions from primary sources before claim escalation.
4. Keep checks protocol-aware and read-only in this framework.
5. If preconditions are unknown, classify as `possible risk`.

### 3.7 Evidence Minimums (Per CVE Claim)

Record all fields before reporting:

- `cve_id`
- `asset`
- `service`
- `detected_version`
- `version_confidence`
- `primary_source_url` (vendor/distro advisory)
- `secondary_source_url` (NVD or KEV)
- `affected_range_text`
- `fixed_version_text`
- `preconditions_text`
- `match_reason`
- `classification` (`confirmed risk` or `possible risk`)

If any required field is missing, do not classify as `confirmed risk`.

Allowed classification values only:

- `confirmed risk`
- `possible risk`
- `hygiene finding`

## Phase 4: Propose Benign Validation Tests

Goal: confirm or dismiss possible risk using safe, non-destructive checks only.

Before running any active validation:

1. State exactly what will be tested.
2. State why the test is benign.
3. State expected network/service impact (should be low/read-only).
4. Ask for explicit user approval.

Approval prompt format:

`I found <service/finding> on <asset>. I can run <specific benign test> to verify <risk hypothesis>. This test is read-only and should not disrupt service. Run it? (yes/no)`

Approval evidence requirement:

1. Record approval decision in `artifacts/<run_id>/reports/approvals.md`.
2. Do not run active validation unless explicit `yes` is recorded.

Benign test categories:

- Protocol negotiation checks (supported versions/ciphers/signing modes).
- Read-only metadata queries and capability enumeration.
- Single-attempt auth-policy checks (no brute force).
- TLS handshake/certificate property checks.

Safe command templates (examples, adapt to scope and approval):

```bash
# Service/version fingerprinting (read-only)
nmap -sV -p <relevant_ports> <host>

# Service-specific checks only after confirming script behavior and category docs
nmap -p <relevant_ports> --script <approved_safe_script_list> <host>
```

```bash
# TLS handshake metadata check when TLS endpoint is explicitly in scope
openssl s_client -connect <host>:<tls_port> -servername <hostname_or_host> -brief < /dev/null
```

Never run by default in this workflow:

- `--script vuln`
- `--script intrusive`
- brute-force scripts
- DoS/flood scripts

Approved NSE categories in this framework:

- `safe`
- `discovery`

Validation command safety check:

```bash
nmap --script-help <script_name>
```

Only run scripts explicitly documented as non-intrusive for the intended use.

Never classify a test as benign if it:

- sends malformed payloads,
- repeatedly stresses auth/session setup,
- attempts command execution or file write,
- attempts privilege escalation.

## Phase 5: Report Actionable Remediation

Goal: give the user a prioritized fix list with enough evidence to act immediately.

For each finding, report:

- `finding_id`
- `status`
- `classification`
- `asset`
- `service_or_exposure`
- `detected_version`
- `version_confidence`
- `evidence`
- `reference` (CVE/CWE/advisory when available)
- `confidence`
- `impact`
- `recommended_fix`
- `priority`
- `effort`
- `retest_step`
- `match_reason`
- `preconditions_text`

Allowed output enums:

- `priority`: `P1` | `P2` | `P3`
- `classification`: `confirmed risk` | `possible risk` | `hygiene finding`
- `confidence`: `high` | `medium` | `low` | `unknown`
- `version_confidence`: `high` | `medium` | `low` | `unknown`
- `status`: `open` | `mitigated` | `remediated` | `accepted_risk`
- `effort`: `low` | `medium` | `high`

Recommendation quality bar:

- Must be concrete (specific package/version/config change).
- Must be minimal-risk and realistic for homelab operators.
- Must include verification guidance after remediation.

Homelab report addendum:

- Explicitly mark which actions may cause service interruption.
- Include a low-downtime option when available.
- Include rollback notes for risky upgrades.

### 5.1 Atomic Closure Criteria

A finding can move to `remediated` only when all are true:

1. Fix or mitigation applied and timestamped.
2. Retest command executed successfully.
3. Retest output shows affected condition no longer present.
4. Evidence files linked in `report.md` and `findings.json`.

If any of the above is missing, keep status as `open` or `mitigated`.

## Example Workflow: Open Service With CVE Risk Hypothesis

1. Discovery observes an open service on a host (for example SMB, SSH, HTTP, DNS, VPN, or RDP).
2. Identification fingerprints the service and captures version evidence.
3. Research uses exact source order:
   - vendor advisory,
   - distro advisory (if package-managed),
   - NVD CVE detail,
   - CISA KEV status.
4. Research verifies CVE preconditions for this specific host path before asserting risk.
5. If evidence is incomplete, ask user for approval to run benign validation:
   - protocol negotiation checks,
   - read-only metadata checks,
   - TLS handshake checks only when TLS is part of the affected path.
6. If vulnerable/outdated condition is confirmed, report:
   - what was observed,
   - why it is risky,
   - exact upgrade/configuration recommendation,
   - retest instruction to confirm closure.

## Output Artifacts

- `report.md` initialized from `templates/homelab_risk_report.md`.
- `findings.json` initialized from `templates/homelab_findings.json`.
- `approvals.md` initialized from `templates/homelab_approvals.md`.
- Raw scan/evidence files retained for audit and reproducibility.

## Anti-Patterns

- Running intrusive scripts by default.
- Treating uncertain version guesses as confirmed vulnerabilities.
- Suggesting exploitation to "prove" vulnerability.
- Reporting risks without concrete remediation steps.
- Skipping user consent before active checks.

## Verification

- Every active test in the run has explicit approval evidence.
- No intrusive/destructive categories were used.
- Each finding includes evidence + remediation + retest step.
- Final report clearly separates:
  - confirmed vulnerabilities,
  - probable vulnerabilities needing follow-up,
  - hardening hygiene improvements.

Verification checklist (must pass before run completion):

1. `commands.log` exists and includes all executed commands.
2. Discovery and service-scan raw outputs exist.
3. Every CVE claim has required evidence fields.
4. Every active test has an approval record.
5. Every `P1`/`P2` finding has a concrete remediation action and retest command.
