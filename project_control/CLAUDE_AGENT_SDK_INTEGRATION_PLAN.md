# Claude Agent SDK Integration Plan

## Current State

Claude Agent SDK support is dry-run only. Project Autopilot can detect whether `ANTHROPIC_API_KEY` is present locally, but it never prints the value and does not call Anthropic.

Current command:

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-sdk-dry-run
```

Expected behavior:

- Detect `ANTHROPIC_API_KEY` as `PRESENT_VALUE_HIDDEN`, `MISSING`, or `EMPTY`.
- Load the Claude Agent SDK provider metadata.
- Confirm automatic Claude execution is disabled.
- Confirm live Claude calls are disabled.
- Confirm policy fixtures and post-builder gates exist.
- Write ignored reports under `logs/`.

## Provider Status Semantics

- `configured=true`: `ANTHROPIC_API_KEY` is present locally and hidden.
- `configured=false`: the key is missing or empty.
- `dry_run_only_configured`: local credentials are present, but no live call is allowed.
- `dry_run_only_missing_credentials`: dry-run provider exists, but credentials are missing or empty.

The SDK package may be missing and dry-run can still pass. Package detection is metadata-only.

## Safety Rules

- Never commit `.env`, `.env.local`, or any secret file.
- Never print `ANTHROPIC_API_KEY`.
- Never call Anthropic without explicit human approval.
- Never enable automatic Claude execution during dry-run readiness.
- Never allow Claude to write outside an approved worktree/sandbox.
- Never send secrets, cookies, JWTs, API keys, or customer data to a model prompt.

## Required Before First Controlled Live Analysis Call

1. Policy fixtures pass.
2. Post-builder policy enforcement is active.
3. Worktree/sandbox strategy is documented and followed.
4. Allowlist/denylist is active for files and commands.
5. Cost/budget gates are configured.
6. Prompt redaction rules are reviewed.
7. Human explicitly approves the single live analysis call.
8. The call is analysis-only and cannot edit files.

## Future Phases

### Phase 1: Controlled Analysis Call

One human-approved live Claude analysis call. No file edits. No command execution. No secrets. Output is reviewed by Project Autopilot and the human.

### Phase 2: Sandboxed Builder

Claude works only inside a dedicated worktree with strict allowlist/denylist, bounded commands, no secrets, no live DB mutations, and post-builder policy review.

### Phase 3: Limited Automatic Execution

Only after repeated dry-run and sandbox success. Scheduler, automatic Claude execution, and auto-commit remain separate approvals.
