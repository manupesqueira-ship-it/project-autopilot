# AUTOPILOT HUMAN DECISION QUEUE STANDARD

Version: 1.0
Status: Canonical
Owner: Project Autopilot Control System

---

## Purpose

The Human Decision Queue (HDQ) is the formal mechanism by which the Project Autopilot system surfaces decisions that exceed its autonomous authority. It defines what requires human input, how to format decision requests, what evidence is required, what responses are valid, and how work is unblocked after a human decides.

The HDQ is not an error log — it is a structured collaboration interface between the Autopilot system and the human operator.

---

## What Requires Human Decision

The following situations ALWAYS require a human decision. Autopilot may not proceed autonomously.

### Category A — Security and Data (CRITICAL)

| Situation | Trigger |
|-----------|---------|
| Supabase migration to be applied | Any migration to production schema |
| RLS policy change | Any modification to Row-Level Security rules |
| Storage bucket policy change | Any modification to Supabase storage policies |
| Auth configuration change | Any change to auth providers or JWT settings |
| Forbidden file accessed | .env, .env.*, or credential file touched by builder |
| Potential secret exposed | Builder report mentions reading a credentials file |
| Privacy/data-retention change | Any change affecting user data storage or deletion |
| SQL executed on production | Any SQL beyond read-only queries |

### Category B — Deployment and Infrastructure (CRITICAL)

| Situation | Trigger |
|-----------|---------|
| Production deployment | Any action that deploys to production environment |
| VPS configuration change | SSH, systemd, nginx, cron changes |
| CI/CD pipeline change | Modification to GitHub Actions workflows |
| Environment variable change | Any change to production environment variables |

### Category C — Policy and Scope (HIGH)

| Situation | Trigger |
|-----------|---------|
| Policy Engine block | Autopilot policy was triggered |
| Repeated scope violation | Same task violated scope twice |
| Task type escalation | Builder determined task is higher risk than classified |
| Ambiguous task requirement | Builder cannot determine correct action |
| Cost limit reached | Estimated cost exceeds approved threshold |

### Category D — Quality and Product (MEDIUM)

| Situation | Trigger |
|-----------|---------|
| Design Director: 2 FAIL rounds | Design corrections failed twice |
| Backend API change (new route) | Any new API endpoint proposed |
| Vendor API integration | New third-party API integration |
| Feature flagging decision | Whether to enable a new feature |
| Abandon task decision | Builder recommends abandoning a task |

### Category E — Autopilot System Changes (HIGH)

| Situation | Trigger |
|-----------|---------|
| Scheduler behavior change | Any change to auto-scheduling logic |
| Auto-Claude trigger change | Any change to conditions that trigger Claude autonomously |
| Control Center behavior change | Changes that affect how Autopilot operates |
| Multi-Step Loop configuration | Changes to loop behavior or termination conditions |

---

## Priority Levels

| Priority | Label | SLA | Definition |
|----------|-------|-----|------------|
| P1 | CRITICAL | Immediate | Security, data exposure, production system at risk. Autopilot fully halted. |
| P2 | HIGH | Within 1 session | Policy violation, scope escalation, repeated failure. Task paused. |
| P3 | MEDIUM | Within next session | Quality or product decision needed. Task paused, others continue. |

---

## Human Decision Queue Item Format

Every item placed in the Human Decision Queue MUST follow this format exactly. Incomplete items are re-queued with a flag.

```
===============================================================
HUMAN DECISION QUEUE ITEM
===============================================================

ITEM ID:        {HDQ-YYYY-MM-DD-NNN}
PRIORITY:       {P1 / P2 / P3}
CATEGORY:       {A / B / C / D / E}
STATUS:         AWAITING DECISION
CREATED:        {ISO 8601 datetime}
TASK AFFECTED:  {TASK_ID — or MULTIPLE if several tasks blocked}
BRANCH:         {branch name}

---------------------------------------------------------------
SITUATION SUMMARY
---------------------------------------------------------------
{2-4 sentences describing exactly what happened and why human
input is needed. Be specific. No jargon abbreviations without
explanation.}

---------------------------------------------------------------
EVIDENCE
---------------------------------------------------------------
Builder report: {TASK_ID builder report reference or excerpt}
Validation output: {paste relevant output}
Files involved: {list of relevant files}
Git diff excerpt: {paste relevant diff lines, if applicable}
Additional context: {any other relevant information}

---------------------------------------------------------------
QUESTION FOR HUMAN
---------------------------------------------------------------
{One clear, specific question the human must answer.
Do not ask compound questions. One question per HDQ item.
If multiple decisions are needed, create multiple items.}

---------------------------------------------------------------
OPTIONS
---------------------------------------------------------------
A. {Option A description — specific and actionable}
B. {Option B description — specific and actionable}
C. {Option C description — specific and actionable}
[Add D, E if needed — do not exceed 5 options]

---------------------------------------------------------------
IMPACT IF NOT DECIDED
---------------------------------------------------------------
Tasks blocked: {list of TASK_IDs that cannot proceed}
Work at risk: {description of what is stalled}
Estimated delay: {rough estimate if decision takes 1 session vs. 3 sessions}

---------------------------------------------------------------
RECOMMENDED OPTION (Auditor's view)
---------------------------------------------------------------
{Auditor recommends: Option [letter] — one sentence reason.
If Auditor has no strong recommendation, state: "No recommendation — requires human judgment."}

===============================================================
```

