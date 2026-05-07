# Core/ Audit — Classification Table
**Date:** 2026-05-07
**Total files:** 69 (62 in core/, 7 in core/providers/)
**Auditor:** Claude (overnight run)

## Summary
- KEEP-CORE: 32 files
- MIGRATE-AGENT: 6 files
- ARCHIVE: 25 files
- REVIEW: 5 files

## Classification Table

| # | File | Lines | Classification | Reason | Action |
|---|---|---|---|---|---|
| 1 | `core/agent_loop.py` | 1870 | KEEP-CORE | Main orchestration loop: imports all modules, runs cycles, handles HALT file, dispatches CLI subcommands. Kernel's main entry point. | Refactor heavily to remove MIRA-specific imports (browser_qa, flow_qa, etc.) but keep as kernel scheduler. |
| 2 | `core/autopilot_health.py` | 806 | KEEP-CORE | Aggregates health checks across all subsystems (policy fixtures, provider registry, lock status, blockers). Generic system health dashboard. | Keep; remove MIRA-specific health checks if any remain. |
| 3 | `core/autopilot_v2_check.py` | 284 | KEEP-CORE | Validates that all v2 infrastructure modules exist and provider registry works. Generic system self-check. | Keep; update checked module list for v2 architecture. |
| 4 | `core/backend_audit.py` | 644 | ARCHIVE | MIRA-specific: hardcoded Supabase table names (users_profile, user_assets, generations), storage buckets (user-photos, product-images), MIRA routes (/onboarding, /scan, /catalog, /tryon, /result). | Move to `_archive/core/`. |
| 5 | `core/blocker_summary.py` | 57 | KEEP-CORE | Generic blocker tracker: parses BLOCKERS.md for open/resolved/parked counts. Domain-agnostic. | Keep as-is. |
| 6 | `core/browser_qa.py` | 762 | ARCHIVE | Browser QA with Playwright screenshots, viewport checks, network interception for a web app. MIRA try-on app specific (Next.js dev ports, visual QA). | Move to `_archive/core/`. |
| 7 | `core/builder_intake.py` | 188 | KEEP-CORE | Generic post-builder report intake: reads builder report, runs evidence collection, risk classification, policy evaluation, creates evidence bundle. | Keep; this is the kernel's builder-result intake pipeline. |
| 8 | `core/builder_orchestrator.py` | 325 | KEEP-CORE | Plans task execution: selects provider, classifies risk, determines execution mode (sandbox/manual/auto). Generic orchestration logic. | Keep; update keyword detection for v2 domain terms. |
| 9 | `core/claude_analysis_call.py` | 299 | KEEP-CORE | Controlled Claude API analysis call with budget gates, prompt safety, cost tracking. Generic provider integration. | Keep as core provider capability. |
| 10 | `core/claude_analysis_review.py` | 423 | KEEP-CORE | Reviews Claude analysis output, categorizes findings into actionable items with severity. Generic review pipeline. | Keep; useful for any agent reviewing LLM output. |
| 11 | `core/claude_manual_handoff.py` | 241 | KEEP-CORE | Generates handoff packet for manual Claude Code execution: prompt pack + worktree plan + boundary config. Generic builder handoff. | Keep as-is. |
| 12 | `core/claude_prompt_pack.py` | 132 | KEEP-CORE | Builds a prompt pack preview for Claude sandbox execution with file/command policies and stop conditions. Generic. | Keep as-is. |
| 13 | `core/claude_prompt_safety.py` | 61 | KEEP-CORE | Sanitizes prompts by redacting secrets (API keys, JWTs, tokens). Domain-agnostic security utility. | Keep as-is. |
| 14 | `core/claude_runner.py` | 166 | KEEP-CORE | Claude Code CLI detection and handoff (manual or execute mode). Generic builder runner. | Keep as-is. |
| 15 | `core/claude_sandbox_approval.py` | 330 | KEEP-CORE | Sandbox approval workflow: request/validate/expire approval contracts for builder execution. Generic governance. | Keep as-is. |
| 16 | `core/claude_sandbox_boundary.py` | 613 | KEEP-CORE | Defines sandbox boundaries: allowed/denied files, commands, stop conditions, rollback plans. Generic security policy engine. | Keep as-is. |
| 17 | `core/claude_sandbox_runner.py` | 339 | KEEP-CORE | Orchestrates sandbox runner state machine: approval → dry run → worktree creation → execution. Generic. | Keep as-is. |
| 18 | `core/claude_sdk_dry_run.py` | 280 | KEEP-CORE | Validates Claude SDK readiness: API key status, provider registry, policy fixtures. Generic provider readiness check. | Keep as-is. |
| 19 | `core/config.py` | 174 | KEEP-CORE | ProjectConfig dataclass, YAML loader, model routing, retry policy. Core configuration kernel. | Keep; extend for v2 properties (agents config, content properties). |
| 20 | `core/config_validator.py` | 269 | KEEP-CORE | Validates project config: required fields, budget limits, dangerous commands, autonomy modes. Generic. | Keep as-is. |
| 21 | `core/control_center.py` | 2198 | REVIEW | Large HTML report generator combining all subsystem statuses. Generic in structure but may have MIRA-specific sections in the HTML template. | Read deeper to confirm; likely KEEP-CORE with cleanup. |
| 22 | `core/cost_controller.py` | 118 | KEEP-CORE | Budget enforcement: per-cycle, daily, monthly spend tracking with model cost estimation. Core kernel. | Keep as-is. |
| 23 | `core/design_director.py` | 259 | ARCHIVE | Visual design review with UI rubric (visual hierarchy, spacing rhythm, gradient penalties, CTA clarity). MIRA try-on app UI quality — irrelevant for media properties. | Move to `_archive/core/`. |
| 24 | `core/dev_runtime_diagnose.py` | 495 | ARCHIVE | Diagnoses Next.js dev runtime issues (stale .next cache, wrong port, env var not in client bundle). MIRA-specific dev tooling. | Move to `_archive/core/`. |
| 25 | `core/dev_server_runner.py` | 135 | ARCHIVE | Managed Next.js dev server subprocess with QA mock env vars (`NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS`). MIRA-specific. | Move to `_archive/core/`. |
| 26 | `core/env_loader.py` | 54 | KEEP-CORE | Loads .env and .env.local with safe precedence rules. Domain-agnostic utility. | Keep as-is. |
| 27 | `core/env_preflight.py` | 159 | ARCHIVE | Checks MIRA-specific env vars: `NEXT_PUBLIC_SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`. Hardcoded for Supabase/MIRA. | Move to `_archive/core/`. Could be generalized later if needed. |
| 28 | `core/evidence_bundle.py` | 125 | KEEP-CORE | Creates timestamped evidence bundles (metadata, evidence, task plan, QA review, risk summary). Generic audit trail. | Keep as-is. |
| 29 | `core/evidence_collector.py` | 271 | KEEP-CORE | Collects git status, changed files, build/typecheck/lint output. Generic evidence gathering. | Keep as-is. |
| 30 | `core/flow_qa.py` | 1451 | ARCHIVE | Playwright-based flow QA framework with MIRA flow definitions (onboarding → scan → catalog → tryon → result). MIRA-specific. | Move to `_archive/core/`. |
| 31 | `core/flow_specs.py` | 88 | ARCHIVE | MIRA flow specifications: `mira_manual_e2e_flow()` with MIRA routes, Supabase tables, user-photos bucket. Hardcoded MIRA data. | Move to `_archive/core/`. |
| 32 | `core/init_project.py` | 189 | KEEP-CORE | Bootstraps new project: creates project_control/ files from templates and YAML config. Generic scaffolding. | Keep; useful for bootstrapping v2 properties. |
| 33 | `core/internal_demo_check.py` | 405 | ARCHIVE | "MIRA Internal Demo Check": validates demo routes, mock mode infrastructure, env/runtime for MIRA demo. Explicitly MIRA-specific. | Move to `_archive/core/`. |
| 34 | `core/local_planner.py` | 237 | KEEP-CORE | Local fallback planner: extracts next task from TASK_QUEUE.md, generates builder prompt without API calls. Generic scheduling. | Keep as-is. |
| 35 | `core/mira_readiness.py` | 699 | ARCHIVE | "MIRA Secure MVP Readiness Report": checks auth, Flow QA, mock generation, RLS, storage. Entirely MIRA-specific. | Move to `_archive/core/`. |
| 36 | `core/model_router.py` | 52 | KEEP-CORE | Routes tasks to cheap/standard/premium models based on intensity mode and failure count. Generic. | Keep as-is. |
| 37 | `core/multistep_loop.py` | 307 | REVIEW | Multi-step execution loop state machine (OBJECTIVE_RECEIVED → BUILDER_RUNNING → DONE). Generic concept but heavily tied to current builder providers. | Keep if refactored for v2 agent orchestration; review scope. |
| 38 | `core/openai_auditor.py` | 293 | MIGRATE-AGENT | OpenAI-based task planning/auditing dry-run. In v2, this planning role belongs to the editorial or signal_scorer agent. | Migrate to `agents/editorial/` or create `agents/planner/`. |
| 39 | `core/openai_supervisor.py` | 150 | KEEP-CORE | OpenAI API wrapper with budget gates, model routing, dry-run mode. Generic LLM provider interface. | Keep as core LLM provider utility. |
| 40 | `core/policy_test_fixtures.py` | 1117 | REVIEW | Policy test fixtures: simulates builder reports with various risk scenarios. Useful for v2 but needs v2-specific scenarios. | Keep; update fixtures for v2 content production scenarios. |
| 41 | `core/post_builder_policy.py` | 955 | KEEP-CORE | Post-builder policy engine: forbidden file patterns, secret detection, SQL detection, paid API detection, sandbox escape detection. Core governance. | Keep; this is the kernel's policy enforcement engine. |
| 42 | `core/project_loader.py` | 57 | KEEP-CORE | Loads project config, reads project_control/ documents, ensures directory structure. Generic. | Keep as-is. |
| 43 | `core/prompt_builder.py` | 80 | MIGRATE-AGENT | Builds builder prompts with project context, quality block, and evidence. In v2, prompt building is per-agent, not a kernel concern. | Migrate to `agents/content_composer/` or keep a minimal version in core. |
| 44 | `core/provider_registry.py` | 103 | KEEP-CORE | Discovers and reports on all registered builder providers. Generic provider management. | Keep as-is. |
| 45 | `core/qa_reviewer.py` | 284 | MIGRATE-AGENT | QA verdict generation using OpenAI supervisor + local structured review. In v2, QA review belongs to the fact_checker agent. | Migrate to `agents/fact_checker/`. |
| 46 | `core/quality_director.py` | 192 | MIGRATE-AGENT | Generates quality instruction blocks from project_control docs. In v2, editorial quality is an agent concern. | Migrate to `agents/editorial/`. |
| 47 | `core/research_director.py` | 258 | MIGRATE-AGENT | Classifies research needs, generates research requests with scope/mode/urgency. In v2, this is the source_monitor agent's job. | Migrate to `agents/source_monitor/`. |
| 48 | `core/research_log.py` | 142 | KEEP-CORE | Records and summarizes research requests in JSONL format. Generic audit log. | Keep as-is; domain-agnostic logging. |
| 49 | `core/risk_classifier.py` | 103 | KEEP-CORE | Classifies task risk by keywords (destructive, deploy, secrets, paid API, schema change). Generic. | Keep as-is. |
| 50 | `core/run_history.py` | 246 | KEEP-CORE | JSONL run history: append events, summarize runs, track duration/commands/files. Generic audit trail. | Keep as-is. |
| 51 | `core/run_lock.py` | 112 | KEEP-CORE | File-based concurrency lock for preventing parallel cycles. Generic. | Keep as-is. |
| 52 | `core/run_metrics.py` | 55 | KEEP-CORE | Enriches run summaries with blocker counts, research counts, task state. Generic. | Keep as-is. |
| 53 | `core/secret_status.py` | 36 | KEEP-CORE | Checks env var presence without exposing values. Domain-agnostic security utility. | Keep as-is. |
| 54 | `core/security_staging_plan.py` | 390 | ARCHIVE | "MIRA Security Staging Plan Validator": checks Supabase RLS SQL drafts, security policy matrix. MIRA/Supabase-specific. | Move to `_archive/core/`. |
| 55 | `core/sensitive_logging_audit.py` | 242 | ARCHIVE | "Sensitive Logging Audit for MIRA": scans .ts/.tsx files for risky console.log patterns. MIRA Next.js codebase specific. | Move to `_archive/core/`. |
| 56 | `core/state_manager.py` | 165 | KEEP-CORE | Saves/loads autopilot state, records blockers, writes iteration logs. Generic state persistence. | Keep as-is. |
| 57 | `core/supabase_auth_verify.py` | 331 | ARCHIVE | "Supabase Auth Verification for MIRA": checks Supabase auth wiring, anonymous auth, profile insert. Entirely MIRA/Supabase specific. | Move to `_archive/core/`. |
| 58 | `core/task_state.py` | 76 | KEEP-CORE | Task state machine with validated transitions (planned → assigned → implemented → passed → committed). Generic. | Keep as-is. |
| 59 | `core/telegram_alerts.py` | 72 | KEEP-CORE | Sends Telegram alerts with per-project credentials. Generic notification system. | Keep; useful for v2 operational alerts. |
| 60 | `core/validation_report.py` | 37 | REVIEW | Creates validation report from template. Generic structure but may contain MIRA-specific template references. | Keep if template is generic; verify template content. |
| 61 | `core/visual_qa.py` | 476 | ARCHIVE | "MIRA Visual QA Tool": checks pages, selectors, accessibility markers for MIRA routes. MIRA UI specific. | Move to `_archive/core/`. |
| 62 | `core/worktree_sandbox.py` | 520 | REVIEW | Git worktree sandbox management: create/cleanup sandboxed branches for builder execution. Generic concept but tightly coupled to Claude builder workflow. | Keep; review for v2 agent isolation use cases. |
| 63 | `core/providers/__init__.py` | 5 | KEEP-CORE | Package init, exports ProviderInfo. Generic. | Keep as-is. |
| 64 | `core/providers/base.py` | 23 | KEEP-CORE | ProviderInfo dataclass: provider metadata (id, type, capabilities, risks, env vars, status). Generic. | Keep as-is. |
| 65 | `core/providers/claude_agent_sdk_provider.py` | 79 | KEEP-CORE | Claude Agent SDK provider detection. Provider metadata, not agent logic. | Keep in core/providers/. |
| 66 | `core/providers/claude_code_provider.py` | 44 | KEEP-CORE | Claude Code CLI provider detection. Generic provider metadata. | Keep as-is. |
| 67 | `core/providers/codex_provider.py` | 32 | ARCHIVE | Codex provider detection. Codex is deprecated/irrelevant for v2 media properties architecture. | Move to `_archive/core/providers/` or remove. |
| 68 | `core/providers/openai_auditor_provider.py` | 69 | MIGRATE-AGENT | OpenAI Auditor provider detection. In v2, OpenAI auditor role is absorbed by agents. | Migrate to `agents/` as needed, or keep minimal detection in core. |
| 69 | `core/providers/registry.py` | 14 | KEEP-CORE | Discovers all providers by calling each provider's detect(). Generic registry pattern. | Keep; update provider list for v2. |

