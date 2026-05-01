# Project Autopilot — VPS Telegram Escalation Plan

**Status:** PREFLIGHT DOCS ONLY — No Telegram integration has been configured.
**VPS IP:** 178.62.200.189 (Amsterdam 3, DigitalOcean)
**Date authored:** 2026-04-30

---

## 1. What Telegram Should Report

Telegram is the primary human-readable channel for Autopilot status during VPS runs. It must provide enough information to answer: "Is the cycle running correctly, and does anything need human attention?"

### 1.1 Mandatory Reporting Events

| Event | When | Message Type |
|---|---|---|
| Cycle started | Beginning of every run | INFO |
| Cycle completed successfully | Clean exit | SUCCESS |
| Cycle completed with warnings | Exit with non-fatal warnings | WARNING |
| Cycle failed | Non-zero exit or unhandled exception | ALERT |
| Human approval required | Gate condition reached | APPROVAL REQUEST |
| Lock file detected (run skipped) | Lock present at start | INFO |
| Unexpected file write detected | Outside designated paths | ALERT |
| Memory or disk threshold exceeded | Resource check fails | ALERT |
| Run duration exceeded expected range | Cycle took too long | WARNING |

### 1.2 Suggested Message Format

Each message should follow this structure:

```
[AUTOPILOT] {STATUS} — {TIMESTAMP_UTC}
Cycle: {cycle_id}
Stage: {current_stage}
{Short description of what happened}
{Action required, if any}
```

Example — success:
```
[AUTOPILOT] SUCCESS — 2026-04-30T14:32:01Z
Cycle: cycle_20260430T143022
Stage: manual_runner_phase
Cycle completed cleanly. 3 decisions made. Evidence at /root/autopilot/evidence/cycle_20260430T143022/
No action required.
```

Example — failure alert:
```
[AUTOPILOT] ALERT — 2026-04-30T14:45:17Z
Cycle: cycle_20260430T144500
Stage: manual_runner_phase
Unhandled exception in research step. Exit code: 1.
ACTION REQUIRED: Check logs at /root/autopilot/logs/manual_run_20260430T144500.log
```

---

## 2. What Telegram Must Never Include

The following must never appear in any Telegram message, under any circumstances.

### 2.1 Absolute Prohibitions

| Category | Examples |
|---|---|
| API keys or tokens | `sk-...`, `Bot123456:...` |
| Database credentials | Supabase URL with key, connection strings |
| Full stack traces with file paths exposing secrets | Any trace that prints env vars |
| User PII | Email addresses, names, identifiers |
| Full SQL query results | Raw DB dumps |
| Private IP addresses or internal network details | Internal routing data |
| Raw LLM prompts containing sensitive context | If prompts reference private data |
| Financial account details | Account IDs, balances |

### 2.2 Why This Matters

Telegram messages are transmitted over the internet and stored on Telegram's servers. Even in a private bot chat, treat every Telegram message as if it could be read by a third party. Secrets in Telegram are secrets exposed.

### 2.3 Safe Alternatives

Instead of including sensitive data, reference the log file path:

BAD: `Error: SUPABASE_KEY=eyJ... returned 401`
GOOD: `Supabase auth failed. See log for details: /root/autopilot/logs/manual_run_20260430T144500.log`

---

## 3. Status Summaries

### 3.1 End-of-Cycle Summary

At the end of each cycle, Telegram receives a structured summary. The summary must be brief (under 20 lines) and human-readable.

Suggested fields:
- Cycle ID
- Start time (UTC)
- End time (UTC)
- Duration (seconds)
- Outcome: SUCCESS / WARNING / FAILURE
- Number of decisions made
- Number of steps completed / total steps
- Any warnings encountered (categories only, no raw data)
- Evidence directory path
- Log file path

### 3.2 Daily Summary (Future — Scheduler Phase)

When the scheduler is active, a daily summary is sent at a fixed time (e.g., 08:00 UTC):
- Cycles run in last 24 hours.
- Success rate.
- Any failures and their cycle IDs.
- Resource usage snapshot.

This feature is disabled during the manual runner phase.

---

## 4. Failure Alerts

### 4.1 What Constitutes a Failure

A failure alert is sent when any of the following occur:
- Python process exits with a non-zero exit code.
- An unhandled exception propagates to the top level.
- A required file or directory is missing at startup.
- A required environment variable is absent (excluding intentionally disabled ones).
- A cycle exceeds the maximum allowed duration (to be defined per project).
- A lock file is stale (older than 2x expected cycle duration).

