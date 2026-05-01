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

Claude Agent SDK is a future formal provider requiring `ANTHROPIC_API_KEY`. Its provider may detect whether the env var name is present, but it must not print values or call Anthropic APIs until explicitly approved and budget-gated.

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
