# Project Autopilot Security Threat Model

**Version:** 1.0
**Date:** 2026-05-01
**Scope:** End-to-end security analysis of the Project Autopilot agent orchestration system

---

## 1. Assets

### 1.1 Critical Assets

| Asset | Classification | Location | Owner |
|-------|---------------|----------|-------|
| `SUPABASE_SERVICE_ROLE_KEY` | SECRET | `.env`, VPS `/home/autopilot/.env` | Infrastructure |
| `OPENAI_API_KEY` | SECRET | `.env`, GitHub Secrets | Infrastructure |
| `ANTHROPIC_API_KEY` | SECRET | `.env`, GitHub Secrets | Infrastructure |
| `TELEGRAM_BOT_TOKEN` | SECRET | `.env` | Infrastructure |
| Production database (Supabase) | CRITICAL | Supabase cloud | Product |
| User PII (`users_profile`, `user_assets`) | CRITICAL | Supabase tables + storage | Product |
| Source code (`master` branch) | HIGH | GitHub, local, VPS clone | Engineering |
| Agent evidence logs | HIGH | `evidence/`, append-only | Operations |
| Cost controller state | MEDIUM | `project_autopilot/` | Operations |

### 1.2 Secondary Assets

| Asset | Classification | Location |
|-------|---------------|----------|
| `TELEGRAM_CHAT_ID` | LOW | `.env` |
| `SEEDANCE_API_KEY` | SECRET | `.env` |
| `NEXT_PUBLIC_SUPABASE_URL` | PUBLIC | `.env`, compiled into client |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | SEMI-PUBLIC | `.env`, compiled into client |
| Builder reports | MEDIUM | `project_control/` |
| Prompt packs / task library | MEDIUM | `project_control/` |
| HALT file | HIGH | repo root |

---

## 2. Trust Boundaries

### 2.1 Boundary Map

```
TRUST LEVEL 0 (HIGHEST): Human operator
  │
  ├─ TRUST LEVEL 1: Local development machine
  │   ├─ Full secrets access
  │   ├─ Direct git push capability
  │   └─ Manual agent trigger
  │
  ├─ TRUST LEVEL 2: Project Autopilot orchestrator
  │   ├─ Reads secrets (env_loader.py)
  │   ├─ Calls external APIs (OpenAI, Anthropic, Telegram)
  │   ├─ Creates git branches and worktrees
  │   ├─ CANNOT merge to master
  │   └─ CANNOT deploy
  │
  ├─ TRUST LEVEL 3: External AI providers
  │   ├─ Codex (OpenAI) — code generation in worktree
  │   ├─ Claude Agent SDK — analysis only
  │   ├─ Claude Code — manual handoff (future)
  │   └─ Receives prompts containing project context
  │
  ├─ TRUST LEVEL 4: VPS execution environment
  │   ├─ Isolated `autopilot` user (not root)
  │   ├─ Separate venv, git clone, .env
  │   ├─ Never touches /root/bot/
  │   └─ SSH key-only access
  │
  ├─ TRUST LEVEL 5: GitHub Actions
  │   ├─ PR-scoped execution
  │   ├─ Repo-scoped secrets (not org-wide)
  │   └─ No merge capability
  │
  └─ TRUST LEVEL 6 (LOWEST): Supabase client (browser)
      ├─ Anon key only
      ├─ RLS enforced (when enabled)
      └─ No server-side operations
```

### 2.2 Critical Boundary Crossings

| Crossing | From | To | Risk |
|----------|------|----|------|
| Prompt submission | Orchestrator | OpenAI/Anthropic API | Data exfiltration via prompt content |
| Worktree code write | Codex output | Local filesystem | Malicious code injection |
| PR creation | Agent branch | GitHub | Untrusted code reaching review |
| Service role query | Server API route | Supabase | RLS bypass, full table access |
| Evidence log write | Agent | Filesystem | Log injection, evidence tampering |
| Telegram alert | Orchestrator | Telegram API | Token exposure, alert spoofing |
| VPS SSH | GitHub Actions | DigitalOcean VPS | Lateral movement risk |

---

## 3. Threat Actors

### 3.1 External Threat Actors

