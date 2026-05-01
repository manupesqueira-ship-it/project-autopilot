# AUTOPILOT FINAL VALIDATION COMMAND PACK
**Version:** v1.0  
**Project:** Project Autopilot  
**Purpose:** Repeatable pre-release validation sequence before returning to MIRA product development.  
**Scope:** Read-only validation. No source code modifications. No env/secrets changes. No scheduler activation.

---

## HOW TO USE THIS PACK

Run commands in the numbered order below.  
Each command is self-contained. If a command fails, consult the Failure Response Playbook before continuing.  
Record all pass/fail results in the Evidence Checklist (`AUTOPILOT_FINAL_EVIDENCE_CHECKLIST.md`).

---

## COMMAND SEQUENCE

---

### 1. COMPILE ALL — Python syntax check

```bash
python -B -m compileall project_autopilot agent
```

**Purpose:** Verify all Python files in `project_autopilot/` and `agent/` have no syntax errors.  
**Expected pass:** `Listing ...` lines followed by no `SyntaxError` output. Exit code 0.  
**Acceptable warnings:** `__pycache__` already exists notices.  
**Unacceptable failure:** Any `SyntaxError`, `IndentationError`, or non-zero exit code.  
**Next action if fail:** Identify the file and line from the error. Do not proceed with remaining commands. Fix syntax error in source, re-run.

---

### 2. DOCTOR — Autopilot environment doctor

```bash
python project_autopilot/doctor.py
```

*(If the script name differs, substitute the correct module path)*

**Purpose:** Verify all required environment variables, dependencies, and configuration are present and valid.  
**Expected pass:** All checks report OK or PASS. No missing secrets. No misconfigured paths.  
**Acceptable warnings:** Informational notices about optional features not enabled.  
**Unacceptable failure:** Missing required env vars, import failures, missing config files.  
**Next action if fail:** Note the specific missing item. If it is an env var, check `.env.local` manually. Do not commit env files.

---

### 3. STATUS — Autopilot runtime status

```bash
python project_autopilot/autopilot.py --status
```

*(Substitute the correct entrypoint and flag)*

**Purpose:** Confirm Autopilot reports idle/ready status without starting any real execution.  
**Expected pass:** Status message indicating Autopilot is idle, no active runs, scheduler disabled.  
**Acceptable warnings:** "No active session" or "Scheduler not started" messages.  
**Unacceptable failure:** Scheduler reports as running, Claude execution starts, any write to logs or DB.  
**Next action if fail:** Stop immediately. Check scheduler config. Confirm `ENABLE_SCHEDULER=false`.

---

### 4. POLICY FIXTURES — Policy engine fixture test

```bash
python -m pytest project_autopilot/tests/test_policy_fixtures.py -v --tb=short
```

*(Substitute the correct test path)*

**Purpose:** Verify policy engine correctly evaluates all known fixture cases (approve, reject, defer).  
**Expected pass:** All tests PASSED. 0 failed, 0 errors.  
**Acceptable warnings:** Pytest deprecation warnings.  
**Unacceptable failure:** Any FAILED or ERROR result.  
**Next action if fail:** Identify which fixture failed. Check policy logic diff since last green run. Do not proceed to sandbox steps.

---

### 5. PROVIDER REGISTRY — Provider registry check

```bash
python project_autopilot/provider_registry.py --list
```

*(Substitute the correct module/flag)*

**Purpose:** Confirm all registered providers are importable and correctly configured.  
**Expected pass:** All providers listed with status `OK` or `registered`.  
**Acceptable warnings:** Providers in `disabled` state due to feature flags.  
**Unacceptable failure:** ImportError, missing provider, registry fails to load.  
**Next action if fail:** Identify which provider is broken. Check import path. Fix before proceeding.

---

### 6. OPENAI AUDITOR — Status and plan

```bash
python project_autopilot/openai_auditor.py --status
python project_autopilot/openai_auditor.py --plan --dry-run
```

**Purpose:** Confirm OpenAI Auditor reports ready status and produces a valid dry-run plan without executing.  
**Expected pass:** Status: ready/idle. Plan output: structured JSON or text with no execution triggered.  
**Acceptable warnings:** "No pending audit items" if queue is empty.  
**Unacceptable failure:** Auditor triggers real OpenAI API calls, writes to logs unexpectedly, or errors on startup.  
**Next action if fail:** Check auditor config for `DRY_RUN=true`. Do not run in live mode during validation.

---

### 7. MULTI-STEP LOOP — Dry-run

