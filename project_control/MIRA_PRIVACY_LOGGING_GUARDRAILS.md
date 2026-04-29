# MIRA Privacy & Logging Guardrails

> Rules for handling sensitive data in logs, console output, API responses, and error messages.
> Last updated: 2026-04-29

---

## 1. Sensitive Data Categories

| Category | Examples | Risk |
|---|---|---|
| User PII | name, email | Identity exposure |
| Body attributes | height_cm, weight_kg, build, gender | Biometric-adjacent |
| Photo paths | storage_path, front_photo, side_photo | Links to body images |
| Generated output paths | image_output_path, video_output_path | Links to user likeness |
| Auth identifiers | auth_user_id, profile ID | User tracking |
| Auth tokens | access_token, refresh_token, session | Session hijacking |
| Service credentials | SUPABASE_SERVICE_ROLE_KEY, sb_secret | Full database access |
| Request bodies | Full POST payloads with profile/photos | All of the above |

## 2. Never Log

- `access_token` or `refresh_token` values
- `SUPABASE_SERVICE_ROLE_KEY` or `sb_secret_*` values
- Full `session` objects
- Full `profile` or `profileRow` objects
- Raw uploaded image data or file contents
- User photo `storage_path` values
- Generated `image_output_path` or `video_output_path` values
- Raw request bodies containing user data
- Raw Supabase error objects (may contain SQL details)

## 3. Safe Logging Examples

```typescript
// SAFE: generic operation label
console.error("[tryon/jobs] generation failed");

// SAFE: non-sensitive status
console.log(`[flow] status: ${status}`);

// SAFE: generic auth warning
console.warn("[mira/auth] Anonymous sign-in unavailable");

// SAFE: operation identifier only
console.error("[result] polling failed");
```

## 4. Unsafe Logging Examples

```typescript
// UNSAFE: raw error object may contain stack traces, SQL, internal paths
console.error("generation failed", err);

// UNSAFE: raw profile payload
console.log("profile:", profileRow);

// UNSAFE: token value
console.log("session:", session);

// UNSAFE: storage path to user photos
console.log("uploaded to:", storagePath);
```

## 5. API Route Error Response Rules

- Return generic error messages: `{ error: "invalid_request" }`
- Never return raw error objects: `{ error: err }`
- Never return stack traces
- Never return SQL error details
- Never return file paths or storage paths
- Use HTTP status codes for error classification (400, 401, 404, 500)

## 6. Frontend Error Display Rules

- Show generic user-friendly messages
- Never display raw `error.message` from Supabase/server
- Never display SQL errors, auth internals, or file paths
- Example: "Failed to save profile. Please try again."
- Not: "duplicate key value violates unique constraint users_profile_email_key"

## 7. Flow QA / Logging Rules

- Flow QA logs are local-only and gitignored
- Flow QA must not log user tokens or sessions
- Flow QA may log non-sensitive flow status (PASS/FAIL/step names)
- Flow QA screenshots may contain test data — keep in gitignored directory

## 8. Automated Audit

Run the sensitive logging audit:
```bash
python -B project_autopilot/sensitive_logging_audit.py --project mira
```

Verdicts:
- **PASS**: No concerning patterns found
- **WARN**: Patterns need human review
- **FAIL**: Obvious secret/token/session exposure found — fix before real customer data

## 9. What Remains Blocked Before Real Users

- RLS must be enabled with row-level ownership policies
- Storage policies must restrict access to owner only
- CAPTCHA must be enabled
- Retention/deletion policy must be decided
- Privacy policy/terms must be written
- Real customer data decision must be approved
