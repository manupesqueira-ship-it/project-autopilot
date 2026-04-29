# Human Questions

Non-blocking questions go here so the agent can keep working while preserving context for later review.

## Open Questions

### 2026-04-28 05:10 UTC - OpenAI API budget for Project Autopilot

Status: open
Severity: non-blocking
Source: agent

Question:
What monthly OpenAI API budget should Project Autopilot use by default? Currently set to $100/month in mira.yaml.

Why it matters:
The budget controls whether `--cycle` can run and how many supervisor calls are allowed per day. Too low and cycles are blocked frequently. Too high and costs accumulate without oversight.

### 2026-04-28 05:10 UTC - Should Project Autopilot live in its own repo?

Status: open
Severity: non-blocking
Source: agent

Question:
Should Project Autopilot eventually be extracted to its own repository, separate from MIRA?

Why it matters:
Currently Project Autopilot lives under `project_autopilot/` inside the MIRA repo. This works for now but means every project that uses it would need a copy or a git submodule. A standalone repo would allow independent versioning and reuse.

### 2026-04-28 05:10 UTC - Scheduler execution environment

Status: open
Severity: non-blocking
Source: agent

Question:
Should the future scheduler run locally (cron on dev machine), on a VPS, or not at all yet?

Why it matters:
The scheduler is listed as a future task but the execution environment affects design decisions (e.g., local cron vs. systemd timer vs. cloud function). No scheduler is needed until the manual workflow is proven reliable.

### 2026-04-29 - Should MIRA use Supabase Anonymous Auth for MVP identity?

Status: open
Severity: non-blocking
Source: Security alignment audit

Question:
Supabase Anonymous Auth would create real auth.users rows and JWTs without requiring user login. This gives every visitor a stable auth.uid() that RLS policies can use. Should MIRA implement this as the MVP identity layer?

Why it matters:
Without auth.uid(), RLS policies cannot enforce row-level ownership. Anonymous Auth is the minimum viable path to data isolation. The alternative is routing all writes through API routes using service_role, which requires more code changes.

### 2026-04-29 - Should all customer-data writes go through API routes?

Status: open
Severity: non-blocking
Source: Security alignment audit

Question:
Currently onboarding and scan pages write directly to Supabase tables and storage from the browser using the anon key. Should all customer-data writes be moved to API routes using service_role, or is client-side writes with RLS acceptable?

Why it matters:
Client-side writes with RLS are simpler but expose table structure. Server-side writes via API routes give more control but require rewriting onboarding and scan flows.

### 2026-04-29 - Are public buckets generations and product-images intentionally public?

Status: open
Severity: non-blocking
Source: Security alignment audit

Question:
The generations bucket (try-on output images/videos) and product-images bucket are both public. Product images being public is expected. But generation outputs contain user likeness — should the generations bucket be made private with signed URLs?

Why it matters:
Public bucket means anyone with the URL can view try-on outputs of any user. This may be acceptable for MVP but could be a privacy concern with real users.

### 2026-04-29 - What is the retention period for uploaded user photos and generated outputs?

Status: open
Severity: non-blocking
Source: Security alignment audit

Question:
How long should MIRA keep user-uploaded photos (body scans) and generated try-on outputs? Options: 30 days, 90 days, indefinite, user-controlled.

Why it matters:
Required for privacy compliance. No retention policy is currently enforced. Body photos are sensitive biometric-adjacent data.

### 2026-04-29 - Is MIRA allowed to store face/body photos during MVP testing?

Status: open
Severity: non-blocking
Source: Security alignment audit

Question:
MIRA's scan flow captures front, side, and back body photos. Are real human photos acceptable during MVP testing, or should only synthetic/placeholder images be used until security is in place?

Why it matters:
With RLS disabled and no auth, any stored photos are accessible to anyone with the anon key. Real body photos should not be stored in this state.

### 2026-04-29 - Should localStorage profile flow be treated as mock-only until auth is added?

Status: open
Severity: non-blocking
Source: Security alignment audit

Question:
The current flow uses localStorage mira_profile_id as the sole identity source. Should this be explicitly treated as a mock/development-only flow, with a clear "this is not secure" boundary?

Why it matters:
If treated as mock-only, the security expectation is set correctly. If treated as production-ready, the identity gap is a critical vulnerability.

### 2026-04-29 - Can existing Supabase test data be deleted, or must it be migrated?

Status: open
Severity: non-blocking
Source: Security alignment audit

