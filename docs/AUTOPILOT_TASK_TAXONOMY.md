# AUTOPILOT TASK TAXONOMY

Version: 1.0
Status: Canonical
Owner: Project Autopilot Control System

---

## Purpose

This taxonomy defines every category of task that the Project Autopilot system can plan, assign, validate, and review. It is the authoritative reference for the OpenAI Auditor, the Multi-Step Loop, the Policy Engine, and the Builder Orchestrator when classifying work.

Every task submitted to Autopilot MUST be assigned exactly one taxonomy type before execution begins. The type determines the default provider, risk level, required gates, allowed file scope, human approval requirement, and auto-commit eligibility.

---

## Taxonomy Table

| # | Task Type | Default Provider | Risk Level | Human Approval | Auto-Commit |
|---|-----------|-----------------|-----------|----------------|-------------|
| 01 | docs-only | Codex or Claude | Low | No | Yes |
| 02 | autopilot-internal-code | Codex (sandboxed) | Medium | No | Yes (after lint + typecheck pass) |
| 03 | ui-product-code | Codex (sandboxed) | Medium | No | Yes (after lint + typecheck pass) |
| 04 | backend-api | Codex (sandboxed) | High | Yes | No |
| 05 | supabase-security | Claude (review) + human | Critical | Yes | No |
| 06 | design-polish | Design Director + Codex | Low-Medium | No | Yes (after screenshot evidence) |
| 07 | research | Research Director | Low | No | Yes |
| 08 | vendor-api-integration | Codex (sandboxed) | High | Yes | No |
| 09 | deployment | Claude (plan) + human | Critical | Yes | No |
| 10 | vps-ops | Claude (plan) + human | Critical | Yes | No |
| 11 | bug-fix | Codex (sandboxed) | Medium | No | Yes (after test pass) |
| 12 | refactor | Codex (sandboxed) | Medium | No | Yes (after lint + typecheck pass) |
| 13 | test-qa | Codex (sandboxed) | Low-Medium | No | Yes (after test pass) |
| 14 | performance | Codex (sandboxed) | Medium | No | Yes (after benchmark evidence) |
| 15 | accessibility | Codex (sandboxed) | Low | No | Yes (after axe/pa11y evidence) |
| 16 | privacy-data-retention | Claude (review) + human | Critical | Yes | No |

---

## Detailed Definitions

---

### 01 — docs-only

**Description:** Creation or update of Markdown documentation, prompt catalogs, standards documents, runbooks, decision logs, and other text-only files. No executable code changes.

**Default Provider:** Codex or Claude (either is acceptable; Claude preferred for long-form reasoning)

**Risk Level:** Low

**Required Gates:**
- `git diff --check` (no whitespace errors)
- `git status --short` confirms only allowed files changed
- Human spot-check recommended but not required

**Allowed Files:**
- `project_control/**/*.md`
- `docs/**/*.md`
- `README.md`
- Explicitly whitelisted documentation paths

**Disallowed Files:**
- Any `.ts`, `.tsx`, `.js`, `.py`, `.sql`, `.env`, `.json` config files
- `supabase/**`
- `agent/**` source files
- `project_autopilot/**` source files

**Human Approval:** No

**Auto-Commit:** Yes — if and only if `git status --short` shows no changes outside allowed file list

---

### 02 — autopilot-internal-code

**Description:** Code changes to the Autopilot system itself: OpenAI Auditor, Multi-Step Loop, Policy Engine, Builder Orchestrator, Control Center, or any agent harness file.

**Default Provider:** Codex running in worktree sandbox

**Risk Level:** Medium

**Required Gates:**
- `python -B -m compileall` passes (if Python files touched)
- `npm run lint` passes
- `npm run typecheck` passes
- No `.env` or secrets files touched
- `git diff --check` clean

**Allowed Files:**
- `agent/**` (autopilot agent source)
- `project_autopilot/**`
- Explicitly scoped agent config files (non-secret)

