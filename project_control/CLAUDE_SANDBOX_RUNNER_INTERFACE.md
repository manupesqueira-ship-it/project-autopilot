# Claude Sandbox Runner Interface

Status: active interface, dry-run only

Purpose: define how Project Autopilot will eventually coordinate a human-approved Claude sandbox runner without enabling it yet.

## Runner States

- `RUNNER_DISABLED`
- `APPROVAL_REQUIRED`
- `APPROVAL_VALIDATED_DRY_RUN_ONLY`
- `WORKTREE_CREATION_BLOCKED_THIS_SPRINT`
- `BUILDER_EXECUTION_BLOCKED_THIS_SPRINT`
- `READY_FOR_FUTURE_HUMAN_APPROVED_WORKTREE`
- `WORKTREE_CREATION_APPROVED`
- `WORKTREE_CREATED`
- `WORKTREE_CLEANUP_REQUIRED`
- `WORKTREE_CLEANED_UP`
- `REJECTED`
- `BLOCKED`

## Commands

```bash
python -B project_autopilot/claude_sandbox_runner.py --project mira --status
python -B project_autopilot/claude_sandbox_runner.py --project mira --approval-preflight --task "<task>"
python -B project_autopilot/claude_sandbox_runner.py --project mira --dry-run --task "<task>"
python -B project_autopilot/claude_sandbox_runner.py --project mira --rollback-plan --task "<task>"
```

Agent loop wrappers:

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-sandbox-runner-status
python -B project_autopilot/agent_loop.py --project mira --claude-sandbox-approval-preflight --task "<task>"
python -B project_autopilot/agent_loop.py --project mira --claude-sandbox-runner-dry-run --task "<task>"
```

Worktree creation-only commands:

```bash
python -B project_autopilot/worktree_sandbox.py --project mira --create-approved --task "Sandbox worktree creation smoke test"
python -B project_autopilot/worktree_sandbox.py --project mira --cleanup-approved --task-id "<task_id>"
python -B project_autopilot/agent_loop.py --project mira --claude-worktree-smoke-test
```

## Current Guarantees

The runner interface must not:

- Execute Claude.
- Call Anthropic.
- Call OpenAI.
- Create a real worktree except through the explicit worktree creation-only approval command.
- Edit product code.
- Read env files.
- Print secrets.
- Execute SQL/RLS.
- Deploy.
- Call paid APIs.
- Enable scheduler.
- Enable automatic Claude execution.
- Auto-merge.

## Evidence Contract

The runner writes ignored evidence:

```text
logs/claude_sandbox/<project_id>/latest/claude_sandbox_runner_plan.md
logs/claude_sandbox/<project_id>/latest/claude_sandbox_runner_plan.json
logs/claude_sandbox/<project_id>/latest/claude_sandbox_approval_contract_preview.json
logs/claude_sandbox/<project_id>/latest/worktree_creation.md
logs/claude_sandbox/<project_id>/latest/worktree_creation.json
logs/claude_sandbox/<project_id>/latest/worktree_cleanup.md
logs/claude_sandbox/<project_id>/latest/worktree_cleanup.json
```

## Worktree Creation-Only Flow

The approved creation flow may create one sandbox worktree at `C:\Users\manup\projects\mira-sandbox-<task_id>` on branch `sandbox/claude-<task_id>`. It may verify branch/status and write evidence. It may not run Claude, edit files, commit, merge, call providers, read env files, or run arbitrary commands.

Cleanup uses only recorded evidence and refuses arbitrary paths. It removes only a path matching the `mira-sandbox-*` pattern under the project parent directory.

## Manual Claude Handoff

The manual handoff flow may generate a no-secret packet for a human to paste into Claude Code after an approved sandbox worktree exists:

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-manual-handoff-dry-run --task "<task>"
python -B project_autopilot/agent_loop.py --project mira --claude-manual-handoff-create-approved --task "<task>"
```

The packet must include the sandbox path, branch, allowed files, denied files, allowed commands, denied commands, stop conditions, required builder report format, post-builder command, and cleanup command. Project Autopilot still does not run Claude Code, call Anthropic/OpenAI, edit files inside the sandbox, commit, merge, or deploy.

## Rollback, Rejection, Cancellation

Rollback/rejection/cancellation are dry-run checklists now. Future implementation must preserve evidence, avoid rewriting history, park rejected worktrees, and return blocked work to OpenAI Auditor for correction planning.

## Next Phase

The next phase may run the first real manual Claude Code task inside an already approved sandbox worktree. Claude builder execution by Project Autopilot remains a later, separately approved phase.
