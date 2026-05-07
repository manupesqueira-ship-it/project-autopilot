# Project Autopilot — VPS Security Checklist

**Status:** PREFLIGHT DOCS ONLY — No changes have been made to the VPS.
**VPS IP:** 178.62.200.189 (Amsterdam 3, DigitalOcean)
**Date authored:** 2026-04-30

These items must be verified or completed before the first manual Autopilot run on the VPS. Each item is a human action, not an automated one.

---

## 1. SSH Hardening Checklist

Complete these before any Autopilot code is placed on the VPS.

### 1.1 Key-Only Authentication
- [ ] Confirm `PasswordAuthentication no` is set in `/etc/ssh/sshd_config`.
- [ ] Confirm `PubkeyAuthentication yes` is set.
- [ ] Confirm `PermitRootLogin` is set to `prohibit-password` (key-only) or `no`.
- [ ] After confirming, reload sshd: `systemctl reload sshd`.

### 1.2 SSH Port Awareness
- [ ] Know which port SSH is on (default: 22).
- [ ] If changing port, update firewall rules before reloading sshd.
- [ ] Document the port in a password manager, not in a repo.

### 1.3 Authorized Keys
- [ ] Only intended operator public keys are in `~/.ssh/authorized_keys` (for all relevant users).
- [ ] No stale or unrecognised keys present.
- [ ] `authorized_keys` file permissions: `chmod 600 ~/.ssh/authorized_keys`.
- [ ] `.ssh/` directory permissions: `chmod 700 ~/.ssh`.

### 1.4 SSH Session Hardening
- [ ] `ClientAliveInterval 300` and `ClientAliveCountMax 2` set to auto-disconnect idle sessions.
- [ ] `MaxAuthTries 3` set to limit brute-force attempts.

### 1.5 Fail2ban
- [ ] Confirm fail2ban is installed: `which fail2ban-server`.
- [ ] Confirm fail2ban is active: `systemctl status fail2ban`.
- [ ] If not installed: `apt install fail2ban` and configure SSH jail.

---

## 2. Separate Linux User

Project Autopilot must not run as root.

### 2.1 Create Autopilot User
```bash
# Future command — do not run until ready
adduser --disabled-password --gecos "" autopilot
```

### 2.2 User Isolation
- [ ] The `autopilot` Linux user has no sudo privileges.
- [ ] The `autopilot` user's home directory is `/home/autopilot/` or a dedicated path outside `/root/`.
- [ ] Autopilot code lives in a directory owned by the `autopilot` user.
- [ ] The `autopilot` user cannot read `/root/bot/` (verified with `sudo -u autopilot ls /root/bot/`).

### 2.3 SSH Access
- [ ] If SSH access is needed for the `autopilot` user, a separate SSH key pair is generated for it.
- [ ] That key pair is not the same as the operator's root/admin key.
- [ ] The operator logs in as their own user or root (key-only), then switches: `sudo -u autopilot bash`.

---

## 3. Secrets Isolation

### 3.1 Environment Variables
- [ ] Secrets are never stored in plaintext files inside the repo directory.
- [ ] Secrets are loaded via a sourced `.env` file with `chmod 600` permissions, owned by `autopilot`.
- [ ] The `.env` file path is documented internally but the file is not committed to git.
- [ ] `.env` is listed in `.gitignore`.

### 3.2 Secrets Inventory
Before VPS deployment, create a local (not committed) inventory of which secrets are needed:

| Secret Name | Source | Where Stored on VPS |
|---|---|---|
| TELEGRAM_BOT_TOKEN | BotFather | `/home/autopilot/.env` (chmod 600) |
| TELEGRAM_CHAT_ID | Telegram | `/home/autopilot/.env` (chmod 600) |
| (others TBD) | TBD | `/home/autopilot/.env` (chmod 600) |

During manual runner phase: only Telegram credentials are needed. All other secrets (Supabase, OpenAI, Anthropic) must be absent.

### 3.3 Secret Rotation Plan
- [ ] Know how to rotate each secret if compromised.
- [ ] Telegram: revoke via BotFather, issue new token.
- [ ] Any other keys: revoke at source, update `.env`, restart process.

---

## 4. No /root/bot Access

The existing `/root/bot/` directory contains a live trading bot. It must not be touched.

- [ ] The `autopilot` Linux user cannot access `/root/bot/` (permissions enforced at OS level).
- [ ] No Autopilot code references `/root/bot/` in any path string.
- [ ] No symlinks from the Autopilot directory to `/root/bot/`.
- [ ] Operator confirms this constraint before every SSH session by reviewing `AUTOPILOT_VPS_NO_TOUCH_ZONES.md`.

See `AUTOPILOT_VPS_NO_TOUCH_ZONES.md` for the full no-touch zone list and warning language.

---

## 5. Firewall Considerations

