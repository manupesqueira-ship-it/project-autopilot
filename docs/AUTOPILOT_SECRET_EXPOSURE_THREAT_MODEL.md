# Project Autopilot Secret Exposure Threat Model

**Version:** 1.0
**Date:** 2026-05-01
**Scope:** Analysis of all vectors through which secrets could be exposed in the Project Autopilot system

---

## 1. Environment Files

### 1.1 File Inventory

| File | Contains Secrets | Gitignored | Locations |
|------|-----------------|------------|-----------|
| `.env` | YES — all production secrets | YES | Local dev, VPS `/home/autopilot/.env` |
| `.env.local` | YES — development overrides | YES | Local dev only |
| `.env.example` | NO — template with empty values | NO (committed) | Repository |

### 1.2 Exposure Vectors

| Vector | Risk | Current Control |
|--------|------|-----------------|
| `.env` accidentally committed to git | CRITICAL | `.gitignore` entry |
| `.env` included in agent prompt context | CRITICAL | `env_loader.py` loads to `os.environ`, not file content |
| `.env` readable by other system users | HIGH | File permissions (should be 600) |
| `.env` in VPS backup/snapshot | MEDIUM | DigitalOcean snapshots include filesystem |
| `.env.example` updated with real values | HIGH | Human error — no automated check |
| `.env.local` clobbers production values | MEDIUM | `env_loader.py` skips empty values |
| `.env` copied to worktree | HIGH | Worktrees share repo root, but agents may copy |

### 1.3 Required Controls

- [ ] Pre-commit hook scanning for secret patterns in staged files
- [ ] `.env` file permissions set to `600` on all environments
- [ ] `.env.example` validated to contain only empty/placeholder values
- [ ] VPS snapshots encrypted or secrets excluded
- [ ] Worktree creation script must never copy `.env` files

---

## 2. API Keys

### 2.1 Key Inventory

| Key | Provider | Scope | Rotation Frequency | Last Rotated |
|-----|----------|-------|-------------------|--------------|
| `OPENAI_API_KEY` | OpenAI | Codex + Auditor calls | NOT DEFINED | UNKNOWN |
| `ANTHROPIC_API_KEY` | Anthropic | Claude Agent SDK | NOT DEFINED | UNKNOWN |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase | Full DB access (bypasses RLS) | NOT DEFINED | UNKNOWN |
| `TELEGRAM_BOT_TOKEN` | Telegram | Alert notifications | NOT DEFINED | UNKNOWN |
| `SEEDANCE_API_KEY` | BytePlus | Video generation | NOT DEFINED | UNKNOWN |

### 2.2 Key Exposure Scenarios

| Scenario | Affected Keys | Impact |
|----------|--------------|--------|
| Git commit of `.env` | ALL | Full compromise — all keys in single file |
| Agent prints key in evidence log | Any key loaded in env | Key visible in append-only logs |
| Agent includes key in generated code | Any key in env | Key committed to git via worktree |
| OpenAI API request logged | `OPENAI_API_KEY` | Key in HTTP headers if debug logging enabled |
| Telegram alert contains key | `TELEGRAM_BOT_TOKEN` + any leaked key | Key visible in Telegram chat |
| GitHub Actions log output | Keys in GH Secrets | Secret masking depends on exact string match |
| VPS process listing | Keys in environment | `ps auxe` shows env vars on Linux |
| Core dump / crash report | Keys in memory | Memory dump contains env vars |

### 2.3 Key Compromise Impact

| Key | If Compromised |
|-----|---------------|
| `OPENAI_API_KEY` | Attacker can make API calls, incur costs, access Codex |
| `ANTHROPIC_API_KEY` | Attacker can make Claude API calls, incur costs |
| `SUPABASE_SERVICE_ROLE_KEY` | CRITICAL: Full database access bypassing RLS, read/write all user data |
| `TELEGRAM_BOT_TOKEN` | Attacker can send messages as the bot, read bot messages |
| `SEEDANCE_API_KEY` | Attacker can generate videos, incur costs |

