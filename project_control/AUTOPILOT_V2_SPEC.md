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
- Route tasks to an appropriate builder mode.
- Create strict design and research gates.
- Enforce unified post-builder policy gates before commit.
- Produce readiness reports.
- Generate evidence and Control Center state.
- Block unsafe work before execution.

## 16. What v2 Cannot Do Yet

- Execute Claude automatically.
- Run scheduled autonomous cycles.
- Deploy.
- Perform live database/RLS/storage changes.
- Use paid image/video/API providers.
- Replace human design judgment for major visual work.

## 17. Definition of Done for v2

See `AUTOPILOT_DEFINITION_OF_DONE.md`.

## 18. Remaining Limitations

- Provider execution is metadata/manual only.
- Design scoring is heuristic and requires screenshots/human review for final UI approval.
- Research is request-based and does not browse automatically.
- Multi-agent parallel writes require explicit worktree discipline.
- Cloud execution and GitHub PR workflows are future work.
