# AUTOPILOT FINAL OPERATOR RUNBOOK
**Version:** v1.0  
**Project:** Project Autopilot  
**Audience:** The operator running final validation before returning to MIRA product development.  
**Purpose:** Practical guide for executing the final validation, interpreting results, and making the GO / NO-GO decision.

---

## SECTION 1 — HOW TO RUN FINAL VALIDATION

### Prerequisites

Before starting:
- [ ] You are on the correct branch (confirm with `git branch --show-current`)
- [ ] The working directory is clean (confirm with `git status --short`)
- [ ] No Autopilot scheduler is running (confirm with Autopilot `--status`)
- [ ] You have access to the validation command pack: `project_control/AUTOPILOT_FINAL_VALIDATION_COMMAND_PACK.md`
- [ ] You have an open copy of the evidence checklist to fill in: `project_control/AUTOPILOT_FINAL_EVIDENCE_CHECKLIST.md`
- [ ] You have the failure playbook open in case you need it: `project_control/AUTOPILOT_FINAL_FAILURE_RESPONSE_PLAYBOOK.md`

### Execution Order

Run the commands **in the numbered order** from the Command Pack. Do not skip steps or run them out of order — some steps depend on the environment state established by prior steps.

**Suggested session structure:**

```
Phase A — Environment checks:    Commands 1–3
Phase B — Policy/config:          Commands 4–6
Phase C — Loop/SDK dry-runs:     Commands 7–9
Phase D — Sandbox validation:    Commands 10–14
Phase E — Worktree/handoff:      Commands 15–16
Phase F — Health/readiness:      Commands 17–20
Phase G — Control/Flow QA:       Commands 21–22
Phase H — Frontend build:        Commands 23–25
Phase I — Git hygiene:           Commands 26–28
```

### How to record results

After each command runs:
1. Note PASS or FAIL.
2. Copy the last 10–20 lines of output to the Evidence Checklist (or note the output file location).
3. If FAIL: consult the Failure Playbook before proceeding.

---

## SECTION 2 — HOW TO READ THE RESULTS

### Green result (PASS)

A command passes if:
- It exits with code 0
- The output does not contain `Error`, `FAILED`, `SyntaxError`, or `CRITICAL` in a context that indicates a failure
- No unexpected side effects occurred (no real API calls, no real writes, no scheduler started)

### Yellow result (WARNING)

Some commands produce warnings that are acceptable. A warning is acceptable if:
- It is listed as "Acceptable warnings" in the Command Pack for that step
- It is informational and does not indicate a functional failure
- It does not change the behavior of the system

Record yellow results but do not treat them as FAIL unless the Command Pack specifies otherwise.

### Red result (FAIL)

A command fails if:
- It exits with a non-zero exit code
- The output explicitly reports an error, test failure, or check failure
- An unexpected side effect occurs (real API call, real write, scheduler starts)

A single unresolved FAIL is a NO-GO. Do not paper over it.

### What "no output" means

For `git diff --check`: no output is a PASS.  
For `git status --short`: output of only allowed doc files is a PASS. Unexpected files = FAIL.  
For status commands: "idle" or "disabled" is the expected output.

---

## SECTION 3 — HOW TO DECIDE GO / NO-GO

### GO criteria (all must be true)

- [ ] All 28 commands in the Command Pack returned PASS (or N/A for optional items)
- [ ] All SECTION 10 safety gates in the Evidence Checklist are confirmed NO
- [ ] No unresolved FAIL items in the Evidence Checklist
- [ ] `git status --short` shows only allowed doc files
- [ ] `npm run build` succeeded
- [ ] Sandbox preflight, simulation, and runner dry-run all passed
- [ ] Autopilot health report: all subsystems OK
- [ ] MIRA readiness: GO

### NO-GO criteria (any one is sufficient)

- Any command exited non-zero and the error was not resolved
- Any scheduler or auto-Claude was enabled during validation
- Any real Claude API call was made during a dry-run step
- Any `.env*` or secrets file was modified or staged
- `npm run build` failed
- Any BLOCKING item in MIRA readiness report

### Edge case: Advisory items

Advisory items (non-blocking warnings, informational notes) do not prevent a GO decision. They should be:
1. Recorded in the Evidence Checklist
2. Acknowledged in the decision notes
3. Scheduled for resolution in MIRA development if relevant

---

## SECTION 4 — WHAT TO SEND BACK TO CHATGPT

When you have completed validation and have a GO or NO-GO decision, send the following to ChatGPT:

**GO message template:**
```
Project Autopilot Final Validation — GO

Run date: [DATE]
Branch: [BRANCH]
Commit: [HASH]

All 28 validation commands: PASS
Build: PASS
Safety gates: ALL CONFIRMED NO
MIRA readiness: GO

Advisory items: [list or "none"]

Ready to return to MIRA product development.
```

**NO-GO message template:**
```
Project Autopilot Final Validation — NO-GO

Run date: [DATE]
Branch: [BRANCH]
Commit: [HASH]

Failures:
- [Command name]: [brief description of failure]
- [Command name]: [brief description of failure]

Blockers:
- [Description]

Next steps needed before GO:
- [Action 1]
- [Action 2]
```

Include the Evidence Checklist summary (Section totals: how many PASS, how many FAIL) as additional context.

---

## SECTION 5 — WHAT TO SEND TO CLAUDE/CODEX

