# Project Autopilot — VPS Runner Plan

**Status:** Planning / Not yet deployed  
**Last updated:** 2026-04-30  
**Target host:** DigitalOcean Amsterdam 3 — 178.62.200.189

---

## 1. VPS Purpose

The VPS runner provides:
- A persistent, always-on execution environment (when enabled)
- A staging ground for testing autonomous cycles before full cloud adoption
- A Telegram notification relay
- An evidence log archive outside the main git repo

The VPS is NOT the primary execution environment until local cycles have proven stable for 30+ days.

---

## 2. Isolation Strategy

The existing project at `/root/bot/` must never be touched by Autopilot.

Isolation rules:
- Autopilot runs under a separate Linux user (`autopilot`)
- All Autopilot files live in `/home/autopilot/` or `/root/autopilot/` (never inside `/root/bot/`)
- Separate Python virtualenv (never shared with `/root/bot/`)
- Separate `.env` file (never read `/root/bot/.env`)
- Separate systemd service name prefix (`autopilot-*`, never `bot-*`)
- Separate log directory
- Separate git clone of the MIRA repo

If there is any doubt about isolation, err on the side of not running.

---

## 3. Directory Layout

```
/home/autopilot/              ← Autopilot Linux user home
  .env                        ← Autopilot-only secrets (NOT /root/bot/.env)
  repos/
    mira-autopilot/           ← git clone of MIRA repo (autopilot branch)
      project_control/        ← policy docs, task queue
      project_autopilot/      ← orchestrator code
      agent/                  ← Claude Agent SDK stubs
  venv/                       ← isolated Python virtualenv
  evidence/                   ← append-only evidence logs
    YYYY-MM-DD/
      cycle_<uuid>.json
  logs/
    autopilot.log             ← rotating log file
    error.log
  run/
    .halt                     ← emergency stop flag
    .run.lock                 ← prevents concurrent execution
    last_cycle.json           ← summary of most recent cycle
```

Never create files in `/root/bot/`, `/root/bot/.env`, or any path that could interfere with existing project.

---

## 4. Linux User Strategy

Create a dedicated `autopilot` user:

```bash
# Future deployment command (do not run yet)
adduser --disabled-password --gecos "" autopilot
usermod -aG sudo autopilot  # only if needed for specific commands
```

Why a separate user:
- Process isolation (if autopilot crashes, /root/bot is unaffected)
- File permission boundaries
- Easier to audit what autopilot wrote
- Can be disabled independently: `usermod -L autopilot`

The `autopilot` user should have no write access to `/root/bot/`.

---

## 5. SSH / Security Notes

- SSH key-based auth only (password auth should already be disabled)
- Use a dedicated deploy key for the MIRA repo (read-only clone)
- Autopilot SSH key stored in `/home/autopilot/.ssh/` only
- Never store autopilot SSH private key in the repo or in CI secrets
- Check open ports before deploying: `ss -tlnp`
- Autopilot runner should not open new ports
- If a webhook receiver is needed in future, use a non-root port (>1024)

Firewall (UFW) rules to verify before VPS deployment:
```
ufw status verbose
# Ensure only 22 (SSH), 80, 443 are open
# Autopilot does not need additional ports in initial phases
```

---

## 6. Python venv Strategy

```bash
# Future setup (do not run yet)
python3 -m venv /home/autopilot/venv
source /home/autopilot/venv/bin/activate
pip install -r /home/autopilot/repos/mira-autopilot/requirements.txt
```

Rules:
- Never use system Python for autopilot
- Never install autopilot packages into `/root/bot/` venv
- Pin all dependencies in `requirements.txt`
- Upgrade dependencies only intentionally, never auto-upgrade

---

## 7. Git Clone / Worktree Strategy

Initial clone (future):
```bash
# Future deployment (do not run yet)
cd /home/autopilot/repos
git clone git@github.com:<org>/mira.git mira-autopilot --branch main
```

Worktree strategy for parallel agent execution:
- Each agent task gets its own git worktree
- Worktrees live in `/home/autopilot/repos/worktrees/<task-id>/`
- Worktree is created fresh for each task, deleted after merge or abandonment
- Never share a worktree between two running agents
- See `AUTOPILOT_WORKTREE_SANDBOX_STRATEGY.md` for full rules

Git pull policy:
- Pull is automatic at start of each cycle
- If pull fails or produces conflicts: write HALT file, send Telegram alert, stop
- Never force-pull or reset --hard without human approval

---

## 8. Logs / Evidence Directory

```
/home/autopilot/evidence/
  YYYY-MM-DD/
    cycle_<uuid>.json         ← per-cycle evidence record
    agent_call_<uuid>.json    ← per-agent-call record

/home/autopilot/logs/
  autopilot.log               ← rotating, max 50MB, 7-day retention
  error.log                   ← errors only, max 10MB, 30-day retention
```

Log rotation with logrotate:
```
/home/autopilot/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 0640 autopilot autopilot
}
```

Evidence is append-only. Logs are rotated. Evidence is never deleted.

---

## 9. Systemd Service Future Plan

Service name: `autopilot-runner.service`  
Prefix rule: always `autopilot-*` to avoid collision with `bot-*` services.

Future service file (do not create yet):
```ini
[Unit]
Description=Project Autopilot Runner
After=network.target

[Service]
Type=simple
User=autopilot
WorkingDirectory=/home/autopilot/repos/mira-autopilot
Environment="PATH=/home/autopilot/venv/bin:/usr/bin:/bin"
EnvironmentFile=/home/autopilot/.env
ExecStart=/home/autopilot/venv/bin/python -m project_autopilot.run
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
```

