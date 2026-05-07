# Project Autopilot — GitHub Actions Plan

**Status:** Planning / Not yet deployed  
**Last updated:** 2026-04-30

---

## 1. Why GitHub Actions

GitHub Actions provides:
- Ephemeral, clean execution environment per run (no state pollution)
- Native integration with PR workflow (the primary review mechanism)
- Audit trail via Actions logs (90-day retention)
- Secret management via GitHub Secrets (not committed)
- Branch protection and required check enforcement
- Free tier for public repos, cost-controlled for private

GitHub Actions is the correct home for CI-style agent runs:
- Read-only analysis of diffs
- Policy gate checks
- Agent review posting as PR comments
- Evidence artifact archival

GitHub Actions is NOT the correct home for:
- Long-running background polling (that is VPS)
- Live Supabase migrations (that is human + manual)
- Auto-merge (permanently prohibited)

---

## 2. Claude Code GitHub Action Role

Claude Code can run as a GitHub Actions step using the official `anthropics/claude-code-action`.

Permitted role:
- Review PR diffs against AGENT_RULES / AUTONOMY_PROTOCOL
- Post structured analysis as PR comments
- Flag policy violations as required-check failures
- Generate architecture review comments for design PRs

Configuration:
```yaml
# .github/workflows/claude-review.yml (future, do not create yet)
name: Claude Code Review
on:
  pull_request:
    types: [opened, synchronize]
  issue_comment:
    types: [created]  # triggers on /review comment

jobs:
  claude-review:
    if: |
      github.event_name == 'pull_request' ||
      (github.event_name == 'issue_comment' && 
       contains(github.event.comment.body, '/review'))
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write  # write comments only
    steps:
      - uses: actions/checkout@v4
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          # Additional config: model, system prompt pointing to AGENT_RULES
```

