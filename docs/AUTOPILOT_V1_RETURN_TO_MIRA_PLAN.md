# Project Autopilot v1 — Return to MIRA Plan

**Created:** 2026-05-01
**Status:** DRAFT — to be activated after GO decision
**Purpose:** Define exactly when to stop building Autopilot and how to resume MIRA product development.

---

## 1. When to Stop Building Autopilot

**Stop now.** Project Autopilot v1 is complete (or nearly complete) when:

- All 16+ required capability commands pass clean.
- Policy fixtures pass at target count (at least 69/69).
- All safety gates confirmed in the Go/No-Go Decision Record.
- Human has declared GO.

After GO:
- **No new Autopilot features** until MIRA product reaches a natural pause point.
- **No scope creep** into VPS, GitHub Actions, scheduler, parallel agents, or cloud execution.
- **Only bounded fixes** allowed — if a policy gate breaks during MIRA work, fix the gate. Do not expand it.
- **Any Autopilot improvement must take less than one commit.** If it requires more, defer it.

---

## 2. How to Resume MIRA Product Development

### Step 1: Close Autopilot branches
- Merge or archive any open `agent/autopilot-*` branches.
- Confirm master is clean: `git status --short` returns empty.

### Step 2: Update TASK_QUEUE.md
- Replace the current Autopilot task with the next MIRA product task.
- Recommended first task: **Enable MIRA Anonymous Sign-Ins and apply RLS policies.**

### Step 3: Set up the MIRA development environment
- Confirm `.env.local` has all 3 Supabase env vars (NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY).
- Run `npm run dev` and confirm the app starts.
- Run `python -B project_autopilot/agent_loop.py --project mira --doctor` to confirm health.

### Step 4: Use Autopilot as infrastructure, not the focus
- Generate builder prompts with `--local-plan`.
- Run post-builder policy on every code change.
- Use manual Claude handoff for complex tasks.
- Do not build more Autopilot.

---

## 3. Recommended First MIRA Tasks After Autopilot v1

### Priority 1: Supabase Security (CRITICAL)
**Enable Anonymous Sign-Ins and apply RLS policies**

1. Enable CAPTCHA (hCaptcha or Turnstile) in Supabase Dashboard.
2. Set `SUPABASE_SERVICE_ROLE_KEY` in `.env.local`.
3. Apply RLS policies from `supabase/drafts/` — staging test first.
4. Follow `MIRA_SUPABASE_MANUAL_ACTIVATION_CHECKLIST.md`.
5. Run `python -B project_autopilot/supabase_auth_verify.py --project mira` after each step.
6. Confirm `NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS=false npm run dev` runs real flow.
7. Run manual E2E from `MIRA_E2E_VALIDATION_PLAN.md`.

### Priority 2: Storage Policies
- Apply storage bucket policies (user-photos owner-only, generations private+signed URL, product-images public read).
- Follow the security staging pack in `project_control/security/`.

### Priority 3: Production Readiness
- Set production Site URL in Supabase Dashboard.
- Configure redirect URLs for OAuth/email.
- Define privacy/retention policy.
- Enable leaked-password protection.

### Priority 4: Real Generation Providers
- Replace mock image/video providers with real API integrations.
- This is MIRA product code, not Autopilot scope.

---

## 4. How to Use Autopilot for MIRA Without Overbuilding

### DO
- Use `--local-plan` before each MIRA task to get a structured builder prompt.
- Run post-builder policy (`--policy-check`) after every code change.
- Use `--doctor` at the start of each work session.
- Use `flow_qa.py --validate-mock-e2e` to validate flow changes.
- Use `claude_manual_handoff.py --dry-run` to generate handoff packets when you want Claude Code to work on a MIRA task in a worktree.

### DO NOT
- Add new Autopilot features "while you're in there."
- Build a VPS runner because it would be "nice to have."
- Enable the scheduler "just to test it."
- Expand the policy fixture suite beyond what current MIRA tasks require.
- Refactor the Autopilot codebase unless a gate is broken.

### Rule of thumb
If an Autopilot change takes more than one commit, it is scope creep. Defer it.

---

## 5. Which Tasks Should Go Through Each Tool

### Codex
- Quick, well-scoped code changes (add a component, fix a bug, add a test).
- Tasks where the change is obvious and the context is small.
- Use when: you know exactly what to change and the file count is small.

### Manual Claude Sandbox
- Complex, multi-file MIRA tasks that benefit from Claude's analysis.
- Tasks where you want a sandboxed worktree with full context.
- Use when: you want Claude to explore the codebase and propose a solution, then you review and merge.
- Flow: `claude_manual_handoff.py --dry-run` to generate packet, invoke Claude Code in worktree, review diff, run post-builder policy, merge if SAFE_TO_COMMIT.

### OpenAI Auditor
- Supervisor-level planning when you want a structured task plan from the OpenAI model.
- Use when: you need a second opinion on task scope or want to validate your plan.
- Note: Requires valid OpenAI API credentials and budget.

### Human Review
- All Supabase Dashboard actions (enable sign-ins, apply RLS, configure CAPTCHA).
- All deployment decisions.
- All security-sensitive changes (storage policies, auth config, production URLs).
- Any change that touches `.env*` files.
- Any change where the post-builder policy returns HUMAN_REVIEW_REQUIRED or BLOCKED.

---

## 6. What MIRA Work Is Still Blocked by Supabase

| Blocked Task | Why | Unblock Action |
|-------------|-----|----------------|
| Real customer data storage | RLS disabled, no policies, anon has full access | Apply RLS + storage policies |
| Real user photos | user-photos bucket has no access policies | Apply storage policies |
| Production deployment | Site URL is localhost:3000 | Set production URL in Dashboard |
| Real generation providers | Generations bucket is public with no restrictions | Apply storage policies, add MIME/size limits |
| User identity beyond localStorage | auth_user_id nullable, no CAPTCHA | Enable CAPTCHA, enforce auth_user_id |
| Privacy compliance | No retention/deletion policy | Define and implement policy |
| OAuth/email auth | Redirect URLs empty | Configure redirect URLs |

---

## 7. What MIRA Work Can Proceed Safely Without Live Supabase

| Safe Task | Why |
|-----------|-----|
| UI/UX improvements | Mock mode provides all needed data |
| New page/component development | Mock providers supply test data |
| Internationalization (i18n) work | String-only, no DB dependency |
| Design system refinement | CSS/Tailwind only |
| Copywriting updates | Content-only changes |
| Flow QA selector maintenance | data-testid attributes, no DB |
| Internal demo improvements | Uses QA mock mode exclusively |
| API route structure changes | Can be tested with mock providers |
| Client-side logic (state, navigation) | No DB dependency |
| Accessibility improvements | DOM-only changes |
| Performance optimization (bundle, images) | Build-time optimization |

All of the above can use `--local-plan`, post-builder policy, and mock E2E validation safely.
