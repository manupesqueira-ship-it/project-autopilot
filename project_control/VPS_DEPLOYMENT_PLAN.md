# VPS Deployment Plan — Project Autopilot

Status: **NOT DEPLOYED**. This document captures the plan for future VPS deployment.

## Target VPS

- Provider: DigitalOcean
- IP: 178.62.200.189
- OS: Ubuntu 24 LTS
- Region: Amsterdam
- Resources: 1 vCPU, 2GB RAM, ~44GB disk free
- Existing project: `/root/bot/` (DO NOT TOUCH)
- Existing services use `bot-*` prefixes

## Coexistence Rules

1. **Never modify `/root/bot/` or any `bot-*` services.**
2. Project Autopilot uses unique paths and service names prefixed with `pa-`.
3. No shared ports, no shared databases, no shared cron entries.
4. Project Autopilot must not interfere with existing services even if it crashes.

## Recommended Install Path

Primary option:

```
/root/project-autopilot/
```

Alternative:

```
/root/projects/mira/
```

Later, prefer a separate Linux user for isolation:

```
sudo adduser --disabled-password autopilot
```

## Separate Virtual Environment

```bash
python3 -m venv /root/project-autopilot/venv
source /root/project-autopilot/venv/bin/activate
pip install -r requirements.txt  # if any
```

## Verify Commands

Run these on the VPS before deployment to confirm the environment:

```bash
which python3
which node
which npm
which git
which docker
which nginx
free -h
df -h
ss -tlnp
systemctl list-units --type=service --state=running
crontab -l
```

## Proposed Service Names

- `pa-mira-cycle.service` — runs one Project Autopilot cycle
- `pa-mira-cycle.timer` — schedules periodic cycles

Templates are in `project_autopilot/templates/systemd/`. They are not installed or enabled.

## What Is NOT Enabled

- No scheduler activation yet.
- No deploy automation.
- No paid APIs by default.
- No automatic builder execution.
- No cron jobs.
- No systemd services installed.

## Deployment Checklist (Future)

1. SSH into VPS.
2. Clone or rsync the repo to the install path.
3. Create venv and install dependencies.
4. Copy `.env` with secrets (never commit).
5. Run `--doctor` to validate environment.
6. Run `--local-plan` to verify prompt generation works.
7. Install systemd templates (after filling placeholders).
8. Enable timer only after manual cycles are proven reliable.
9. Verify coexistence: `bot-*` services still running, no port conflicts.

## Why Not Yet

The scheduler should wait until manual cycles are boringly reliable. Before deploying:

- Repeated clean runs of doctor, local-plan, evidence bundle, post-builder.
- Run lock proven to prevent concurrent cycles.
- HALT_AUTOPILOT tested and working.
- Telegram alerts confirmed.
- No human cleanup required between cycles.