---

## Evidence Requirements by Category

### Category A (Security/Data) — Required Evidence
- Full builder report
- Exact files touched (from git status)
- Relevant git diff lines
- Which policy or security rule was triggered
- Assessment of whether secrets may have been exposed

### Category B (Deployment/Infrastructure) — Required Evidence
- Full plan document (if Claude produced one)
- List of systems that would be affected
- Rollback plan (if one exists)
- Estimated risk of proceeding vs. not proceeding

### Category C (Policy/Scope) — Required Evidence
- Which policy was triggered
- The specific action that triggered it
- Builder report excerpt showing what was attempted
- Auditor's diagnosis of root cause

### Category D (Quality/Product) — Required Evidence
- Design Director report(s) if design-related
- Screenshot evidence before and after (if UI)
- Description of the product decision being made

### Category E (Autopilot System) — Required Evidence
- Current behavior description
- Proposed behavior description
- Which component would be affected
- Risk assessment

---

## Allowed Human Responses

The human must respond using one of the following structured formats. Freeform responses are acceptable but the Auditor will interpret them and confirm interpretation before acting.

### Standard Response Format

```
HDQ ITEM ID: {HDQ-YYYY-MM-DD-NNN}
DECISION: [OPTION LETTER or custom decision]
NOTES: {optional clarification}
AUTHORIZATION: APPROVED / REJECTED / DEFER
```

### Response Types

| Response | Meaning | Autopilot Action |
|----------|---------|-----------------|
| `APPROVED: [Option letter]` | Human authorizes the selected option | Autopilot unblocks and executes per option |
| `REJECTED: [reason]` | Human rejects all options | Autopilot abandons or redesigns the task |
| `DEFER: [reason]` | Human needs more time | Autopilot keeps task paused; re-queues at next session |
| `APPROVED: RESUME` | Special signal after forbidden-file incident | Autopilot may resume ONLY if explicitly stated |
| `APPROVED: EXCEPTION` | Human grants a one-time policy exception | Auditor logs exception; proceeds with extra monitoring |
| `ESCALATE: [person or team]` | Human routes to someone else | Autopilot keeps task paused; notes escalation |

---

## Escalation Flow

```
Blocker detected
    │
    ▼
Auditor classifies blocker
    │
    ├── Can resolve programmatically?
    │       └── Yes → Generate correction prompt (AUTOPILOT_CORRECTION_PROMPT_STANDARD.md)
    │
    └── No → Create HDQ item
                │
                ▼
            Assign priority (P1/P2/P3)
                │
                ▼
            Surface to human (Control Center, notification, or queue display)
                │
                ▼
            Human reviews evidence
                │
                ▼
            Human responds (APPROVED / REJECTED / DEFER / etc.)
                │
                ├── APPROVED → Unblock per instructions below
                ├── REJECTED → Abandon or redesign task
                └── DEFER   → Keep paused; re-surface next session
```

---

## How to Unblock Work After Human Decision

### After APPROVED

1. Auditor reads the approved option.
2. Auditor updates the task's allowed actions or scope as specified by the option.
3. Auditor generates a new sprint prompt (using AUTOPILOT_PROMPT_CATALOG.md) incorporating the human's decision.
4. Auditor logs: `HDQ-{ID} resolved: APPROVED [Option]. Task {TASK_ID} unblocked.`
5. Resume the task in the next Multi-Step Loop round.

### After APPROVED: RESUME (forbidden-file incident)

1. Auditor confirms with human: "Confirming resumption of task {TASK_ID} on branch {BRANCH}. Any credentials potentially exposed have been rotated. Proceeding."
2. Task is redesigned with explicit forbidden-file prohibition restated.
3. Extra scope restriction: Auditor adds a pre-commit scope check step to the new prompt.
4. Task resumes with tighter monitoring.