```bash
python project_autopilot/multi_step_loop.py --dry-run --steps 1
```

**Purpose:** Verify multi-step loop initializes, runs one step in dry-run mode, and exits cleanly without triggering real operations.  
**Expected pass:** Step 1 executes in simulation mode. No real API calls. Exit 0.  
**Acceptable warnings:** "Dry-run mode: skipping real execution" or similar.  
**Unacceptable failure:** Real API calls made, loop does not exit, scheduler locks acquired.  
**Next action if fail:** Check `DRY_RUN` flag. Abort and inspect loop termination logic.

---

### 8. CLAUDE SDK — Dry-run

```bash
python project_autopilot/claude_sdk_runner.py --dry-run
```

**Purpose:** Verify Claude SDK runner starts, validates configuration, and exits without invoking the Claude API.  
**Expected pass:** "Dry-run complete" or "Config valid" message. No Claude API call made. Exit 0.  
**Acceptable warnings:** SDK version mismatch notices.  
**Unacceptable failure:** Real Claude API call triggered, any write to conversation log.  
**Next action if fail:** Confirm `DRY_RUN=true` and API key is not live in dry-run mode. Stop.

---

### 9. CLAUDE ANALYSIS REVIEW — Review output

```bash
python project_autopilot/claude_analysis.py --review --dry-run
```

**Purpose:** Confirm analysis module can load its configuration and produce a review summary without executing analysis.  
**Expected pass:** Review output printed to stdout. No real analysis run. Exit 0.  
**Acceptable warnings:** "No prior analysis found" if history is empty.  
**Unacceptable failure:** Analysis executes against live data, API calls made.  
**Next action if fail:** Verify `--dry-run` flag is respected. Check for hardcoded execution paths.

---

### 10. CLAUDE SANDBOX — Preflight

```bash
python project_autopilot/claude_sandbox.py --preflight
```

**Purpose:** Validate sandbox environment setup: isolation, file system access restrictions, dependency availability.  
**Expected pass:** All preflight checks pass. Sandbox is ready. Exit 0.  
**Acceptable warnings:** "Isolation mode: soft" if hard isolation is not available.  
**Unacceptable failure:** Sandbox fails to initialize, preflight checks report missing dependencies, escape paths detected.  
**Next action if fail:** Address each failed preflight item. Do not proceed to simulation without a clean preflight.

---

### 11. CLAUDE SANDBOX — Simulation

```bash
python project_autopilot/claude_sandbox.py --simulate --dry-run
```

**Purpose:** Run a full sandbox simulation without executing real Claude calls. Verify input/output flow end-to-end.  
**Expected pass:** Simulation completes. Input accepted, output produced (mocked). No real Claude invocation.  
**Acceptable warnings:** "Using mock Claude response" in simulation mode.  
**Unacceptable failure:** Real Claude invoked, unexpected writes outside sandbox, simulation hangs.  
**Next action if fail:** Check sandbox isolation config. Kill process if hanging. Do not retry without diagnosing.

---

### 12. CLAUDE SANDBOX RUNNER — Status

```bash
python project_autopilot/sandbox_runner.py --status
```

**Purpose:** Confirm sandbox runner is idle, not processing any active job, and scheduler is confirmed off.  
**Expected pass:** Runner status: idle. No active jobs. Scheduler: disabled.  
**Acceptable warnings:** "No jobs in queue."  
**Unacceptable failure:** Runner reports active job, scheduler active, or any live execution underway.  
**Next action if fail:** Halt immediately. Check scheduler flags. Do not proceed until runner is confirmed idle.

---

### 13. CLAUDE SANDBOX — Approval preflight

```bash
python project_autopilot/claude_sandbox.py --approval-preflight
```

**Purpose:** Confirm the approval gate logic is correctly configured and would block unapproved runs.  
**Expected pass:** Approval gate active. Would block run without explicit approval. Exit 0.  
**Acceptable warnings:** "Auto-approval disabled" — this is expected and correct.  
**Unacceptable failure:** Approval gate bypassed, auto-approve is enabled, or approval check skipped.  
**Next action if fail:** Review approval gate configuration. Auto-approve must remain off during validation.

---

### 14. CLAUDE SANDBOX RUNNER — Dry-run

```bash
python project_autopilot/sandbox_runner.py --dry-run --task "validation-test"
```

