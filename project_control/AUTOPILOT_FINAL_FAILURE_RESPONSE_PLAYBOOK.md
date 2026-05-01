# AUTOPILOT FINAL FAILURE RESPONSE PLAYBOOK
**Version:** v1.0  
**Project:** Project Autopilot  
**Purpose:** Structured responses to each failure mode that may arise during final validation.  
**Rule:** Do not improvise. When a failure occurs, find the matching entry here, follow the safe response, and do not take any action listed under "What NOT to do."

---

## HOW TO USE THIS PLAYBOOK

1. Identify the failure type from the section headings below.
2. Note the **Severity** — this tells you how urgently you must stop.
3. Check the **Immediate Stop Condition** — if matched, halt all further commands now.
4. Follow the **Safe Response** steps in order.
5. Record the failure in the Evidence Checklist before resuming.

---

## SEVERITY SCALE

| Level | Meaning |
|-------|---------|
| CRITICAL | Stop all work. Do not commit. Do not retry without diagnosis. |
| HIGH | Stop current phase. Fix before proceeding to downstream commands. |
| MEDIUM | Investigate. Do not dismiss. May proceed with documented justification. |
| LOW | Advisory. Note in checklist. Safe to proceed. |

---

## FAILURE 1 — LINT FAILURE

**Severity:** HIGH  
**Trigger:** `npm run lint` exits non-zero. One or more lint errors reported.

**Immediate stop condition:** Any lint error (not warning) present.

**Safe response:**
1. Read the lint output carefully. Identify the file and rule violated.
2. Fix only the lint error — do not refactor surrounding code.
3. Re-run `npm run lint` to confirm clean.
4. Re-run `git diff --check` to confirm no whitespace issues introduced.
5. Record fix in Evidence Checklist.

**What NOT to do:**
- Do not add `// eslint-disable` comments to suppress errors without understanding them.
- Do not fix "while you're there" — fix only what lint reported.
- Do not commit with a failing lint run.

---

## FAILURE 2 — TYPECHECK FAILURE

**Severity:** HIGH  
**Trigger:** `npm run typecheck` exits non-zero. TypeScript type errors reported.

**Immediate stop condition:** Any type error (not informational warning) present.

**Safe response:**
1. Read the full type error output. Identify the file, line, and type mismatch.
2. Fix the specific type error. Do not use `@ts-ignore` unless the cause is a known third-party issue with no fix available, and it must be documented in the code.
3. Re-run `npm run typecheck` to confirm clean.
4. Record fix in Evidence Checklist.

**What NOT to do:**
- Do not cast to `any` to silence errors.
- Do not add `@ts-ignore` without a comment explaining why.
- Do not skip typecheck if it fails. A failing typecheck is a hard NO-GO.

---

## FAILURE 3 — BUILD FAILURE

**Severity:** CRITICAL  
**Trigger:** `npm run build` exits non-zero. Build artifacts not produced.

**Immediate stop condition:** Build fails for any reason.

**Safe response:**
1. Read the build output from top to bottom. Identify the first error — this is almost always the root cause.
2. Check if the failure is from a missing module, a type error, or a configuration issue.
3. Fix the root cause.
4. Re-run `npm run typecheck` first to confirm no type errors before rebuilding.
5. Re-run `npm run build`.
6. Record in Evidence Checklist.

**What NOT to do:**
- Do not proceed to any other validation step while the build is broken.
- Do not skip the build ("it's docs-only") — if a build failure exists, it must be resolved before GO.
- Do not modify build configuration to work around the failure.

---

## FAILURE 4 — POLICY FIXTURE FAILURE

**Severity:** CRITICAL  
**Trigger:** One or more pytest tests in `test_policy_fixtures.py` FAIL or ERROR.

**Immediate stop condition:** Any FAILED or ERROR result from the policy fixture test suite.

**Safe response:**
1. Read the pytest output. Identify which fixture and which assertion failed.
2. Check the policy logic for recent changes that may have shifted evaluation results.
3. Do not modify the fixture to match the new behavior without understanding why the policy changed.
4. If the policy logic is correct and the fixture is outdated, update the fixture deliberately and document why.
5. Re-run tests to confirm all pass.
6. Record in Evidence Checklist.

**What NOT to do:**
- Do not skip failing tests with `pytest.mark.skip`.
- Do not modify policy logic to force tests to pass without understanding the behavioral change.
- Do not proceed to sandbox steps with failing policy fixtures.

---

## FAILURE 5 — SANDBOX PREFLIGHT FAILURE

**Severity:** CRITICAL  
**Trigger:** `claude_sandbox.py --preflight` reports one or more checks failed.

