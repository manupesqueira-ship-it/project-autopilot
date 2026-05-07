# Docs/ Audit — Classification Table
**Date:** 2026-05-07
**Total files:** 105 (93 in docs/, 6 in docs/security/, 1 in docs/visual/, plus core/README.md and templates/)
**Auditor:** Claude (overnight run)

## Summary
- KEEP: 22 files
- UPDATE-NEEDED: 30 files
- ARCHIVE: 53 files

## Classification Table

| # | File | Lines | Classification | Reason | Action |
|---|---|---|---|---|---|
| 1 | `docs/AGENT_RULES.md` | 89 | UPDATE-NEEDED | Generic agent rules useful for v2. Contains MIRA-specific references and Codex as primary builder. | Remove MIRA refs; generalize for LATAM media properties. |
| 2 | `docs/AUTONOMY_PROTOCOL.md` | 246 | UPDATE-NEEDED | Generic autonomy model useful for v2. Says "MIRA uses Project Autopilot". | Replace MIRA with generic project reference. |
| 3 | `docs/AUTOPILOT_AGENT_BENCHMARKS.md` | 278 | KEEP | Agent capability levels (L0-L5) and gates. Fully generic. | No action needed. |
| 4 | `docs/AUTOPILOT_AGENT_ESCAPE_THREAT_MODEL.md` | 417 | KEEP | Generic agent escape threat model. No MIRA-specific content. | No action needed. |
| 5 | `docs/AUTOPILOT_AGENT_OPERATING_MODEL.md` | 519 | UPDATE-NEEDED | Defines orchestrator/builder roles. Contains MIRA references in examples. | Replace MIRA examples with v2 project examples. |
| 6 | `docs/AUTOPILOT_BRANCH_RETENTION_POLICY.md` | 129 | ARCHIVE | Lists MIRA repository branches by name. No reusable principles. | Move to `_archive/docs/`. |
| 7 | `docs/AUTOPILOT_BUILDER_REPORT_STANDARD.md` | 303 | KEEP | Generic builder report format standard. No MIRA-specific content. | No action needed. |
| 8 | `docs/AUTOPILOT_CLOUD_EXECUTION_ARCHITECTURE.md` | 373 | UPDATE-NEEDED | Generic cloud execution architecture. Contains MIRA repo layout diagram. | Replace MIRA repo references with v2 structure. |
| 9 | `docs/AUTOPILOT_CORRECTION_PROMPT_STANDARD.md` | 396 | KEEP | Generic correction prompt templates. No MIRA-specific content. | No action needed. |
| 10 | `docs/AUTOPILOT_DEFERRED_SCOPE.md` | 164 | ARCHIVE | All deferral conditions are MIRA-specific. | Move to `_archive/docs/`. |
| 11 | `docs/AUTOPILOT_DEFINITION_OF_DONE.md` | 215 | UPDATE-NEEDED | Generic DoD gates useful. Contains `--project mira` commands. | Replace with generic project reference. |
| 12 | `docs/AUTOPILOT_DESIGN_BENCHMARKS.md` | 229 | ARCHIVE | MIRA-specific design benchmarks (fashion, virtual try-on). | Move to `_archive/docs/`. |
| 13 | `docs/AUTOPILOT_EXECUTION_QUALITY_METRICS.md` | 309 | KEEP | Generic execution quality metrics. No MIRA-specific content. | No action needed. |
| 14 | `docs/AUTOPILOT_FINAL_EVIDENCE_CHECKLIST.md` | 304 | UPDATE-NEEDED | Generic evidence checklist. Contains MIRA-specific command paths. | Update command references for v2. |
| 15 | `docs/AUTOPILOT_FINAL_FAILURE_RESPONSE_PLAYBOOK.md` | 353 | KEEP | Generic failure response playbook. No MIRA-specific content. | No action needed. |
| 16 | `docs/AUTOPILOT_FINAL_OPERATOR_RUNBOOK.md` | 287 | UPDATE-NEEDED | Generic operator runbook. References MIRA-specific paths. | Update for v2 command paths. |
| 17 | `docs/AUTOPILOT_FINAL_VALIDATION_COMMAND_PACK.md` | 473 | UPDATE-NEEDED | Generic validation commands. Contains `--project mira`. | Update all project references for v2. |
| 18 | `docs/AUTOPILOT_FINISH_LINE_CUTOVER_PLAN.md` | 233 | ARCHIVE | MIRA v1 finish-line document. Historical record. | Move to `_archive/docs/`. |
| 19 | `docs/AUTOPILOT_GITHUB_ACTIONS_PLAN.md` | 322 | UPDATE-NEEDED | Generic GitHub Actions plan. Contains MIRA context assumptions. | Update project references for v2. |
| 20 | `docs/AUTOPILOT_GO_NO_GO_DECISION.md` | 187 | ARCHIVE | MIRA v1 Go/No-Go decision. `--project mira` throughout. | Move to `_archive/docs/`. |
| 21 | `docs/AUTOPILOT_HUMAN_DECISION_QUEUE_STANDARD.md` | 372 | KEEP | Generic human decision queue standard. No MIRA-specific content. | No action needed. |
| 22 | `docs/AUTOPILOT_MERGE_QUEUE_PLAN.md` | 122 | ARCHIVE | MIRA-specific branch names and commit hashes. | Move to `_archive/docs/`. |
| 23 | `docs/AUTOPILOT_PROMPT_CATALOG.md` | 613 | UPDATE-NEEDED | Generic prompt templates. Some may reference MIRA context. | Review templates; update examples for v2. |
| 24 | `docs/AUTOPILOT_PROMPT_INJECTION_THREAT_MODEL.md` | 342 | KEEP | Generic prompt injection threat model. No MIRA content. | No action needed. |
| 25 | `docs/AUTOPILOT_RESEARCH_BENCHMARKS.md` | 228 | KEEP | Generic research quality levels (R0-R4). No MIRA content. | No action needed. |
| 26 | `docs/AUTOPILOT_SECRET_EXPOSURE_THREAT_MODEL.md` | 333 | UPDATE-NEEDED | Generic secret exposure model. Contains MIRA-specific secrets inventory. | Update secrets inventory for v2 stack. |
| 27 | `docs/AUTOPILOT_SECURITY_THREAT_MODEL.md` | 383 | UPDATE-NEEDED | Generic security threat model. Contains MIRA-specific assets. | Update asset inventory for v2. |
| 28 | `docs/AUTOPILOT_SUPPLY_CHAIN_RISK_PLAN.md` | 400 | UPDATE-NEEDED | Generic supply chain risk. Contains MIRA npm dependency list. | Update dependency inventory for v2. |
| 29 | `docs/AUTOPILOT_TASK_TAXONOMY.md` | 563 | KEEP | Generic task taxonomy (16 task types). Fully reusable. | No action needed. |
| 30 | `docs/AUTOPILOT_V1_COMPLETION_CHECKLIST.md` | 207 | ARCHIVE | MIRA v1 completion checklist. Historical record. | Move to `_archive/docs/`. |
| 31 | `docs/AUTOPILOT_V1_FINAL_STATUS_SUMMARY.md` | 163 | ARCHIVE | MIRA v1 final status summary. Historical record. | Move to `_archive/docs/`. |
| 32 | `docs/AUTOPILOT_V1_GO_NO_GO_DECISION_RECORD.md` | 207 | ARCHIVE | MIRA v1 Go/No-Go record. Historical record. | Move to `_archive/docs/`. |
| 33 | `docs/AUTOPILOT_V1_RETURN_TO_MIRA_PLAN.md` | 156 | ARCHIVE | Entirely MIRA-specific: "Return to MIRA Plan". | Move to `_archive/docs/`. |
| 34 | `docs/AUTOPILOT_V1_RISK_ACCEPTANCE_RECORD.md` | 147 | ARCHIVE | MIRA v1 risk acceptance. Historical record. | Move to `_archive/docs/`. |
| 35 | `docs/AUTOPILOT_V2_SPEC.md` | 294 | KEEP | Generic v2 spec for reusable control plane. Project-agnostic. | No action needed. |
| 36 | `docs/AUTOPILOT_VPS_DIRECTORY_AND_SERVICE_PLAN.md` | 301 | UPDATE-NEEDED | Generic VPS layout. Contains MIRA paths. | Update for v2 VPS deployment. |
| 37 | `docs/AUTOPILOT_VPS_MANUAL_RUNNER_PREFLIGHT.md` | 205 | UPDATE-NEEDED | Generic VPS preflight. Contains MIRA VPS IP and `--project mira`. | Update VPS target for v2. |
| 38 | `docs/AUTOPILOT_VPS_NO_TOUCH_ZONES.md` | 226 | UPDATE-NEEDED | Generic no-touch zones. References specific VPS IP and `/root/bot/`. | Update VPS details for v2. |
| 39 | `docs/AUTOPILOT_VPS_RUNNER_PLAN.md` | 371 | UPDATE-NEEDED | Generic VPS runner plan. Contains MIRA repo clone references. | Update for v2 project structure. |
| 40 | `docs/AUTOPILOT_VPS_SECURITY_CHECKLIST.md` | 241 | KEEP | Generic VPS security checklist. No MIRA content. | No action needed. |
| 41 | `docs/AUTOPILOT_VPS_TELEGRAM_ESCALATION_PLAN.md` | 250 | KEEP | Generic Telegram escalation plan. No MIRA content. | No action needed. |
| 42 | `docs/AUTOPILOT_WORKTREE_AND_BRANCH_INVENTORY.md` | 87 | ARCHIVE | MIRA-specific worktree paths and branch names. | Move to `_archive/docs/`. |
| 43 | `docs/AUTOPILOT_WORKTREE_CLEANUP_PLAYBOOK.md` | 191 | UPDATE-NEEDED | Generic cleanup principles. Contains MIRA-specific paths. | Replace MIRA paths with generic placeholders. |
| 44 | `docs/AUTOPILOT_WORKTREE_SANDBOX_STRATEGY.md` | 412 | UPDATE-NEEDED | Generic sandbox strategy. Contains `--project mira` and `mira-sandbox-*` naming. | Replace with generic v2 references. |
| 45 | `docs/AUTOPILOT_WORLD_CLASS_SCORECARD.md` | 230 | KEEP | Generic world-class scorecard. No MIRA content. | No action needed. |
| 46 | `docs/BLOCKERS.md` | 294 | ARCHIVE | MIRA-specific historical blockers. All resolved. | Move to `_archive/docs/`. |
| 47 | `docs/CLAUDE_AGENT_SDK_INTEGRATION_PLAN.md` | 193 | UPDATE-NEEDED | Generic Claude SDK integration. Contains `--project mira`. | Replace with v2 project. |
| 48 | `docs/CLAUDE_MANUAL_HANDOFF_PROTOCOL.md` | 233 | UPDATE-NEEDED | Generic handoff lifecycle. Contains `--project mira` throughout. | Replace with generic references. |
| 49 | `docs/CLAUDE_SANDBOX_APPROVAL_CONTRACT.md` | 101 | UPDATE-NEEDED | Generic approval contract. Contains `mira-sandbox-*` naming. | Replace with generic naming. |
| 50 | `docs/CLAUDE_SANDBOX_RUNNER_INTERFACE.md` | 119 | UPDATE-NEEDED | Generic runner interface. Contains `--project mira`. | Replace with v2 project. |
| 51 | `docs/COPYWRITING_STANDARD.md` | 13 | ARCHIVE | MIRA-specific copy rules. Too brief to be useful standalone. | Move to `_archive/docs/`. |
| 52 | `docs/COST_POLICY.md` | 35 | UPDATE-NEEDED | Generic cost policy. Says "MIRA uses Project Autopilot". | Replace MIRA references; update config paths. |
| 53 | `docs/CURRENT_STATE.md` | 46 | ARCHIVE | MIRA-specific: "MIRA is a Next.js 14.2.35 App Router project". | Move to `_archive/docs/`. |
| 54 | `docs/CUSTOMER_DATA_POLICY.md` | 99 | ARCHIVE | MIRA-specific data inventory (users_profile, try-on photos). | Move to `_archive/docs/`. |
| 55 | `docs/DECISIONS.md` | 43 | ARCHIVE | MIRA-specific historical decisions. | Move to `_archive/docs/`. |
| 56 | `docs/DEEP_RESEARCH_PROTOCOL.md` | 25 | KEEP | Generic deep research protocol. No MIRA content. | No action needed. |
| 57 | `docs/DESIGN_DIRECTOR_STANDARD.md` | 20 | KEEP | Generic Design Director standard. No MIRA content. | No action needed. |
| 58 | `docs/DESIGN_REFERENCES.md` | 20 | ARCHIVE | MIRA-specific design direction (dark cinematic, fashion-tech). | Move to `_archive/docs/`. |
| 59 | `docs/DESIGN_RUBRIC.md` | 26 | KEEP | Generic 20-category design rubric. No MIRA content. | No action needed. |
| 60 | `docs/EXTERNAL_BUILDER_POLICY.md` | 129 | UPDATE-NEEDED | Generic external builder policy. Contains MIRA references. | Replace with generic project references. |
| 61 | `docs/HUMAN_QUESTIONS.md` | 243 | ARCHIVE | MIRA-specific open questions. Historical. | Move to `_archive/docs/`. |
| 62 | `docs/INNOVATION_STANDARD.md` | 17 | KEEP | Generic innovation standard. No MIRA content. | No action needed. |
| 63 | `docs/MASTER_PLAN.md` | 20 | ARCHIVE | Old MIRA-specific master plan. Superseded by root MASTER_PLAN.md v2. | Move to `_archive/docs/`. |
| 64 | `docs/MIRA_DATA_MAP.md` | 93 | ARCHIVE | MIRA data collection map. | Move to `_archive/docs/`. |
| 65 | `docs/MIRA_E2E_VALIDATION_PLAN.md` | 336 | ARCHIVE | MIRA Supabase E2E validation. | Move to `_archive/docs/`. |
| 66 | `docs/MIRA_INTERACTION_AND_MOTION_STANDARD.md` | 204 | ARCHIVE | MIRA motion/interaction design. | Move to `_archive/docs/`. |
| 67 | `docs/MIRA_INTERNAL_DEMO_READY_REPORT.md` | 120 | ARCHIVE | MIRA internal demo instructions. | Move to `_archive/docs/`. |
| 68 | `docs/MIRA_LOCAL_AUTH_VERIFICATION_PLAN.md` | 133 | ARCHIVE | MIRA Supabase auth verification. | Move to `_archive/docs/`. |
| 69 | `docs/MIRA_MOCK_GENERATION_PLAN.md` | 67 | ARCHIVE | MIRA QA mock mode implementation. | Move to `_archive/docs/`. |
| 70 | `docs/MIRA_PRIVACY_LOGGING_GUARDRAILS.md` | 108 | ARCHIVE | MIRA-specific logging guardrails. | Move to `_archive/docs/`. |
| 71 | `docs/MIRA_PRODUCT_EXCELLENCE_STANDARD.md` | 172 | ARCHIVE | MIRA product personality and try-on excellence. | Move to `_archive/docs/`. |
| 72 | `docs/MIRA_RLS_DECISION_MATRIX.md` | 96 | ARCHIVE | MIRA Supabase RLS decisions. | Move to `_archive/docs/`. |
| 73 | `docs/MIRA_RLS_STORAGE_MIGRATION_DRAFT.md` | 461 | ARCHIVE | MIRA Supabase RLS/storage migration SQL. | Move to `_archive/docs/`. |
| 74 | `docs/MIRA_SECURE_MVP_RUNBOOK.md` | 320 | ARCHIVE | MIRA secure MVP runbook. | Move to `_archive/docs/`. |
| 75 | `docs/MIRA_SUPABASE_BACKFILL_AND_OWNERSHIP_PLAN.md` | 433 | ARCHIVE | MIRA Supabase backfill plan. | Move to `_archive/docs/`. |
| 76 | `docs/MIRA_SUPABASE_MANUAL_ACTIVATION_CHECKLIST.md` | 155 | ARCHIVE | MIRA Supabase dashboard activation. | Move to `_archive/docs/`. |
| 77 | `docs/MIRA_SUPABASE_MIGRATION_REVIEW_CHECKLIST.md` | 319 | ARCHIVE | MIRA Supabase migration review. | Move to `_archive/docs/`. |
| 78 | `docs/MIRA_SUPABASE_RLS_SQL_DRAFT_NOT_FOR_EXECUTION.sql.md` | 434 | ARCHIVE | MIRA Supabase RLS SQL draft. | Move to `_archive/docs/`. |
| 79 | `docs/MIRA_SUPABASE_RLS_STAGING_PLAN.md` | 515 | ARCHIVE | MIRA Supabase RLS staging plan. | Move to `_archive/docs/`. |
| 80 | `docs/MIRA_SUPABASE_ROLLBACK_PLAN.md` | 372 | ARCHIVE | MIRA Supabase rollback SQL. | Move to `_archive/docs/`. |
| 81 | `docs/MIRA_SUPABASE_SECURITY_ALIGNMENT_PLAN.md` | 764 | ARCHIVE | MIRA Supabase security alignment. | Move to `_archive/docs/`. |
| 82 | `docs/MIRA_SUPABASE_SECURITY_TEST_MATRIX.md` | 655 | ARCHIVE | MIRA Supabase security test matrix. | Move to `_archive/docs/`. |
| 83 | `docs/MIRA_SUPABASE_SECURITY_VALIDATION_QUERIES_DRAFT.md` | 567 | ARCHIVE | MIRA Supabase validation queries. | Move to `_archive/docs/`. |
| 84 | `docs/MIRA_SUPABASE_STORAGE_POLICY_PLAN.md` | 529 | ARCHIVE | MIRA Supabase storage policy. | Move to `_archive/docs/`. |
| 85 | `docs/MIRA_SUPABASE_STORAGE_SQL_DRAFT_NOT_FOR_EXECUTION.sql.md` | 384 | ARCHIVE | MIRA Supabase storage SQL draft. | Move to `_archive/docs/`. |
| 86 | `docs/MIRA_UI_ANTI_PATTERNS.md` | 217 | ARCHIVE | MIRA-specific UI anti-patterns. | Move to `_archive/docs/`. |
| 87 | `docs/MIRA_UX_PRINCIPLES.md` | 184 | ARCHIVE | MIRA UX principles. | Move to `_archive/docs/`. |
| 88 | `docs/MIRA_VISUAL_DESIGN_STANDARD.md` | 234 | ARCHIVE | MIRA visual design standard. | Move to `_archive/docs/`. |
| 89 | `docs/MULTISTEP_AGENT_LOOP_STANDARD.md` | 67 | UPDATE-NEEDED | Generic multi-step loop. Contains `--project mira`. | Replace with generic references. |
| 90 | `docs/OPENAI_AUDITOR_STANDARD.md` | 54 | UPDATE-NEEDED | Generic OpenAI Auditor role. Contains `--project mira`. | Replace with generic references. |
| 91 | `docs/QA_PROTOCOL.md` | 96 | KEEP | Generic QA protocol. No MIRA content. | No action needed. |
| 92 | `docs/QUALITY_BAR.md` | 41 | UPDATE-NEEDED | Generic quality bar. Contains "No new MIRA product features" line. | Remove MIRA-specific gate reference. |
| 93 | `docs/RESEARCH_DIRECTOR_STANDARD.md` | 33 | KEEP | Generic Research Director standard. No MIRA content. | No action needed. |
| 94 | `docs/RESEARCH_PROTOCOL.md` | 51 | KEEP | Generic research protocol. No MIRA content. | No action needed. |
| 95 | `docs/TASK_QUEUE.md` | 52 | ARCHIVE | MIRA-specific task queue. | Move to `_archive/docs/`. |
| 96 | `docs/TECHNICAL_ARCHITECTURE.md` | 35 | ARCHIVE | MIRA-specific: Next.js 14 App Router, MIRA stack. | Move to `_archive/docs/`. |
| 97 | `docs/VPS_DEPLOYMENT_PLAN.md` | 104 | UPDATE-NEEDED | Generic VPS deployment. Contains MIRA VPS IP and paths. | Update for v2. |
| 98 | `docs/WORLD_CLASS_STANDARD.md` | 67 | KEEP | Generic world-class standard. No MIRA content. | No action needed. |
| 99 | `docs/security/MIRA_RLS_POLICY_MATRIX.md` | 95 | ARCHIVE | MIRA Supabase RLS policy matrix. | Move to `_archive/docs/`. |
| 100 | `docs/security/MIRA_RLS_STORAGE_STAGING_PLAN.md` | 150 | ARCHIVE | MIRA RLS & storage staging plan. | Move to `_archive/docs/`. |
| 101 | `docs/security/MIRA_SECURITY_OWNERSHIP_FINDINGS.md` | 112 | ARCHIVE | MIRA API route ownership findings. | Move to `_archive/docs/`. |
| 102 | `docs/security/MIRA_SECURITY_ROLLBACK_PLAN.md` | 120 | ARCHIVE | MIRA Supabase RLS rollback SQL. | Move to `_archive/docs/`. |
| 103 | `docs/security/MIRA_SECURITY_TEST_PLAN.md` | 113 | ARCHIVE | MIRA A/B security test plan. | Move to `_archive/docs/`. |
| 104 | `docs/security/MIRA_STORAGE_POLICY_MATRIX.md` | 113 | ARCHIVE | MIRA Supabase storage policy matrix. | Move to `_archive/docs/`. |
| 105 | `docs/visual/MIRA_VISUAL_QUALITY_STANDARD.md` | 252 | ARCHIVE | MIRA visual quality standard. | Move to `_archive/docs/`. |