**Disallowed Files:**
- `.env`, `.env.*`
- `supabase/migrations/**`
- Any file outside the agent or project_autopilot scope
- Production deployment configs

**Human Approval:** No (unless risk flags raised by Auditor)

**Auto-Commit:** Yes — after all gates pass

---

### 03 — ui-product-code

**Description:** Changes to the MIRA product UI: React components, pages, hooks, styles, client-side logic. Excludes API routes and server-side logic.

**Default Provider:** Codex running in worktree sandbox

**Risk Level:** Medium

**Required Gates:**
- `npm run lint` passes
- `npm run typecheck` passes
- Visual screenshot evidence attached to builder report
- No server-side or API files touched
- `git diff --check` clean

**Allowed Files:**
- `app/**` (Next.js app directory, client components only)
- `components/**`
- `styles/**`
- `public/**`

**Disallowed Files:**
- `app/api/**`
- `supabase/**`
- `.env`, `.env.*`
- `agent/**`

**Human Approval:** No (unless Auditor flags regression risk)

**Auto-Commit:** Yes — after lint, typecheck, and screenshot evidence pass

---

### 04 — backend-api

**Description:** Changes to server-side API routes, server actions, middleware, authentication logic, or data-fetching layers.

**Default Provider:** Codex running in worktree sandbox

**Risk Level:** High

**Required Gates:**
- `npm run lint` passes
- `npm run typecheck` passes
- Integration test or curl evidence attached
- No `.env` or secrets touched
- Auditor review of diff required before commit
- Human approval before merge to main

**Allowed Files:**
- `app/api/**`
- `lib/**` (server-side utilities only)
- `middleware.ts`

**Disallowed Files:**
- `supabase/migrations/**`
- `.env`, `.env.*`
- Any file touching auth secrets or payment keys
- `agent/**`

**Human Approval:** Yes

**Auto-Commit:** No — requires human approval gate

---

### 05 — supabase-security

**Description:** Schema migrations, Row-Level Security (RLS) policy changes, storage bucket policies, Edge Functions with data access, or any Supabase configuration change.

**Default Provider:** Claude (review and planning only) — no automated execution

**Risk Level:** Critical

**Required Gates:**
- Claude security review document produced
- RLS policy reviewed against MIRA_RLS_DECISION_MATRIX.md
- Human reads and approves migration SQL before apply
- No automated migration apply permitted
- Post-apply validation query results attached

**Allowed Files:**
- `supabase/migrations/**` (plan only — no auto-apply)
- `project_control/**` (security planning docs)

**Disallowed Files:**
- Any file that would auto-apply migrations
- `.env`, `.env.*`
- Production Supabase credentials

**Human Approval:** Yes — MANDATORY. No exceptions.

**Auto-Commit:** No

---

### 06 — design-polish

**Description:** Visual improvements, spacing fixes, typography adjustments, color refinements, animation polish, and component styling that does not change data logic.

**Default Provider:** Design Director (analysis) + Codex (implementation)

**Risk Level:** Low-Medium

**Required Gates:**
- Design Director review against DESIGN_RUBRIC.md
- Before/after screenshot evidence
- `npm run lint` passes
- No data logic or API files touched

**Allowed Files:**
- `components/**` (styling only)
- `styles/**`
- `app/**` (layout and visual only)
- `public/**` (assets)

**Disallowed Files:**
- `app/api/**`
- `supabase/**`
- `.env`, `.env.*`
- `agent/**`

**Human Approval:** No

**Auto-Commit:** Yes — after screenshot evidence and lint pass

---

### 07 — research

**Description:** Research Director tasks: competitive analysis, technical feasibility studies, library evaluations, pattern research, or documentation of findings.

**Default Provider:** Research Director (Claude-powered)

**Risk Level:** Low

**Required Gates:**
- Research report in standard format
- Sources cited
- No code files modified
- `git status --short` shows only docs changed

**Allowed Files:**
- `project_control/**/*.md`
- `docs/**/*.md`

**Disallowed Files:**
- All source code files
- `.env`, `.env.*`
- `supabase/**`