### 2.4 Required Controls

- [ ] Define rotation schedule for all keys (minimum quarterly)
- [ ] Set up API key usage alerts/limits at provider level
- [ ] Use scoped/restricted API keys where providers support them
- [ ] Never pass API keys as command-line arguments (visible in process list)
- [ ] Implement key usage auditing at the orchestrator level

---

## 3. Supabase Service Role Key

### 3.1 Special Risk Profile

The `SUPABASE_SERVICE_ROLE_KEY` deserves dedicated analysis because it **bypasses all Row-Level Security policies**. This makes it the single most dangerous secret in the system.

### 3.2 Current Usage

| Usage | File | Risk |
|-------|------|------|
| Server-side Supabase client | `lib/supabase/server.ts` | Required for server API routes |
| Dev fallback flag | `ALLOW_SUPABASE_ANON_SERVER_FALLBACK` | If enabled, anon key used server-side (dev only) |
| Not used by agents | N/A | Agents have no Supabase access currently |

### 3.3 Exposure Scenarios Specific to Service Role

| Scenario | Consequence |
|----------|-------------|
| Key leaked → attacker calls Supabase REST API | Full read/write to all tables: `users_profile`, `user_assets`, `generations`, etc. |
| Key leaked → attacker accesses storage buckets | Download all user photos, scans, meshes |
| Key used in client-side code by mistake | Key visible in browser DevTools, public |
| Key included in agent prompt | Agent could output it, or AI provider logs it |
| `ALLOW_SUPABASE_ANON_SERVER_FALLBACK=true` in prod | Server uses anon key — if RLS disabled, same as service role |

### 3.4 Required Controls

- [ ] Service role key must NEVER appear in client-side bundles (`NEXT_PUBLIC_` prefix forbidden)
- [ ] `lib/supabase/env.ts` must validate service role key is not in public env vars
- [ ] `ALLOW_SUPABASE_ANON_SERVER_FALLBACK` must be `false` or absent in production
- [ ] Agent prompts must be scanned for Supabase key patterns (`sbp_`, `eyJ`)
- [ ] Enable RLS on all tables so even service role key compromise has limited blast radius with proper policies
- [ ] Set up Supabase audit logging to detect unauthorized access

---

## 4. Log Exposure

### 4.1 Log Locations

| Log Type | Location | Contains Secrets? | Access Control |
|----------|----------|-------------------|----------------|
| Evidence logs | `evidence/` | SHOULD NOT | Append-only policy |
| Agent stdout/stderr | Console / redirected | POSSIBLE | Process-level |
| Cost controller logs | `project_autopilot/` | NO | Filesystem |
| GitHub Actions logs | GitHub UI | SHOULD NOT (masked) | Repo access |
| VPS systemd journal | `journalctl` | POSSIBLE | VPS user access |
| Telegram messages | Telegram chat | SHOULD NOT | Chat access |
| Next.js server logs | Console / Vercel | POSSIBLE | Deployment platform |

### 4.2 Log Leakage Scenarios

| Scenario | Risk |
|----------|------|
| Agent writes secret to evidence log | HIGH — logs are append-only, secret persists |
| `env_loader.py` debug mode prints values | HIGH — all secrets visible in console |
| API call error includes auth header | MEDIUM — error messages may contain `Authorization: Bearer sk-...` |
| Subprocess stderr captures secret | MEDIUM — child process may echo env vars |
| `secret_status.py` bug exposes values | HIGH — designed to hide values but code error could reveal |
| Stack trace includes env var values | MEDIUM — Python tracebacks can include local variables |

### 4.3 Required Controls

- [ ] All log writes must pass through a redaction filter before disk/network
- [ ] `secret_status.py` must use `PRESENT_VALUE_HIDDEN` pattern (currently implemented)
- [ ] Evidence logs must be scanned for secret patterns after each write
- [ ] GitHub Actions must use `::add-mask::` for all secret values
- [ ] Telegram alert messages must never include raw error output
- [ ] Stack traces in production must be sanitized before logging
- [ ] VPS journal access restricted to `autopilot` user only