### 5.1 UFW Status
- [ ] Confirm UFW is active: `ufw status verbose`.
- [ ] Confirm SSH port is allowed before enabling UFW (to avoid lockout).

### 5.2 Autopilot Outbound
- [ ] Autopilot only needs outbound HTTPS (port 443) for Telegram reporting.
- [ ] During manual runner phase, no inbound ports are opened for Autopilot.
- [ ] No web server or API server is exposed for Autopilot during this phase.

### 5.3 No New Inbound Rules for Autopilot
- [ ] Do not open any new inbound ports for Autopilot during the manual runner phase.
- [ ] If a health-check endpoint is added later, it must be behind an auth layer and documented separately.

---

## 6. Log Retention

### 6.1 Log Location
- All Autopilot logs land in `/root/autopilot/logs/` (or the designated path from the directory plan).
- Log files are named with timestamps: `manual_run_YYYYMMDDTHHMMSS.log`.

### 6.2 Log Permissions
- [ ] Log directory: `chmod 750`, owned by `autopilot`.
- [ ] Log files: `chmod 640`, owned by `autopilot`.
- [ ] Logs must not contain secrets. Review the first log file manually after the first run.

### 6.3 Retention Policy
- Keep the last 30 days of logs.
- Archive (compress) logs older than 7 days.
- During manual runner phase, retain all logs — do not delete any until the phase is complete.

### 6.4 logrotate
A logrotate config will be authored in the scheduler phase. During the manual runner phase, log rotation is manual and operator-driven.

---

## 7. Backup Strategy

### 7.1 What to Back Up
- [ ] The Autopilot code directory (git repo — push to remote regularly).
- [ ] The `.env` file — store a copy in a password manager, not on the VPS.
- [ ] Evidence artifacts (if valuable) — copy to local machine after each manual run.

### 7.2 What Not to Back Up
- [ ] Do not back up `/root/bot/` as part of Autopilot procedures.
- [ ] Do not back up secrets to any cloud storage in plaintext.

### 7.3 DigitalOcean Snapshots
- [ ] Enable DigitalOcean weekly snapshots for the droplet (via DO control panel — not via SSH).
- [ ] This is a safety net only; the primary backup is the git remote.

---

## 8. Emergency HALT Procedure

The operator must know these commands before starting any run.

### 8.1 Kill the Current Process
If a manual run is observed to be misbehaving:

```bash
# Find the PID
ps aux | grep python

# Kill it immediately
kill -9 <PID>
```

### 8.2 Kill All Python Processes (Nuclear)
```bash
pkill -9 -u autopilot python
```

Only use if the targeted kill fails.

### 8.3 Disconnect from VPS
Closing the SSH terminal does NOT stop a running process unless `nohup` or `tmux` was used. During manual runner phase, do NOT use `nohup` or `tmux` — the process is tied to the terminal by design, so closing the terminal kills it.

### 8.4 DigitalOcean Console Kill
If SSH is unresponsive: use the DigitalOcean web console to access the droplet and issue kill commands. This is the last resort before a droplet power cycle.

### 8.5 HALT Telegram Alert
If Telegram reporting is active and a run goes wrong, send a manual Telegram message to the bot chat immediately. The message should say: `HALT — manual kill issued at HH:MM UTC. Investigating.`

---

## 9. Run Lock

To prevent accidental double-runs during the manual phase:

### 9.1 Lock File Convention
Before each run, check for a lock file:

```bash
ls /tmp/autopilot.lock && echo "ALREADY RUNNING — DO NOT START"
```

If no lock file exists, create one before starting:

```bash
touch /tmp/autopilot.lock
```

Remove it after the run completes or is killed:

```bash
rm -f /tmp/autopilot.lock
```

### 9.2 Formal Lock in Code
The Autopilot runner code should create and check a lock file itself. During the manual runner phase, the operator also checks manually as a belt-and-suspenders measure.

---

## 10. Budget Caps

### 10.1 VPS Cost
- DigitalOcean droplet costs are fixed at the selected plan rate. No action needed, but the operator should know the monthly cost and confirm the DO billing alert is set.

### 10.2 API Cost Caps
- During manual runner phase, all paid APIs are disabled (see Preflight Section 8).
- When paid APIs are enabled in a future phase, set hard spending limits at the provider:
  - Anthropic: set a monthly spending limit in the console.
  - OpenAI: set a monthly spending limit in the console.
- [ ] Budget alerts must be configured before any live API key is added to the VPS.

### 10.3 Telegram
- Telegram Bot API is free. No cost cap needed.

### 10.4 Budget Alert Action
If a budget alert fires from any provider, the response is immediate:
1. SSH to VPS.
2. Kill all Autopilot processes.
3. Remove or blank the relevant API key from `.env`.
4. Investigate before re-enabling.
