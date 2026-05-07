# Project Autopilot — VPS Directory and Service Plan

**Status:** PREFLIGHT DOCS ONLY — No directories have been created on the VPS.
**VPS IP:** 178.62.200.189 (Amsterdam 3, DigitalOcean)
**Date authored:** 2026-04-30

---

## 1. Suggested Directory Layout

The following layout is proposed for the Autopilot deployment. All paths are outside `/root/bot/` and operate under a dedicated Linux user account.

```
/home/autopilot/                         # Home for the autopilot Linux user
├── .env                                 # Secrets file (chmod 600, NOT in git)
│
/root/autopilot/                         # OR: /home/autopilot/autopilot/
│                                        # (Final path decided at deploy time)
├── repo/                                # Git clone of the Autopilot codebase
│   ├── project_autopilot/               # Main Python package
│   ├── agent/                           # Agent modules
│   ├── project_control/                 # Docs (this file lives here)
│   ├── requirements.txt                 # Pinned dependencies
│   ├── pyproject.toml                   # If used
│   ├── .gitignore                       # Must include .env, logs/, evidence/
│   └── ...
│
├── venv/                                # Python virtual environment (NOT in git)
│   ├── bin/
│   │   └── python                       # Always invoke this directly
│   └── lib/
│
├── logs/                                # All run logs
│   ├── manual_run_20260430T120000.log
│   ├── manual_run_20260430T140000.log
│   └── ...
│
├── evidence/                            # Cycle output artifacts
│   ├── cycle_20260430T120000/
│   │   ├── summary.json
│   │   ├── decisions.json
│   │   └── raw_output.txt
│   └── ...
│
├── locks/                               # Run lock files
│   └── autopilot.lock                   # Present = running. Absent = idle.
│
└── archive/                             # Compressed old logs (logrotate future)
    └── ...
```

### 1.1 Path Decision Note

The exact base path (`/root/autopilot/` vs `/home/autopilot/autopilot/`) will be decided at deployment time based on whether the `autopilot` Linux user is created. During the manual runner phase, the operator may use either, but must document the chosen path before running.

### 1.2 Ownership and Permissions

| Path | Owner | Permissions |
|---|---|---|
| `/root/autopilot/` (if root-owned) | root | 750 |
| `/home/autopilot/.env` | autopilot | 600 |
| `repo/` | autopilot (or root during manual phase) | 755 |
| `venv/` | autopilot (or root during manual phase) | 755 |
| `logs/` | autopilot | 750 |
| `evidence/` | autopilot | 750 |
| `locks/` | autopilot | 750 |

---

## 2. Python Virtual Environment

### 2.1 Creation

```bash
# Future command — do not run until ready
cd /root/autopilot/
python3 -m venv venv
```

Confirm the Python version before creating the venv:

```bash
python3 --version
# Expected: 3.12.x or compatible with project requirements
```

### 2.2 Activation for Manual Runs

Do not activate the venv via `source`. Always invoke the venv Python directly:

```bash
/root/autopilot/venv/bin/python --version
/root/autopilot/venv/bin/pip list
```

This avoids contamination from shell state.

### 2.3 Installing Dependencies

```bash
# Future command — do not run until ready
/root/autopilot/venv/bin/pip install --upgrade pip
/root/autopilot/venv/bin/pip install -r /root/autopilot/repo/requirements.txt
```

### 2.4 Pinning

`requirements.txt` must be a fully pinned file (`pip freeze` output), not a loose-version file. This ensures the VPS environment exactly matches the tested local environment.

---

## 3. Git Clone Path

### 3.1 Clone Command (Future)

```bash
# Future command — do not run until ready
git clone https://github.com/<org>/<repo>.git /root/autopilot/repo
```

Or, if using SSH:

```bash
git clone git@github.com:<org>/<repo>.git /root/autopilot/repo
```

### 3.2 Branch Policy

- Clone the specific branch intended for VPS deployment.
- Do not clone `main` unless `main` is explicitly the deployment branch.
- After cloning, confirm the branch: `git -C /root/autopilot/repo branch --show-current`.

### 3.3 Pull Policy During Manual Phase

- Pull updates manually before each manual run.
- Never set up `git pull` on a timer or cron during the manual runner phase.
- After pulling, re-run `pip install -r requirements.txt` if `requirements.txt` changed.
- After pulling, verify no new secrets have been added to tracked files.

### 3.4 No VPS-Side Git Push

The VPS is a read-only consumer of the git repository during the manual runner phase. No commits or pushes should originate from the VPS.

---

## 4. Logs Path

### 4.1 Location

All run logs go to: `/root/autopilot/logs/`

