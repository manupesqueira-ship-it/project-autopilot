# Project Autopilot v2 Spec

## 1. Purpose

Project Autopilot is a reusable autonomous control plane for software projects. It coordinates planning, builder handoff, QA, design review, research, evidence, blockers, validation, and safe commit decisions across projects.

Project Autopilot is a control plane, not a replacement for Codex, Claude, Lovable, Replit, or other builders.

## 2. Non-Goals

- Do not replace coding agents.
- Do not enable scheduler yet.
- Do not enable automatic Claude execution yet.
- Do not deploy.
- Do not call paid APIs by default.
- Do not bypass human approval for security, secrets, database, privacy, legal, deployment, or paid-provider decisions.

## 3. Current Capabilities

- Doctor, status, backend audit, Browser QA, Flow QA, no-human mock E2E validation.
- Managed dev server runner.
- Control Center.
- Readiness reports.
- Evidence bundles.
- Run history and metrics.
- Risk classifier.
- Run lock and HALT support.
- Post-builder intake and QA verdicts.
- Manual Claude handoff.
- Codex as current primary builder.

## 4. Target Architecture

Project Autopilot v2 is organized as:

- Project-specific context in `project_control/`.
- Reusable orchestration code in `project_autopilot/`.
- Provider registry for builder capabilities.
- Builder Orchestrator for task routing.
- QA/evidence engine for validation.
- Design Director for UI quality.
- Research Director for decisions needing evidence.
- Control Center for human-readable state.

## 5. Agent Provider Model

Providers expose metadata only until execution modes are explicitly enabled:

- Provider ID.
- Display name.
- Provider type.
- Configured status.
- Capabilities.
- Risks.
- Required environment variables.
- Missing environment variable names only.
- Supported execution modes.
- Current status.
- Notes.

## 6. Builder Orchestration Model

The Builder Orchestrator decides:

- Recommended provider.
- Fallback provider.
- Execution mode.
- Required approvals.
- Whether research is required.
- Whether design review is required.
- Whether backend/security review is required.
- Whether Flow QA is required.
- Risk level.
- Stop conditions.
- Validation commands.
- Auto-commit policy.
- Allowed and disallowed file scopes.

It does not execute builders in v2 foundation.

## 7. Claude Integration Model

Claude Code is a future/manual/CLI provider. It may be used through manual prompt handoff today and future CLI non-interactive mode later.

Automatic Claude execution remains disabled.

Claude Agent SDK is a future formal provider requiring `ANTHROPIC_API_KEY`. Its provider may detect whether the env var is `PRESENT_VALUE_HIDDEN`, `MISSING`, or `EMPTY`, but it must not print values or call Anthropic APIs until explicitly approved and budget-gated.

