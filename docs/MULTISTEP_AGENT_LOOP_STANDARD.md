# Multi-Step Agent Loop Standard

## Purpose

The multi-step loop defines how Project Autopilot will eventually coordinate a planner/auditor, a builder, QA, evidence, blockers, retries, and policy gates.

This is a state model and dry-run scaffold only. It is not automatic execution.

## Lifecycle States

- `OBJECTIVE_RECEIVED`
- `OPENAI_PLANNING`
- `BUILDER_SELECTED`
- `ASSIGNED_TO_CLAUDE`
- `ASSIGNED_TO_CODEX`
- `BUILDER_RUNNING`
- `BUILDER_BLOCKED`
- `OPENAI_REVIEWING_BLOCKER`
- `CORRECTION_PROMPT_READY`
- `BUILDER_RETRY_READY`
- `BUILDER_DONE`
- `OPENAI_REVIEWING_OUTPUT`
- `VALIDATING`
- `POLICY_REVIEW`
- `SAFE_TO_COMMIT`
- `NEEDS_FIX`
- `BLOCKED`
- `HUMAN_REVIEW_REQUIRED`
- `DONE`

## Current Commands

```bash
python -B project_autopilot/multistep_loop.py --project mira --status
python -B project_autopilot/multistep_loop.py --project mira --dry-run-objective "Improve MIRA result page design"
python -B project_autopilot/agent_loop.py --project mira --multistep-dry-run --objective "Improve MIRA result page design"
```

These commands must not call OpenAI, call Anthropic, execute builders, run scheduler, deploy, mutate Supabase, or edit product code.

## Blocker and Retry Model

If Claude or Codex is blocked, the builder returns a report to Project Autopilot. OpenAI Auditor may diagnose and draft a correction prompt in dry-run/planning mode. The builder retries only after human or policy-approved handoff.

## Completion Model

When the builder finishes, OpenAI Auditor may review the evidence, but Project Autopilot remains final judge:

1. Validation commands.
2. Flow QA/mock E2E if relevant.
3. Design Director if UI/design changed.
4. Research Director if uncertain/vendor/security/paid decisions changed.
5. Backend audit if backend/security changed.
6. Post-builder policy.
7. Definition of Done.

Only `SAFE_TO_COMMIT` permits commit.

## Disabled Until Separate Approval

- Automatic Claude execution.
- Scheduler.
- Auto-merge.
- Deployment.
- Live SQL/RLS/storage mutation.
- Paid APIs.
- Multi-agent parallel writes without dedicated worktrees.
