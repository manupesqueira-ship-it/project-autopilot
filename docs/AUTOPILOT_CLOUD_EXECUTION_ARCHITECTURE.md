# Project Autopilot — Cloud Execution Architecture

**Status:** Planning / Not yet deployed  
**Last updated:** 2026-04-30  
**Branch:** agent/autopilot-cloud-plan

---

## 1. Purpose

This document defines the target architecture for moving Project Autopilot from a local-only execution model to a resilient, auditable, cloud-assisted autonomous agent control plane.

The goal is not speed — it is correctness, traceability, safety, and eventually autonomous execution with human approval gates at every irreversible action.

---

## 2. Current Local Architecture

```
Developer laptop
└── MIRA repo (main worktree)
    ├── project_autopilot/        ← orchestrator, policy, scheduler
    ├── project_control/          ← docs, rules, task queue
    ├── agent/                    ← Claude Agent SDK dry-run stubs
    └── app/                      ← MIRA product (Next.js)

Execution flow (local):
  1. Human runs: python -m project_autopilot.run
  2. Policy gate checks AGENT_RULES / AUTONOMY_PROTOCOL
  3. Task picked from TASK_QUEUE
  4. Claude Agent SDK (dry-run) called
  5. Output reviewed locally
  6. Human commits if safe
```

Limitations:
- Laptop must be awake and running
- No parallel task execution
- No audit trail beyond local logs
- No rollback mechanism
- Scheduler disabled (correctly, for now)
- No isolation between builder agents

---

## 3. Target Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    HUMAN CONTROL CENTER                         │
│  (Telegram / Web dashboard / local terminal)                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │ approves / rejects / escalates
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PROJECT AUTOPILOT (Orchestrator)               │
│  Runs on: VPS or GitHub Actions runner                          │
│  - Reads TASK_QUEUE                                             │
│  - Applies policy gates                                         │
│  - Routes tasks to correct agent/runner                         │
│  - Records all decisions to evidence log                        │
└──────┬───────────────────┬───────────────────┬──────────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
  Codex (cloud)     Claude Agent SDK     Claude Code
  (OpenAI)          (Anthropic)          (GitHub Actions)
  code generation   analysis/review      PR-based execution
       │                   │                   │
       └───────────────────┴───────────────────┘
                           │
                    Git worktree (isolated)
                           │
                    PR → branch protection → required checks
                           │
                    Human approval gate
                           │
                    Merge to main
```

---

## 4. Local Control Plane

The local control plane remains the canonical source of truth and the last safety gate.

Components:
- `project_control/TASK_QUEUE.md` — human-curated task list
- `project_control/AGENT_RULES.md` — what agents may and may not do
- `project_control/AUTONOMY_PROTOCOL.md` — autonomy level per task class
- `project_autopilot/policy/` — programmatic policy enforcement
- `.halt` file — emergency stop (any agent checks this before acting)
- `.run.lock` — prevents concurrent runs of the same agent

Local control plane is always writable by human owner. Cloud runners are read-only consumers of policy from this source.

---

## 5. GitHub Cloud Workflow

```
GitHub Actions trigger:
  - Manual dispatch (workflow_dispatch)
  - PR comment: /run-autopilot
  - Scheduled (disabled until local cycle is stable)

Workflow steps:
  1. Checkout repo (read-only analysis branch or worktree)
  2. Check .halt file — abort if present
  3. Run policy gate validation
  4. Run agent task (dry-run by default)
  5. Post results as PR comment
  6. Require human approval before any write action
  7. Archive evidence to GitHub artifacts
  8. Notify via Telegram if configured

GitHub secrets:
  - ANTHROPIC_API_KEY (Claude)
  - OPENAI_API_KEY (Codex)
  - TELEGRAM_BOT_TOKEN
  - TELEGRAM_CHAT_ID
  All secrets scoped to repo, not org-wide.
  No Supabase secrets in CI until RLS is complete.
```

---

## 6. VPS Runner Workflow

```
DigitalOcean Amsterdam 3 (178.62.200.189)
  - Ubuntu 24 LTS
  - /root/bot/ — EXISTING PROJECT: DO NOT TOUCH
  - /root/autopilot/ — new project directory

VPS runner role:
  - Long-running background polling (when enabled)
  - git pull → policy check → task execution → log
  - Telegram escalation on any anomaly
  - HALT file checked before every cycle

