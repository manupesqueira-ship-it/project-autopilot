# Project Autopilot — VPS No-Touch Zones

**Status:** PREFLIGHT DOCS ONLY — No VPS access has occurred.
**VPS IP:** 178.62.200.189 (Amsterdam 3, DigitalOcean)
**Date authored:** 2026-04-30

---

## WARNING — READ BEFORE EVERY SSH SESSION

> STOP. Before you run any command on the VPS, read this file.
> The following zones are permanently off-limits for all Project Autopilot activity.
> Touching any of these zones — even accidentally — may destroy a live trading system,
> expose production secrets, or corrupt irreplaceable data.
> If you are unsure whether a command affects a no-touch zone, do not run it.
> Ask first. There is no recovery shortcut.

---

## 1. /root/bot/

**Zone:** `/root/bot/` and all subdirectories.
**Status:** PERMANENTLY OFF-LIMITS.

This directory contains a live, independently operating trading bot that is unrelated to Project Autopilot. It may be running at the moment you SSH in. It has its own environment files, configuration, and state.

**Prohibited actions:**
- Reading files in `/root/bot/` (this includes `ls /root/bot/`, `cat`, `grep`, or any read command).
- Writing any file to `/root/bot/`.
- Deleting any file in `/root/bot/`.
- Killing processes that belong to the `/root/bot/` system.
- Modifying environment variables used by `/root/bot/`.
- Changing file permissions in `/root/bot/`.
- Running `git` commands inside `/root/bot/`.

**Human Warning:**

> IF YOU FIND YOURSELF TYPING ANY COMMAND THAT REFERENCES `/root/bot/` OR ANY PATH INSIDE IT, STOP IMMEDIATELY. CLOSE THE COMMAND. DO NOT PROCEED. THE LIVE TRADING BOT RUNNING THERE IS NOT YOURS TO TOUCH.

---

## 2. Existing Bot Environment Files

**Zone:** Any `.env` file, `.env.local`, `.env.production`, or similar secrets file that exists on the VPS prior to Autopilot deployment.
**Status:** PERMANENTLY OFF-LIMITS.

The existing bot has its own environment files. These must not be:
- Read (they contain live secrets).
- Modified (this would break the live bot).
- Copied (the secrets would be duplicated and potentially leaked).
- Deleted (this would immediately break the live bot).

**How to identify these files:** Do not look for them. If you encounter an `.env` file outside of `/root/autopilot/` (the Autopilot directory), do not open it.

**Human Warning:**

> IF YOU FIND AN `.env` FILE THAT YOU DID NOT PLACE THERE AS PART OF AUTOPILOT SETUP, DO NOT OPEN IT, DO NOT COPY IT, DO NOT MODIFY IT. CLOSE YOUR TERMINAL IF YOU ACCIDENTALLY SEE ITS CONTENTS.

---

## 3. Production Secrets

**Zone:** Any secret, credential, token, key, or password that belongs to the live trading system or any other production system on this VPS.
**Status:** PERMANENTLY OFF-LIMITS.

Production secrets include, but are not limited to:
- Exchange API keys (any exchange).
- Trading account credentials.
- Live Supabase service role keys.
- Live Supabase project URLs.
- Webhook tokens for the live bot.
- Any token or key that was not explicitly created for Project Autopilot.

**If you accidentally see a production secret:**
1. Do not write it down.
2. Do not copy it to any file.
3. Do not send it anywhere.
4. Close the terminal window.
5. Notify the system owner immediately.

**Human Warning:**

> A PRODUCTION SECRET SEEN IS A PRODUCTION SECRET AT RISK. IF YOU SEE ANY KEY, TOKEN, OR PASSWORD THAT IS NOT YOURS, TREAT IT AS COMPROMISED UNTIL PROVEN OTHERWISE. NOTIFY THE OWNER.

---

## 4. Live Database Systems

**Zone:** The live Supabase project and any other live database used by the trading bot or any other production system.
**Status:** PERMANENTLY OFF-LIMITS during manual runner phase.

This means:
- Do not run SQL queries against the live Supabase project from the VPS.
- Do not use the live `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` combination.
- Do not run `psql` connections to production databases.
- Do not use the Supabase Studio or dashboard to make changes during Autopilot testing.

The Autopilot manual runner phase uses only local mock data and local SQLite/PostgreSQL instances.

**Human Warning:**

> THE LIVE DATABASE CONTAINS REAL TRADING STATE AND POTENTIALLY REAL USER DATA. A MISTAKEN WRITE OR DELETE CANNOT BE EASILY UNDONE. DO NOT CONNECT TO IT DURING THE AUTOPILOT MANUAL RUNNER PHASE.

---

## 5. System Service Files Outside Autopilot Scope

