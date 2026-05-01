# Project Autopilot — Agent Operating Model

**Status:** Planning / Not yet deployed  
**Last updated:** 2026-04-30

---

## 1. Roles

### Project Autopilot (Orchestrator)

**What it is:** The master process. Reads task queue, enforces policy, routes tasks to agents, records evidence, escalates to human.

**What it does:**
- Reads `project_control/TASK_QUEUE.md`
- Applies policy gates from `project_control/AGENT_RULES.md`
- Decides which agent handles each task
- Creates and destroys worktrees
- Monitors budget, HALT file, lock file
- Sends Telegram alerts
- Archives evidence

**What it does NOT do:**
- Generate code (delegates to Codex)
- Generate analysis prose (delegates to Claude)
- Make product decisions
- Approve its own decisions
- Merge PRs

---

### Codex (OpenAI)

**What it is:** The code generation agent. Receives a structured task spec and produces implementation code.

**What it does:**
- Receives task spec (not raw conversation)
- Generates TypeScript or Python code
- Returns structured diff or file content
- Returns evidence JSON

**What it does NOT do:**
- Execute code it generates
- Read `.env` files
- Push to git directly
- Make architectural decisions
- Review its own output

**When to use:** Implementing well-specified, bounded coding tasks. Best for: adding a new API endpoint, refactoring a module, writing tests for a known spec.

**When NOT to use:** Architectural decisions, security-sensitive changes, anything requiring product judgment, anything touching auth or billing without human review.

---

### Claude Agent SDK (Anthropic)

**What it is:** The analysis and reasoning agent. Receives artifacts and produces structured verdicts.

**What it does:**
- Analyzes diffs, logs, test results
- Produces policy compliance reports
- Identifies risks and anomalies
- Returns structured JSON verdicts
- Flags items for human review

**What it does NOT do:**
- Execute shell commands
- Write to disk (except evidence, via autopilot runner)
- Approve its own analysis
- Call Supabase directly

**When to use:** Code review, policy compliance checking, anomaly detection, structured analysis tasks.

**When NOT to use:** Code generation (use Codex), product decisions (use human), security-critical review without human sign-off.

---

### Claude Code

**What it is:** Interactive assistant / GitHub Actions reviewer.

**What it does:**
- Responds to developer queries interactively
- Posts structured PR review comments via GitHub Actions
- Runs policy gate analysis in CI
- Provides architecture guidance

**What it does NOT do:**
- Merge PRs
- Push to protected branches
- Approve PRs autonomously
- Execute migrations

**When to use:** PR review automation, interactive developer assistance, architecture documentation.

---

### ChatGPT / Codex (Design + Research)

**What it is:** Research and design input. External perspective, not core loop.

**What it does:**
- Provides research on external libraries, patterns, best practices
- Generates UI/UX design alternatives
- Produces comparative analysis of approaches

**What it does NOT do:**
- Write code that goes directly into the repo
- Make policy decisions
- Have access to codebase secrets or internal state

**When to use:** Research tasks in RESEARCH_DIRECTOR_STANDARD.md, design exploration, external benchmarking.

---

### Human Owner

**What they are:** The sole decision-maker for irreversible actions.

**What they do:**
- Review PRs and approve merges
- Manage HALT file (remove it to resume)
- Approve deploys
- Approve scheduler activation
- Add new secrets
- Sign off on phase transitions
- Resolve merge conflicts
- Veto any agent output

**What they are NOT expected to do:**
- Write boilerplate code (agents handle this)
- Manually format code (linters handle this)
- Manually run repetitive checks (CI handles this)

---

## 2. Task Lifecycle

### Phase 1: Plan

**Owner:** Human + Project Autopilot  
**Actions:**
- Human adds task to `TASK_QUEUE.md` with full spec
- Human assigns priority, risk level, agent assignment
- Autopilot reads queue, validates task spec completeness
- Autopilot flags incomplete specs to human before proceeding

**Exit criteria:** Task has: ID, description, acceptance criteria, risk level, assigned agent, any relevant file paths.

---

### Phase 2: Assign

**Owner:** Project Autopilot  
**Actions:**
- Autopilot selects task from queue (priority order)
- Checks HALT file — abort if present
- Checks budget — abort if at cap
- Checks lock file — abort if another cycle running
- Creates worktree with correct naming convention
- Writes `.agent_lock` in worktree
- Logs task start to evidence

**Exit criteria:** Worktree created, lock held, task start logged, Telegram notified.

---

### Phase 3: Implement

**Owner:** Assigned agent (Codex or Claude SDK)  
**Actions:**
- Agent receives task spec (structured prompt, not raw queue)
- Agent generates code or analysis within worktree
- Agent runs self-checks: lint, typecheck, build
- Agent writes evidence record
- Agent reports completion to autopilot runner

**Exit criteria:** All checks pass, evidence written, agent output structured and ready for policy review.

---

### Phase 4: Validate

**Owner:** Project Autopilot + CI  
**Actions:**
- Autopilot runs policy gate on agent output
- CI runs all required checks on the worktree branch
- Claude Agent SDK reviews diff if configured
- Evidence record updated with validation results