---

## 5. Prompt Pack Exposure

### 5.1 What Are Prompt Packs?

Prompt packs are bundled collections of project context, task definitions, and agent instructions assembled by the orchestrator before sending to AI providers.

### 5.2 Prompt Pack Content Risks

| Content Type | Secret Risk | Mitigation |
|-------------|-------------|------------|
| Task descriptions | LOW | Human-authored, unlikely to contain secrets |
| Source code snippets | MEDIUM | Code may import or reference secret env vars |
| Project control docs | LOW | Policy docs, no secrets expected |
| File paths | LOW | Paths may reveal infrastructure details |
| Git diffs | MEDIUM | Diffs could include `.env` changes if gitignore bypassed |
| Builder reports | MEDIUM | Agent output may contain leaked secrets |
| Error output | HIGH | Error messages may contain secret values |

### 5.3 Prompt Pack Destinations

| Destination | Logging Policy | Data Retention |
|-------------|---------------|----------------|
| OpenAI API | API logs (30 days default, opt-out available) | Per OpenAI data policy |
| Anthropic API | API logs (30 days default, opt-out available) | Per Anthropic data policy |
| Local evidence log | Permanent (append-only) | Until manually deleted |

### 5.4 Required Controls

- [ ] Scan all prompt packs for secret patterns before API submission
- [ ] Opt out of API provider training data usage (both OpenAI and Anthropic)
- [ ] Prompt assembly must exclude `.env` file contents
- [ ] Prompt assembly must exclude `node_modules/`, `venv/`, `.git/`
- [ ] Log prompt pack metadata (size, file count) but not content
- [ ] Implement prompt content hash for deduplication and audit trail

---

## 6. Builder Report Exposure

### 6.1 Builder Report Content

Builder reports are generated by agents after completing tasks. They may contain:
- Code snippets (potentially including secrets)
- File paths and directory structures
- Error messages (potentially including secrets)
- Command output (potentially including env vars)
- Analysis findings (potentially referencing sensitive data)

### 6.2 Exposure Vectors

| Vector | Risk |
|--------|------|
| Report committed to git | MEDIUM — reports are in `project_control/`, which is committed |
| Report included in next cycle's prompt | HIGH — sent to external AI provider |
| Report contains user PII from database | HIGH — if agent accessed Supabase data |
| Report contains API error with auth header | HIGH — secret in error message |
| Report viewable in GitHub UI | MEDIUM — anyone with repo access sees it |

### 6.3 Required Controls

- [ ] Builder reports must be scanned for secret patterns before saving
- [ ] Builder reports must not contain raw error output — summarize only
- [ ] Builder reports must not reference database record contents
- [ ] Reports containing flagged content must be quarantined, not committed
- [ ] Implement report redaction filter matching the same patterns as log redaction

---

## 7. Control Center Exposure

### 7.1 What Is the Control Center?

The Control Center refers to the collection of tools and interfaces used to manage Project Autopilot:
- `project_control/` directory (docs, task queue, agent rules)
- `project_autopilot/` directory (orchestrator code)
- CLI tools for manual agent execution
- Evidence logs viewer
- Cost dashboard (planned)

### 7.2 Control Center Exposure Risks

| Component | Secret Risk | Access Model |
|-----------|-------------|-------------|
| `project_control/` docs | LOW | Git repo access |
| `project_autopilot/` code | LOW (code, not secrets) | Git repo access |
| CLI tool output | MEDIUM | Local terminal |
| Evidence viewer | MEDIUM | Filesystem access |
| Cost dashboard | LOW | Planned, no implementation |
| VPS management SSH | HIGH | SSH key access |
| Supabase dashboard | CRITICAL | Supabase account credentials |
| GitHub repo settings | HIGH | GitHub account credentials |

### 7.3 Required Controls

