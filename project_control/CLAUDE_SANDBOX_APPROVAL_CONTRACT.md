# Claude Sandbox Approval Contract

Status: active interface, dry-run only

Purpose: define the exact human approval object required before any future Claude sandbox worktree creation or builder execution.

## Current Rule

`APPROVED_FOR_WORKTREE_CREATION_ONLY` is active and permits creating sandbox worktrees for manual Claude handoff. Claude builder execution inside the sandbox is manual — the human opens Claude Code and pastes the handoff packet. Automated builder execution remains future-only. No approval status enables automatic Claude execution, auto-merge, deploy, SQL/RLS work, env access, or paid APIs.

See `CLAUDE_MANUAL_HANDOFF_PROTOCOL.md` for the full manual handoff lifecycle.

## Approval Statuses

- `APPROVAL_NOT_REQUESTED`
- `APPROVAL_REQUESTED`
- `APPROVED_FOR_DRY_RUN_ONLY`
- `APPROVED_FOR_WORKTREE_CREATION_ONLY`
- `APPROVED_FOR_WORKTREE_CREATION_FUTURE`
- `APPROVED_FOR_BUILDER_EXECUTION_FUTURE`
- `REJECTED`
- `EXPIRED`
- `INVALID`

## Worktree Creation-Only Approval

`APPROVED_FOR_WORKTREE_CREATION_ONLY` is the first approval that permits a real local side effect: creating one sandbox git worktree outside the main repository. It permits only:

- `git worktree add` for a generated `mira-sandbox-*` path under the project parent directory.
- Safe verification checks such as branch/status checks.
- Evidence writing under ignored `logs/`.
- Cleanup using the recorded sandbox path.

It still forbids Claude execution, file edits by Claude, commits in the sandbox, merges, force-pushes, env/secrets access, SQL/RLS, deploys, paid APIs, scheduler changes, and automatic Claude execution.

## Required Contract Fields

- `project_id`
- `task_id`
- `task_summary`
- `requested_provider`
- `requested_execution_mode`
- `allowed_files`
- `denied_files`
- `allowed_commands`
- `denied_commands`
- `max_runtime_minutes`
- `max_command_count`
- `max_file_edits`
- `requires_no_secrets`
- `requires_no_sql`
- `requires_no_deploy`
- `requires_no_paid_api`
- `requires_post_builder_policy`
- `requires_openai_auditor_review`
- `requires_rollback_plan`
- `human_approver`
- `approval_timestamp`
- `expiration_timestamp`
- `approval_scope`
- `explicit_forbidden_actions`

## Validation Rules

The contract is invalid if it lacks:

- No-secret rule.
- No SQL/RLS rule.
- No deploy rule.
- No paid API rule.
- File allowlist and denylist.
- Command allowlist and denylist.
- Rollback plan requirement.
- Post-builder policy requirement.
- OpenAI Auditor review requirement.

The contract is also invalid if it enables worktree creation beyond `APPROVED_FOR_WORKTREE_CREATION_ONLY`, or if it enables Claude builder execution in the current sprint.

## Evidence

Approval contract previews are generated under ignored logs:

```text
logs/claude_sandbox/<project_id>/latest/claude_sandbox_approval_contract_preview.json
```

The preview is evidence only. It is not an execution token.

## Safety Invariants

Regardless of approval status, the following are permanently prohibited:

- Auto-merge to any branch.
- Scheduler activation.
- Automatic Claude execution.
- Reading, printing, or modifying env/secret files.
- SQL/RLS mutations or deploys.
- Paid external API calls.
- Claude approving its own output.

These rules apply to both manual handoff and any future automated execution.
