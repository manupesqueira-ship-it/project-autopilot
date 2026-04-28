# Blockers

Blocking questions and decisions go here. These items should stop autonomous progress until a human resolves them.

## Open Blockers

### 2026-04-28 05:10 UTC - OpenAI API rate limit on --cycle

Status: open
Severity: non-critical
Source: Project Autopilot

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

Status: open
Severity: blocking
Source: Project Autopilot

Question or blocker:
MissingOpenAICredentials
OPENAI_API_KEY is missing

Failure log:
logs\mira_autopilot_failure_20260428_053643.md

Recommended action:
OpenAI supervisor unavailable. A local fallback plan has been generated. Resolve the underlying issue (billing, quota, credentials) when convenient.

### 2026-04-28 05:39 UTC - Autopilot blocked: MissingOpenAICredentials

Status: open
Severity: blocking
Source: Project Autopilot

Question or blocker:
MissingOpenAICredentials
OPENAI_API_KEY is missing

Failure log:
logs\mira_autopilot_failure_20260428_053911.md

Recommended action:
OpenAI supervisor unavailable. A local fallback plan has been generated. Resolve the underlying issue (billing, quota, credentials) when convenient.
