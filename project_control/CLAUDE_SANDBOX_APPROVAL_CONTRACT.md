# Claude Sandbox Approval Contract

Status: active interface, dry-run only

Purpose: define the exact human approval object required before any future Claude sandbox worktree creation or builder execution.

## Current Rule

No approval status enables actual Claude builder execution in the current sprint. Worktree creation and builder execution are both future-only.

## Approval Statuses

- `APPROVAL_NOT_REQUESTED`
- `APPROVAL_REQUESTED`
- `APPROVED_FOR_DRY_RUN_ONLY`
- `APPROVED_FOR_WORKTREE_CREATION_FUTURE`
- `APPROVED_FOR_BUILDER_EXECUTION_FUTURE`
- `REJECTED`
- `EXPIRED`
- `INVALID`

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

The contract is also invalid if it enables worktree creation or builder execution in the current sprint.

## Evidence

Approval contract previews are generated under ignored logs:

```text
logs/claude_sandbox/<project_id>/latest/claude_sandbox_approval_contract_preview.json
```

The preview is evidence only. It is not an execution token.
