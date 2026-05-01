# Claude Manual Handoff Protocol

**Status:** Active, manual-only  
**Last updated:** 2026-05-01

---

## Purpose

This document defines the exact lifecycle for a manual Claude Code builder task inside a Project Autopilot sandbox worktree. It is the single reference for operators and Claude builders during manual handoff execution.

---

## Commands

Dry-run packet only:

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-manual-handoff-dry-run --task "<task>"
```

Create one approved sandbox worktree and handoff packet:

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-manual-handoff-create-approved --task "<task>"
```

Post-builder intake after the human saves Claude's report:

```bash
python -B project_autopilot/agent_loop.py --project mira --post-builder <path_to_claude_builder_report>
```

Cleanup:

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-worktree-cleanup-approved --task-id "<task_id>"
```

Direct module commands:

```bash
python -B project_autopilot/claude_manual_handoff.py --project mira --task "<task>" --dry-run
python -B project_autopilot/claude_manual_handoff.py --project mira --task "<task>" --create-worktree-approved
```

---

## 1. Manual Handoff Lifecycle

```text
1. Project Autopilot generates a handoff packet and creates an approved worktree.
2. Human reviews the packet and opens Claude Code in the sandbox worktree directory.
3. Human pastes the handoff packet into Claude Code manually.
4. Claude edits only the files listed in the packet's allowed files section.
5. Claude runs the validation commands listed in the packet.
6. Claude produces a builder report in the chat response.
7. Human saves the builder report to a markdown file.
8. Human runs post-builder policy from the main repo:
   python -B project_autopilot/agent_loop.py --project <id> --post-builder <report_path>
9. Project Autopilot policy produces a verdict (SAFE_TO_COMMIT / NEEDS_FIX / BLOCKED).
10. Human decides: commit, fix, or abandon.
11. Human runs cleanup when the sandbox is no longer needed.
```

**Key rule:** Claude never approves its own work. Project Autopilot post-builder policy is the final judge.

---

## 2. What Claude May Do

Inside the sandbox worktree, Claude may:

- Read files within the worktree to understand context.
- Edit files listed in the handoff packet's allowed files section.
- Create new files only if they fall within the allowed files scope.
- Run validation commands listed in the handoff packet (lint, typecheck, build, git checks).
- Run `git status`, `git diff`, and `git log` for awareness.
- Commit to the sandbox branch if all validations pass and only allowed files changed.
- Produce a structured builder report.

---

## 3. What Claude Must Not Do

Claude must never:

| Prohibition | Category |
|---|---|
| Read, print, copy, or modify `.env`, `.env.local`, `.env.*`, keys, tokens, or credentials | Secrets |
| Execute SQL, enable RLS, alter policies, or modify Supabase live resources | Database |
| Deploy to production or staging | Deploy |
| Call OpenAI, Anthropic, or any paid external API | Paid APIs |
| Enable scheduler or automatic Claude execution | Automation |
| Auto-merge, force-push, rebase shared branches, or rewrite git history | Git safety |
| Edit files outside the allowed files list | Scope |
| Run commands outside the allowed commands list | Scope |
| Install packages (`npm install`, `pip install`) | Scope |
| Push to remote unless explicitly approved in the packet | Git safety |
| Approve its own work or bypass post-builder policy | Self-approval |

---

## 4. When to Stop Immediately

Claude must stop work and report the blocker if any of the following occur:

1. The task requires reading or modifying env/secret files.
2. The task requires live SQL, RLS, or storage policy changes.
3. The task requires deploying, enabling scheduler, or enabling automatic Claude execution.
4. The task requires editing files outside the allowed files list.
5. The task requires running commands outside the allowed commands list.
6. A validation command fails and the fix would require touching disallowed files.
7. The task requires calling a paid external API.
8. The builder cannot produce a complete report.
9. Any command or file from the deny list is triggered.

**When stopped:** Report exactly what happened, what was attempted, and why it cannot proceed. Do not attempt workarounds that violate the packet boundaries.

---

## 5. How to Return the Builder Report

After finishing work, Claude must produce a builder report **in the chat response** with this exact structure:

```markdown
# Manual Claude Builder Report

## Task
- Title: <task title>
- Sandbox worktree path: <path>
- Sandbox branch: <branch>

## Files Created
- None, or list paths.

## Files Modified
- None, or list paths.

## Commands Run
- Command, exit code, concise result.

## Validation Results
- lint/typecheck/build/QA results, or explain not run.

## Evidence Captured
- Screenshots/logs/reports, sanitized only.

## Blockers
- None, or list blockers.

## Risks
- None, or list risks.

## Git Status
- Paste `git status --short` from the sandbox worktree.

## Safety Checklist
- External APIs called: YES/NO (expected: NO)
- Secrets/env files touched: YES/NO (expected: NO)
- Scheduler enabled: YES/NO (expected: NO)
- Automatic Claude execution enabled: YES/NO (expected: NO)
- MIRA product code touched: YES/NO (expected: NO)

## Commit
- Commit created: YES/NO
- Commit hash: <hash or N/A>

## Current State
- Current branch: <branch>
- Current git status: <clean/dirty>

## Return Command
python -B project_autopilot/agent_loop.py --project <id> --post-builder <path_to_this_report>
```

The human saves this report to a file and runs the return command from the **main repo**, not the sandbox.

---

## 6. Cleanup Instructions

When the sandbox is no longer needed, the human runs from the **main repo**:

```bash
python -B project_autopilot/agent_loop.py --project <id> --claude-worktree-cleanup-approved --task-id "<task_id>"
```

Cleanup rules:

- Only the human initiates cleanup. Claude does not clean up the sandbox.
- Cleanup removes only the recorded `mira-sandbox-*` path.
- Cleanup refuses arbitrary paths.
- The sandbox must remain active until Project Autopilot post-builder review completes.

---

## 7. Packet Evidence

The packet and metadata are written under ignored logs:

```text
logs/claude_sandbox/<project_id>/latest/manual_handoff_packet.md
logs/claude_sandbox/<project_id>/latest/manual_handoff_metadata.json
```

The metadata must show that Project Autopilot did not execute Claude, did not call Anthropic/OpenAI, did not enable automatic Claude execution, and did not touch product code.

---

## 8. Non-Negotiable Safety Rules

These rules apply to every manual Claude handoff, without exception:

1. **No auto-merge.** Claude never merges to main, develop, or any protected branch.
2. **No scheduler.** Claude never enables or modifies scheduler configuration.
3. **No automatic Claude execution.** Claude never enables `allow_automatic_builder_execution`.
4. **No env/secrets.** Claude never reads, prints, copies, or modifies secret files.
5. **No SQL/RLS/deploy.** Claude never executes database mutations or deploys.
6. **No paid APIs.** Claude never calls OpenAI, Anthropic, or other paid external APIs.
7. **No self-approval.** Claude cannot approve its own output. Post-builder policy decides.

---

## 9. Cross-References

| Document | Purpose |
|---|---|
| `CLAUDE_SANDBOX_RUNNER_INTERFACE.md` | Runner states and commands |
| `CLAUDE_SANDBOX_APPROVAL_CONTRACT.md` | Approval contract fields and validation |
| `AUTOPILOT_WORKTREE_SANDBOX_STRATEGY.md` | Worktree lifecycle and sandbox rules |
| `AUTOPILOT_AGENT_OPERATING_MODEL.md` | Agent roles and task lifecycle |
| `project_autopilot/README.md` | Quick reference and operator commands |