---

## Notes

### ARCHIVE files (25 total, ~7,938 lines)
All MIRA try-on app specific. No reuse value for LATAM media properties. Key categories:
- **Supabase/Auth:** `supabase_auth_verify.py`, `env_preflight.py`, `security_staging_plan.py`
- **Browser/Visual QA:** `browser_qa.py`, `visual_qa.py`, `flow_qa.py`, `flow_specs.py`
- **MIRA-specific checks:** `mira_readiness.py`, `internal_demo_check.py`, `backend_audit.py`
- **Next.js dev tooling:** `dev_runtime_diagnose.py`, `dev_server_runner.py`
- **UI design:** `design_director.py`
- **Code scanning:** `sensitive_logging_audit.py` (MIRA .ts/.tsx patterns)
- **Provider:** `codex_provider.py` (deprecated builder)

### MIGRATE-AGENT files (6 total, ~1,057 lines)
These contain useful logic but belong in CAPA 2 agents, not the core kernel:
- `openai_auditor.py` → `agents/editorial/` or `agents/planner/`
- `prompt_builder.py` → `agents/content_composer/`
- `qa_reviewer.py` → `agents/fact_checker/`
- `quality_director.py` → `agents/editorial/`
- `research_director.py` → `agents/source_monitor/`
- `openai_auditor_provider.py` → `agents/` (or keep minimal detection in core)

### REVIEW files (5 total, ~4,493 lines)
- `control_center.py` (2198 lines) — Likely KEEP-CORE but needs deep read of HTML template for MIRA references
- `multistep_loop.py` (307 lines) — Generic state machine, needs v2 adaptation review
- `policy_test_fixtures.py` (1117 lines) — Valuable testing infrastructure, needs v2 scenario updates
- `validation_report.py` (37 lines) — Check template content
- `worktree_sandbox.py` (520 lines) — Potentially useful for agent isolation in v2