**Immediate stop condition:** Any preflight check fails.

**Safe response:**
1. Read the preflight output carefully. Identify which specific check failed.
2. Common causes: missing dependency, misconfigured path, missing env var.
3. Fix the specific missing item only. Do not touch other config.
4. Re-run `--preflight` to confirm all checks pass.
5. Do not proceed to `--simulate` until preflight is fully clean.

**What NOT to do:**
- Do not bypass or disable preflight checks.
- Do not run sandbox simulation with a failed preflight — the simulation result is meaningless.
- Do not modify sandbox isolation config to make preflight pass artificially.

---

## FAILURE 6 — WORKTREE CLEANUP FAILURE

**Severity:** HIGH  
**Trigger:** Unexpected worktrees found in `git worktree list`, or a dry-run accidentally created a real worktree.

**Immediate stop condition:** A real (non-dry-run) worktree was created during validation.

**Safe response:**
1. Run `git worktree list` to identify all worktrees.
2. For each unexpected worktree, verify its origin — is it from this validation run or from prior work?
3. If from this run (should not have been created): run `git worktree remove --force <path>` after confirming no important changes exist in it.
4. Run `git worktree prune` to clean up stale references.
5. Re-run `git worktree list` to confirm clean state.
6. Record in Evidence Checklist.

**What NOT to do:**
- Do not delete a worktree without first inspecting its contents.
- Do not run `git worktree remove` if you are unsure whether it contains uncommitted work.

---

## FAILURE 7 — CONTROL CENTER GENERATION FAILURE

**Severity:** MEDIUM  
**Trigger:** `control_center.py --generate` fails to produce a report, errors on startup, or produces an empty/malformed output.

**Immediate stop condition:** Report not generated at all.

**Safe response:**
1. Check the error output. Common causes: missing data source, import error, output directory not writable.
2. Fix the specific cause.
3. Re-run generation.
4. If Control Center depends on a prior run (e.g., health check output), ensure that prerequisite ran first.
5. Record result in Evidence Checklist.

**What NOT to do:**
- Do not manually create a fake Control Center report.
- Do not mark this as PASS if the report was not actually generated.

---

## FAILURE 8 — FLOW QA FAILURE

**Severity:** HIGH  
**Trigger:** `flow_qa.py --mock-e2e` fails to complete, or any Flow QA stage reports a failure.

**Immediate stop condition:** Real external API calls made during Flow QA. Any stage FAIL result.

**Safe response:**
1. Read the Flow QA output. Identify which stage failed and why.
2. If real external calls were detected: stop immediately and verify no data was written.
3. Fix the mock configuration to prevent real calls.
4. Fix the stage logic if the failure is a genuine functional issue.
5. Re-run `--mock-e2e` to confirm clean.

**What NOT to do:**
- Do not skip failing Flow QA stages.
- Do not run Flow QA against real data to work around a mock configuration issue.

---

## FAILURE 9 — BACKEND AUDIT WARNING

**Severity:** MEDIUM  
**Trigger:** `backend_audit.py --run` reports warnings (not failures).

**Immediate stop condition:** If a warning indicates a non-empty unexpected queue or a broken Supabase connection.

**Safe response:**
1. Read each warning carefully. Distinguish advisory items from operational warnings.
2. Investigate any unexpected queue contents — this may indicate a leftover task from prior testing.
3. If Supabase connectivity is warning: test the connection directly before proceeding.
4. Document each warning in the Evidence Checklist with a brief explanation.
5. Proceed only if all warnings are advisory and non-blocking.

**What NOT to do:**
- Do not ignore non-empty queue warnings.
- Do not proceed to MIRA development if Supabase connectivity is degraded.

---

## FAILURE 10 — MIRA READINESS WARNING

**Severity:** HIGH (BLOCKING items) / LOW (advisory items)  
**Trigger:** `mira_readiness.py --check` reports one or more BLOCKING items or advisory warnings.

**Immediate stop condition:** Any item marked BLOCKING.

**Safe response:**
1. For BLOCKING items: do not resume MIRA development. Address each blocker explicitly.
2. For advisory items: document in Evidence Checklist. Confirm they are intentionally deferred.
3. Re-run `mira_readiness.py --check` after resolving blockers to confirm GO state.

**What NOT to do:**
- Do not dismiss BLOCKING items as low priority to ship faster.
- Do not modify the readiness checker to suppress warnings.

---

## FAILURE 11 — DIRTY REPO

**Severity:** CRITICAL  
**Trigger:** `git status --short` shows unexpected modified, staged, or untracked files beyond allowed docs.