**Human Approval:** No

**Auto-Commit:** Yes — research docs only

---

### 08 — vendor-api-integration

**Description:** Integration with third-party APIs, SDKs, or external services: payment processors, analytics, email, SMS, AI providers, etc.

**Default Provider:** Codex running in worktree sandbox

**Risk Level:** High

**Required Gates:**
- `npm run lint` passes
- `npm run typecheck` passes
- No production API keys committed
- Secrets accessed only via environment variable references
- Auditor confirms no credentials in diff
- Human approval before merge

**Allowed Files:**
- `lib/**` (integration clients)
- `app/api/**` (webhook handlers)
- Non-secret config files

**Disallowed Files:**
- `.env`, `.env.*`
- Any file containing hardcoded API keys or secrets
- `supabase/migrations/**`

**Human Approval:** Yes

**Auto-Commit:** No

---

### 09 — deployment

**Description:** Changes to deployment configuration: CI/CD pipelines, GitHub Actions workflows, Docker configs, Vercel/Netlify config, or production environment setup.

**Default Provider:** Claude (planning document only)

**Risk Level:** Critical

**Required Gates:**
- Human reads full plan before any execution
- No automated deployment trigger permitted
- Rollback plan documented
- Human approval at every step

**Allowed Files:**
- `.github/workflows/**` (plan only)
- `project_control/**` (planning docs)

**Disallowed Files:**
- `.env`, `.env.*`
- Production secrets
- Any auto-executing deployment scripts

**Human Approval:** Yes — MANDATORY

**Auto-Commit:** No

---

### 10 — vps-ops

**Description:** VPS server operations: SSH configuration, systemd services, nginx config, cron jobs, server monitoring, log rotation, or infrastructure changes.

**Default Provider:** Claude (planning document only)

**Risk Level:** Critical

**Required Gates:**
- Human reads and approves runbook before execution
- No automated SSH or shell execution permitted
- Rollback documented
- Change log entry required

**Allowed Files:**
- `project_control/**` (ops planning docs)
- `infra/**` (config templates — no auto-apply)

**Disallowed Files:**
- Production server credentials
- `.env`, `.env.*`
- Auto-executing scripts

**Human Approval:** Yes — MANDATORY

**Auto-Commit:** No

---

### 11 — bug-fix

**Description:** Targeted fixes for identified bugs: logic errors, broken rendering, incorrect calculations, broken API responses, or UI defects.

**Default Provider:** Codex running in worktree sandbox

**Risk Level:** Medium

**Required Gates:**
- Bug reproduction documented
- Fix verified against reproduction case
- `npm run lint` passes
- `npm run typecheck` passes
- No unrelated files touched (minimal diff principle)

**Allowed Files:**
- Files directly related to the bug (scoped by Auditor)

**Disallowed Files:**
- Files unrelated to the bug
- `.env`, `.env.*`
- `supabase/migrations/**` (unless bug is data-layer; escalate to supabase-security type)

**Human Approval:** No (unless critical path or auth-related)

**Auto-Commit:** Yes — after gates pass and Auditor confirms minimal scope

---

### 12 — refactor

**Description:** Code restructuring without behavior change: renaming, extracting functions/components, reducing duplication, improving readability.

**Default Provider:** Codex running in worktree sandbox

**Risk Level:** Medium

**Required Gates:**
- `npm run lint` passes
- `npm run typecheck` passes
- Before/after behavior equivalence confirmed (test or manual verification)
- No new logic introduced
- Auditor confirms diff is behavior-neutral

**Allowed Files:**
- Scoped to the refactor target (defined before sprint starts)

**Disallowed Files:**
- `.env`, `.env.*`
- `supabase/migrations/**`
- Files outside defined refactor scope

**Human Approval:** No

**Auto-Commit:** Yes — after gates pass

---

### 13 — test-qa

**Description:** Writing or improving automated tests: unit tests, integration tests, end-to-end tests, or QA scripts.

**Default Provider:** Codex running in worktree sandbox