**Exit criteria:** All required checks pass. Policy gate passes. Evidence complete.

---

### Phase 5: Policy Review

**Owner:** Project Autopilot + Claude Agent SDK  
**Actions:**
- Policy gate produces structured verdict: pass / fail / escalate
- If fail: write reason, block PR, send Telegram, await human
- If escalate: flag specific concern, block PR, require human decision
- If pass: open DRAFT PR with evidence

**Exit criteria:** Verdict recorded. PR opened as draft. Human notified.

---

### Phase 6: Commit

**Owner:** Agent (within worktree) + Autopilot (push)  
**Actions:**
- Agent commits within worktree (auto-commit rules apply)
- Autopilot pushes worktree branch to origin
- PR opened as DRAFT
- Evidence artifact uploaded to GitHub

**Exit criteria:** Commit exists on origin. Draft PR open. Evidence artifact attached.

---

### Phase 7: Escalate

**Triggered by:** Policy gate failure, validation failure, budget cap, HALT file, unhandled exception, merge conflict, anything unexpected.

**Owner:** Project Autopilot (automated escalation) + Human (resolution)  
**Actions:**
- Telegram alert with full context
- Evidence record marked: `verdict: escalate`
- HALT file written (if exception or policy violation)
- PR blocked from merge
- Human decision queue updated in `HUMAN_QUESTIONS.md`

**Exit criteria:** Human acknowledged, decision recorded, cycle resumed or abandoned.

---

## 3. Provider Routing Rules

| Task type | Primary agent | Fallback |
|-----------|--------------|---------|
| Code generation | Codex | Human |
| Code review / analysis | Claude Agent SDK | Claude Code |
| Policy gate check | Autopilot (rule-based) | Claude Agent SDK |
| Architecture design | Human + Claude Code | — |
| Research | ChatGPT / Claude | Human |
| Security audit | Human (always) | Claude Agent SDK (advisory) |
| Database migration | Human (always) | None |
| Deploy | Human (always) | None |

Routing is deterministic (rule-based first, AI second).  
AI agents are never routed tasks that require product judgment without human approval.

---

## 4. Design Director Role

**Persona:** Senior product designer. Evaluates all user-facing changes.

**Input:** PR diff, design spec, DESIGN_DIRECTOR_STANDARD.md  
**Output:** Structured review: pass / needs-revision / reject  

**Evaluation criteria:**
- Does the change meet DESIGN_RUBRIC.md standards?
- Is it consistent with COPYWRITING_STANDARD.md?
- Does it match design references in DESIGN_REFERENCES.md?
- Does it introduce any accessibility regressions?

Design Director review is required for any change to `app/`, `components/`.  
Design Director review is advisory in Phase 1 (informational PR comment).  
Design Director review becomes blocking in Phase 3+ (required check).

---

## 5. Research Director Role

**Persona:** Senior technical researcher. Evaluates external library choices, architecture patterns, competitive approaches.

**Input:** Task spec, RESEARCH_DIRECTOR_STANDARD.md, DEEP_RESEARCH_PROTOCOL.md  
**Output:** Research summary with recommendation  

**Evaluation criteria:**
- Is the proposed approach the best available option?
- Are there newer / more appropriate libraries?
- What are the security and maintenance risks?
- What do comparable products do?

Research Director is invoked before any significant new dependency is added.  
Research Director output is written to `project_control/` as a standalone doc.

---

## 6. Backend / Security Audit Role

**Persona:** Senior backend engineer with security focus.

**Input:** PR diff, MIRA_SECURE_MVP_RUNBOOK.md, CUSTOMER_DATA_POLICY.md  
**Output:** Security audit verdict  

**Evaluation criteria:**
- No secrets exposed in code or logs
- No SQL injection vectors
- No XSS introduction
- Auth and authorization correct
- No PII logged
- RLS policies correct (when relevant)

Security audit is required for any change touching:
- Auth flows
- Supabase queries
- API endpoints
- User data handling

Security audit is always human-reviewed, not just AI-reviewed.

---

## 7. Flow QA Role

**Persona:** QA engineer testing end-to-end user flows.

**Input:** PR diff, MIRA_E2E_VALIDATION_PLAN.md, QA_PROTOCOL.md  
**Output:** QA verdict with specific test cases  

**Evaluation criteria:**
- Does the change break any critical user flow?
- Are new flows covered by tests or manual test plan?
- Is the change consistent with QUALITY_BAR.md?

Flow QA is invoked for any change to `app/`, `lib/` (user-facing behavior).  
Initially advisory. Becomes blocking when test suite is established.

---

## 8. Evidence Role

Every agent action that changes state must produce evidence.  
Evidence is the audit trail that makes autonomous operation trustworthy.

Evidence producer responsibilities:
- Record what was done, not just what was intended
- Include: agent, task, cycle, timestamps, cost, verdict
- Produce valid JSON (not freeform text)
- Avoid including secrets or user data

Evidence consumer responsibilities:
- Human reviews evidence before approving merge
- Dashboard (future) displays evidence summary
- Budget tracking reads evidence to compute daily spend
- Post-mortem analysis reads evidence to trace failures

