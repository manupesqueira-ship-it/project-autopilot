# Project Autopilot — Worktree Sandbox Strategy

**Status:** Planning / Not yet deployed  
**Last updated:** 2026-04-30

---

## Current Worktree Creation-Only Phase

Project Autopilot may create one sandbox worktree only through explicit human approval:

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-worktree-create-approved --task "<task>"
python -B project_autopilot/agent_loop.py --project mira --claude-worktree-cleanup-approved --task-id "<task_id>"
python -B project_autopilot/agent_loop.py --project mira --claude-worktree-smoke-test
```

The worktree path must be outside the main repo and match `C:\Users\manup\projects\mira-sandbox-<task_id>`. The branch must match `sandbox/claude-<task_id>`. This phase writes evidence and cleanup records, but it still forbids Claude execution, file edits, commits, auto-merge, deploy, SQL/RLS, env/secrets access, paid APIs, scheduler changes, and automatic Claude execution.

Cleanup is evidence-scoped: Project Autopilot removes only the recorded `mira-sandbox-*` path and refuses arbitrary paths.

---

## 1. Why Worktrees Are Required for Parallel Writes

Git worktrees allow multiple checked-out branches from a single repository simultaneously, each in its own directory.

Without worktrees:
- Two agents writing to the same working directory → race conditions
- Switching branches during a task → corrupts in-progress changes
- Stashing and unstashing → fragile, loses context

With worktrees:
- Each agent gets a fully isolated filesystem view of a branch
- Agents can run in parallel without interference
- Each worktree is independently committable and pushable
- Main worktree stays clean and reviewable at all times

Worktrees are mandatory for any parallel agent execution.  
Single-agent local development may use the main worktree directly.

---

## 2. Naming Conventions

Worktree branch names follow a strict pattern:

```
<agent>/<task-id>-<short-slug>
```

Examples:
```
codex/TASK-042-add-session-expiry
claude/TASK-043-review-auth-flow
autopilot/TASK-044-policy-gate-update
```

Agent prefixes:
| Prefix | Agent |
|--------|-------|
| `codex/` | Codex (OpenAI) builder |
| `claude/` | Claude Agent SDK or Claude Code |
| `autopilot/` | Project Autopilot orchestrator |
| `human/` | Human-initiated feature branch |

Worktree directory names (on VPS):
```
/home/autopilot/repos/worktrees/TASK-042-add-session-expiry/
```

Never use generic names like `worktree-1` or `tmp`. Always include task ID.

---

## 3. One Agent Per Worktree Rule

A single worktree is owned by exactly one agent at a time.

Rules:
- No two agents share the same worktree simultaneously
- Ownership is recorded in the worktree's `.agent_lock` file:
  ```json
  {
    "agent": "codex",
    "task_id": "TASK-042",
    "cycle_id": "uuid",
    "started": "2026-04-30T10:00:00Z",
    "pid": 12345
  }
  ```
- If `.agent_lock` exists: refuse to start, send alert, abort
- Claude SDK and Codex never share a worktree even if working on related tasks
- Human developer may inspect a worktree but must not commit while agent lock is held

---

## 4. Allowed / Forbidden Actions in a Worktree

### Allowed
- Read any file in the worktree
- Write to `app/`, `lib/`, `components/`, `project_autopilot/` within scope of task
- Write new test files
- Run lint, typecheck, build within the worktree
- `git add` and `git commit` within the worktree
- `git push` the worktree branch to origin (to open PR)
- Write to `project_control/evidence/` for evidence records

### Forbidden
- Write to `.env`, `.env.*`, `.env.local`, or any secret file
- Modify `project_control/AGENT_RULES.md` or `AUTONOMY_PROTOCOL.md` (requires human)
- Run `git merge` or `git rebase` without human review
- Run `git push --force`
- Run `git push` to `main`, `develop`, or any protected branch
- Modify another worktree's files
- Execute `supabase db push` or any migration command
- Remove or disable the `.halt` file check
- Modify systemd service files
- Write to `/root/bot/` or any path outside designated directories

---

## 5. Merge Rules

Merging a worktree branch to main follows this process:

```
1. Agent completes work in worktree branch
2. Agent runs: lint, typecheck, build, policy-gate (all must pass)
3. Agent pushes branch to origin
4. Agent opens DRAFT PR (never marks ready for review)
5. Required CI checks run automatically
6. Agent posts evidence record as PR comment
7. HUMAN converts draft to ready (the human approval signal)
8. HUMAN reviews diff
9. HUMAN approves PR
10. HUMAN merges (squash merge preferred for clean history)
11. Worktree is deleted after successful merge
```

No step in this process is automated end-to-end. Human is required at step 7-10.

---

## 6. Conflict Handling

If a worktree branch has conflicts with main:

Automatic behavior:
1. `git fetch origin main`
2. `git merge origin/main --no-commit --no-ff` (dry run)
3. If conflicts detected:
   - Write HALT file for this worktree
   - Post conflict summary as PR comment
   - Send Telegram alert
   - Do NOT attempt auto-resolution
   - Do NOT `git merge --strategy-option theirs`

Human resolution:
1. Human reviews conflict markers
2. Human resolves manually
3. Human commits resolution
4. CI re-runs

Agents never resolve merge conflicts autonomously.  
Reason: conflict resolution requires judgment about intent, not just syntax.

---

## 7. Rollback Strategy

If a merged PR is found to have introduced a regression:

Rollback options (human chooses):
1. `git revert <merge-commit>` — creates a new revert commit (preferred)
2. Hotfix PR — fix the issue in a new branch (for minor issues)
3. `git reset --hard` — only if not yet pushed (last resort, human only)

Agent rollback preparation:
- Every agent commit must produce an evidence record
- Evidence record includes: commit hash, diff hash, task ID
- This allows precise identification of what to revert

Agents never execute rollbacks. They prepare the evidence needed for human rollback.

---

## 8. Auto-commit Rules

Agents may auto-commit within a worktree under these conditions:
- All required checks pass (lint, typecheck, build, policy-gate)
- Commit is to the worktree branch only (never main)
- Commit message follows format: `[AGENT:<agent>] <task-id>: <description>`
- Commit is accompanied by an evidence record
- HALT file is absent

Auto-commit message format:
```
[AGENT:codex] TASK-042: Add session expiry validation