VPS is not primary execution environment yet.
Primary remains local until scheduler is proven stable.
```

See `AUTOPILOT_VPS_RUNNER_PLAN.md` for full VPS details.

---

## 7. Codex Cloud Role

Codex (OpenAI) is used exclusively as a code generation agent, not a policy agent.

Allowed:
- Generate implementation code stubs in a git worktree
- Refactor code within a single worktree
- Produce typed TypeScript or Python diffs

Not allowed:
- Write to main branch directly
- Read or write `.env` files
- Execute database migrations
- Trigger deploys
- Make autonomous policy decisions

Codex output always lands in a named worktree. A human reviews the diff before merge.

---

## 8. Claude Agent SDK Role

Claude Agent SDK is the analysis and review layer, not the code generator.

Allowed:
- Analyze diffs, test results, and logs
- Produce policy compliance reports
- Generate structured JSON verdicts
- Flag anomalies for human review

Not allowed:
- Execute shell commands autonomously
- Write to disk outside designated evidence directory
- Call Supabase directly
- Approve its own output

Claude Agent SDK calls are always logged with: model, prompt hash, response hash, timestamp, token count.

---

## 9. Claude Code GitHub Actions Role

Claude Code can be configured as a GitHub Actions step.

Allowed:
- Read-only analysis of PR diffs
- Post structured review comments
- Run policy gate checks as a CI step
- Generate architecture suggestions in PR body

Not allowed:
- Merge PRs
- Push to protected branches
- Execute migrations
- Approve PRs on behalf of human

Trigger: PR opened, synchronize, or manual `/review` comment.

---

## 10. Telegram Escalation Role

Telegram is the human notification and approval channel.

Events that trigger Telegram message:
- Autopilot cycle start (if enabled)
- Policy gate violation detected
- Agent produced unexpected output
- HALT file was written
- Any error with exit code != 0
- Budget cap exceeded
- Task completed successfully (summary)
- Human decision required

Telegram is one-way notification by default. Interactive approval (bot commands) is a future phase feature.

Bot token and chat ID stored in GitHub Secrets and VPS env only. Never committed.

---

## 11. Control Center Role

Control Center is the human-facing dashboard for reviewing autopilot state.

Current: terminal + project_control/*.md files  
Future: lightweight web UI reading from evidence directory

Control Center responsibilities:
- Display current task queue
- Show last N cycle summaries
- Highlight pending human decisions
- Show agent verdict history
- Link to PR evidence artifacts

Control Center is read-only from agent perspective. Only humans write to it.

---

## 12. Evidence / Log Storage

Every agent action produces an evidence record.

Evidence record format:
```json
{
  "cycle_id": "uuid",
  "timestamp": "ISO8601",
  "task_id": "string",
  "agent": "codex|claude-sdk|claude-code|autopilot",
  "action": "string",
  "input_hash": "sha256",
  "output_hash": "sha256",
  "verdict": "pass|fail|escalate",
  "tokens_used": 0,
  "cost_usd": 0.00,
  "notes": "string"
}
```

Storage locations:
- Local: `project_control/evidence/` (gitignored large logs)
- VPS: `/root/autopilot/evidence/` (not synced to git)
- GitHub: PR artifacts (attached to workflow runs, 30-day retention)

Evidence is append-only. Never deleted. Never modified after write.

---

## 13. Secrets Strategy

| Secret | Where stored | Who reads it |
|--------|-------------|--------------|
| ANTHROPIC_API_KEY | GitHub Secrets + VPS .env | Claude SDK agent |
| OPENAI_API_KEY | GitHub Secrets + VPS .env | Codex agent |
| SUPABASE_SERVICE_KEY | GitHub Secrets (future) | Migration runner only |
| TELEGRAM_BOT_TOKEN | GitHub Secrets + VPS .env | Notifier |
| TELEGRAM_CHAT_ID | GitHub Secrets + VPS .env | Notifier |

Rules:
- No secrets in any committed file ever
- No secrets in PR comments or logs
- VPS .env is for autopilot project only, isolated from /root/bot/.env
- Rotate secrets on any suspected leak immediately

---

## 14. Budget / Cost Strategy

| Agent | Daily cap | Per-call cap | Alert threshold |
|-------|-----------|-------------|----------------|
| Claude Agent SDK | $5.00 | $0.50 | $3.00 |
| Codex | $5.00 | $1.00 | $3.00 |
| Combined | $8.00 | — | $6.00 |

Budget caps enforced in code, not just by provider limits.  
If cap exceeded: write HALT file, send Telegram alert, stop cycle.  
Budget resets midnight UTC.

---

## 15. Human Approval Gates

The following actions ALWAYS require explicit human approval:

| Action | Why |
|--------|-----|
| Merge any PR to main | Irreversible code change |
| Execute any Supabase migration | Irreversible DB change |
| Enable live scheduler | Starts autonomous cycles |
| Push to production | Irreversible deploy |
| Add new secret | Security scope change |
| Enable new agent provider | New cost/risk surface |
| Remove HALT file | Resume after emergency stop |

Approval mechanism: human runs command, or explicitly approves in Telegram (future).  
Approval is never automated. Never delegated to an agent.

---

## 16. What Must Stay Disabled by Default

- Scheduler (all cycles): disabled until local cycle is boringly reliable for 30+ days
- Live Supabase writes from CI: disabled until RLS audit complete
- Auto-merge PRs: permanently disabled
- Codex direct push: permanently disabled
- Claude SDK shell execution: permanently disabled
- VPS systemd service: disabled until VPS plan validated by human
- Telegram approval bot: disabled until Phase 2

---

## 17. Recommended Staged Rollout

### Stage 0 — Now (local only)
- Local dry-run cycles working
- Policy gates enforced
- Evidence logging to local files
- All agents in dry-run mode

### Stage 1 — GitHub Actions (read-only)
- Claude Code GitHub Action set up as PR reviewer
- No write permissions
- Evidence posted as PR comments
- Human merges manually

### Stage 2 — VPS runner (polling, no scheduler)
- VPS running manual trigger cycles
- Telegram alerts wired
- HALT/lock files respected
- Budget caps enforced

### Stage 3 — Codex integration
- Codex writing to worktrees only
- All output reviewed before merge
- Evidence records for every call

### Stage 4 — Scheduled cycles
- Only after 30 days of clean Stage 2/3 operation
- Scheduler starts with 4-hour minimum interval
- Human approval required to reduce interval

### Stage 5 — Full autonomous execution
- Human approval gates remain for irreversible actions
- Autonomous handling of low-risk, reversible tasks only
- Full audit trail at every step
