# Project Autopilot v1 — Deferred Scope

**Created:** 2026-04-30
**Status:** ACTIVE — authoritative deferral register
**Purpose:** Every item in this document is explicitly out of scope for Project Autopilot v1. Nothing in this document may be built, configured, or enabled until the specific deferral condition is met and a human explicitly re-authorizes the work.

If a feature is not in this document and not in the v1 required capabilities list, it is also out of scope. When in doubt, defer.

---

## Section 1 — Deferred Until After MIRA MVP Progresses

These items exist in planning documents but must not be touched while MIRA's product core (RLS, security, production readiness, real generation providers) is the priority.

**Scheduler activation**
- The scheduler cron mechanism exists in planning docs (`TASK_QUEUE.md` "Add Scheduler — Later").
- Activation requires: manual workflow proven over multiple clean cycles, human sign-off, bounded test plan.
- Do not implement, configure, or test scheduler triggering until MIRA MVP has completed at least one real user flow with live Supabase and real providers.

**Automatic Claude execution**
- Claude Agent SDK is registered as a provider in dry-run-only mode.
- Enabling live Claude builder calls requires a separate human-approved sprint that was explicitly scoped out of v1.
- Do not enable until MIRA MVP is stable enough that automated builder cycles provide more value than risk.

**Builder Orchestrator live routing**
- The Builder Orchestrator currently selects providers and produces routing plans but does not execute.
- Live routing (actually calling Codex or Claude from the orchestrator) requires a separate controlled sprint.
- Do not enable until the policy fixture suite is extended to cover live routing scenarios and human approves.

**Research Director automated invocation**
- Research Director is manually invoked during planning sessions.
- Automating Research Director invocation (e.g., triggering on task spec detection) is not needed for v1.
- Defer until the team has used manual invocation long enough to understand the failure modes.

**Design Director blocking enforcement**
- Design Director review is currently advisory.
- Making it a hard blocking gate in CI or the post-builder policy requires a sprint to define the escalation path.
- Defer until MIRA UI work resumes in earnest and the team has calibrated acceptable failure rates.

---

## Section 2 — Deferred Until After Multiple Clean Local Cycles

These items should only be considered after the team has run at least 5 complete local cycles (plan → builder prompt → manual builder work → post-builder policy → commit) without a hard gate failure.

**OpenAI Auditor live call in automated cycle**
- Currently: `openai_auditor.py --plan` and `--status` run without calling OpenAI.
- Live call deferral condition: 5 clean local cycles, no open policy fixtures gaps, explicit human approval for the first paid OpenAI call from the orchestrator.

**Multi-step loop execution**
- Currently: `multistep_loop.py --dry-run-objective` previews lifecycle states.
- Full multi-step execution (actually progressing through lifecycle phases automatically) is deferred.
- Deferral condition: clean local cycles proven, human has reviewed a full dry-run lifecycle trace, explicit approval for first live multi-step run.

**Claude analysis live call on real task**
- Controlled analysis (`--claude-analysis-approved`) is available but has only been used in smoke tests.
- Using it on a real MIRA task requires the human to explicitly invoke it with a real task description.
- This is not deferred indefinitely — it is deferred until the team has a real analysis task that warrants it.

**Runner approval loop with real worktree creation on a real task**
- Worktree creation-only smoke test has passed.
- Creating a real worktree for a real MIRA task (not a smoke test) requires at least one clean smoke test on record and human approval for the specific task.

---

## Section 3 — Deferred Until VPS Setup

These items require infrastructure that does not exist and must not be simulated locally.

**VPS runner deployment**
- `AUTOPILOT_VPS_RUNNER_PLAN.md` and `VPS_DEPLOYMENT_PLAN.md` document the intended VPS architecture.
- No VPS runner will be deployed during v1.
- When VPS setup begins: requires a dedicated sprint, a security review of the runner environment, confirmation that the bot directory isolation rules are respected, and human sign-off before the runner goes live.

**Cloud execution architecture**
- `AUTOPILOT_CLOUD_EXECUTION_ARCHITECTURE.md` documents the intended cloud execution model.
- No cloud execution is enabled during v1.
- Deferred until VPS is set up, tested locally in isolation, and human-approved for limited cloud operation.

**Remote HALT file management**
- Currently the HALT file is managed locally.
- Remote HALT management (writing/removing HALT from a Telegram command or API endpoint) requires the VPS environment and a security review of who can remove the HALT.

