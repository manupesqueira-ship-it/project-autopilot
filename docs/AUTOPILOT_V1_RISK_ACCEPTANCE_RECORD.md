# Project Autopilot v1 — Risk Acceptance Record

**Created:** 2026-05-01
**Status:** DRAFT — to be reviewed and signed off with Go/No-Go decision
**Purpose:** Explicitly document which risks are accepted, deferred, or forbidden for v1.

---

## 1. Accepted Risks for v1

These risks are known, understood, and accepted as part of declaring v1 complete.

| # | Risk | Severity | Mitigation | Acceptance Rationale |
|---|------|----------|------------|---------------------|
| A1 | OpenAI `--cycle` may fail due to billing/quota | Low | `--local-plan` fallback always available | Local planning is the primary mode; OpenAI is optional |
| A2 | Telegram alerts not recently smoke-tested | Low | Alerts are advisory, not safety-critical | Alert failure does not affect policy gates or safety |
| A3 | `npm run build` may fail on MIRA product issues | Low | Not an Autopilot gate; product issues tracked separately | Build failures are MIRA product scope, not Autopilot |
| A4 | Policy fixtures cover known scenarios only | Medium | Fixture suite is extensible; human reviews edge cases | 69+ fixtures cover all identified risk vectors; new fixtures added as risks discovered |
| A5 | Manual Claude handoff tested in dry-run only | Low | Live handoff deferred until human-approved sprint | Dry-run proves the packet generation; live execution is a future controlled step |
| A6 | No E2E test with real Supabase | Medium | Mock E2E validates full flow; real E2E blocked by security model | Real E2E is a MIRA product milestone, not an Autopilot v1 requirement |
| A7 | Evidence bundles not yet validated in CI | Low | Evidence is generated and reviewed locally | CI integration is a v2 concern |

---

## 2. Deferred Risks

These risks are recognized but explicitly deferred to a future sprint with specific conditions for re-evaluation.

| # | Risk | Deferred Until | Condition to Address |
|---|------|---------------|---------------------|
| D1 | Scheduler could be enabled accidentally | Future sprint after 5+ clean local cycles | Add config validation that hard-blocks scheduler without explicit flag |
| D2 | VPS runner environment isolation | VPS setup sprint | Security review of runner sandboxing before deployment |
| D3 | GitHub Actions workflow scope creep | GitHub Actions sprint | Define narrowly-scoped workflow with human approval |
| D4 | Multi-step loop execution failures | After multi-step dry-run proven | Full lifecycle trace reviewed by human before live run |
| D5 | Parallel agent worktree conflicts | After single-agent flow proven over many cycles | Worktree isolation testing, policy fixture coverage for cross-worktree scenarios |
| D6 | Agent-to-agent result injection | After agent communication is designed | Dedicated design sprint with trust boundary analysis |
| D7 | Cloud execution cost overruns | After VPS + cloud architecture approved | Budget hard limits, per-cycle caps, human approval for first cloud run |

---

## 3. Forbidden Risks

These risks are permanently prohibited. No sprint, no config change, and no human approval can enable them without a new policy document replacing this one.

| # | Forbidden Risk | Why |
|---|---------------|-----|
| F1 | Auto-merge of any PR | Irreversible action; human must always approve merges |
| F2 | Push to main/protected branches from any agent | Only human pushes to main; agents commit to worktree branches only |
| F3 | Live Supabase mutations from Autopilot commands | Autopilot does not write rows, run migrations, alter RLS, or delete data |
| F4 | Logging or transmitting user PII or secrets | Absolute prohibition; any violation is a hard security failure |
| F5 | Accessing `/root/bot/` or other tenant directories on VPS | Permanent security boundary; no cross-tenant access ever |
| F6 | Removing HALT file automatically | HALT removal is human-only; no script or policy outcome removes it |
| F7 | Bypassing policy gates via flags or config | No `--skip-policy`, `--force`, or `--no-policy` flag exists or will be created |
| F8 | Paid image/video generation from Autopilot | Generation API calls belong in MIRA product code, not Autopilot |

---

## 4. Supabase / MIRA Risks

| # | Risk | Status | Impact | Mitigation |
|---|------|--------|--------|------------|
| S1 | RLS disabled on all customer tables | OPEN — MIRA product blocker | Anyone with anon key can read/modify/delete all customer data | Must enable RLS before any real customer data |
| S2 | Storage buckets have no access policies | OPEN — MIRA product blocker | Uploads/reads uncontrolled | Must apply storage policies from security staging pack |
| S3 | CAPTCHA not enabled | OPEN — MIRA product blocker | Anonymous sign-ups open to abuse | Must enable hCaptcha or Turnstile |
| S4 | auth_user_id nullable and unpopulated on some rows | OPEN — code-side partially fixed | Rows without auth identity cannot be protected by RLS | Backfill or delete orphan rows after RLS enabled |
| S5 | Production Site URL not configured | OPEN — MIRA product blocker | OAuth redirects will fail outside localhost | Set in Supabase Dashboard before production |
| S6 | No privacy/retention policy | OPEN — legal/compliance gap | No defined data lifecycle | Must define before storing real customer data |