**Immediate stop condition:** Any file outside `project_control/*.md` is modified or staged.

**Safe response:**
1. Read `git status --short` output carefully. List every unexpected file.
2. For each unexpected file: determine if it was modified intentionally (it should not have been).
3. Do not stage or commit until all unexpected files are explained.
4. If files were modified unintentionally: use `git checkout -- <file>` to restore them after confirming no important work is lost.
5. Re-run `git status --short` to confirm only allowed files remain.

**What NOT to do:**
- Do not run `git add -A` or `git add .` — this is how secrets and logs get committed.
- Do not commit with unexpected files staged.
- Do not use `git checkout -- .` without understanding what changes will be discarded.

---

## FAILURE 12 — UNEXPECTED GENERATED LOGS STAGED

**Severity:** CRITICAL  
**Trigger:** `git status --short` shows `*.log`, `*.jsonl`, or other generated output files staged.

**Immediate stop condition:** Any generated log file is staged for commit.

**Safe response:**
1. Unstage immediately: `git reset HEAD <file>`.
2. Verify the log does not contain sensitive data (API keys, user data, conversation content).
3. Add the file pattern to `.gitignore` if not already present.
4. Re-run `git status --short` to confirm it is unstaged.
5. Record incident in Evidence Checklist.

**What NOT to do:**
- Do not commit generated logs — they can contain sensitive information and pollute git history.
- Do not delete the log file before verifying it does not contain useful debugging information.

---

## FAILURE 13 — ENV/SECRETS TOUCHED

**Severity:** CRITICAL  
**Trigger:** `git status --short` shows any `.env*`, `*.secret`, `secrets.*`, or credential file modified.

**Immediate stop condition:** Immediate. Stop all activity.

**Safe response:**
1. Do not stage. Do not commit.
2. Run `git diff <file>` to understand what changed — do not paste output publicly.
3. Restore the original file: `git checkout -- <file>`.
4. Verify the restored file matches the expected state.
5. Identify how the file was modified (which command touched it) and eliminate that path.
6. Record incident in Evidence Checklist.

**What NOT to do:**
- Under no circumstances commit an env or secrets file.
- Do not push to remote if env/secrets were modified — force-push is not a safe resolution.
- Do not share the diff output in public channels.

---

## FAILURE 14 — SCHEDULER ACCIDENTALLY ENABLED

**Severity:** CRITICAL  
**Trigger:** Autopilot `--status` or runner `--status` reports scheduler is active/running.

**Immediate stop condition:** Immediate.

**Safe response:**
1. Stop any running Autopilot process immediately (kill process if necessary).
2. Identify which config or flag caused the scheduler to start.
3. Set `ENABLE_SCHEDULER=false` in the appropriate config.
4. Re-run `--status` to confirm scheduler is reported as disabled.
5. Verify no tasks were queued or executed during the accidental run.
6. Record in Evidence Checklist.

**What NOT to do:**
- Do not leave the scheduler running "just for a moment."
- Do not proceed with any validation steps while the scheduler is active.
- Do not restart Autopilot after this failure without confirming the scheduler flag is off.

---

## FAILURE 15 — AUTO-CLAUDE ACCIDENTALLY ENABLED

**Severity:** CRITICAL  
**Trigger:** Any log output, status check, or dry-run response indicates real Claude API calls are being made or auto-invoke is enabled.

**Immediate stop condition:** Immediate.

**Safe response:**
1. Stop the process immediately.
2. Check recent logs for any Claude API calls that may have completed.
3. Identify what config or flag enabled auto-Claude invocation.
4. Set `ENABLE_AUTO_CLAUDE=false` (or equivalent) in config.
5. Re-run the relevant status check to confirm auto-Claude is disabled.
6. If any real Claude calls were made: review what was sent and received. Do not discard this information.
7. Record in Evidence Checklist.

**What NOT to do:**
- Do not continue validation with auto-Claude enabled.
- Do not assume "it only ran once" is acceptable — investigate fully.
- Do not modify the Claude invocation code to suppress the behavior rather than fixing the root cause.

---

## GENERAL PRINCIPLES

1. **Read the error before acting.** Most failures have a clear error message. Read it in full before taking any action.
2. **Fix the root cause, not the symptom.** Do not suppress warnings, disable checks, or force-pass failing tests.
3. **One fix at a time.** Make the minimal change to fix the reported failure, then re-validate.
4. **Record everything.** Every failure and its resolution goes in the Evidence Checklist.
5. **When in doubt, stop.** It is better to stop and ask than to proceed and create a harder problem.

---

*End of AUTOPILOT FINAL FAILURE RESPONSE PLAYBOOK v1.0*
