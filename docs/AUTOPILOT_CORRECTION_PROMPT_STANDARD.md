# AUTOPILOT CORRECTION PROMPT STANDARD

Version: 1.0
Status: Canonical
Owner: Project Autopilot Control System

---

## Purpose

When the OpenAI Auditor receives a builder report with REPORT STATUS: BLOCKED or REPORT STATUS: ABORTED, it MUST generate a correction prompt before any follow-up execution is attempted.

This document defines how correction prompts are constructed for each blocker type. Correction prompts are the Auditor's primary tool for unblocking work without requiring human intervention.

---

## Correction Prompt Decision Table

| Blocker Type | Resolution Path | Human Required |
|-------------|----------------|----------------|
| builder-blocked (technical) | Targeted fix prompt | No |
| validation-failed | Minimal repair prompt | No |
| policy-blocked | Human escalation | Yes |
| design-failed | Design Director re-review prompt | No |
| research-required | Research Director prompt | No |
| backend-security-failed | Human escalation + security review | Yes |
| scope-violation | Scope-correction prompt + restart | No (unless repeated) |
| forbidden-files-touched | Immediate human escalation | Yes |

---

## Blocker Type Definitions and Correction Prompts

---

### Blocker Type: builder-blocked

**Definition:** The builder was unable to complete implementation due to a technical obstacle — a missing dependency, a compilation error, an unexpected API shape, or a tool failure that is not a policy or security issue.

**Auditor Decision:** Generate a targeted fix prompt addressing the specific technical obstacle. Re-send to the same builder with corrected context.

**Correction Prompt Template:**

```
CORRECTION PROMPT — Builder Blocked (Technical)

ORIGINAL TASK ID: {TASK_ID}
ORIGINAL TASK TITLE: {TASK_TITLE}
BLOCKER REPORTED: {BLOCKER_DESCRIPTION}

CORRECTION MISSION:
Resolve the following technical blocker and complete the original task:

BLOCKER DETAIL:
{FULL_BLOCKER_TEXT_FROM_BUILDER_REPORT}

TECHNICAL CONTEXT ADDED BY AUDITOR:
{AUDITOR_DIAGNOSIS}

CORRECTED INSTRUCTIONS:
{SPECIFIC_CORRECTION}

All original SAFETY RULES, ALLOWED FILES, DISALLOWED FILES, and VALIDATION COMMANDS
from the original task prompt remain in effect. Do not expand scope beyond the original task.

If this correction does not resolve the blocker, report BLOCKED again with:
- What you attempted
- The exact error or obstacle
- Your recommendation (human-escalation / task-redesign / abandon)

FINAL REPORT FORMAT: Same as original task — AUTOPILOT_BUILDER_REPORT_STANDARD.md.
```

**Auditor Retry Limit:** Maximum 2 correction attempts. After 2 failed corrections, escalate to human decision queue.

---

### Blocker Type: validation-failed

**Definition:** The builder completed implementation but one or more validation gates failed: lint errors, TypeScript errors, test failures, or `git diff --check` whitespace errors.

**Auditor Decision:** Generate a minimal repair prompt targeting the specific validation failure. The builder must fix only what is needed to pass the gate — no new features, no scope expansion.

**Correction Prompt Template:**

```
CORRECTION PROMPT — Validation Failed

ORIGINAL TASK ID: {TASK_ID}
ORIGINAL TASK TITLE: {TASK_TITLE}
VALIDATION THAT FAILED: {VALIDATION_NAME}

VALIDATION OUTPUT:
{VALIDATION_FAILURE_OUTPUT}

CORRECTION MISSION:
Fix the specific validation failure below. Do NOT add new features or change logic
beyond what is required to pass the failing gate.

MINIMAL REPAIR INSTRUCTIONS:
1. Read the validation output above carefully.
2. Identify the minimum set of changes needed to pass the gate.
3. Make those changes only.
4. Re-run all validation commands.
5. If all gates now pass and only allowed files were touched, commit.
6. If a new failure appears, report BLOCKED — do not cascade-fix.

ALL ORIGINAL SAFETY RULES AND FILE SCOPE REMAIN IN EFFECT.

If repair is not possible without expanding scope, report BLOCKED with recommendation.

VALIDATION COMMANDS TO RE-RUN:
{VALIDATION_COMMANDS_LIST}

FINAL REPORT FORMAT: AUTOPILOT_BUILDER_REPORT_STANDARD.md.
```