Question:
When implementing auth and RLS, existing rows in users_profile, user_assets, and generations have NULL auth_user_id. Can these be deleted (fresh start), or must they be migrated to new auth identities?

Why it matters:
Fresh deletion is simpler and safer. Migration requires creating anonymous auth users and backfilling auth_user_id, which is complex and fragile. Decision depends on whether any existing data has value.

### 2026-04-29 - Should Anonymous Sign-Ins be enabled now?

Status: open
Severity: non-blocking
Source: Supabase Auth Dashboard audit

Question:
Anonymous Sign-Ins are currently OFF. The code-side auth helper (`getOrCreateAnonymousUser()`) returns null until this is enabled, so `auth_user_id` stays null on every profile row. Should Anonymous Sign-Ins be enabled now for development, or only at a specific milestone?

Why it matters:
This is the single prerequisite gating RLS enablement. Without it, all auth-related code runs in fallback mode and no row-level data isolation is possible.

### 2026-04-29 - Should new signups remain open before launch?

Status: open
Severity: non-blocking
Source: Supabase Auth Dashboard audit

Question:
Supabase currently allows new user signups (email/password) with no CAPTCHA and no leaked-password protection. Should signups be restricted or should abuse protection be enabled before any public-facing testing?

Why it matters:
Open signups without CAPTCHA allow bots to create unlimited auth.users rows and potentially spam the database. Even for internal testing this creates noise and potential cost.

### 2026-04-29 - Should CAPTCHA/Turnstile be enabled before public testing?

Status: open
Severity: non-blocking
Source: Supabase Auth Dashboard audit

Question:
CAPTCHA / Attack Protection is OFF. Supabase supports hCaptcha and Cloudflare Turnstile. Should one of these be enabled now, or deferred until closer to launch?

Why it matters:
Without CAPTCHA, sign-up and sign-in endpoints are unprotected. If Anonymous Sign-Ins are enabled, anonymous session creation is also unprotected. This is low-risk for private dev but should be resolved before any public URL is shared.

### 2026-04-29 - What production Site URL and Redirect URLs should be configured?

Status: open
Severity: non-blocking
Source: Supabase Auth Dashboard audit

Question:
Site URL is currently `http://localhost:3000` and Redirect URLs are empty. What production domain should be set? Are there staging URLs that should be added? This affects email confirmation links, OAuth callbacks, and password reset flows.

Why it matters:
Email confirmation and any future OAuth flow will fail for users not on localhost. This must be set before any real user interacts with auth.

### 2026-04-29 - Will auth remain email-only, or should Google OAuth be enabled later?

Status: open
Severity: non-blocking
Source: Supabase Auth Dashboard audit

Question:
All OAuth providers are currently OFF. For the MVP, is email + anonymous auth sufficient, or should Google OAuth (or another provider) be planned?

Why it matters:
Adding OAuth later is straightforward but affects UX design, redirect URL configuration, and consent flow. Better to decide early so the auth UI can be designed accordingly.

### 2026-04-29 - Should image-generation logic stay in Next.js or move to Edge Functions?

Status: open
Severity: non-blocking
Source: Supabase Auth Dashboard audit

Question:
There are 0 Edge Functions deployed. Try-on generation currently runs as a fire-and-forget background task inside the Next.js API route. Should this remain in Next.js, or should Supabase Edge Functions be considered for better isolation, timeouts, and scaling?

Why it matters:
Next.js API routes run in the same process as the web server. Long-running generation tasks can block other requests or be killed by platform timeouts. Edge Functions provide isolated execution but add deployment complexity. This is an architecture decision that affects the scheduler readiness milestone.

### 2026-04-29 - Is SUPABASE_SERVICE_ROLE_KEY set in .env.local?

Status: open
Severity: non-blocking
Source: Anonymous auth foundation sprint

Question:
The generation-store now uses `createServiceRoleServer()` which requires `SUPABASE_SERVICE_ROLE_KEY` in `.env.local` to bypass RLS for server-side writes. If not set, it falls back to the anon client (which works today but will break when RLS is enabled). Is this key already in `.env.local`?

Why it matters:
Once RLS is enabled on the `generations` table, server-side INSERT/UPDATE from API routes will fail unless service_role is configured. This is a prerequisite for the RLS enablement sprint.

## Format

```md
### YYYY-MM-DD HH:MM - Short title

Status: open
Severity: non-blocking
Source: agent | builder | qa | human

Question:
...

Why it matters:
...
```
