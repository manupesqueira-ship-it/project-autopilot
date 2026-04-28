# Customer Data Policy

Every project must explicitly map what customer data it collects, where it is stored, how sensitive it is, and what must never be exposed. This document is the source of truth for data handling expectations.

## Data Inventory

| Field | Table / Bucket | Sensitivity | Retention | Notes |
|---|---|---|---|---|
| name | users_profile.name | PII | Until deletion | Display name, not legal name |
| email | users_profile.email | PII | Until deletion | Used for identification, not auth yet |
| height_cm | users_profile.height_cm | Body data | Until deletion | Used for try-on fitting |
| weight_kg | users_profile.weight_kg | Body data | Until deletion | Used for try-on fitting |
| usual_size | users_profile.usual_size | Preference | Until deletion | Clothing size |
| build | users_profile.build | Body data | Until deletion | Body type classification |
| gender | users_profile.gender | PII | Until deletion | Used for try-on model selection |
| Front photo | user-photos bucket | Biometric | Until deletion | Private bucket. Full body photo. |
| Side photo | user-photos bucket | Biometric | Until deletion | Private bucket. |
| Back photo | user-photos bucket | Biometric | Until deletion | Private bucket. |
| Try-on image | generations bucket | Generated | Until deletion | Public bucket. AI-generated composite. |
| Try-on video | generations bucket | Generated | Until deletion | Public bucket. AI-generated composite. |

## Sensitivity Levels

- **PII**: Personally identifiable information. Must be stored securely, never logged.
- **Body data**: Physical measurements and body type. Must be treated as sensitive PII.
- **Biometric**: Photos of the user's body. Highest sensitivity. Private storage only.
- **Generated**: AI-generated output. Lower sensitivity but may reveal body shape.
- **Preference**: User preferences. Low sensitivity but still personal.

## Storage Rules

- **Private buckets** (user-photos): No public URLs. Access requires auth or signed URLs.
- **Public buckets** (generations, product-images): URLs are accessible. Do not store raw user photos here.
- **Database**: Supabase with RLS planned for production. Currently off for MVP.

## What Must Never Appear In

- **Logs**: No email, name, photo URLs, body measurements, or profile IDs in log files.
- **Prompts**: Builder prompts must not contain real user data. Use placeholders or references.
- **Screenshots**: QA screenshots must not show real user data. Use test data.
- **Error messages**: Error responses must not leak user data. Return generic messages.
- **Git history**: No user data in commits, diffs, or commit messages.
- **Telegram alerts**: No user data in alert messages. Reference IDs only.

## Deletion Expectations

- Users should be able to request deletion of their profile and all associated data.
- Deletion must cascade: profile -> assets -> generations -> events.
- Implementation is not required yet but the schema must support it (ON DELETE CASCADE is already in place).

## Current Gaps

- RLS is off. Must be enabled before any real user data is stored.
- No auth. Profile IDs are stored in localStorage. Not secure for production.
- No signed URLs for private bucket access. Photos are uploaded but not yet securely served.
- No data export or deletion endpoint exists yet.