**Auditor Retry Limit:** Maximum 3 validation correction attempts. After 3 failures, redesign the task or escalate.

---

### Blocker Type: policy-blocked

**Definition:** The Policy Engine rejected the task or an action within the task because it violated an Autopilot policy — file scope, risk level, cost limit, or capability boundary.

**Auditor Decision:** STOP. Do not retry programmatically. Escalate to human decision queue immediately. Document the policy that was triggered.

**Correction Prompt Template:**

```
CORRECTION PROMPT — Policy Blocked (Human Decision Required)

ORIGINAL TASK ID: {TASK_ID}
ORIGINAL TASK TITLE: {TASK_TITLE}
POLICY TRIGGERED: {POLICY_NAME_OR_RULE}

POLICY BLOCK DETAILS:
{POLICY_BLOCK_DESCRIPTION}

AUDITOR ASSESSMENT:
This block cannot be resolved programmatically. Human decision is required.

HUMAN DECISION QUEUE ITEM:
[See AUTOPILOT_HUMAN_DECISION_QUEUE_STANDARD.md for format]

Priority: {P1/P2/P3}
Question: {SPECIFIC_QUESTION_FOR_HUMAN}
Options:
  A. {Option A — e.g., Approve exception to policy for this task}
  B. {Option B — e.g., Redesign task to stay within policy}
  C. {Option C — e.g., Abandon task}

AUTOPILOT IS PAUSED ON THIS TASK until human decision is received.
Do not retry this task. Do not modify scope independently.
```

**Auto-retry:** NEVER for policy-blocked. Human decision is mandatory.

---

### Blocker Type: design-failed

**Definition:** The Design Director reviewed the builder's output and returned a verdict of FAIL or CONDITIONAL PASS with required P1 corrections.

**Auditor Decision:** Generate a targeted design-correction prompt using the Design Director's specific correction instructions. Send to Codex for implementation, then re-request Design Director review.

**Correction Prompt Template:**

```
CORRECTION PROMPT — Design Failed

ORIGINAL TASK ID: {TASK_ID}
ORIGINAL TASK TITLE: {TASK_TITLE}
DESIGN VERDICT: {FAIL / CONDITIONAL PASS}

DESIGN DIRECTOR FINDINGS:
{DESIGN_DIRECTOR_REPORT_FINDINGS_SECTION}

P1 CORRECTIONS REQUIRED:
{P1_CORRECTION_LIST}

CORRECTION MISSION:
Implement only the P1 design corrections listed above. Do not add new features.
Do not change data logic or API behavior.

IMPLEMENTATION INSTRUCTIONS:
{SPECIFIC_IMPLEMENTATION_INSTRUCTIONS_FROM_DESIGN_DIRECTOR}

EVIDENCE REQUIRED:
- Before/after screenshots for each corrected element
- Screenshots must show the full component in context

ALL ORIGINAL SAFETY RULES AND FILE SCOPE REMAIN IN EFFECT.
Scope is additionally restricted to: {SPECIFIC_FILES_NEEDING_DESIGN_FIX}

VALIDATION COMMANDS:
- npm run lint
- git diff --check
- git status --short

AUTO-COMMIT: Yes — after lint passes and screenshots attached.

FINAL REPORT FORMAT: AUTOPILOT_BUILDER_REPORT_STANDARD.md with screenshots section required.
```

