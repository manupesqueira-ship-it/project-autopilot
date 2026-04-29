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