Claude Agent SDK dry-run readiness is validated with:

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-sdk-dry-run
```

Dry-run mode confirms provider routing, key presence, policy fixtures, post-builder gates, cost/budget controls, worktree/sandbox documentation, and explicit approval requirements. It does not import or call the live SDK in a way that can make network requests.

## 8. Codex Integration Model

Codex is the current primary builder. Project Autopilot generates prompts, plans validation, collects evidence, and runs QA around Codex work.

Project Autopilot does not execute Codex itself.

## 9. Design Director Model

The Design Director enforces a strict quality bar for visual hierarchy, spacing, typography, color discipline, accessibility, CTA clarity, responsiveness, interaction feedback, loading/error states, originality, premium feel, brand coherence, copy clarity, flow friction, emotional pull, information density, trust, and product-market tone fit.

It is heuristic/static first and must be honest when screenshots or human visual review are required.

## 10. Research Director Model

The Research Director identifies when implementation should pause for research. It does not run research automatically and does not invent sources.

Research is required or recommended for vendor choices, security-sensitive decisions, paid APIs, legal/privacy issues, UX benchmarks, unknown architecture, cloud/VPS/deployment design, AI model/vendor comparison, generation provider choice, retention policy, RLS/security design, and innovation benchmarks.

## 11. QA/Evidence Model

Every meaningful run should leave evidence:

- Git status and diff.
- Changed files.
- Command outputs.
- QA verdict.
- Browser/Flow QA reports.
- Backend audit when relevant.
- Design Director review when relevant.
- Research requests when relevant.
- Blockers and human questions.

## 11.1 Post-Builder Policy Enforcement

After a builder finishes, Project Autopilot must decide whether the work is safe to commit. The v2 post-builder policy consumes provider status, risk classification, changed files, forbidden path checks, validation evidence, Design Director, Research Director, backend audit, Flow QA, evidence bundles, and the Definition of Done.

Unified verdicts:

- `SAFE_TO_COMMIT`
- `NEEDS_FIX`
- `BLOCKED`
- `HUMAN_REVIEW_REQUIRED`
- `SAFE_NO_CHANGES`

`SAFE_TO_COMMIT` requires all applicable hard gates to pass. `NEEDS_FIX` means a builder can safely correct the work. `BLOCKED` means the builder must not bypass the gate and a human decision or safer alternative is required. `HUMAN_REVIEW_REQUIRED` means the system cannot honestly approve the work without human visual, research, security, or strategic review.

Post-builder policy behavior is protected by a deterministic fixture suite:

```bash
python -B project_autopilot/policy_test_fixtures.py --project mira --run all
```

The fixtures use simulated changed files and builder reports. They do not touch real env files, mutate Supabase, call external APIs, execute SQL, deploy, enable scheduler, or execute builders. The suite must pass before Project Autopilot expands into Claude Agent SDK execution, scheduler runs, or automatic builder execution.

## 11.2 Operational Health

Project Autopilot exposes a consolidated operator command:

```bash
python -B project_autopilot/agent_loop.py --project mira --autopilot-health
```

This command summarizes provider registry, Design Director, Research Director, Builder Orchestrator, Autopilot v2 check, post-builder policy availability, policy fixture health, Flow QA/mock E2E, backend audit, MIRA readiness, Control Center, HALT/run lock, scheduler status, automatic Claude execution status, Claude Agent SDK readiness, blockers, next actions, and evidence paths.

MIRA real-data blockers should not make the control plane blocked unless they block Project Autopilot itself. Scheduler disabled and automatic Claude execution disabled are expected/pass states.

Pre-Claude readiness requires local `ANTHROPIC_API_KEY`, provider dry-run mode, sandbox/worktree policy, allowlist/denylist, cost/budget gates, passing policy fixtures, and explicit human approval for the first live Claude SDK call. Project Autopilot must not call Anthropic during readiness checks.

The controlled live Claude analysis call is a future phase. It must be analysis-only, human-approved, budget-gated, and unable to edit files. Sandboxed builder execution is a later phase after that.

The controlled analysis command is:

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-analysis-approved --task "<analysis task>"
```

It may make exactly one Anthropic call only when explicitly approved. It must sanitize the prompt, send no secrets, use no tools, edit no files, execute no commands, and save ignored evidence. This is not builder execution and does not enable automatic Claude execution.

After the call, Project Autopilot must run a local Claude analysis review:

```bash
python -B project_autopilot/claude_analysis_review.py --project mira --latest
```

The review reads saved evidence only, makes no external API calls, extracts Claude risks/recommendations, maps them to policy gates, and emits `PROCEED_TO_SANDBOX_DESIGN`, `NEEDS_POLICY_FIXTURE`, `NEEDS_RESEARCH`, `BLOCKED`, or `HUMAN_REVIEW_REQUIRED`.

`PROCEED_TO_SANDBOX_DESIGN` means only that a sandbox design sprint may begin. It does not enable Claude builder execution, scheduler, deploy automation, auto-merge, live DB changes, or paid APIs.

## 12. Human Approval Gates

Human approval is required for:

- Secrets or env changes.
- Live DB/Supabase changes.
- SQL/RLS/storage policies.
- Deployment.
- Paid API usage.
- Legal/privacy/data retention decisions.
- Automatic builder execution.
- Scheduler activation.
- Parallel writes without worktrees.

## 13. Cloud/GitHub/VPS Roadmap

Future phases may support GitHub PR execution, cloud runners, VPS scheduled operation, provider-managed agent sessions, and dashboard-based approvals.

These are not enabled in v2 foundation.

## 14. Security Model

- Secrets are never printed.
- Env files are not edited by agents.
- Paid APIs are disabled by default.
- Scheduler remains disabled.
- Automatic Claude execution remains disabled.
- Deploy automation remains disabled.
- Worktrees are required for parallel writes.
- HALT and run lock must be respected.

## 15. What v2 Can Do

- Describe available providers.
- Model OpenAI Auditor as a planner/reviewer provider in dry-run mode.
- Preview a multi-step planner-builder-review-policy lifecycle without execution.
- Route tasks to an appropriate builder mode.
- Create strict design and research gates.
- Enforce unified post-builder policy gates before commit.
- Produce readiness reports.
- Generate evidence and Control Center state.
- Block unsafe work before execution.

## 16. What v2 Cannot Do Yet