Service must remain disabled (`systemctl disable autopilot-runner`) until:
- Local cycles have run cleanly for 30+ days
- Budget caps are proven to work
- HALT file behavior is tested
- Telegram alerts are confirmed working

---

## 10. Scheduler Future Plan

The VPS scheduler is disabled for the same reason as the local scheduler:  
**Autonomous cycles must not start until the system is boringly reliable.**

Scheduler activation criteria (all must be met):
1. Local dry-run cycles: 30+ consecutive clean runs
2. VPS manual trigger: 10+ consecutive clean runs
3. Budget caps: tested and verified to halt correctly
4. HALT file: tested and verified to stop all processes
5. Telegram alerts: confirmed delivery on error conditions
6. Human sign-off: explicit written approval in project_control

When eventually enabled:
- Start at minimum 4-hour interval
- Never decrease interval without human approval
- Always check HALT file at cycle start

---

## 11. HALT File Behavior

HALT file location: `/home/autopilot/run/.halt`

Rules:
- Any agent process checks for this file before taking any action
- If file exists: log reason, send Telegram alert, exit immediately
- HALT file is written by: budget cap breach, unhandled exception, git conflict, policy gate failure
- HALT file is removed only by: human, explicitly, after reviewing the cause
- HALT file content: human-readable reason for halt

```python
# Required in every agent cycle (pseudocode)
HALT_FILE = Path("/home/autopilot/run/.halt")
if HALT_FILE.exists():
    reason = HALT_FILE.read_text()
    telegram_alert(f"HALT file found: {reason}. Aborting.")
    sys.exit(1)
```

---

## 12. Run Lock Behavior

Lock file location: `/home/autopilot/run/.run.lock`

Rules:
- Written at start of each cycle with: pid, start_time, task_id
- Removed at end of cycle (success or failure)
- If lock exists at cycle start: check if PID is alive
  - If alive: another cycle is running — abort silently
  - If dead: stale lock — remove and continue (log the stale lock)
- Lock is never held across a HALT condition

```python
# Lock file content format
{
  "pid": 12345,
  "started": "2026-04-30T10:00:00Z",
  "task_id": "TASK-042",
  "cycle_id": "uuid"
}
```

---

## 13. Budget Caps

VPS runner enforces the same budget caps as local:

| Agent | Daily cap | Per-call cap |
|-------|-----------|-------------|
| Claude Agent SDK | $5.00 | $0.50 |
| Codex | $5.00 | $1.00 |
| Combined daily | $8.00 | — |

Implementation:
- Budget state stored in `/home/autopilot/run/budget_state.json`
- Reset at midnight UTC
- If cap breached: write HALT file immediately, send Telegram, abort cycle

---

## 14. Telegram Escalation

Telegram bot token and chat ID stored in `/home/autopilot/.env` only.  
Never in git, never in shared config files.

Alert types from VPS:
| Event | Priority |
|-------|---------|
| Cycle started | INFO |
| Cycle completed (summary) | INFO |
| Policy gate blocked action | WARNING |
| Budget cap approaching (80%) | WARNING |
| Budget cap exceeded | CRITICAL |
| HALT file written | CRITICAL |
| Unhandled exception | CRITICAL |
| Agent call failed | ERROR |
| Git pull conflict | ERROR |
| Lock file stale | WARNING |

Message format:
```
[AUTOPILOT VPS] {PRIORITY} | {timestamp}
{event_description}
Cycle: {cycle_id}
Task: {task_id}
```

---

## 15. What Not to Enable Yet

| Feature | Reason to wait |
|---------|---------------|
| Systemd autostart | Scheduler not yet validated |
| Live Supabase access from VPS | RLS audit not complete |
| Auto-merge on VPS | Permanently prohibited |
| Codex execution on VPS | Local integration not proven |
| Telegram approval bot | Phase 2 feature |
| VPS scheduler | 30+ clean local cycles required first |
| VPS worktree push | Only after GitHub Actions plan validated |

---

## 16. Step-by-Step Future Deployment Checklist

This checklist is for future reference only. Do not execute yet.

### Pre-deployment
- [ ] Local cycles clean for 30+ consecutive runs
- [ ] Budget cap code tested locally
- [ ] HALT file behavior tested locally
- [ ] Telegram alerts tested locally
- [ ] Human approval: written sign-off in project_control

### VPS setup
- [ ] SSH to VPS as root
- [ ] `ss -tlnp` — verify no unexpected ports open
- [ ] `ls /root/bot/` — confirm existing project still intact (read-only check)
- [ ] Create `autopilot` user
- [ ] Create `/home/autopilot/` directory structure
- [ ] Create isolated `.env` (never copy from /root/bot/.env)
- [ ] Test Python venv creation
- [ ] Clone MIRA repo with read-only deploy key
- [ ] Run `python -m project_autopilot.run --dry-run` manually
- [ ] Verify HALT file stops execution
- [ ] Verify Telegram alert delivered
- [ ] Verify budget cap halts correctly
- [ ] Verify evidence file written correctly

### First live run
- [ ] Enable manually triggered run only (no scheduler)
- [ ] Run single cycle manually
- [ ] Review evidence log
- [ ] Review Telegram alert
- [ ] Confirm no interference with /root/bot/
- [ ] Human signs off in project_control

### Scheduler activation (separate checklist, future)
- [ ] 10+ consecutive clean manual VPS runs
- [ ] Written human approval in project_control
- [ ] Create systemd service file (disabled)
- [ ] Test service start/stop manually
- [ ] Enable with 4-hour minimum interval only