**Purpose:** Execute one dry-run task through the sandbox runner pipeline end-to-end without real execution.  
**Expected pass:** Task accepted, processed in simulation, result returned. No real Claude call. Exit 0.  
**Acceptable warnings:** "Dry-run task: skipping real execution."  
**Unacceptable failure:** Real Claude invoked, task written to production queue, scheduler started.  
**Next action if fail:** Verify dry-run flag propagation through runner. Check task queue writes.

---

### 15. WORKTREE — Plan and simulate

```bash
git worktree list
python project_autopilot/worktree_manager.py --plan --dry-run
python project_autopilot/worktree_manager.py --simulate --dry-run
```

**Purpose:** Verify worktree manager can plan and simulate worktree operations without creating real worktrees or branches.  
**Expected pass:** Plan output shows intended operations. Simulation completes. No actual worktree created. Git state unchanged.  
**Acceptable warnings:** "Dry-run: no worktree created."  
**Unacceptable failure:** Real worktree created, new branch pushed, git state modified.  
**Next action if fail:** Check `--dry-run` propagation. Run `git worktree list` and `git branch` to verify no unintended state.

---

### 16. MANUAL HANDOFF — Dry-run (if available)

```bash
python project_autopilot/manual_handoff.py --dry-run
```

*(Skip if module does not exist — note as N/A in evidence checklist)*

**Purpose:** Confirm manual handoff module can produce a handoff packet without triggering real delivery.  
**Expected pass:** Handoff packet printed to stdout or written to dry-run output. No real send. Exit 0.  
**Acceptable warnings:** "Manual handoff not configured — skipping."  
**Unacceptable failure:** Real message sent, webhook triggered, email delivered.  
**Next action if fail:** Check delivery config. Disable real endpoints before re-running.

---

### 17. AUTOPILOT HEALTH — Health check

```bash
python project_autopilot/health.py --check
```

*(Substitute correct module/flag)*

**Purpose:** Run the full Autopilot health check. Verify all subsystems report healthy.  
**Expected pass:** All subsystems: OK. Overall health: PASS.  
**Acceptable warnings:** Optional subsystems disabled.  
**Unacceptable failure:** Any subsystem reports FAIL or CRITICAL.  
**Next action if fail:** Identify failing subsystem from output. Fix before proceeding to downstream steps.

---

### 18. V2 CHECK — v2 feature/compatibility check

```bash
python project_autopilot/v2_check.py --report
```

*(Substitute correct module)*

**Purpose:** Produce a v2 compatibility and readiness report.  
**Expected pass:** Report generated. No blocking issues. All v2 features in expected state.  
**Acceptable warnings:** "Feature X not yet enabled" if intentionally deferred.  
**Unacceptable failure:** v2 blockers present, incompatible state detected.  
**Next action if fail:** Note blockers in evidence checklist. Resolve before declaring v1 complete.

---

### 19. BACKEND AUDIT — Backend audit

```bash
python project_autopilot/backend_audit.py --run
```

*(Substitute correct module)*

**Purpose:** Audit backend integrations: Supabase connections, API clients, queue state.  
**Expected pass:** All backend checks pass. No broken connections. Queues empty.  
**Acceptable warnings:** Informational notes on connection pool sizing.  
**Unacceptable failure:** Supabase connection failure, API client errors, non-empty unexpected queues.  
**Next action if fail:** Check backend connectivity separately. Do not proceed to MIRA readiness until backend audit passes.

---

### 20. MIRA READINESS — Readiness check

```bash
python project_autopilot/mira_readiness.py --check
```

*(Substitute correct module)*

**Purpose:** Confirm Project Autopilot is ready for MIRA product development to resume.  
**Expected pass:** Readiness: GO. All blockers resolved.  
**Acceptable warnings:** Advisory items for future improvement.  
**Unacceptable failure:** Any item marked BLOCKING or NO-GO.  
**Next action if fail:** Address each blocking item before resuming MIRA development.

---

### 21. CONTROL CENTER — Generate control center report

```bash
python project_autopilot/control_center.py --generate
```

*(Substitute correct module)*

**Purpose:** Generate a Control Center status snapshot showing current system state.  
**Expected pass:** Report generated to stdout or output file. No errors.  
**Acceptable warnings:** "No active session data" if system has not been run.  
**Unacceptable failure:** Generation fails, report is empty or malformed.  
**Next action if fail:** Check that all required data sources are accessible. Re-run after fixing.

---

### 22. FLOW QA — Mock E2E

```bash
python project_autopilot/flow_qa.py --mock-e2e
```

*(Substitute correct module)*

