# Audit Summary — core/ + docs/
**Date:** 2026-05-07
**Auditor:** Claude (overnight run)
**Total files audited:** 174 (69 in core/, 105 in docs/)

---

## Overall Classification

| Category | core/ | docs/ | Total |
|---|---|---|---|
| KEEP / KEEP-CORE | 32 | 22 | **54** |
| MIGRATE-AGENT | 6 | 0 | **6** |
| UPDATE-NEEDED | 0 | 30 | **30** |
| ARCHIVE | 25 | 53 | **78** |
| REVIEW | 5 | 0 | **5** |
| **Total** | **68** | **105** | **173** |

**Key stat:** 78 files (45%) can be archived immediately. Only 54 files (31%) are clean keeps.

---

## Top 10 KEEP-CORE Files (most important for v2)

| # | File | Lines | Why critical |
|---|---|---|---|
| 1 | `core/agent_loop.py` | 1870 | Main orchestration loop — kernel entry point |
| 2 | `core/post_builder_policy.py` | 955 | Policy enforcement engine — secret detection, forbidden patterns |
| 3 | `core/autopilot_health.py` | 806 | System health dashboard |
| 4 | `core/claude_sandbox_boundary.py` | 613 | Sandbox security boundaries |
| 5 | `core/claude_sandbox_runner.py` | 339 | Sandbox execution state machine |
| 6 | `core/builder_orchestrator.py` | 325 | Task execution planning |
| 7 | `core/claude_sandbox_approval.py` | 330 | Governance approval workflow |
| 8 | `core/claude_analysis_review.py` | 423 | LLM output review pipeline |
| 9 | `core/evidence_collector.py` | 271 | Evidence gathering (generic audit trail) |
| 10 | `core/cost_controller.py` | 118 | Budget enforcement |

---

## Top 6 MIGRATE-AGENT Files (with destination)

| File | Lines | Destination Agent | Rationale |
|---|---|---|---|
| `core/research_director.py` | 258 | `agents/source_monitor/` | Research need classification = source monitoring |
| `core/quality_director.py` | 192 | `agents/editorial/` | Quality instruction blocks = editorial concern |
| `core/qa_reviewer.py` | 284 | `agents/fact_checker/` | QA verdict generation = fact checking |
| `core/openai_auditor.py` | 293 | `agents/editorial/` | Task planning/auditing = editorial planning |
| `core/prompt_builder.py` | 80 | `agents/content_composer/` | Prompt building = per-agent, not kernel |
| `core/providers/openai_auditor_provider.py` | 69 | `agents/` | OpenAI auditor role absorbed by agents |

---

## ARCHIVE Totals

### core/ — 25 files to archive (~7,938 lines)
- **Supabase/Auth (3):** supabase_auth_verify, env_preflight, security_staging_plan
- **Browser/Visual QA (4):** browser_qa, visual_qa, flow_qa, flow_specs
- **MIRA checks (3):** mira_readiness, internal_demo_check, backend_audit
- **Next.js dev (2):** dev_runtime_diagnose, dev_server_runner
- **UI design (1):** design_director
- **Code scanning (1):** sensitive_logging_audit
- **Provider (1):** codex_provider
- **Other (10):** remaining MIRA-specific utilities

### docs/ — 53 files to archive (~12,500+ lines)
- **MIRA Supabase (17):** All RLS, storage, migration, security docs
- **MIRA product (8):** UX, visual design, interaction, product excellence, data map
- **MIRA operations (7):** demo reports, task queues, blockers, decisions
- **Historical v1 records (6):** completion checklists, go/no-go records, risk acceptance
- **MIRA plans (5):** return to MIRA, finish line, branch retention, merge queue, deferred scope
- **Other (10):** MIRA-specific standards and references

---

## REVIEW Files (5 — human decisions needed)

| File | Lines | Question for Manuel |
|---|---|---|
| `core/control_center.py` | 2198 | Large HTML report generator. Likely KEEP but needs deep read for MIRA-specific HTML sections. Worth the refactor? |
| `core/multistep_loop.py` | 307 | Generic state machine. Keep for v2 agent orchestration or rebuild from scratch? |
| `core/policy_test_fixtures.py` | 1117 | Valuable testing infra. Update fixtures for v2 content production scenarios? |
| `core/validation_report.py` | 37 | Check if template content is MIRA-specific. |
| `core/worktree_sandbox.py` | 520 | Git worktree isolation. Useful for v2 agent isolation? Or overkill? |

---

## UPDATE-NEEDED docs/ — 30 files

Most of these only need `--project mira` → generic project reference replacement. Estimated effort:

- **Simple find-replace (20 files):** ~2 hours. Just replace `--project mira`, `mira-sandbox-*`, MIRA path references.
- **Moderate rewrite (7 files):** ~3 hours. Update asset inventories, dependency lists, or architecture diagrams.
- **Significant update (3 files):** ~2 hours. Threat models and supply chain risks need v2 stack context.

---

## Estimated Effort to Execute

| Action | Files | Estimated Hours |
|---|---|---|
| Archive (git mv to _archive/) | 78 | 0.5 |
| Migrate agent files | 6 | 1-2 |
| Simple find-replace in docs | 20 | 2 |
| Moderate rewrite in docs | 7 | 3 |
| Significant update in docs | 3 | 2 |
| Review 5 files + decide | 5 | 1 |
| **Total** | **119** | **~9.5-11.5 hours** |

**Recommendation:** Start with archive (0.5h, biggest cleanup). Then migrate agent files (1-2h, enables v2 development). Leave docs updates for when each doc is actually needed — don't batch-update 30 docs if you'll only reference 5 of them in the next month.

---

## Detailed Classification Files
- `docs/audits/2026-05-07_core-classification.md` — 69 files with per-file reasoning
- `docs/audits/2026-05-07_docs-classification.md` — 105 files with per-file reasoning