Evidence is not optional. A cycle without evidence is treated as a failure.

---

## 9. Human Decision Queue

File: `project_control/HUMAN_QUESTIONS.md`

Format:
```markdown
## TASK-042 — Session Expiry: Needs decision
**Date:** 2026-04-30
**Cycle:** <uuid>
**Agent:** codex
**Question:** The implementation handles token expiry but not refresh token rotation. Should we add rotation in this PR or defer?
**Options:**
- [ ] Add rotation now (estimated: +2h Codex cycle)
- [ ] Defer to TASK-047
**Evidence:** [cycle_<uuid>.json](evidence/...)
**Deadline:** Non-blocking
```

Human adds their decision by checking one option and signing with initials.  
Autopilot reads this file before resuming a blocked task.

---

## 10. What Can Be Autonomous Now

| Action | Autonomous? | Condition |
|--------|------------|-----------|
| Read TASK_QUEUE | Yes | Always |
| Run lint/typecheck/build | Yes | Always |
| Run policy gate (rule-based) | Yes | Always |
| Write evidence record | Yes | Always |
| Send Telegram notification | Yes | When configured |
| Create worktree | Yes | After HALT check |
| Commit to worktree branch | Yes | After all checks pass |
| Push to worktree branch | Yes | After commit |
| Open DRAFT PR | Yes | After push |
| Post CI review comment | Yes | Claude Code in CI |
| Upload evidence artifact | Yes | In CI workflow |

---

## 11. What Requires Human Approval

| Action | Why human required |
|--------|-------------------|
| Convert draft PR to ready | Human has reviewed the diff |
| Approve and merge PR | Irreversible code change |
| Execute Supabase migration | Irreversible DB change |
| Enable scheduler | Starts autonomous cycles |
| Deploy to production | Irreversible |
| Remove HALT file | Resume after emergency stop |
| Add new secret | Security scope change |
| Enable new agent provider | New cost/risk surface |
| Change AGENT_RULES | Policy change |
| Change AUTONOMY_PROTOCOL | Autonomy level change |
| Resolve merge conflict | Requires intent judgment |
| Rollback a merge | Requires scope judgment |
| Approve phase transition | Architecture decision |

---

## 12. What Is Forbidden

These actions are forbidden for all agents, in all contexts, permanently:

| Action | Category |
|--------|---------|
| Auto-merge any PR | Permanent prohibition |
| Write to `.env` or secret files | Permanent prohibition |
| Push to main / develop directly | Permanent prohibition |
| Execute database migrations autonomously | Permanent prohibition |
| Approve an agent's own output | Permanent prohibition |
| Bypass policy gate with `--skip-policy` | Permanent prohibition |
| Log or transmit user PII | Permanent prohibition |
| Remove HALT file autonomously | Permanent prohibition |
| Disable HALT file check | Permanent prohibition |
| Run `git push --force` | Permanent prohibition |
| Access `/root/bot/` on VPS | Permanent prohibition |
| Read another agent's worktree | Permanent prohibition |
| Generate code that disables policy gates | Permanent prohibition |
| Send secrets in Telegram messages | Permanent prohibition |
| Include secrets in evidence records | Permanent prohibition |

**If an agent produces output that violates any prohibition:** reject the output, write HALT, escalate to human immediately. Do not attempt to sanitize or partially apply the output.

---

## 13. Claude Sandboxed Builder Boundary

Claude can become a builder only after a separate human-approved sandbox execution phase. The current operating model supports boundary preflight only:

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-sandbox-preflight --task "<task>"
python -B project_autopilot/agent_loop.py --project mira --claude-sandbox-simulate --task "<task>"
```

Future flow:

```text
Human objective
-> OpenAI Auditor dry-run planning
-> Builder Orchestrator selects future Claude sandbox
-> Sandbox preflight
-> Sandbox simulation
-> Human approval
-> Dedicated worktree execution in a later sprint
-> Builder report
-> OpenAI Auditor review if blocked/done
-> Validation
-> Post-builder policy
-> Human-controlled commit/merge decision
```

Preflight and simulation do not execute providers. They only prove that worktree lifecycle, file scope, command scope, no-secret prompt pack, rollback/rejection, evidence, and policy review requirements are present.

Claude builder execution remains disabled until a later sprint explicitly implements human-approved sandbox execution.

---

## 14. Runner Approval Loop

The future Claude sandbox runner adds an approval loop before any worktree or builder action:

```text
sandbox preflight
-> approval contract preview
-> runner dry-run
-> human decision
-> future worktree creation sprint
-> later future builder execution sprint
```

The runner states are documented in `CLAUDE_SANDBOX_RUNNER_INTERFACE.md`. In the current mode, `APPROVED_FOR_WORKTREE_CREATION_FUTURE` and `APPROVED_FOR_BUILDER_EXECUTION_FUTURE` are audit labels only, not executable permissions.

If approval is rejected, expired, invalid, missing rollback, missing post-builder policy, or includes forbidden actions, the runner must stop and preserve evidence.