When delegating a specific failure fix to Claude Code or Codex, provide:

1. **The failing command** and its exact output (last 20–30 lines)
2. **The file it failed on** (file path and line number if available)
3. **The constraint**: "Fix only this specific error. Do not refactor. Do not touch env files, scheduler config, or deployment config."
4. **The verification step**: "After your fix, re-run `[command]` and confirm it exits 0."

Example:
```
Claude, fix the following lint error only:

File: src/components/TaskCard.tsx:42
Error: 'result' is assigned a value but never used. (no-unused-vars)

Fix: remove the unused variable or use it. Do not change anything else in the file.
After fix, re-run: npm run lint
Expected result: exit 0, no errors.
```

Do not send Claude:
- The full Evidence Checklist (too much context)
- Open-ended "fix all issues" requests
- Any task that involves env files, secrets, or deployment config

---

## SECTION 6 — WHAT NOT TO DO MANUALLY

These are actions that operators sometimes attempt during validation that cause more problems than they solve. Avoid all of them.

| Do NOT | Reason |
|--------|--------|
| Run `git add -A` or `git add .` | Will stage logs, env files, generated artifacts |
| Manually edit `.env*` files to fix a test | Env changes belong in secrets management, not manual edits |
| Comment out failing tests to get a green run | A suppressed test is a hidden bug |
| Add `@ts-ignore` to silence typecheck failures | Hides real type bugs |
| Run Autopilot in live mode to "verify it works" | This is not part of validation and could trigger real execution |
| Push to remote without completing all 28 checks | Incomplete validation = incomplete confidence |
| Skip the build step because "nothing changed" | Build failures can be caused by indirect dependency changes |
| Modify scheduler config "temporarily" | There is no temporary — always restore config explicitly |
| Make a worktree manually to test something | Use the dry-run commands; manual worktrees create orphaned state |
| Delete generated logs without inspecting them | Logs may contain evidence of accidental execution |

---

## SECTION 7 — HOW TO RESUME MIRA PRODUCT DEVELOPMENT

Once you have a confirmed GO:

1. **Close the Autopilot validation context.** You do not need to keep these docs open during MIRA development.

2. **Record the commit hash** of the final validation state in your notes. This is your known-good Autopilot baseline.

3. **Switch to the MIRA development branch.** Confirm with `git branch --show-current` that you are on the right branch.

4. **Confirm Autopilot is idle.** A quick `--status` check before starting MIRA work confirms nothing is running in the background.

5. **Do not re-run Autopilot validation during MIRA development** unless you make changes to Autopilot itself. The validation you just ran is sufficient.

6. **Log any Autopilot bugs discovered during MIRA work** as issues for the next Autopilot iteration. Do not context-switch back into Autopilot to fix minor issues mid-MIRA sprint.

7. **If Autopilot needs to be re-run for a MIRA task**: use the Command Pack to confirm a healthy state first, then execute the specific Autopilot feature needed. Do not run ad-hoc.

---

## SECTION 8 — HOW TO AVOID OVERBUILDING AUTOPILOT

Project Autopilot exists to accelerate MIRA development — not to become a product itself. Watch for these warning signs that Autopilot is consuming more effort than it saves:

### Warning signs of scope creep

- You are adding Autopilot features that "would be nice" but are not needed for the current MIRA task
- Autopilot validation is taking longer than the MIRA work it was meant to accelerate
- You are refactoring Autopilot infrastructure during a MIRA sprint
- The number of Autopilot commands and modules is growing faster than the MIRA features they support
- You have started building a UI or dashboard for Autopilot

### The right question to ask

Before adding anything to Autopilot, ask: **"Does MIRA development fail without this?"**

If the answer is no, defer it. Add it to a backlog, not the current sprint.

### Minimum viable Autopilot

Autopilot's job is to:
1. Run repeatable tasks without manual intervention
2. Validate its own health before running
3. Report results clearly
4. Stay out of the way when not needed

Everything beyond this is optional. Resist the urge to make Autopilot more capable than MIRA currently needs it to be.

### When to stop Autopilot development

Stop adding to Autopilot when:
- All 28 validation commands pass consistently
- MIRA readiness is GO
- You can run and recover from a full Autopilot cycle without consulting documentation

At that point, freeze Autopilot at v1 and return to MIRA. Future Autopilot improvements belong in a v2 sprint, scheduled only when MIRA has a specific need for them.

---

## APPENDIX — QUICK REFERENCE

### Critical "stop and check" signals during any validation run

- Scheduler reports `active` or `running` — STOP
- Auto-Claude reports `enabled` — STOP
- `git status` shows `.env*` files — STOP
- Any command triggers a real API call — STOP
- Build exits non-zero — STOP

### Key files in this pack

| File | Purpose |
|------|---------|
| `AUTOPILOT_FINAL_VALIDATION_COMMAND_PACK.md` | All 28 commands with pass/fail criteria |
| `AUTOPILOT_FINAL_EVIDENCE_CHECKLIST.md` | Fill-in record of every validation result |
| `AUTOPILOT_FINAL_FAILURE_RESPONSE_PLAYBOOK.md` | Structured responses for each failure type |
| `AUTOPILOT_FINAL_OPERATOR_RUNBOOK.md` | This file — how to run, read, decide, and resume |

---

*End of AUTOPILOT FINAL OPERATOR RUNBOOK v1.0*
