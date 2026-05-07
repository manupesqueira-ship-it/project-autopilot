# AUTOPILOT BUILDER REPORT STANDARD

Version: 1.0
Status: Canonical
Owner: Project Autopilot Control System

---

## Purpose

Every builder (Codex, Claude sandboxed, or any automated agent) that executes a task in the Project Autopilot system MUST produce a report in this format upon task completion, blocking, or abortion.

The OpenAI Auditor and the Multi-Step Loop use this report as the authoritative record of what happened. An incomplete or missing report is treated as a BLOCKER with severity HIGH.

---

## Report Format

All reports must be produced as a structured Markdown document. Each field is mandatory unless marked OPTIONAL. Fields must appear in the order listed below.

---

### Section 1 — Identity

```
TASK ID:         {task ID assigned by Auditor}
TASK TITLE:      {title of the task}
TASK TYPE:       {taxonomy type from AUTOPILOT_TASK_TAXONOMY.md}
BUILDER:         {Codex / Claude / Design Director / Research Director}
BRANCH:          {git branch name}
REPORT TIMESTAMP: {ISO 8601 datetime}
REPORT STATUS:   {COMPLETE / BLOCKED / ABORTED}
```

---

### Section 2 — Executive Summary

A single paragraph (3-6 sentences) describing:
- What was attempted
- What was accomplished
- Whether it succeeded, was blocked, or was aborted
- Any critical finding the Auditor must act on immediately

Example:
> Implemented the session timeout warning modal in `components/SessionWarning.tsx`. All three validation commands passed. No secrets were touched. The component renders correctly in development. Auto-commit was performed on branch `feature/session-warning`. Recommended next step is a Design Director review of the new modal's visual treatment.

---

### Section 3 — Files Created

List every file that was newly created during this task.

```
FILES CREATED:
- {absolute or repo-relative path} — {one-line description}
- {path} — {description}
(None — if no files were created)
```

---

### Section 4 — Files Modified

List every file that was modified during this task.

```
FILES MODIFIED:
- {path} — {what changed in one line}
- {path} — {what changed}
(None — if no files were modified)
```

---

### Section 5 — Files Deleted (OPTIONAL)

List any files deleted, with reason.

```
FILES DELETED:
- {path} — {reason for deletion}
(None — if no files were deleted)
```

---

### Section 6 — Commands Run

List every shell command executed during the task, in order, with output summary.

```
COMMANDS RUN:
1. {command}
   Output: {PASS / FAIL / output summary}

2. {command}
   Output: {PASS / FAIL / output summary}
```

---

### Section 7 — Validations

Report each required validation gate and its result.

```
VALIDATIONS:
- npm run lint:        {PASS / FAIL / SKIPPED — reason}
- npm run typecheck:   {PASS / FAIL / SKIPPED — reason}
- python -B -m compileall: {PASS / FAIL / SKIPPED — reason}
- git diff --check:    {PASS / FAIL}
- test suite:          {PASS / FAIL / SKIPPED — reason}
- git status --short:  {output}
- git diff --stat:     {output}
```

Additional validation commands specific to the task type must also be listed.

---

### Section 8 — Risks

List any risks identified during the task, even if the task succeeded.

```
RISKS:
- {risk description} — Severity: {CRITICAL / HIGH / MEDIUM / LOW}
(None identified — if clean)
```

If a CRITICAL or HIGH risk is identified, the Auditor MUST be notified regardless of task status.

---

### Section 9 — Blockers

List any blockers that prevented full completion.

```
BLOCKERS:
- {blocker description}
  Type: {scope-violation / validation-failure / policy-violation / design-failure /
         research-required / backend-security-failure / forbidden-file / ambiguous}
  Severity: {CRITICAL / HIGH / MEDIUM}
  Recommended resolution: {correction-prompt / human-escalation / task-redesign / abandon}
(None — if no blockers)
```

---

### Section 10 — Screenshots / Evidence (OPTIONAL for most types; REQUIRED for design-polish, ui-product-code, accessibility)

```
SCREENSHOTS / EVIDENCE:
- {description}: {file path or URL}
- Benchmark before: {value}
- Benchmark after:  {value}
(None — if not applicable)
```

---

### Section 11 — Security Checklist

These fields are MANDATORY on every report. Answering incorrectly is a policy violation.

```
SECRETS TOUCHED:           {NO / YES — if YES, list which files and what was accessed}
APIS CALLED:               {NO / YES — if YES, list which APIs and for what purpose}
SQL EXECUTED:              {NO / YES — if YES, paste the SQL or describe the operation}
SCHEDULER ENABLED:         {NO / YES — if YES, describe what was scheduled}
AUTO-CLAUDE ENABLED:       {NO / YES — if YES, describe what was triggered}
ENV FILES READ OR WRITTEN: {NO / YES — if YES, list which files}
SUPABASE MIGRATIONS APPLIED: {NO / YES — if YES, describe migration}
```