| Actor | Motivation | Capability | Likelihood |
|-------|-----------|------------|------------|
| **Compromised dependency** | Supply chain attack | Code execution via npm/pip | MEDIUM |
| **Malicious AI model output** | Prompt injection | Code generation with backdoors | MEDIUM |
| **GitHub account compromise** | Repo takeover | Full push access, secret theft | LOW |
| **Supabase compromise** | Data theft | User PII, service role escalation | LOW |
| **VPS intrusion** | Lateral movement | Access to bot, secrets, evidence | LOW |
| **Network attacker (MITM)** | Credential theft | Intercept API keys in transit | VERY LOW |

### 3.2 Internal / Accidental Threat Actors

| Actor | Scenario | Impact |
|-------|----------|--------|
| **Misconfigured agent** | Autonomy level escalated without review | Unreviewed code merged |
| **Runaway cost** | Budget cap bypass or misconfiguration | Excessive API spend |
| **Accidental secret commit** | `.env` added to git | All secrets exposed in history |
| **RLS not enabled** | Supabase tables without RLS | Full data access via anon key |
| **HALT file deleted** | Emergency stop mechanism removed | No way to halt runaway agent |

---

## 4. Attack Surfaces

### 4.1 API Key Exposure Surface

- **`.env` file** — contains all secrets; gitignored but present on disk
- **`.env.local`** — development overrides; gitignored
- **Process environment** — secrets loaded into `os.environ` at runtime
- **Agent prompts** — may accidentally include secret values in context
- **Builder reports** — could contain leaked values if agent misbehaves
- **Evidence logs** — append-only but could contain secrets if not filtered
- **GitHub Actions logs** — stdout/stderr could print secrets
- **Telegram messages** — alert payloads could include sensitive data
- **VPS `.env`** — separate copy; if VPS compromised, secrets exposed

### 4.2 Code Execution Surface

- **Codex-generated code** — executes in worktree; could contain malicious logic
- **Claude Agent SDK** — analysis-only mode; shell execution disabled
- **`subprocess` calls** — used in `claude_runner.py`, `claude_sandbox_runner.py`
- **`npm run` commands** — executed during validation; package.json scripts trusted
- **Python `compileall`** — bytecode compilation; limited attack surface
- **Git hooks** — pre-commit hooks execute on commit; could be tampered

### 4.3 Network Surface

- **OpenAI API (HTTPS)** — prompt/response payloads
- **Anthropic API (HTTPS)** — analysis call payloads
- **Telegram Bot API (HTTPS)** — alert notifications
- **Supabase REST API (HTTPS)** — database operations
- **BytePlus/Seedance API (HTTPS)** — video generation
- **GitHub API (HTTPS)** — PR creation, status checks
- **VPS SSH (port 22)** — remote execution
- **VPS HTTP/HTTPS (ports 80, 443)** — if web services exposed

---

## 5. Agent Risks

### 5.1 Agent Autonomy Escalation

| Risk | Current State | Mitigation |
|------|--------------|------------|
| Agent merges to master | BLOCKED — agents cannot merge | Branch protection + human-only merge |
| Agent deploys application | BLOCKED — no deploy capability | Agent rules hard restriction |
| Agent modifies `.env` | BLOCKED — agent rules forbid | File-level restriction in AGENT_RULES.md |
| Agent deletes evidence | BLOCKED — append-only policy | No delete commands allowed |
| Agent bypasses HALT | POSSIBLE — depends on implementation | HALT check at cycle start, not continuous |
| Agent exceeds budget | MITIGATED — cost_controller.py | Daily/cycle/monthly caps enforced |
| Agent creates unauthorized branches | POSSIBLE — git access required for work | Branch naming convention enforced |

### 5.2 Multi-Agent Coordination Risks

- **Race condition:** Two agents modifying same files in separate worktrees
- **Conflicting PRs:** Multiple agents creating PRs that conflict
- **Evidence corruption:** Concurrent writes to evidence logs
- **Run lock bypass:** `.run.lock` not checked atomically
- **Cost double-spend:** Budget checked before call but not atomically deducted

### 5.3 Agent Misbehavior Patterns

- **Hallucinated commands:** Agent generates shell commands not in allowlist
- **Prompt leakage:** Agent includes secrets in generated code or comments
- **Scope creep:** Agent modifies files outside assigned task scope
- **Infinite retry:** Agent retries failed operations without backoff
- **Evidence fabrication:** Agent writes misleading success evidence

---

## 6. Repository Risks

### 6.1 Git-Level Risks

