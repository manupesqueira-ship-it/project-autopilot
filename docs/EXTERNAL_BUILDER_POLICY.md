# External Builder Policy

> Governs how outputs from external visual reference tools (Base44, Lovable, or similar) enter the MIRA project.

---

## Core Principle

**Base44, Lovable, and similar tools are optional visual reference generators only.**

They are NOT:
- The source of truth for MIRA's architecture.
- The source of truth for MIRA's design system.
- Authorized to receive production credentials.
- Authorized to merge code directly.

---

## What External Builders CANNOT Receive

| Prohibited | Reason |
|------------|--------|
| `.env` / `.env.local` / any secrets | Security — credentials must never leave the repo |
| Production Supabase URL or keys | Security — prevents unauthorized database access |
| Real customer data | Privacy — MIRA customer data never leaves controlled systems |
| Real customer photos | Privacy — photos are sensitive biometric-adjacent data |
| API keys for paid services | Cost — prevents unauthorized billing |
| Production database access | Security — prevents data corruption or exfiltration |
| RLS policies or migration SQL | Security — prevents security bypass |
| Auth middleware or session logic | Security — prevents auth bypass |

---

## What External Builders CAN Receive

- Abstract design briefs describing layout, color, typography goals.
- Wireframe-level descriptions of page structure.
- Component names and prop interfaces (no implementation).
- Mock data schemas (no real data).
- Screenshot references of public-facing UI (no admin/debug views).
- Tailwind config tokens (colors, spacing, fonts — no secrets).

---

## Intake Process

All external builder output must follow this pipeline before entering MIRA:

### Step 1: Isolation

- External output must enter through a **dedicated branch or worktree**.
- Branch naming: `external/<tool>/<purpose>` (e.g., `external/lovable/catalog-redesign`).
- Never commit external output directly to `master` or any active agent branch.

### Step 2: Project Autopilot Intake

- Use the `EXTERNAL_BUILDER_IMPORT_REVIEW.template.md` template.
- Codex/Claude reviews the output against MIRA's architecture.
- All files are listed and categorized (safe visual / unsafe backend / unknown).

### Step 3: Security Review

External output is treated as **untrusted code**. Review must verify:

- [ ] No hardcoded secrets, API keys, or credentials.
- [ ] No Supabase client initialization or direct database calls.
- [ ] No authentication or session management logic.
- [ ] No server-side API route definitions.
- [ ] No file upload to external services.
- [ ] No `fetch()` to unknown external URLs.
- [ ] No `eval()`, `dangerouslySetInnerHTML`, or XSS vectors.
- [ ] No `localStorage` writes that conflict with MIRA's auth flow.
- [ ] No npm package additions without review.

### Step 4: Architecture Preservation

Imported components must:

- [ ] Use MIRA's existing design tokens (colors, spacing, fonts from `tailwind.config.ts`).
- [ ] Preserve existing `data-testid` attributes — never remove or rename.
- [ ] Preserve existing `aria-*` attributes — never remove.
- [ ] Follow MIRA's component structure (`components/ui/`, `components/app/`).
- [ ] Use MIRA's existing routing structure (`app/[locale]/...`).
- [ ] Not introduce new state management libraries.
- [ ] Not introduce new CSS frameworks or override Tailwind.

### Step 5: QA Validation

Before merge, imported code must pass:

- [ ] `npm run lint` — no new warnings.
- [ ] `npm run typecheck` — no type errors.
- [ ] `npm run build` — successful build.
- [ ] `flow_qa.py --validate-mock-e2e` — existing flows unbroken.
- [ ] `visual_qa.py --project mira` — visual standards met.
- [ ] Manual mobile review at 375px width.

### Step 6: Merge

- Merge via PR with review notes documenting:
  - What was imported.
  - What was modified from the original output.
  - What was rejected and why.
- Squash merge preferred to keep history clean.

---

## Rejected Patterns

The following patterns from external builders must always be rejected:

1. **Backend generation** — External tools must never generate API routes, middleware, or server logic.
2. **Auth implementation** — Session, login, signup, or token management from external tools is never accepted.
3. **Database schemas** — Table definitions, migrations, or RLS policies from external tools are never accepted.
4. **Storage integration** — File upload, bucket creation, or storage policies from external tools are never accepted.
5. **Environment variable usage** — Any `process.env` reference in external output is rejected.
6. **Direct deployment** — External tools must never have deploy access or CI/CD integration.

---

## Accountability

- The developer importing external output is responsible for the security review.
- Project Autopilot templates provide structure but do not replace human judgment.
- Any security incident traceable to unreviewed external code is a process failure.

---

*This policy exists to let MIRA benefit from external visual prototyping tools without compromising architecture, security, or data privacy.*