**After correction:** Auditor automatically schedules a second Design Director review.
**Retry limit:** Maximum 2 design correction rounds. After 2 failures, escalate to human with both Design Director reports.

---

### Blocker Type: research-required

**Definition:** The builder encountered an implementation decision requiring domain knowledge or technical research that was not provided in the original task context.

**Auditor Decision:** Pause the implementation task. Generate a Research Director request. Resume implementation after research report is complete.

**Correction Prompt Template:**

```
CORRECTION PROMPT — Research Required

ORIGINAL TASK ID: {TASK_ID}
ORIGINAL TASK TITLE: {TASK_TITLE}
RESEARCH NEEDED: {RESEARCH_QUESTION_FROM_BUILDER}

AUDITOR ACTION:
Pausing implementation task {TASK_ID}. Creating research subtask.

RESEARCH SUBTASK (using Template 07 — Research Director Request):
MISSION: Research — {RESEARCH_QUESTION}
SCOPE: {RESEARCH_SCOPE}
OUTPUT FILE: project_control/RESEARCH_{TASK_ID}_{SLUG}.md
WEB SEARCH ALLOWED: {Yes/No}

After research completes, the implementation task will be resumed with:
- Research findings as additional context
- Any constraints or decisions from research incorporated into allowed actions

IMPLEMENTATION TASK STATUS: PAUSED — awaiting research output
RESEARCH SUBTASK ID: {RESEARCH_SUBTASK_ID}
```

**No human approval needed** unless research reveals a policy or security concern.

---

### Blocker Type: backend-security-failed

**Definition:** The builder attempted or proposed a change to backend API, authentication, authorization, or data-handling logic, and the Auditor determined it poses a security risk.

**Auditor Decision:** STOP all automated execution. Escalate to human. Generate a security review document.

**Correction Prompt Template:**

```
CORRECTION PROMPT — Backend/Security Failed (Human Decision Required)

ORIGINAL TASK ID: {TASK_ID}
ORIGINAL TASK TITLE: {TASK_TITLE}
SECURITY CONCERN: {SECURITY_CONCERN_DESCRIPTION}

AUDITOR SECURITY ASSESSMENT:
{AUDITOR_ASSESSMENT}

Risk level: {CRITICAL / HIGH}
Affected area: {AFFECTED_SYSTEM_OR_COMPONENT}

HUMAN DECISION REQUIRED:
This task has been halted due to a security concern. No further automated action
will be taken until a human reviews and approves a resolution path.

HUMAN DECISION QUEUE ITEM:
Priority: P1
Security concern: {SECURITY_CONCERN_DESCRIPTION}
Evidence: {BUILDER_REPORT_REFERENCE}
Options:
  A. Approve a redesigned task with explicit security constraints (specify)
  B. Assign to Claude for security planning review before implementation
  C. Abandon task and redesign from scratch
  D. Escalate to external security review

AUTOPILOT IS PAUSED ON THIS TASK AND ALL DEPENDENT TASKS.
```

**Auto-retry:** NEVER for backend-security-failed. Human decision is mandatory.

---

### Blocker Type: scope-violation

**Definition:** The builder touched, read, or proposed changes to files outside the defined ALLOWED FILES list for the task.

**Auditor Decision:** Revert the scope violation if possible. Generate a corrected prompt with explicit re-statement of scope boundaries. If the builder repeatedly violates scope, escalate to human.

**Correction Prompt Template:**

