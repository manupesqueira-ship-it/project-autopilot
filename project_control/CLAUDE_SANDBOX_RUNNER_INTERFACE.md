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

## Current Guarantees

The runner interface must not:

- Execute Claude.
- Call Anthropic.
- Call OpenAI.
- Create a real worktree.
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
```

## Rollback, Rejection, Cancellation

Rollback/rejection/cancellation are dry-run checklists now. Future implementation must preserve evidence, avoid rewriting history, park rejected worktrees, and return blocked work to OpenAI Auditor for correction planning.

## Next Phase

The next phase may create a human-approved worktree only. Claude builder execution remains a later, separately approved phase.