Expected values for standard tasks:
- SECRETS TOUCHED: NO
- SCHEDULER ENABLED: NO
- AUTO-CLAUDE ENABLED: NO
- SUPABASE MIGRATIONS APPLIED: NO (unless task type is supabase-security with human approval)

Any YES answer triggers automatic Auditor review before the task is closed.

---

### Section 12 — Git State

```
COMMIT HASH:       {full commit hash, or "NO COMMIT" if auto-commit did not occur}
COMMIT MESSAGE:    {commit message, or "N/A"}
CURRENT BRANCH:    {branch name}
GIT STATUS:        {output of git status --short}
GIT DIFF STAT:     {output of git diff --stat HEAD~1 or equivalent}
```

---

### Section 13 — Recommended Next Step

A single, actionable recommendation for what the Auditor or human should do next.

```
RECOMMENDED NEXT STEP:
{One clear instruction. Examples:
  - "Assign Design Director review of the new modal."
  - "Escalate BLOCKER to human decision queue — scope exceeds autopilot authority."
  - "Run next task in queue: {TASK_ID}."
  - "Human approval required before applying migration."
  - "Task complete. No further action needed."}
```

---

## Report Completeness Rules

1. A report with any mandatory field missing is classified as INCOMPLETE.
2. An INCOMPLETE report is treated as a BLOCKER by the Auditor.
3. The Auditor MUST request a corrected report before proceeding with dependent tasks.
4. A report with REPORT STATUS: BLOCKED that lacks a BLOCKERS section is invalid.
5. A report claiming REPORT STATUS: COMPLETE with no COMMIT HASH (when auto-commit was applicable) is flagged for Auditor investigation.

---

## Report Archiving

All builder reports MUST be:
- Stored in the task's execution record (in-memory or persistent log as configured)
- Referenced by TASK ID in the Multi-Step Loop's state
- Available to the Auditor for the next planning sprint

Reports are NOT committed to the repository unless the task type is docs-only and the report is part of the deliverable. Builder reports are operational records, not documentation.

---

## Example: Minimal Valid Report (COMPLETE)

```
TASK ID:          TASK-042
TASK TITLE:       Add session timeout warning modal
TASK TYPE:        ui-product-code
BUILDER:          Codex
BRANCH:           feature/session-warning
REPORT TIMESTAMP: 2026-04-30T14:22:00Z
REPORT STATUS:    COMPLETE

EXECUTIVE SUMMARY:
Created SessionWarning.tsx component and integrated it into the root layout.
The modal displays when session is within 5 minutes of expiry. All validation
gates passed. Screenshot evidence attached. Auto-committed on branch feature/session-warning.
Recommended next step is Design Director review.

FILES CREATED:
- components/SessionWarning.tsx — New modal component for session expiry warning

FILES MODIFIED:
- app/layout.tsx — Added SessionWarning component to root layout

COMMANDS RUN:
1. npm run lint
   Output: PASS (0 warnings)
2. npm run typecheck
   Output: PASS
3. git diff --check
   Output: PASS
4. git status --short
   Output: M components/SessionWarning.tsx M app/layout.tsx

VALIDATIONS:
- npm run lint:        PASS
- npm run typecheck:   PASS
- git diff --check:    PASS
- test suite:          SKIPPED — no tests for this component yet (low-risk UI only)
- git status --short:  M components/SessionWarning.tsx M app/layout.tsx

RISKS:
- None identified

BLOCKERS:
- None

SCREENSHOTS / EVIDENCE:
- Modal at 4 minutes remaining: /tmp/session-warning-4min.png
- Modal at 1 minute remaining: /tmp/session-warning-1min.png

SECRETS TOUCHED:           NO
APIS CALLED:               NO
SQL EXECUTED:              NO
SCHEDULER ENABLED:         NO
AUTO-CLAUDE ENABLED:       NO
ENV FILES READ OR WRITTEN: NO
SUPABASE MIGRATIONS APPLIED: NO

COMMIT HASH:       a3f1c8e2b9d4071f6e8a2c3b1d0e4f5a6b7c8d9e
COMMIT MESSAGE:    feat(ui): Add session timeout warning modal
CURRENT BRANCH:    feature/session-warning
GIT STATUS:        nothing to commit, working tree clean
GIT DIFF STAT:     2 files changed, 87 insertions(+), 1 deletion(-)

RECOMMENDED NEXT STEP:
Assign Design Director review of the new modal's visual treatment against MIRA design rubric.
```