| Risk | Severity | Likelihood |
|------|----------|------------|
| Force push to master | CRITICAL | LOW (branch protection) |
| History rewrite (rebase/amend) | HIGH | LOW (agent rules forbid) |
| Accidental `.env` commit | CRITICAL | MEDIUM |
| Large binary committed | MEDIUM | LOW |
| Merge conflict auto-resolution | HIGH | LOW (no auto-merge) |
| Git hook tampering | HIGH | LOW |
| Worktree left in dirty state | MEDIUM | MEDIUM |

### 6.2 File-Level Risks

- **`project_control/` tampering** — agents modifying their own rules
- **`project_autopilot/` code changes** — agents modifying orchestrator
- **`.gitignore` modification** — could expose secrets or include unwanted files
- **`package.json` script injection** — malicious scripts in npm lifecycle hooks
- **Symlink attacks** — worktree symlinks pointing outside repo

---

## 7. CI/VPS Risks

### 7.1 GitHub Actions Risks

| Risk | Severity | Current State |
|------|----------|--------------|
| Workflow injection via PR | HIGH | No workflows exist yet |
| Secret exfiltration in logs | HIGH | Secrets planned as repo-scoped |
| Third-party action compromise | MEDIUM | No actions configured yet |
| Workflow file modification by agent | HIGH | Agent rules forbid CI changes |
| Self-hosted runner compromise | N/A | Not using self-hosted runners |
| Workflow dispatch abuse | MEDIUM | Manual triggers only (planned) |

### 7.2 VPS Risks (DigitalOcean Amsterdam 3)

| Risk | Severity | Mitigation |
|------|----------|------------|
| Root access from autopilot user | CRITICAL | Separate user, no sudo |
| Lateral movement to `/root/bot/` | CRITICAL | Filesystem isolation, separate user |
| SSH key compromise | HIGH | Deploy key (read-only), key rotation |
| Secrets on disk (`/home/autopilot/.env`) | HIGH | File permissions (600), encrypted at rest |
| Runaway process (CPU/memory) | MEDIUM | systemd resource limits |
| Open ports beyond SSH/HTTP/HTTPS | MEDIUM | UFW firewall, port 22/80/443 only |
| Evidence log tampering on VPS | HIGH | Append-only policy (enforcement TBD) |
| VPS snapshot/backup exposure | MEDIUM | Secrets in snapshots if taken |

---

## 8. Supabase Risks

### 8.1 Authentication & Authorization Risks

| Risk | Severity | Current State |
|------|----------|--------------|
| RLS not enabled on tables | CRITICAL | RLS currently DISABLED in schema |
| Service role key leaked | CRITICAL | Bypasses all RLS, full table access |
| Anon key abuse (no RLS) | HIGH | Without RLS, anon key = full access |
| `ALLOW_SUPABASE_ANON_SERVER_FALLBACK` in prod | HIGH | Dev-only flag, must be removed |
| Storage bucket misconfiguration | HIGH | `user-photos` must be private |
| SQL injection via API routes | MEDIUM | Supabase client parameterizes queries |

### 8.2 Data Exposure Risks

| Table | Data | Risk if Exposed |
|-------|------|-----------------|
| `users_profile` | Height, weight, gender, build | PII exposure, privacy violation |
| `user_assets` | Photos, scans, meshes | Biometric data exposure |
| `generations` | Try-on results | User likeness exposure |
| `events` | Analytics | Usage pattern exposure |
| `sellers` | Brand accounts | Business data exposure |
| `products` | Inventory, pricing | Competitive data exposure |

### 8.3 Agent-Supabase Risks

- **No agent Supabase access currently** — agents do not call Supabase directly
- **Future risk:** If agents gain Supabase access, service role key grants full bypass
- **Migration risk:** Agent-generated SQL migrations could drop tables or alter RLS
- **Backup risk:** Database backups could be accessed if Supabase dashboard compromised

---

## 9. Mitigations

### 9.1 Implemented Mitigations

| Mitigation | Protects Against | Implementation |
|-----------|-----------------|----------------|
| HALT file | Runaway agents | `HALT_AUTOPILOT.md` checked at cycle start |
| Run lock | Concurrent execution | `.run.lock` prevents parallel runs |
| Agent rules (90 hard rules) | Agent misbehavior | `AGENT_RULES.md` enforced by orchestrator |
| Cost controller | Budget overrun | Daily/cycle/monthly caps in `cost_controller.py` |
| Secret status checker | Accidental exposure | `secret_status.py` reports presence, never values |
| Worktree isolation | Code contamination | Each task gets isolated worktree |
| Human-only merge | Unreviewed code | Branch protection, no auto-merge |
| Append-only evidence | Evidence tampering | Policy: logs never deleted |
| Dry-run default | Unintended execution | All execution disabled until explicitly enabled |
| Prompt safety module | Prompt injection | `claude_prompt_safety.py` sanitizes inputs |
| Env loader safeguards | Secret clobbering | Empty `.env.local` values don't overwrite `.env` |
| `.gitignore` for secrets | Accidental commit | `.env`, `.env.local` excluded from git |