Task: TASK-042
Cycle: <uuid>
Agent: codex
Evidence: evidence/2026-04-30/cycle_<uuid>.json
```

Auto-commit does NOT mean auto-push. Push to origin is a separate step, also allowed within worktree branch.

---

## 9. No Auto-merge Policy

**Auto-merge is permanently prohibited for all agents, in all contexts, at all times.**

This is not a phase-1 restriction. It is a permanent architectural constraint.

Rationale:
- Merging is an irreversible action affecting the main codebase
- Agents cannot assess full context (team conventions, product intent, security implications)
- The cost of a bad auto-merge (regression, data loss, security hole) far exceeds the cost of human review time
- Trust in automation is built incrementally; merge authority is the last thing delegated

Any code that implements auto-merge logic is itself a policy violation and must be rejected.

---

## 10. Manual Claude Handoff in Sandbox Worktree

When a sandbox worktree has been created through the approved flow, a human may manually open Claude Code in that worktree and paste a handoff packet. This is the **manual Claude handoff flow**.

The full lifecycle is defined in `CLAUDE_MANUAL_HANDOFF_PROTOCOL.md`. Key rules for worktree context:

- Claude operates only within the sandbox worktree directory.
- Claude edits only files listed in the handoff packet's allowed files.
- Claude runs only commands listed in the handoff packet's allowed commands.
- Claude commits only to the sandbox branch, never to main or develop.
- After Claude finishes, the human runs post-builder policy from the main repo.
- The sandbox remains active until post-builder review completes.
- Cleanup is human-initiated using the recorded sandbox path only.

The manual handoff flow does not enable automatic Claude execution, scheduler, auto-merge, env/secrets access, SQL/RLS, deploy, or paid APIs.

---

## 11. Sandbox Rules for Claude Builder (Future Automated)

Claude Agent SDK, when used as a code builder:

Allowed in sandbox:
- Read all files in scope
- Write generated code to worktree files
- Run analysis and produce structured output
- Write evidence record

Forbidden in sandbox:
- Shell execution outside designated safe commands (lint, typecheck, build)
- Network requests outside designated APIs
- File writes outside worktree boundary
- Reading `/home/autopilot/.env`
- Any action requiring elevated permissions

Claude builder runs with environment variable `SANDBOX=true` set.  
Any code path that checks `SANDBOX` and behaves differently is a red flag and must be reviewed.

---

## 12. Sandbox Rules for Codex Builder

Codex (OpenAI), when used as a code builder:

Allowed in sandbox:
- Receive task spec as structured prompt
- Generate code files
- Output structured diff or file content
- Output evidence JSON

Forbidden in sandbox:
- Direct file system access (all writes are mediated by autopilot runner)
- Network access other than OpenAI API call
- Receiving `.env` content or secrets in prompt
- Generating code that disables policy gates

Autopilot runner mediates all Codex file writes:
```
Codex output (JSON diff) → autopilot runner validates → writes to worktree
```

Codex never has direct worktree access. It outputs structured content that the runner applies.

---

## 13. Evidence Requirements

Every worktree operation must produce an evidence record before the worktree is closed.

Minimum required evidence:
```json
{
  "worktree": "codex/TASK-042-add-session-expiry",
  "branch": "codex/TASK-042-add-session-expiry",
  "task_id": "TASK-042",
  "agent": "codex",
  "cycle_id": "uuid",
  "started": "ISO8601",
  "completed": "ISO8601",
  "commits": ["sha1", "sha2"],
  "files_modified": ["path/to/file.ts"],
  "checks_passed": ["lint", "typecheck", "build", "policy-gate"],
  "checks_failed": [],
  "pr_url": "https://github.com/.../pull/123",
  "verdict": "ready_for_review",
  "tokens_used": 1234,
  "cost_usd": 0.04,
  "notes": "Added session expiry validation per TASK-042 spec"
}
```

Evidence file is written to:
1. Worktree: `project_control/evidence/<cycle_id>.json`
2. VPS archive: `/home/autopilot/evidence/YYYY-MM-DD/<cycle_id>.json`
3. GitHub artifact: uploaded by CI workflow

---

## 14. Post-builder Policy Requirements

After any agent completes work in a worktree, before opening a PR:

Checklist (enforced by policy gate):
- [ ] Evidence record written and valid JSON
- [ ] All checks passing: lint, typecheck, build, policy-gate
- [ ] No `.env` files modified
- [ ] No secrets in diff (gitleaks scan)
- [ ] No auto-merge logic introduced
- [ ] No scheduler enablement
- [ ] No direct database write code added without review flag
- [ ] PR description filled with required fields
- [ ] PR opened as DRAFT (not ready for review)
- [ ] Telegram notification sent

If any item fails: do NOT open PR. Write HALT, send Telegram, await human.

---

## 15. Claude Sandbox Boundary Preflight

Claude builder execution is not enabled. The current safe step is boundary preflight and simulation only:

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-sandbox-preflight --task "<task>"
python -B project_autopilot/agent_loop.py --project mira --claude-sandbox-simulate --task "<task>"
```