- [ ] All CLI tools must use `secret_status.py` pattern — never print secret values
- [ ] Evidence viewer must redact secret patterns in display
- [ ] VPS SSH access limited to specific IP allowlist
- [ ] Supabase dashboard access uses MFA
- [ ] GitHub repo uses branch protection and required reviews
- [ ] No secrets stored in `project_control/` or `project_autopilot/` directories

---

## 8. Redaction Requirements

### 8.1 Mandatory Redaction Patterns

All output paths (logs, reports, prompts, alerts, CLI output) MUST redact the following patterns:

| Pattern | Type | Replacement |
|---------|------|-------------|
| `sk-[a-zA-Z0-9]{20,}` | OpenAI API key | `[REDACTED:OPENAI_KEY]` |
| `sk-ant-[a-zA-Z0-9-]{20,}` | Anthropic API key | `[REDACTED:ANTHROPIC_KEY]` |
| `sbp_[a-zA-Z0-9]{20,}` | Supabase key | `[REDACTED:SUPABASE_KEY]` |
| `eyJ[a-zA-Z0-9_-]{50,}` | JWT token | `[REDACTED:JWT]` |
| `[0-9]{8,10}:AA[a-zA-Z0-9_-]{30,}` | Telegram bot token | `[REDACTED:TELEGRAM_TOKEN]` |
| `ghp_[a-zA-Z0-9]{30,}` | GitHub personal access token | `[REDACTED:GITHUB_PAT]` |
| `ghs_[a-zA-Z0-9]{30,}` | GitHub app token | `[REDACTED:GITHUB_APP]` |
| `AKIA[A-Z0-9]{16}` | AWS access key | `[REDACTED:AWS_KEY]` |
| Exact match of any loaded env secret value | Any secret | `[REDACTED:ENV_VALUE]` |

### 8.2 Redaction Implementation Points

| Output Path | Implementation | Status |
|-------------|---------------|--------|
| Evidence log writes | Redaction filter before `write()` | NOT IMPLEMENTED |
| Builder report saves | Redaction filter before file write | NOT IMPLEMENTED |
| Prompt assembly | Secret pattern scan in `claude_prompt_safety.py` | PARTIAL |
| Telegram alerts | Redaction filter before API call | NOT IMPLEMENTED |
| CLI tool output | `secret_status.py` for env display | IMPLEMENTED |
| GitHub Actions logs | `::add-mask::` for secrets | NOT CONFIGURED |
| VPS systemd journal | Redaction filter in log handler | NOT IMPLEMENTED |

### 8.3 Redaction Testing Requirements

- [ ] Unit tests that attempt to pass each secret pattern through each output path
- [ ] Integration test that runs a full agent cycle with test secrets and verifies no leakage
- [ ] Regex pattern tests against real-world key formats from each provider
- [ ] Edge case tests: partial keys, keys in URLs, keys in JSON, base64-encoded keys
- [ ] Test that redaction doesn't break legitimate output (e.g., JWT-like strings in source code)

### 8.4 Redaction Failures

If redaction fails or a secret is detected in output after the fact:

1. **Immediate:** Rotate the affected secret
2. **If in git:** Remove from history using BFG Repo-Cleaner or `git filter-repo`
3. **If in logs:** Purge affected log entries (exception to append-only policy)
4. **If sent to AI provider:** Cannot be recalled — rotate key, assess exposure window
5. **If in Telegram:** Delete message, rotate bot token
6. **Post-incident:** Add the missed pattern to the redaction filter, add regression test

---

## Appendix: Secret Flow Diagram

```
.env file (disk)
    │
    ▼
env_loader.py → os.environ (memory)
    │
    ├──► agent_loop.py → prompt assembly → AI provider API
    │                         │
    │                         └──► evidence log (disk)
    │
    ├──► cost_controller.py → API calls (Authorization header)
    │
    ├──► claude_runner.py → subprocess env → child process memory
    │
    ├──► telegram alerts → Telegram API (HTTPS)
    │
    └──► secret_status.py → CLI output (PRESENT_VALUE_HIDDEN)

EVERY arrow (──►) is a potential leak point requiring redaction.
```