**VPS-based Telegram bot with command handling**
- Currently Telegram alerts are one-way (outbound).
- Inbound command handling (e.g., `/halt`, `/resume`) requires a VPS-hosted bot, not a local process.

---

## Section 4 — Deferred Until Explicit Human Approval

These items are architecturally planned but each requires a separate, explicit human decision before any implementation begins. Planning docs existing is not approval to implement.

**GitHub Actions automation**
- `AUTOPILOT_GITHUB_ACTIONS_PLAN.md` documents the intended CI integration.
- No workflow file will be created, modified, or connected to GitHub Actions during v1.
- Requires: VPS runner plan finalized, security review of what the Actions job can access, human approval for the specific workflow scope.

**Claude Code in CI (PR review automation)**
- Claude Code posting structured review comments on PRs via GitHub Actions is architecturally planned.
- Requires: GitHub Actions automation approved, specific review scope defined, human decision on which PR checks are advisory vs. blocking.

**Auto-commit from within worktrees**
- Auto-commit (without explicit human action) is currently blocked by the manual post-builder policy.
- Enabling auto-commit requires: Definition of Done gate fully enforced, all 5 verdict states tested, human approval for auto-commit under specific conditions only.
- Even after approval, auto-commit applies only to worktree branches — never to main or protected branches.

**Agent-to-agent communication**
- No agent currently communicates directly with another agent.
- If/when the team wants OpenAI Auditor to pass a structured result to Claude Agent SDK automatically, this requires a dedicated design sprint and human approval.

**Multi-agent parallel writers**
- Multiple agents writing code in parallel (multiple simultaneous worktrees with active builders) is architecturally possible but not implemented.
- Requires: single-agent worktree flow proven over many cycles, explicit worktree isolation verified, policy fixtures covering cross-worktree conflicts, human approval for the first parallel run.

**Database migration execution from Autopilot**
- Autopilot may generate a migration plan, but it must never execute `supabase db push` or direct SQL against live databases.
- This deferral has no projected lift date — it requires extraordinary human oversight by design.

---

## Section 5 — Deferred Indefinitely

These items are prohibited until the prohibition is explicitly lifted by the human owner. There is no planned date for lifting these prohibitions.

**Auto-merge**
- No mechanism will ever merge a PR without human action.
- This prohibition applies to all agents, in all environments, permanently unless the human owner explicitly rescinds it in a new policy document.

**Push to main or protected branches from any agent**
- Agents commit to worktree branches only.
- Only the human pushes to main, or explicit CI rules that have been human-approved and are narrowly scoped.

**Live Supabase mutations from any Autopilot command without human-initiated approval flow**
- Autopilot does not write rows, run migrations, alter RLS, modify storage policies, or delete data in any Supabase instance.
- The security staging pack (`project_control/security/`) contains SQL drafts with explicit DO NOT RUN warnings.

**Paid image or video generation APIs from Autopilot**
- Autopilot does not call OpenAI image generation, Seedance, or any paid generation provider.
- If/when real generation providers are integrated into MIRA, the calls will be made from MIRA's product code, not from Autopilot.

**Accessing `/root/bot/` or any other tenant's directory on a shared VPS**
- This is a permanent security boundary.
- No agent, no script, and no CI job will read from or write to any directory other than the project's own designated workspace.

**Removing the HALT file without human action**
- HALT file removal is a human-only action.
- No script, no CI job, no Telegram command, and no policy gate outcome will remove the HALT file automatically.

**Bypassing any policy gate with a flag, environment variable, or config override**
- Policy gates are not optional.
- No `--skip-policy`, `--force`, `--no-policy` or equivalent flag will be added or honored.

**Logging or transmitting user PII or secrets in any evidence record, Telegram message, or log file**
- This prohibition is absolute, without exception.
- Any code that would log user body measurements, photos, names, or authentication tokens is a hard security failure.

---

## Enforcement

Any sprint that attempts to implement a deferred item must be rejected by the post-builder policy with a BLOCKED verdict. If the policy engine does not catch it, the human reviewing the diff must stop the commit and write a new blocker entry in BLOCKERS.md.

The existence of a planning document (e.g., `AUTOPILOT_GITHUB_ACTIONS_PLAN.md`, `AUTOPILOT_VPS_RUNNER_PLAN.md`) is not authorization to implement. Planning and implementing are separate human decisions.