**Key principle:** These are MIRA product risks, not Autopilot risks. Autopilot does not interact with Supabase. These risks are documented here because Autopilot must not be used to bypass them.

---

## 5. Claude Sandbox Risks

| # | Risk | Status | Mitigation |
|---|------|--------|------------|
| C1 | Claude builder could write to master branch | MITIGATED | Worktree-only execution; post-builder policy blocks direct master writes |
| C2 | Claude builder could access secrets | MITIGATED | Handoff packet excludes all `.env*` files; secret exclusion in allowlists |
| C3 | Claude builder could run SQL/migrations | MITIGATED | Policy fixtures block SQL/RLS/deploy actions; handoff denylists include Supabase files |
| C4 | Claude builder could call paid APIs | MITIGATED | Handoff rules explicitly deny paid API calls; post-builder policy blocks |
| C5 | Claude builder could modify Autopilot code | MITIGATED | Handoff allowlists restrict to MIRA product files; Autopilot files in denylist |
| C6 | Live Claude execution without human approval | PREVENTED | Automatic Claude execution DISABLED; requires explicit human invocation |
| C7 | Handoff packet could contain stale or wrong context | LOW | Packet generated from current repo state; human reviews before invoking |

---

## 6. VPS Risks

| # | Risk | Status | Mitigation |
|---|------|--------|------------|
| V1 | VPS not deployed | NOT APPLICABLE for v1 | VPS is deferred scope; no VPS risk exists because no VPS exists |
| V2 | Cross-tenant directory access | DEFERRED | Security boundary defined in policy; enforcement requires VPS setup sprint |
| V3 | Runner process escape | DEFERRED | Runner isolation design documented but not implemented |
| V4 | Unattended execution on VPS | DEFERRED | Requires scheduler (disabled) + VPS (not deployed) |

---

## 7. Scheduler Risks

| # | Risk | Status | Mitigation |
|---|------|--------|------------|
| SC1 | Scheduler triggers unattended cycles | PREVENTED | Scheduler DISABLED; config confirmed in health report and Control Center |
| SC2 | Scheduler could be enabled via config change | LOW | No config file enables scheduler; requires code change + human approval |
| SC3 | Scheduler + auto-Claude = fully autonomous | PREVENTED | Both independently disabled; enabling either requires separate human sprint |

---

## 8. Auto-Merge Risks

| # | Risk | Status | Mitigation |
|---|------|--------|------------|
| AM1 | PR merged without human review | PERMANENTLY PREVENTED | No auto-merge mechanism exists; forbidden in policy |
| AM2 | Auto-merge added in future sprint | PERMANENTLY PREVENTED | Deferred indefinitely in `AUTOPILOT_DEFERRED_SCOPE.md`; policy fixtures would need to be deliberately disabled |

---

## 9. Paid API Risks

| # | Risk | Status | Mitigation |
|---|------|--------|------------|
| P1 | OpenAI Auditor live call cost | LOW | `--local-plan` is default; OpenAI call requires valid credentials + budget |
| P2 | Claude analysis call cost | LOW | Requires explicit `--claude-analysis-approved` invocation by human |
| P3 | Uncontrolled API spend | MITIGATED | Cost controller tracks estimated usage; budget limits enforced; local fallback always available |
| P4 | Image/video generation from Autopilot | PREVENTED | Permanently forbidden; generation APIs are MIRA product scope only |

---

## 10. Human Approval Requirements

These are the actions that require explicit human approval. No agent, no policy pass, and no automation can substitute for human action on these items.

| # | Action | Approval Method |
|---|--------|----------------|
| H1 | Declare v1 complete | Human fills Go/No-Go Decision Record |
| H2 | First live Claude analysis on real task | Human types `--claude-analysis-approved` with real task |
| H3 | First real sandbox worktree for MIRA task | Human confirms in approval flow |
| H4 | Enable scheduler | Forbidden until future sprint with written authorization |
| H5 | Enable automatic Claude execution | Forbidden until future sprint with written authorization |
| H6 | Merge any PR | Human clicks merge (no auto-merge) |
| H7 | Deploy to production/staging | Human-only action |
| H8 | Enable RLS / apply storage policies | Human action in Supabase Dashboard |
| H9 | Set production Site URL | Human action in Supabase Dashboard |
| H10 | Enable CAPTCHA | Human action in Supabase Dashboard |
| H11 | Add SUPABASE_SERVICE_ROLE_KEY to env | Human edits `.env.local` directly |
| H12 | Approve paid API budget increase | Human reviews cost controller limits |
| H13 | Remove HALT file | Human-only action; no automated removal |
| H14 | Re-authorize Autopilot feature work | Human writes explicit authorization in a new sprint scope document |