### 9.2 Required but Not Yet Implemented

| Mitigation | Priority | Status |
|-----------|----------|--------|
| **Enable RLS on all Supabase tables** | P0 CRITICAL | Candidate policies drafted |
| **Remove `ALLOW_SUPABASE_ANON_SERVER_FALLBACK`** | P0 CRITICAL | Must happen before production |
| **GitHub branch protection rules** | P0 HIGH | Planned, not configured |
| **GitHub Actions workflows** | P1 HIGH | Planned, not created |
| **Secret rotation procedure** | P1 HIGH | No rotation schedule exists |
| **VPS filesystem permission audit** | P1 HIGH | Planned for VPS setup |
| **Atomic budget deduction** | P2 MEDIUM | Current check-then-deduct has race |
| **HALT file integrity monitoring** | P2 MEDIUM | No file watcher exists |
| **Evidence log integrity (checksums)** | P2 MEDIUM | Append-only policy not enforced technically |
| **Git pre-commit secret scanner** | P1 HIGH | No scanner configured |
| **Dependency vulnerability scanning** | P1 HIGH | No automated scanning |
| **Rate limiting on agent API calls** | P2 MEDIUM | Cost cap exists but no per-minute rate limit |

### 9.3 Defense-in-Depth Layers

```
Layer 1: Agent Rules (AGENT_RULES.md)
  └─ 90 hard restrictions on agent behavior

Layer 2: Orchestrator Controls (agent_loop.py)
  ├─ HALT check
  ├─ Run lock
  ├─ Budget enforcement
  └─ Prompt sanitization

Layer 3: Git Controls
  ├─ Branch protection (planned)
  ├─ Worktree isolation
  ├─ No force-push
  └─ Human-only merge

Layer 4: Infrastructure Controls
  ├─ VPS user isolation
  ├─ UFW firewall
  ├─ SSH key-only auth
  └─ Repo-scoped secrets

Layer 5: Database Controls
  ├─ RLS policies (planned)
  ├─ Service role separation
  ├─ Storage bucket ACLs
  └─ No agent DB access (current)

Layer 6: Human Oversight
  ├─ All merges require human
  ├─ All deploys require human
  ├─ Evidence review
  └─ Emergency HALT
```

### 9.4 Incident Response

| Scenario | Immediate Action | Recovery |
|----------|-----------------|----------|
| Secret leaked in git | Rotate all affected keys immediately | `git filter-branch` or BFG to remove from history |
| Agent writes malicious code | Create HALT file, close PR | Review all recent agent PRs |
| VPS compromised | Kill SSH sessions, rotate VPS secrets | Rebuild VPS from scratch |
| Supabase data breach | Rotate service role key, enable RLS | Audit access logs, notify affected users |
| Runaway API spend | Create HALT file, revoke API keys | Review cost_controller.py caps |
| Agent modifies own rules | Revert to last known-good commit | Audit all agent rule changes |

---

## Appendix A: Risk Heat Map

```
              LOW LIKELIHOOD    MEDIUM         HIGH
            ┌─────────────────┬──────────────┬──────────────┐
 CRITICAL   │ VPS root escape │ .env commit  │ RLS disabled │
            │ GitHub takeover │              │ (CURRENT)    │
            ├─────────────────┼──────────────┼──────────────┤
 HIGH       │ Git history     │ Dependency   │              │
            │ rewrite         │ compromise   │              │
            ├─────────────────┼──────────────┼──────────────┤
 MEDIUM     │ Evidence        │ Worktree     │              │
            │ fabrication     │ dirty state  │              │
            ├─────────────────┼──────────────┼──────────────┤
 LOW        │ Telegram spoof  │              │              │
            └─────────────────┴──────────────┴──────────────┘
```

## Appendix B: Review Schedule

- **Weekly:** Review agent evidence logs for anomalies
- **Monthly:** Audit cost controller caps and actual spend
- **Quarterly:** Review and update this threat model
- **On change:** Re-evaluate when new agents, providers, or execution environments are added
- **On incident:** Immediate review and update of affected sections