### 4.2 Naming Convention

```
manual_run_YYYYMMDDTHHMMSS.log
```

Example: `manual_run_20260430T143022.log`

### 4.3 Content

Each log file must contain:
- Start timestamp (UTC).
- Python version and venv path used.
- Command line arguments passed.
- Full stdout and stderr of the cycle.
- End timestamp (UTC).
- Exit code.

### 4.4 Secrets in Logs

Logs must never contain:
- API keys or tokens.
- Passwords or secrets.
- Full SQL dumps with PII.

If any of these appear in logs, treat it as a security incident: rotate the exposed secret immediately, then fix the logging code.

### 4.5 Log Review

The operator must read each log file after each manual run during this phase. No exceptions.

---

## 5. Evidence Path

### 5.1 Location

Cycle output artifacts go to: `/root/autopilot/evidence/cycle_YYYYMMDDTHHMMSS/`

### 5.2 Content

Evidence directories should contain structured output from the cycle:
- `summary.json` — High-level cycle outcome (what was decided, what was skipped).
- `decisions.json` — Machine-readable list of decisions made.
- `raw_output.txt` — Unstructured cycle output for debugging.

### 5.3 Retention

- During the manual runner phase, retain all evidence directories.
- After the manual runner phase is complete, archive evidence older than 30 days.
- Evidence directories must not contain secrets.

### 5.4 Local Copy

After each manual run, the operator should copy the evidence directory to their local machine for review:

```bash
# Local command (not on VPS)
scp -r root@178.62.200.189:/root/autopilot/evidence/cycle_20260430T143022 ./local_evidence/
```

---

## 6. systemd Naming (Future Reference)

When the scheduler phase is approved, the following systemd unit naming convention is proposed:

| Unit Type | Name | Purpose |
|---|---|---|
| Service | `autopilot-runner.service` | The Autopilot cycle runner |
| Timer | `autopilot-runner.timer` | Triggers the runner on schedule |
| Service | `autopilot-health.service` | Health check / watchdog |

### 6.1 Unit File Location

```
/etc/systemd/system/autopilot-runner.service
/etc/systemd/system/autopilot-runner.timer
```

### 6.2 Manual Override Command (Future)

To run one cycle manually even when scheduler is active:

```bash
systemctl start autopilot-runner.service
```

### 6.3 Status Check (Future)

```bash
systemctl status autopilot-runner.service
journalctl -u autopilot-runner.service -n 50 --no-pager
```

These commands are documented here for future reference only. They must not be run until the scheduler phase is approved.

---

## 7. Manual-Only First Stage

### Stage 1: Manual Runner

- No systemd units installed.
- No cron entries.
- Operator invokes one cycle at a time, in a live terminal, watching output.
- Duration: until 5+ consecutive clean cycles are achieved.
- Exit criteria documented in `AUTOPILOT_VPS_MANUAL_RUNNER_PREFLIGHT.md`.

### Stage 1 Commands

```bash
# Health check before run
/root/autopilot/venv/bin/python --version
ls /root/autopilot/logs/
ls /tmp/autopilot.lock 2>/dev/null && echo "LOCKED — DO NOT RUN" || echo "Clear to run"

# Dry run
/root/autopilot/venv/bin/python -B -m project_autopilot.runner --dry-run --cycles 1 \
  2>&1 | tee /root/autopilot/logs/manual_run_$(date +%Y%m%dT%H%M%S).log

# After dry run is validated: live mock run
/root/autopilot/venv/bin/python -B -m project_autopilot.runner --cycles 1 \
  2>&1 | tee /root/autopilot/logs/manual_run_$(date +%Y%m%dT%H%M%S).log
```

---

## 8. Scheduler Future Stage

### Stage 2: Scheduler (Not Yet Approved)

This stage begins only after Stage 1 exit criteria are met and a separate document is authored and approved.

Planned additions in Stage 2:
- `/etc/systemd/system/autopilot-runner.service` — unit file.
- `/etc/systemd/system/autopilot-runner.timer` — timer file.
- `systemctl enable autopilot-runner.timer` — enables on-boot.
- `systemctl start autopilot-runner.timer` — starts the timer.
- logrotate config for `/root/autopilot/logs/`.
- Telegram alerting for unattended failure detection.
- A documented human escalation path for overnight failures.

### Stage 2 Prerequisites

- [ ] Stage 1 exit criteria met (documented and signed off).
- [ ] `AUTOPILOT_VPS_SCHEDULER_PLAN.md` authored and reviewed.
- [ ] Human approval given explicitly.
- [ ] Budget caps configured at all API providers.
- [ ] On-call escalation plan defined.