```
CORRECTION PROMPT — Scope Violation

ORIGINAL TASK ID: {TASK_ID}
ORIGINAL TASK TITLE: {TASK_TITLE}
SCOPE VIOLATION: Files outside ALLOWED FILES were touched

FILES THAT SHOULD NOT HAVE BEEN TOUCHED:
{OUT_OF_SCOPE_FILES}

AUDITOR ACTION:
Reverting out-of-scope changes (if possible). Re-issuing task with explicit scope warning.

CORRECTED TASK:
[Re-issue original task prompt verbatim, with the following added at the top:]

CRITICAL SCOPE REMINDER:
A previous execution attempt violated scope by touching:
{OUT_OF_SCOPE_FILES}

These files are STRICTLY OFF-LIMITS. Do NOT read, write, or reference them.
If completing this task requires touching these files, STOP and report BLOCKED.
Do not make assumptions about scope expansion.

[Original task prompt continues...]

FINAL REPORT FORMAT: AUTOPILOT_BUILDER_REPORT_STANDARD.md.
SCOPE VERIFICATION REQUIRED: Run git status --short before committing. If any
file outside ALLOWED FILES appears in the diff, do NOT commit. Report BLOCKED.
```

**Escalation:** If scope violation occurs twice on the same task, immediately escalate to human decision queue with both builder reports attached.

---

### Blocker Type: forbidden-files-touched

**Definition:** The builder read, wrote, or modified a file that is categorically forbidden: `.env`, `.env.*`, production secrets, Supabase credentials, or any file whose modification was explicitly disallowed by policy.

**Auditor Decision:** IMMEDIATE ESCALATION. This is a CRITICAL policy violation. Stop all Autopilot execution on this branch. Alert human immediately.

**Correction Prompt Template:**

```
CRITICAL ALERT — Forbidden Files Touched

ORIGINAL TASK ID: {TASK_ID}
ORIGINAL TASK TITLE: {TASK_TITLE}
VIOLATION TYPE: FORBIDDEN FILE ACCESS

FORBIDDEN FILES TOUCHED:
{FORBIDDEN_FILES_LIST}

CRITICAL ACTION REQUIRED:
1. ALL AUTOPILOT EXECUTION ON BRANCH {BRANCH_NAME} IS HALTED IMMEDIATELY.
2. Human must review what was accessed and whether any secrets were exposed.
3. If .env or credential files were modified, human must rotate any exposed secrets.
4. Do NOT retry this task under any circumstances without explicit human authorization.

HUMAN DECISION QUEUE ITEM:
Priority: P1 — CRITICAL
Alert: Forbidden file accessed during automated execution
Files: {FORBIDDEN_FILES_LIST}
Builder report: {BUILDER_REPORT_REFERENCE}
Immediate actions for human:
  1. Review git diff for the branch to determine what was read/written
  2. Determine if any secrets, keys, or credentials were exposed
  3. Rotate any potentially exposed credentials
  4. Decide whether to continue this task (redesigned) or abandon

AUTOPILOT WILL NOT RESUME THIS TASK without explicit human "APPROVED: RESUME" response.
```

**No retry allowed.** Human must explicitly authorize resumption.

---

## Correction Prompt Construction Rules

1. Every correction prompt MUST include the original TASK ID for traceability.
2. Every correction prompt MUST restate all original SAFETY RULES unless explicitly modified.
3. Correction prompts MUST NOT silently expand scope. If scope expansion is needed, it requires a new task.
4. The Auditor MUST log every correction prompt issued — including the blocker type, the prompt sent, and the outcome.
5. Correction prompts for security, policy, and forbidden-file blockers MUST produce a human decision queue item — the human decision queue item cannot be omitted.
6. "Retry without a correction prompt" is never acceptable. Every retry MUST use this standard.

---

## Correction Attempt Limits

| Blocker Type | Max Auto-Retries | After Limit |
|-------------|-----------------|-------------|
| builder-blocked | 2 | Human escalation |
| validation-failed | 3 | Task redesign or human |
| policy-blocked | 0 | Human (immediate) |
| design-failed | 2 | Human + both reports |
| research-required | N/A | Resume after research |
| backend-security-failed | 0 | Human (immediate) |
| scope-violation | 1 | Human escalation |
| forbidden-files-touched | 0 | Human (immediate, CRITICAL) |
