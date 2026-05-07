# External Builder Import Review

> Use this template when reviewing output from Base44, Lovable, or similar tools before importing into MIRA.

---

## Import Metadata

- **Source tool:** `[Base44 / Lovable / Other]`
- **Branch:** `external/[tool]/[purpose]`
- **Date:** `[YYYY-MM-DD]`
- **Reviewer:** `[Name or agent ID]`
- **Files received:** `[count]`

---

## File Inventory

List every file from the external output and classify it:

| File | Type | Classification | Action |
|------|------|---------------|--------|
| `example/Component.tsx` | React component | SAFE — visual only | Import with modifications |
| `example/api/route.ts` | API route | UNSAFE — backend logic | **REJECT** |
| `example/lib/supabase.ts` | Supabase client | UNSAFE — database access | **REJECT** |
| ... | ... | ... | ... |

### Classification Key

- **SAFE** — Pure visual/UI code, no side effects.
- **UNSAFE** — Backend, auth, database, storage, or security logic. **Always reject.**
- **NEEDS REVIEW** — Mixed or unclear. Requires manual inspection.

---

## Security Checklist

- [ ] No hardcoded secrets, API keys, or credentials.
- [ ] No Supabase client initialization (`createClient`, `createBrowserClient`).
- [ ] No direct database queries (`from('table')`, `.select()`, `.insert()`).
- [ ] No authentication logic (login, signup, session, token refresh).
- [ ] No server-side API routes (`app/api/`, `pages/api/`).
- [ ] No file upload to external services.
- [ ] No `fetch()` to unknown external URLs.
- [ ] No `eval()`, `Function()`, or dynamic code execution.
- [ ] No `dangerouslySetInnerHTML` without sanitization.
- [ ] No `localStorage` writes that conflict with MIRA's auth flow.
- [ ] No new npm package dependencies.
- [ ] No environment variable references (`process.env`).

**Security verdict:** `[PASS / FAIL — list violations]`

---

## Architecture Preservation Checklist

- [ ] Uses MIRA's Tailwind design tokens (no custom theme overrides).
- [ ] Follows MIRA's component directory structure (`components/ui/`, `components/app/`).
- [ ] Follows MIRA's routing structure (`app/[locale]/...`).
- [ ] Preserves all existing `data-testid` attributes.
- [ ] Preserves all existing `aria-*` attributes.
- [ ] Does not introduce new state management (Redux, Zustand, Jotai, etc.).
- [ ] Does not override Tailwind with custom CSS or another framework.
- [ ] Does not modify `next.config.mjs`, `tsconfig.json`, or `package.json`.
- [ ] Does not add middleware or modify existing middleware.

**Architecture verdict:** `[PASS / FAIL — list violations]`

---

## Visual Quality Checklist

- [ ] Matches MIRA Visual Quality Standard spacing rhythm (4px base).
- [ ] Matches MIRA typography hierarchy.
- [ ] All buttons have hover, focus, active, disabled states.
- [ ] Loading states are designed (not blank).
- [ ] Error states are designed (not raw error text).
- [ ] Empty states are designed (not blank area).
- [ ] Mobile layout works at 375px without horizontal scroll.
- [ ] Touch targets are 44×44px minimum.
- [ ] Color contrast meets WCAG AA.

**Visual quality verdict:** `[PASS / FAIL — list issues]`

---

## Accessibility Checklist

- [ ] All interactive elements have keyboard focus indicators.
- [ ] All images have alt text.
- [ ] All form inputs have associated labels.
- [ ] Toggle/chip buttons use `aria-pressed`.
- [ ] Error messages use `role="alert"`.
- [ ] Status updates use `aria-live`.
- [ ] No content only accessible via hover (no tooltips without keyboard trigger).

**Accessibility verdict:** `[PASS / FAIL — list issues]`

---

## Modifications Required

List changes needed to make the imported code MIRA-compatible:

1. `[File]` — `[What needs to change and why]`
2. ...

---

## Test Validation

After import, verify:

- [ ] `npm run lint` — passes.
- [ ] `npm run typecheck` — passes.
- [ ] `npm run build` — passes.
- [ ] `flow_qa.py --validate-mock-e2e` — existing flows unbroken.
- [ ] `visual_qa.py --project mira` — visual standards met.
- [ ] Manual mobile review at 375px.

---

## Final Verdict

- [ ] **APPROVED FOR IMPORT** — all checks pass, modifications documented.
- [ ] **APPROVED WITH CONDITIONS** — import after listed modifications.
- [ ] **REJECTED** — security or architecture violations found. Do not import.

**Rejection reasons (if any):**
```
[List specific reasons for rejection]
```

---

*Template version: 1.0 | See: project_control/EXTERNAL_BUILDER_POLICY.md*