The commands must:

- Plan the worktree path and branch without creating them.
- Require one builder agent per worktree.
- Deny direct master/main writes.
- Deny auto-merge and force-push.
- Generate file allowlist/denylist.
- Generate command allowlist/denylist.
- Generate a no-secret prompt pack preview.
- Generate rollback and rejection flow.
- Require post-builder policy review and evidence bundle.
- Return blocked/retry cases to OpenAI Auditor for correction planning.

The commands must not:

- Execute Claude.
- Call Anthropic or OpenAI.
- Create a real worktree.
- Read or print env files.
- Execute SQL/RLS/storage changes.
- Deploy.
- Call paid APIs.
- Enable scheduler or automatic Claude execution.

`SANDBOX_SIMULATION_PASS` means only that the boundary model is coherent enough for a future human-approved sandbox execution design sprint.

---

## 16. Runner Approval Interface

Before a real worktree can be created in a future sprint, the runner must validate an approval contract:

```bash
python -B project_autopilot/claude_sandbox_runner.py --project mira --approval-preflight --task "<task>"
python -B project_autopilot/claude_sandbox_runner.py --project mira --dry-run --task "<task>"
```

Current behavior:

- Worktree creation disabled.
- Builder execution disabled.
- Real worktree creation blocked.
- Approval statuses are future-only.
- Runner plan and approval preview are evidence only.

## 16. Manual Claude Handoff

After an approved sandbox worktree exists, Project Autopilot may generate a manual Claude Code handoff packet:

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-manual-handoff-dry-run --task "<task>"
python -B project_autopilot/agent_loop.py --project mira --claude-manual-handoff-create-approved --task "<task>"
```

The handoff packet tells the human to open Claude Code in the sandbox worktree path and paste the packet manually. It includes allowlists, denylists, stop conditions, validation commands, the required builder report format, the post-builder intake command, and cleanup instructions.

This is still manual-only. Project Autopilot must not execute Claude, call Anthropic/OpenAI, run Claude Code, edit sandbox files, commit in the sandbox, merge to master, read env files, deploy, execute SQL/RLS, call paid APIs, enable scheduler, or enable automatic Claude execution.

The next phase is the first real manual Claude builder task inside an approved sandbox worktree, followed by `--post-builder <report>` policy review.
