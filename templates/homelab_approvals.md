# Homelab Active-Validation Approvals

Record every active validation request and decision.

## Decision Log

| timestamp_utc | asset | proposed_test | benign_reason | expected_impact | user_response | execution_status | notes |
|---|---|---|---|---|---|---|---|
| 2026-01-01T00:00:00Z | 192.168.1.10 | `openssl s_client -connect 192.168.1.10:443 -brief` | read-only TLS handshake | low | yes | completed | baseline check |

Allowed values:

- `user_response`: `yes` | `no`
- `execution_status`: `completed` | `skipped_no_approval` | `failed_command` | `not_applicable`

Rules:

1. No active command runs without a preceding `yes`.
2. If response is `no`, set `execution_status` to `skipped_no_approval`.
3. Keep exact command strings for reproducibility.