**Purpose:** Run a mock end-to-end Flow QA pass to confirm the QA pipeline executes correctly with mocked data.  
**Expected pass:** All flow QA stages complete. No real external calls. Report generated.  
**Acceptable warnings:** "Using mock data source."  
**Unacceptable failure:** Real external calls, QA fails to complete, report not generated.  
**Next action if fail:** Check mock configuration. Ensure real API calls are disabled.

---

### 23. NPM LINT

```bash
npm run lint
```

**Purpose:** Verify no ESLint or equivalent linting errors in frontend/app code.  
**Expected pass:** Exit 0. No errors. Warnings acceptable.  
**Acceptable warnings:** Style warnings, informational notices.  
**Unacceptable failure:** Any lint error (exit non-zero).  
**Next action if fail:** Fix lint errors in the reported files. Do not suppress with `eslint-disable` unless justified.

---

### 24. NPM TYPECHECK

```bash
npm run typecheck
```

**Purpose:** Verify TypeScript compilation succeeds with no type errors.  
**Expected pass:** Exit 0. No type errors.  
**Acceptable warnings:** Deprecation notices for third-party packages.  
**Unacceptable failure:** Any type error (exit non-zero).  
**Next action if fail:** Fix type errors. Do not use `@ts-ignore` unless genuinely unavoidable and documented.

---

### 25. NPM BUILD

```bash
npm run build
```

**Purpose:** Verify production build succeeds end-to-end.  
**Expected pass:** Build completes successfully. Exit 0. Output artifacts generated.  
**Acceptable warnings:** Bundle size warnings below threshold.  
**Unacceptable failure:** Build fails (exit non-zero), missing modules, compilation errors.  
**Next action if fail:** Identify build error. Fix before declaring readiness. A failing build is a hard NO-GO.

---

### 26. GIT DIFF CHECK — Whitespace/conflict markers

```bash
git diff --check
```

**Purpose:** Confirm no whitespace errors or conflict markers exist in tracked files.  
**Expected pass:** No output. Exit 0.  
**Acceptable warnings:** None — all output from this command is a failure signal.  
**Unacceptable failure:** Any output (whitespace errors, conflict markers).  
**Next action if fail:** Fix each reported file before committing.

---

### 27. GIT STATUS — Final status check

```bash
git status --short
```

**Purpose:** Confirm only intended files are modified. No untracked secrets or generated logs staged.  
**Expected pass:** Only `project_control/*.md` files listed as new/modified. No `.env*` files. No log files.  
**Acceptable warnings:** None.  
**Unacceptable failure:** Any `.env*`, `*.log`, `*.secret`, or source code file listed as modified.  
**Next action if fail:** STOP. Do not commit. Investigate each unexpected file before proceeding.

---

### 28. GIT WORKTREE LIST — Worktree state

```bash
git worktree list
```

**Purpose:** Confirm no orphaned or unexpected worktrees exist.  
**Expected pass:** Only the main worktree listed.  
**Acceptable warnings:** None.  
**Unacceptable failure:** Unexpected worktrees present from a previous dry-run or test.  
**Next action if fail:** Prune orphaned worktrees with `git worktree prune`. Verify source before removing.

---

## QUICK REFERENCE: PASS CRITERIA SUMMARY

| # | Command | Hard STOP if fail? |
|---|---------|-------------------|
| 1 | compileall | YES |
| 2 | doctor | YES |
| 3 | status | YES |
| 4 | policy fixtures | YES |
| 5 | provider registry | YES |
| 6 | OpenAI auditor | YES |
| 7 | multi-step loop | YES |
| 8 | Claude SDK | YES |
| 9 | Claude analysis | YES |
| 10 | sandbox preflight | YES |
| 11 | sandbox simulation | YES |
| 12 | sandbox runner status | YES |
| 13 | approval preflight | YES |
| 14 | sandbox runner dry-run | YES |
| 15 | worktree plan/simulate | YES |
| 16 | manual handoff | NO (N/A if absent) |
| 17 | autopilot health | YES |
| 18 | v2 check | YES |
| 19 | backend audit | YES |
| 20 | MIRA readiness | YES |
| 21 | control center | YES |
| 22 | flow QA | YES |
| 23 | npm lint | YES |
| 24 | npm typecheck | YES |
| 25 | npm build | YES |
| 26 | git diff --check | YES |
| 27 | git status | YES |
| 28 | git worktree list | YES |

---

*End of AUTOPILOT FINAL VALIDATION COMMAND PACK v1.0*
