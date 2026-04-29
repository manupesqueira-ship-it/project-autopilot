# MIRA Data Map

This document maps what MIRA currently appears to collect, where it is expected to flow, and what still needs manual Supabase verification. It is product-specific; reusable data rules live in `CUSTOMER_DATA_POLICY.md`.

## A. Data Collected By User Flow

| Flow step | Data / object | Example QA value | Sensitivity | Notes |
|---|---|---|---|---|
| Onboarding | Name | QA Test User | personal | Fake QA value only. |
| Onboarding | Email | qa-test+manual-001@example.com | personal | Used as profile identifier in MVP, not auth. |
| Onboarding | Height | 170 cm | sensitive body data | Stored as numeric profile data. |
| Onboarding | Weight | 68 kg | sensitive body data | Stored as numeric profile data when provided. |
| Onboarding | Usual size | M | personal preference | Stored as profile preference. |
| Onboarding | Build | regular | sensitive body data | Stored as controlled body classification. |
| Onboarding | Gender | skip/f/m/nb | personal | Optional but sensitive enough to avoid logs. |
| Scan | Front photo | safe dummy image | biometric/photo-sensitive | Required for upload path; manual validation required. |
| Scan | Side photo | safe dummy image | biometric/photo-sensitive | Optional. |
| Scan | Back photo | safe dummy image | biometric/photo-sensitive | Optional. |
| Catalog/product | Selected product | local product id | internal/product preference | Current catalog uses local static product data. |
| Try-on | Selected size | M | personal preference | Sent to `/api/tryon/jobs`. |
| Try-on | Generation request metadata | product id, selected size, profile/photos payload | sensitive if profile/photos included | Current payload appears to read legacy localStorage keys; verify manually. |
| Result | Generated output metadata | image URL, video URL, status | generated/personal | Mock providers currently return external placeholder URLs. |

## B. Data Storage Location

| Field / object | Frontend state | localStorage key | Supabase table | Storage bucket/path | API route involved | Persistence status |
|---|---|---|---|---|---|---|
| Profile name | onboarding React state | none | `users_profile.name` | none | none | likely; manual verification required |
| Profile email | onboarding React state | none | `users_profile.email` | none | none | likely; manual verification required |
| Height | onboarding React state | none | `users_profile.height_cm` | none | none | likely; manual verification required |
| Weight | onboarding React state | none | `users_profile.weight_kg` | none | none | likely; manual verification required |
| Usual size | onboarding React state | none | `users_profile.usual_size` | none | none | likely; manual verification required |
| Build | onboarding React state | none | `users_profile.build` | none | none | likely; manual verification required |
| Gender | onboarding React state | none | `users_profile.gender` | none | none | likely; manual verification required |
| Profile id | browser after onboarding | `mira_profile_id` | `users_profile.id` | none | none | likely; manual verification required |
| Front photo preview | scan React state as data URL | none | optional `user_assets` row | `user-photos/<profileId>/front-<timestamp>.<ext>` | none | likely; manual verification required |
| Side photo preview | scan React state as data URL | none | optional `user_assets` row | `user-photos/<profileId>/side-<timestamp>.<ext>` | none | likely; manual verification required |
| Back photo preview | scan React state as data URL | none | optional `user_assets` row | `user-photos/<profileId>/back-<timestamp>.<ext>` | none | likely; manual verification required |
| Asset metadata | not durable in frontend after upload | none | `user_assets.asset_type`, `storage_path`, `user_profile_id` | `user-photos` | none | likely; manual verification required |
| Selected product | try-on page state/static route param | none | `generations.product_id` currently null by design | none | `/api/tryon/jobs` | partial; local product IDs are not Supabase UUIDs |
| Selected size | try-on page state | none | not directly stored in schema | none | `/api/tryon/jobs` | not persisted directly |
| Generation row | API route/server state | none | `generations` | generated output paths in columns | `/api/tryon/jobs`, `/api/tryon/status/[generationId]` | likely; manual verification required |
| Generation display metadata | server memory cache | none | not persisted | none | status API | mock/in-memory |
| Result polling data | result page state | none | reads `generations` through server route | none | `/api/tryon/status/[generationId]` | likely for status; metadata may be lost after restart |
| Legacy try-on profile payload | try-on request body | `mira_profile` | none | none | `/api/tryon/jobs` | unknown; key is read but not written by current onboarding |
| Legacy try-on photos payload | try-on request body | `mira_photos` | none | none | `/api/tryon/jobs` | unknown; key is read but not written by current scan |

## C. Sensitivity

| Data class | Sensitivity | Handling expectation |
|---|---|---|
| Product ids, route paths, product names | public/internal | Safe in logs unless combined with personal data. |
| Name, email, gender, size preference | personal | Do not log, paste into LLM chats, or expose in screenshots except sanitized QA evidence. |
| Height, weight, build | sensitive | Treat as sensitive body data; do not log. |
| User photos | biometric/photo-sensitive | Use safe dummy images only in QA; never paste or commit. |
| Storage paths containing profile ids | sensitive identifier | Do not share outside local evidence. |
| Generated images/videos | generated/personal | May reveal body shape; do not treat as public evidence unless sanitized. |
| Supabase anon key | public credential but still sensitive operational data | Do not print or paste values. |
| Service-role keys, JWTs, cookies | secret | Never print, store, commit, screenshot, or paste into LLM chats. |

## D. Logging Restrictions

Do not include the following in logs, screenshots, builder reports, Telegram alerts, prompts, or commit messages:

- Real names, real emails, real body measurements, or real gender/body profile data.
- Real customer photos or generated try-on outputs derived from real people.
- JWTs, cookies, refresh tokens, Supabase service-role keys, API keys, or passwords.
- Raw `.env` or `.env.local` contents.
- Full storage URLs or signed URLs if they expose private bucket access.
- Supabase screenshots containing unrelated users or production data.

Acceptable evidence:

- Fake QA email `qa-test+manual-001@example.com`.
- Redacted Supabase table screenshots or notes.
- Object path shape without private tokens.
- Browser console/network status with secrets redacted.
- Browser QA reports that do not contain customer data.

## E. Open Questions

- Are RLS policies enabled in the actual Supabase project for `users_profile`, `user_assets`, and `generations`?
- Is the `user-photos` bucket private in the actual Supabase project?
- Are storage access policies scoped so one user cannot read another user's photos?
- What is the intended retention period for profile rows, photos, and generated outputs?
- How will users request deletion of profile data, photos, and generated outputs?
- Should try-on persist selected size and product display metadata in `generations` or a related table?
- Should `generations.user_profile_id` be populated from `mira_profile_id` during the try-on request?
- Should current `mira_profile` / `mira_photos` localStorage reads be replaced with persisted Supabase-backed state?
- Where should generated image/video outputs be stored once real providers are enabled?
- What cleanup process should remove fake QA data after manual validation?