What Claude Code may NOT do in this workflow:
- Push commits
- Merge PRs
- Approve PRs (this is a GitHub policy decision, not Claude's)
- Write files to the repo
- Execute SQL or call Supabase

---

## 3. Codex / Cloud Builder Role

Codex (OpenAI) can be triggered from GitHub Actions to generate code in a worktree branch.

Codex workflow pattern:
```
trigger: /build-feature comment on issue or PR
  → GitHub Action starts
  → Creates git worktree branch: codex/task-<id>
  → Runs Codex with task spec from project_control/TASK_QUEUE.md
  → Codex writes to worktree only
  → Action opens draft PR from codex branch
  → Human reviews diff
  → Requires explicit human approval before merge
  → Evidence artifact attached to PR
```

Codex is never the approver of its own output.  
Codex never pushes to main, develop, or any protected branch.

---

## 4. PR-Based Workflow

All agent-generated code enters the repo via pull request. No exceptions.

PR workflow:
```
1. Agent (Codex or Claude) writes to isolated branch
2. PR opened as DRAFT automatically
3. Required checks run (lint, typecheck, build, policy gate)
4. Claude Code review posted as comment
5. Evidence artifact attached
6. Human converts draft → ready for review
7. Human reviews diff
8. Human approves and merges (only human can merge)
```

PR title format for agent-generated PRs:
```
[AGENT] <task-id>: <short description>
```

PR description must include:
- Task ID and source from TASK_QUEUE
- Agent that generated the code
- Evidence record reference
- Cycle ID
- Token usage and cost
- What was and was not tested

---

## 5. Branch Protection

Protected branches: `main`, `develop` (if used)

Required settings:
```
- Require pull request before merging: YES
- Require approvals: 1 (human owner)
- Dismiss stale reviews: YES
- Require status checks to pass: YES
- Require branches to be up to date: YES
- Include administrators: YES (prevents owner bypass)
- Restrict who can push: NO robots (humans only)
- Allow force pushes: NO
- Allow deletions: NO
```

No automation may bypass branch protection.  
No `--no-verify` in any CI workflow.

---

## 6. Required Checks

Before any PR can merge, these checks must pass:

| Check | What it verifies |
|-------|-----------------|
| `lint` | Code style, no obvious errors |
| `typecheck` | TypeScript/Python type safety |
| `build` | Project builds without error |
| `policy-gate` | Agent Rules / Autonomy Protocol compliance |
| `no-secrets-check` | No committed secrets (gitleaks or similar) |

Policy gate check is implemented as a Python script reading AGENT_RULES.md and validating the diff.

Future checks (not yet):
- `test` — unit and integration tests
- `claude-review` — Claude Code analysis (informational, not blocking initially)

---

## 7. Autopilot Policy Gates

The policy gate runs as a required CI check:

```python
# project_autopilot/policy/ci_gate.py (future)
# Checks the PR diff against AGENT_RULES.md rules:
# - No .env files modified
# - No secrets introduced
# - No direct Supabase DDL in app code
# - No scheduler enablement
# - No direct push to main
# - No auto-merge logic introduced
# Returns: exit 0 (pass) or exit 1 (fail with reason)
```

Policy gate failures block merge and post detailed comment explaining the violation.

---

## 8. Secret Handling

GitHub Secrets used by workflows:

| Secret name | Used by | Scope |
|-------------|---------|-------|
| `ANTHROPIC_API_KEY` | Claude Code review, Claude SDK | Repo |
| `OPENAI_API_KEY` | Codex builder | Repo |
| `TELEGRAM_BOT_TOKEN` | Notification step | Repo |
| `TELEGRAM_CHAT_ID` | Notification step | Repo |

Rules:
- Secrets are never printed in logs (`::add-mask::` enforced)
- Secrets are never passed as env vars to untrusted steps
- No Supabase service key in GitHub Secrets until RLS audit complete
- No production database credentials in CI ever
- Rotate all secrets if a workflow log is accidentally made public

---

## 9. No Live Supabase Changes from CI

This is a hard rule. Rationale:

- RLS audit is not complete
- Live data is real user data
- Migrations are irreversible
- CI runners are ephemeral and cannot be trusted as migration runners

What CI may do with Supabase:
- Run tests against a local Supabase instance (future)
- Validate migration files for syntax errors (future)
- Check that migration files match expected schema (future)

What CI may NEVER do:
- Execute `supabase db push` against production
- Call Supabase REST API with service key
- Modify RLS policies
- Seed production data

---

## 10. No Deploy Until Explicit Approval

The deploy step is always the last step and always gated.

Deploy gate:
```yaml
# Future pattern
deploy:
  needs: [lint, typecheck, build, policy-gate, no-secrets-check]
  environment: production  # GitHub environment requires human approval
  steps:
    - name: Deploy (requires human approval in GitHub UI)
      ...
```

GitHub Environments with required reviewers ensures a human clicks "Approve" in the GitHub UI before any deploy runs.

This cannot be bypassed by any agent.

---

## 11. How PR Comments Trigger Agents

Supported comment commands (future):

| Comment | Triggered agent | What happens |
|---------|----------------|-------------|
| `/review` | Claude Code | Posts diff analysis as comment |
| `/build-feature` | Codex | Creates worktree branch, opens draft PR |
| `/policy-check` | Autopilot policy gate | Runs policy gate, posts result |
| `/evidence` | Autopilot | Retrieves evidence record for this cycle |

Implementation pattern:
```yaml
on:
  issue_comment:
    types: [created]

jobs:
  dispatch:
    if: startsWith(github.event.comment.body, '/')
    runs-on: ubuntu-latest
    steps:
      - name: Parse command
        # Validate comment author is authorized
        # Route to correct agent workflow
        # Post acknowledgement comment
```

Authorization: only repo collaborators can trigger agent commands.  
Public commenters are silently ignored.

---

## 12. How Control Center / Evidence Connects

Every workflow run that invokes an agent must:

1. Produce a JSON evidence record (see AUTOPILOT_CLOUD_EXECUTION_ARCHITECTURE.md §12)
2. Upload it as a GitHub Actions artifact: `actions/upload-artifact@v4`
3. Post a summary as a PR comment with: cycle_id, agent, verdict, cost, artifact link
4. Send Telegram notification if configured

Evidence artifacts:
- Retention: 30 days (GitHub default)
- Format: `evidence_<cycle_id>.json`
- Never contains secrets (validated by policy gate)

Long-term evidence archive: `/home/autopilot/evidence/` on VPS (outside git)

---

## 13. Future Roadmap

| Phase | GitHub Actions milestone |
|-------|------------------------|
| Phase 1 | Claude Code review workflow (read-only, informational) |
| Phase 2 | Policy gate as required check |
| Phase 3 | Codex builder workflow (draft PRs to worktree branches) |
| Phase 4 | Automated evidence archival to VPS |
| Phase 5 | PR comment command routing |
| Phase 6 | Scheduled analysis cycles (disabled by default) |
| Phase 7 | Full audit-trail dashboard integration |

Each phase requires:
- Human sign-off in project_control
- Clean run history from previous phase
- Updated AGENT_RULES.md to reflect new permissions
