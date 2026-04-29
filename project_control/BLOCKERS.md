# Blockers

Blocking questions and decisions go here. These items should stop autonomous progress until a human resolves them.

## Open Blockers

### 2026-04-28 05:10 UTC - OpenAI API rate limit on --cycle

Status: resolved
Severity: non-critical
Source: Project Autopilot
Resolved: 2026-04-29
Resolution: Historical blocker. Root cause was identified as OpenAI API billing/quota balance, not a Project Autopilot code failure. Project Autopilot now handles 429 cleanly and local-plan/dry-run remain available.

Question or blocker:
OpenAI API `--cycle` returned HTTP 429 (Too Many Requests) during earlier testing. The supervisor planning cycle cannot complete until API billing, quota, or rate limits are verified.

This does NOT block:
- `--dry-run` mode (no API call).
- `--local-plan` mode (no API call).
- Claude Code builder workflow (uses local fallback plan).
- `--doctor` and `--status` modes.

Recommended action:
Verify OpenAI API billing and quota at platform.openai.com. Confirm the API key has access to the configured models (gpt-5.4-mini, gpt-5.4, gpt-5.5). Retry `--cycle` once resolved.

## Format

```md
### YYYY-MM-DD HH:MM - Short title

Status: open
Severity: blocking
Source: agent | builder | qa | human

Question or blocker:
...

Recommended action:
...
```

### 2026-04-28 05:36 UTC - Autopilot blocked: MissingOpenAICredentials

Status: resolved
Severity: blocking
Source: Project Autopilot
Resolved: 2026-04-29
Resolution: Historical blocker. Root cause was an empty local environment override causing OPENAI_API_KEY to be unavailable. Project Autopilot now reports missing credentials without printing secret values and falls back to local planning.

Question or blocker:
MissingOpenAICredentials
OPENAI_API_KEY is missing

Failure log:
logs\mira_autopilot_failure_20260428_053643.md

Recommended action:
OpenAI supervisor unavailable. A local fallback plan has been generated. Resolve the underlying issue (billing, quota, credentials) when convenient.

### 2026-04-28 05:39 UTC - Autopilot blocked: MissingOpenAICredentials

Status: resolved
Severity: blocking
Source: Project Autopilot
Resolved: 2026-04-29
Resolution: Historical duplicate of the local environment OPENAI_API_KEY issue. Kept for audit history, but no longer blocks local planning or product validation tooling.

Question or blocker:
MissingOpenAICredentials
OPENAI_API_KEY is missing

Failure log:
logs\mira_autopilot_failure_20260428_053911.md

Recommended action:
OpenAI supervisor unavailable. A local fallback plan has been generated. Resolve the underlying issue (billing, quota, credentials) when convenient.

### 2026-04-29 02:04 UTC - Post-builder QA: HUMAN_DECISION_REQUIRED

Status: parked
Severity: blocking
Source: Project Autopilot post-builder QA
Parked: 2026-04-29
Reason: Superseded by the 2026-04-29 02:31 UTC backend validation post-builder blocker, which captures the current manual Supabase verification requirement.

Question or blocker:
HUMAN_DECISION_REQUIRED

Post-builder log:
logs\mira_post_builder_20260429_020431.md

Recommended action:
Get human decision before more builder work.

### 2026-04-29 02:31 UTC - Post-builder QA: HUMAN_DECISION_REQUIRED

Status: parked
Severity: blocking
Source: Project Autopilot post-builder QA
Parked: 2026-04-29
Reason: Superseded by the later post-builder run after dependency installation and final validation gates.

Question or blocker:
HUMAN_DECISION_REQUIRED

Post-builder log:
logs\mira_post_builder_20260429_023122.md

Recommended action:
Get human decision before more builder work.

### 2026-04-29 02:39 UTC - Post-builder QA: HUMAN_DECISION_REQUIRED

Status: open
Severity: blocking
Source: Project Autopilot post-builder QA

Question or blocker:
HUMAN_DECISION_REQUIRED

Post-builder log:
logs\mira_post_builder_20260429_023939.md

Recommended action:
Get human decision before more builder work.