**Risk Level:** Low-Medium

**Required Gates:**
- Tests run and pass
- Coverage report attached (if applicable)
- No production code changed (test files only, unless fixing a testability issue)
- `npm run lint` passes

**Allowed Files:**
- `__tests__/**`
- `*.test.ts`, `*.test.tsx`, `*.spec.ts`, `*.spec.tsx`
- `e2e/**`
- `playwright/**`

**Disallowed Files:**
- Production source files (unless explicitly scoped for testability)
- `.env`, `.env.*`
- `supabase/**`

**Human Approval:** No

**Auto-Commit:** Yes — after tests pass

---

### 14 — performance

**Description:** Performance optimization: reducing bundle size, improving render performance, optimizing queries, adding caching, or improving load times.

**Default Provider:** Codex running in worktree sandbox

**Risk Level:** Medium

**Required Gates:**
- Before/after benchmark evidence attached
- No behavior change (pure optimization)
- `npm run lint` passes
- `npm run typecheck` passes
- Auditor confirms no functional regression risk

**Allowed Files:**
- Scoped to performance target (defined before sprint)

**Disallowed Files:**
- `.env`, `.env.*`
- `supabase/migrations/**` (escalate if query optimization needed)

**Human Approval:** No

**Auto-Commit:** Yes — after benchmark evidence and gates pass

---

### 15 — accessibility

**Description:** Accessibility improvements: ARIA labels, keyboard navigation, focus management, color contrast, screen reader compatibility.

**Default Provider:** Codex running in worktree sandbox

**Risk Level:** Low

**Required Gates:**
- axe-core or pa11y scan results showing improvement
- No visual regression (screenshot comparison)
- `npm run lint` passes
- No data logic changed

**Allowed Files:**
- `components/**`
- `app/**` (layout and page files)
- `styles/**`

**Disallowed Files:**
- `app/api/**`
- `supabase/**`
- `.env`, `.env.*`

**Human Approval:** No

**Auto-Commit:** Yes — after scan evidence attached

---

### 16 — privacy-data-retention

**Description:** Changes affecting data collection, storage duration, user data deletion, GDPR/CCPA compliance, logging guardrails, or privacy policy implementation.

**Default Provider:** Claude (review and planning) + human

**Risk Level:** Critical

**Required Gates:**
- Legal/compliance review checklist completed
- Data map updated (MIRA_DATA_MAP.md)
- Human approval before any code execution
- Privacy policy document reviewed
- No automated data deletion executed

**Allowed Files:**
- `project_control/**` (planning docs)
- Source files only after human approval

**Disallowed Files:**
- Production database (no automated data operations)
- `.env`, `.env.*`
- Any file that auto-executes data deletion

**Human Approval:** Yes — MANDATORY

**Auto-Commit:** No

---

## Risk Level Definitions

| Risk Level | Meaning |
|------------|---------|
| Low | Reversible, no user data impact, no production risk |
| Low-Medium | Minor visual or doc change; easily reverted |
| Medium | Code change with lint/type safety gates; isolated scope |
| High | External integration, API exposure, or data-adjacent change |
| Critical | Irreversible if wrong, user data at risk, or production system affected |

---

## Auto-Commit Decision Tree

```
Task complete?
  └── Yes → Gates defined for this type all pass?
              └── Yes → Only allowed files changed?
                          └── Yes → Human approval required for this type?
                                      └── No  → AUTO-COMMIT ALLOWED
                                      └── Yes → BLOCK — require human approval
                          └── No  → BLOCK — scope violation
              └── No  → BLOCK — run correction prompt
```

---

## Policy Integration Notes

- The Policy Engine MUST check this taxonomy before allowing any builder to proceed.
- The OpenAI Auditor MUST classify every planned task against this taxonomy before generating a sprint prompt.
- If a task spans multiple types (e.g., bug fix that requires a migration), it MUST be split into separate tasks with separate type assignments.
- "When in doubt, escalate" — unclassifiable tasks default to Human Approval: Yes.