- Execute Claude automatically.
- Execute OpenAI Auditor live calls automatically.
- Run the multi-step agent loop automatically.
- Run scheduled autonomous cycles.
- Deploy.
- Perform live database/RLS/storage changes.
- Use paid image/video/API providers.
- Replace human design judgment for major visual work.

## 17. Definition of Done for v2

See `AUTOPILOT_DEFINITION_OF_DONE.md`.

## 18. Remaining Limitations

- Provider execution is metadata/manual only.
- OpenAI Auditor is dry-run only until a controlled live auditor-call sprint is explicitly approved.
- Multi-step loop is a scaffold, not an execution engine.
- Design scoring is heuristic and requires screenshots/human review for final UI approval.
- Research is request-based and does not browse automatically.
- Multi-agent parallel writes require explicit worktree discipline.
- Cloud execution and GitHub PR workflows are future work.

## 19. Claude Sandboxed Builder Boundary

Project Autopilot v2 now models the boundary needed before Claude can ever act as a sandboxed builder:

- `claude_sandbox_boundary.py` evaluates worktree, file, command, prompt, rollback, evidence, and post-builder policy requirements.
- `claude_prompt_pack.py` generates a no-secret prompt pack preview for future manual/human-approved Claude builder handoff.
- `worktree_sandbox.py` plans the branch/worktree lifecycle without creating a real worktree.
- `--claude-sandbox-preflight` runs the boundary and writes ignored evidence.
- `--claude-sandbox-simulate` simulates the future lifecycle without executing providers.

The boundary requires one agent per worktree, no direct master writes, no auto-merge, no force-push, no env/secret access, no SQL/RLS/deploy/paid API commands, no scheduler activation, no automatic Claude execution, a rollback plan, an evidence bundle, and post-builder policy review.

This is still not builder execution. Future sandboxed Claude execution requires a separate human-approved sprint after the preflight and simulation remain green.

## 20. Human-Approved Claude Sandbox Runner Interface

The runner interface defines the approval contract and state machine for future sandboxed Claude work:

- `claude_sandbox_approval.py` defines approval request, decision, status, contract, and validation result.
- `claude_sandbox_runner.py` defines dry-run runner status, approval preflight, runner dry-run, rollback/rejection/cancellation checklists, and evidence paths.
- `APPROVED_FOR_WORKTREE_CREATION_FUTURE` and `APPROVED_FOR_BUILDER_EXECUTION_FUTURE` are future-only statuses. They do not enable execution now.
- `RUNNER_DISABLED`, `APPROVAL_REQUIRED`, `APPROVAL_VALIDATED_DRY_RUN_ONLY`, `WORKTREE_CREATION_BLOCKED_THIS_SPRINT`, `BUILDER_EXECUTION_BLOCKED_THIS_SPRINT`, `READY_FOR_FUTURE_HUMAN_APPROVED_WORKTREE`, `REJECTED`, and `BLOCKED` are the runner states.

The runner must reject missing approval, missing rollback, missing post-builder policy, env/secret scope, direct master writes, auto-merge, unapproved worktree creation, arbitrary cleanup paths, and builder execution. Control Center and Autopilot Health surface the latest runner and approval status.

## 21. Worktree Creation-Only Flow

Project Autopilot may create a real sandbox worktree only through `APPROVED_FOR_WORKTREE_CREATION_ONLY` and the explicit `--claude-worktree-create-approved` or `--claude-worktree-smoke-test` command. The worktree is created outside the main repo at `mira-sandbox-<task_id>` on branch `sandbox/claude-<task_id>`.

This is still not Claude builder execution. The flow writes creation and cleanup evidence, performs only safe git status/branch verification, and removes only the recorded sandbox path during cleanup. It forbids Claude execution, file edits, commits, merges, auto-merge, external APIs, env/secrets access, SQL/RLS, deploy, scheduler changes, automatic Claude execution, and product code changes.

## 22. Manual Claude Handoff

Project Autopilot may generate a manual Claude Code handoff packet for a human-operated sandbox session:

- `claude_manual_handoff.py` generates the packet and metadata.
- `--claude-manual-handoff-dry-run` writes packet evidence without creating a worktree.
- `--claude-manual-handoff-create-approved` creates one approved sandbox worktree and writes the packet.

The packet includes the sandbox path, branch, task objective, allowed files, denied files, allowed commands, denied commands, stop conditions, validation commands, required builder report format, post-builder command, cleanup command, and evidence paths.

Manual handoff is not automatic execution. Project Autopilot does not run Claude Code, call Anthropic/OpenAI, edit files in the sandbox, commit, merge, deploy, execute SQL/RLS, access env files, call paid APIs, enable scheduler, or enable automatic Claude execution.
