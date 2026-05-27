# Homelab Risk Assessment Report

## Run Metadata

- `run_id`: `YYYY-MM-DD-HH-mm-ss`
- `date`: `YYYY-MM-DD`
- `operator`: `<name_or_id>`
- `profile`: `Observe` | `Validate` | `Adversarial-safe`
- `scope`: `<cidr_or_asset_list>`
- `shell`: `bash` | `powershell`
- `tools_missing`: `<none_or_csv>`

Rule: if a value is unknown, write `unknown` explicitly.

## Executive Summary

| metric | value |
|---|---|
| total_assets_seen | 0 |
| assets_with_open_ports | 0 |
| total_findings | 0 |
| confirmed_risks | 0 |
| possible_risks | 0 |
| hygiene_findings | 0 |
| P1 | 0 |
| P2 | 0 |
| P3 | 0 |

## Findings (Ordered by Priority Then Confidence)

For each finding, use this exact block format:

### `[F-0001] <short_title>`

- `status`: `open` | `mitigated` | `remediated` | `accepted_risk`
- `classification`: `confirmed risk` | `possible risk` | `hygiene finding`
- `priority`: `P1` | `P2` | `P3`
- `asset`: `<ip_or_hostname>`
- `service_or_exposure`: `<service_and_port>`
- `detected_version`: `<version_or_unknown>`
- `version_confidence`: `high` | `medium` | `low` | `unknown`
- `confidence`: `high` | `medium` | `low` | `unknown`
- `reference`: `<CVE/CWE/advisory_or_none>`
- `impact`: `<one_to_three_sentences>`
- `evidence`: `<artifact_path_or_url_list>`
- `recommended_fix`: `<concrete_patch_or_config_change>`
- `effort`: `low` | `medium` | `high`
- `retest_step`: `<exact_command>`
- `notes`: `<optional>`

## Pending Active Validation Approvals

- List tests that were proposed but not yet approved.
- Point to `reports/approvals.md` for all decision records.

## Remediation Plan

| priority | action | owner | target_date | downtime_risk |
|---|---|---|---|---|
| P1 | `<action>` | `<owner>` | `YYYY-MM-DD` | `low`/`medium`/`high` |
| P2 | `<action>` | `<owner>` | `YYYY-MM-DD` | `low`/`medium`/`high` |
| P3 | `<action>` | `<owner>` | `YYYY-MM-DD` | `low`/`medium`/`high` |

## Evidence Index

- `raw/commands.log`
- `raw/host_discovery.nmap`
- `raw/top1000.nmap`
- `parsed/live_hosts.txt`
- `parsed/open_ports_by_host.csv`
- `parsed/host_to_open_ports.txt`
- Any service-specific evidence files used by findings

## Completion Checklist

- [ ] Every finding has required fields.
- [ ] Every active test has explicit approval evidence.
- [ ] No intrusive/destructive checks were run.
- [ ] Every `P1`/`P2` has a concrete remediation action and retest command.