### 4.2 Failure Alert Contents

A failure alert must include:
- Timestamp (UTC).
- Cycle ID (if available).
- Stage where failure occurred.
- One-line error summary (exception type, not full trace).
- Log file path to review.
- Suggested immediate action.

A failure alert must NOT include:
- Full Python stack trace (may contain file paths with secrets).
- Raw exception message if it contains secrets.
- Any secret values.

### 4.3 Failure Response Protocol

When a failure alert is received:
1. Do not start another cycle.
2. SSH to VPS and review the log file.
3. Identify whether the failure is transient (network blip) or systematic (code bug).
4. If transient: clear lock, run once more, observe.
5. If systematic: stop all runs, fix locally, re-test locally, re-deploy, then re-run on VPS.
6. Document the failure in `project_control/BLOCKERS.md` if it cannot be resolved immediately.

---

## 5. Human Approval Requests

### 5.1 When to Request Approval

Autopilot must request human approval via Telegram when it reaches a gate condition that requires a human decision before proceeding. During the manual runner phase, the human is present in the terminal, so Telegram approval requests are supplementary — not a replacement for direct observation.

Gate conditions that trigger an approval request:
- Before any action that writes to a location outside designated paths.
- Before any action that would make an external API call (if APIs are not disabled by flag).
- Before any action that would modify system configuration.
- Before the first run of a new cycle type or new code path.

### 5.2 Approval Request Format

```
[AUTOPILOT] APPROVAL REQUIRED — 2026-04-30T14:32:01Z
Cycle: cycle_20260430T143022
Gate: G4 — First live-mock run
Proposed action: Run cycle without --dry-run flag.
Dry-run output reviewed: [operator must confirm]
Reply YES to proceed, NO to cancel.
(Operator must act within 5 minutes or cycle will self-cancel.)
```

### 5.3 Approval Mechanism

During manual runner phase:
- The operator approves by typing a command in the terminal (not via Telegram reply).
- Telegram approval requests during this phase are informational — they alert the operator's phone in case they are not watching the terminal.

In a future phase (when unattended), a structured reply mechanism may be implemented. That is out of scope for this document.

---

## 6. No Secrets Policy

This section formalises the no-secrets rule for Telegram.

### 6.1 Code-Level Enforcement

The Autopilot codebase must include a `sanitize_for_telegram(message: str) -> str` function that:
- Strips known secret patterns (regex for `sk-`, `eyJ`, `Bot\d+:`, etc.).
- Replaces them with `[REDACTED]`.
- Is applied to every string before it is sent to Telegram.

### 6.2 Review Requirement

Before enabling Telegram reporting on the VPS, the operator must:
- [ ] Review the `sanitize_for_telegram` function in code review.
- [ ] Run a local test that passes a fake secret string and confirms it is redacted.
- [ ] Confirm the first Telegram message received on VPS does not contain any path or value that hints at secrets.

### 6.3 If a Secret Is Sent

If a secret is accidentally sent to Telegram:
1. Immediately rotate the exposed secret.
2. Delete the Telegram message (Telegram allows deleting sent messages).
3. Audit the sanitize function and fix the gap.
4. Document the incident.

---

## 7. No Spam Policy

### 7.1 Rate Limiting

Telegram must not be flooded with messages. Rate limits:
- Maximum 1 message per 10 seconds from Autopilot.
- Maximum 20 messages per cycle.
- If a cycle would produce more than 20 messages, aggregate them into a summary.

### 7.2 Deduplication

- Do not send the same message twice within the same cycle.
- If an error repeats (e.g., retry loop failing 10 times), send one message with the count: `Step X failed 10 times. Aborting.`

### 7.3 Silent Periods

- Do not send messages for normal, expected intermediate steps.
- Only send messages for: start, end, warnings, failures, and approval requests.
- Do not send a message for every sub-step or log line.

### 7.4 Telegram API Rate Limits

Telegram's Bot API limits messages to approximately 30 per second globally and 20 per minute per chat. The Autopilot Telegram integration must implement exponential backoff and queue messages if the rate limit is hit, rather than dropping them silently.

### 7.5 Test Mode

Before enabling Telegram on the VPS, test the integration locally with a test bot and test chat ID. Confirm:
- [ ] Messages arrive in the correct chat.
- [ ] Sanitization works.
- [ ] Rate limiting works.
- [ ] Format is readable on a mobile screen.