**Zone:** All systemd unit files, cron entries, and init scripts that exist on the VPS prior to Autopilot deployment.
**Status:** PERMANENTLY OFF-LIMITS.

This means:
- Do not modify `/etc/systemd/system/` files that are not Autopilot unit files.
- Do not run `systemctl enable`, `systemctl disable`, `systemctl start`, or `systemctl stop` on services that are not Autopilot services.
- Do not modify `/etc/cron.d/`, `/etc/cron.daily/`, or user crontabs (`crontab -e`) for users other than the `autopilot` user.
- Do not modify `/etc/rc.local` or any other startup script not created for Autopilot.

**Human Warning:**

> MODIFYING SYSTEM SERVICES THAT ARE NOT YOURS CAN STOP THE LIVE BOT OR PREVENT THE SERVER FROM STARTING CORRECTLY AFTER A REBOOT. IF YOU ARE NOT CERTAIN A SERVICE FILE IS PART OF AUTOPILOT, DO NOT TOUCH IT.

---

## 6. Unrelated Repositories

**Zone:** Any git repository on the VPS that is not the Project Autopilot repository.
**Status:** PERMANENTLY OFF-LIMITS.

This includes:
- `/root/bot/` (already covered above).
- Any other git repository that existed before Autopilot deployment.
- Any clones of unrelated projects made by other team members.

Do not run `git` commands in any repository other than `/root/autopilot/repo/`.

**Human Warning:**

> RUNNING `git reset --hard`, `git clean -f`, OR `git checkout` IN THE WRONG REPOSITORY DESTROYS UNCOMMITTED WORK. ALWAYS CONFIRM YOUR CURRENT DIRECTORY BEFORE RUNNING DESTRUCTIVE GIT COMMANDS: `git rev-parse --show-toplevel`

---

## 7. Destructive Commands

The following categories of commands are prohibited without explicit, written, pre-approved justification:

### 7.1 File Deletion
```bash
rm -rf        # PROHIBITED without explicit approval
rm -f         # CAUTION — check path before running
find . -delete # PROHIBITED
```

### 7.2 Process Killing Outside Autopilot
```bash
pkill python  # PROHIBITED — may kill the live bot's Python processes
killall python # PROHIBITED — same reason
kill -9 <PID> # Only for Autopilot PIDs. Verify PID belongs to Autopilot first.
```

### 7.3 Permission Recursion
```bash
chmod -R 777  # PROHIBITED
chown -R root # PROHIBITED outside Autopilot directories
```

### 7.4 Network Configuration
```bash
ufw disable   # PROHIBITED — disables the firewall
iptables -F   # PROHIBITED — flushes all firewall rules
```

### 7.5 Package Manager (Without Review)
```bash
apt remove    # PROHIBITED without review — may remove shared dependencies
apt autoremove # CAUTION — review what will be removed before confirming
```

### 7.6 Disk Operations
```bash
dd            # PROHIBITED
mkfs          # PROHIBITED
fdisk         # PROHIBITED
```

**Human Warning:**

> DESTRUCTIVE COMMANDS ON A SHARED SERVER CAN BREAK MULTIPLE SYSTEMS SIMULTANEOUSLY. ALWAYS ASK: "DOES THIS COMMAND AFFECT ANYTHING OUTSIDE OF `/root/autopilot/`?" IF THE ANSWER IS "MAYBE", STOP AND THINK.

---

## 8. No-Touch Zone Verification Protocol

Before starting any SSH session for Autopilot work, the operator must:

1. **Recall the zones.** Say to yourself: "I must not touch `/root/bot/`, existing env files, production secrets, live databases, system services not mine, unrelated repos, or run destructive commands without approval."

2. **Check your working directory.** Immediately after SSH:
   ```bash
   pwd
   # Expected: /root or /root/autopilot or /home/autopilot
   # If you see /root/bot: cd out immediately. DO NOT PROCEED.
   ```

3. **Do not use tab-completion near `/root/bot/`.** Tab-completion may accidentally reveal file names from the no-touch zone.

4. **Close the session when done.** Do not leave SSH sessions open and unattended. Active sessions with root access are a security risk.

---

## Appendix: Quick Reference Card

Print or pin this summary:

```
NO-TOUCH ZONES — AUTOPILOT VPS

1. /root/bot/                  — NEVER TOUCH
2. Existing .env files          — NEVER TOUCH
3. Production secrets           — NEVER TOUCH, NEVER COPY
4. Live Supabase DB             — NEVER CONNECT
5. System services not mine     — NEVER MODIFY
6. Unrelated git repos          — NEVER TOUCH
7. Destructive commands         — NEVER WITHOUT APPROVAL
8. pkill/killall python         — NEVER (may kill live bot)

IF IN DOUBT: EXIT THE SSH SESSION. ASK FIRST.
```