### After REJECTED

1. Auditor logs: `HDQ-{ID} resolved: REJECTED. Task {TASK_ID} abandoned.`
2. Auditor removes task from active queue.
3. Auditor adds a note to TASK_QUEUE.md: `TASK-{ID}: Abandoned after human rejection. Reason: {reason}.`
4. Auditor checks for dependent tasks and marks them blocked with reason: "dependency abandoned."
5. Auditor recommends redesigned task to human if applicable.

### After DEFER

1. Auditor logs: `HDQ-{ID} deferred. Will re-surface at next session.`
2. Task remains paused. No other automated action.
3. At next session start, Auditor re-surfaces all deferred HDQ items before planning new tasks.

### After ESCALATE

1. Auditor logs: `HDQ-{ID} escalated to {person/team}.`
2. Task remains paused.
3. Auditor does not attempt to resolve independently.
4. When the escalated party responds, treat their response as a human decision using the same unblock flow.

---

## Queue Management Rules

1. P1 items HALT all Autopilot execution on the affected branch until resolved.
2. P1 items MUST be displayed prominently in the Control Center — not buried in a log.
3. P2 items pause the affected task but do not halt other unrelated tasks.
4. P3 items pause the affected task; the queue continues for unrelated work.
5. An HDQ item is CLOSED only after the human responds and the Auditor confirms the decision has been acted upon.
6. Closed HDQ items are archived with: item ID, question, decision, timestamp, and outcome.
7. HDQ archive is NOT committed to the repository automatically — it is an operational log.

---

## Prohibited Autopilot Behaviors

The following are NEVER acceptable, regardless of circumstance:

- Proceeding past a P1 HDQ item without human response
- Self-approving a policy exception
- Interpreting silence as approval
- Re-queuing a forbidden-file incident as a lower-priority item
- Modifying the HDQ item after it has been surfaced to the human
- Closing an HDQ item without a recorded human response

---

## Example P1 HDQ Item

```
===============================================================
HUMAN DECISION QUEUE ITEM
===============================================================

ITEM ID:        HDQ-2026-04-30-001
PRIORITY:       P1
CATEGORY:       A
STATUS:         AWAITING DECISION
CREATED:        2026-04-30T15:44:00Z
TASK AFFECTED:  TASK-019
BRANCH:         feature/auth-refactor

---------------------------------------------------------------
SITUATION SUMMARY
---------------------------------------------------------------
Builder report for TASK-019 indicates that during the auth refactor,
the builder read the file `.env.local` to inspect the Supabase URL.
This file is categorically forbidden. No evidence of key extraction
or external transmission, but the read itself is a policy violation.
All execution on branch feature/auth-refactor has been halted.

---------------------------------------------------------------
EVIDENCE
---------------------------------------------------------------
Builder report: TASK-019 (REPORT STATUS: COMPLETE — but security flag raised)
Files involved: .env.local (read), lib/auth.ts (modified)
Git diff excerpt:
  // read from process.env.NEXT_PUBLIC_SUPABASE_URL
  (No hardcoded secrets found in diff)
Additional context: Builder used .env.local to verify the URL format
before writing a runtime check. The URL itself is not secret (NEXT_PUBLIC),
but the file access violated policy.

---------------------------------------------------------------
QUESTION FOR HUMAN
---------------------------------------------------------------
Should Autopilot resume task TASK-019 on branch feature/auth-refactor,
given that only a NEXT_PUBLIC (non-secret) value was read from .env.local?

---------------------------------------------------------------
OPTIONS
---------------------------------------------------------------
A. APPROVED: RESUME — The read was low-risk (NEXT_PUBLIC only). Resume with
   explicit prohibition on reading any .env file in future prompts.
B. REJECT — Abandon TASK-019. Redesign the task to avoid any .env file
   reference entirely, using only type definitions.
C. DEFER — Review the builder report in full before deciding.

---------------------------------------------------------------
IMPACT IF NOT DECIDED
---------------------------------------------------------------
Tasks blocked: TASK-019, TASK-020 (depends on TASK-019)
Work at risk: Auth refactor stalled; Design Director review cannot proceed.
Estimated delay: 1 session if decided now; 2-3 sessions if deferred.

---------------------------------------------------------------
RECOMMENDED OPTION (Auditor's view)
---------------------------------------------------------------
Auditor recommends: Option A — The accessed value is public-prefixed and
non-sensitive. Risk is low. Resume with explicit .env prohibition added.

===============================================================
```
