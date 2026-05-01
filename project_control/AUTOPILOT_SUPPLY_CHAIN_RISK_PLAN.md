# Project Autopilot Supply Chain Risk Plan

**Version:** 1.0
**Date:** 2026-05-01
**Scope:** Analysis and mitigation of supply chain risks across all dependency vectors in the Project Autopilot system

---

## 1. npm Dependencies

### 1.1 Current Dependency Profile

| Category | Package | Version | Risk Profile |
|----------|---------|---------|-------------|
| Framework | `next` | 14.2.35 | LOW — Vercel-maintained, widely audited |
| Auth | `@supabase/ssr` | 0.5.2 | LOW — Supabase-maintained |
| Auth | `@supabase/supabase-js` | 2.45.4 | LOW — Supabase-maintained |
| i18n | `next-intl` | 3.21.1 | LOW — Well-maintained OSS |
| Animation | `motion` | 11.11.0 | LOW — Framer-maintained |
| Styling | `tailwindcss` | 3.4.13 | LOW — Widely audited |
| Styling | `tailwind-merge` | 2.5.4 | LOW — Utility package |
| Validation | `zod` | 3.23.8 | LOW — Widely adopted |
| Dev | `typescript` | (devDep) | LOW — Microsoft-maintained |
| Dev | `eslint` | (devDep) | LOW — OpenJS Foundation |

### 1.2 npm Supply Chain Attack Vectors

| Vector | Severity | Likelihood | Example |
|--------|----------|------------|---------|
| Compromised maintainer account | CRITICAL | LOW | `ua-parser-js` incident (2021) |
| Typosquatting package | HIGH | MEDIUM | `crossenv` vs `cross-env` |
| Dependency confusion (private scope) | HIGH | LOW | Internal `@mira/` packages if created |
| Malicious postinstall script | CRITICAL | LOW | Runs arbitrary code on `npm install` |
| Protestware / sabotage | MEDIUM | LOW | `colors`/`faker` incident (2022) |
| Abandoned package takeover | MEDIUM | MEDIUM | Unmaintained packages with new owners |
| Transitive dependency compromise | HIGH | MEDIUM | Deep dependency tree vulnerability |
| Lockfile manipulation (PR attack) | HIGH | MEDIUM | Modified lockfile points to attacker registry |

### 1.3 npm Risk Mitigations

- [ ] Run `npm audit` before every deployment and agent cycle
- [ ] Pin exact versions in `package.json` (no `^` or `~` prefixes)
- [ ] Review `package-lock.json` diffs in every PR — never rubber-stamp
- [ ] Enable `npm audit signatures` to verify package provenance
- [ ] Set `ignore-scripts=true` in `.npmrc` for CI environments
- [ ] Use `npm ci` (not `npm install`) in CI to enforce lockfile
- [ ] Subscribe to GitHub security advisories for direct dependencies
- [ ] Quarterly review of dependency list — remove unused packages

---

## 2. package-lock.json Changes

### 2.1 Why package-lock.json Is a Critical File

The lockfile determines the exact code that runs in production. A manipulated lockfile can:
- Redirect package downloads to a malicious registry
- Pin vulnerable versions that `npm audit` would flag
- Add new transitive dependencies without changing `package.json`
- Change integrity hashes to accept tampered packages

### 2.2 Lockfile Attack Scenarios

| Scenario | Detection Difficulty |
|----------|---------------------|
| Agent PR modifies lockfile to add dependency | MEDIUM — visible in diff but may be overlooked |
| Lockfile points to alternate registry URL | HIGH — registry field buried in large diff |
| Integrity hash changed for existing package | HIGH — hash changes look like routine updates |
| New transitive dependency added | MEDIUM — appears as expected lockfile churn |
| Version downgrade of security-patched package | MEDIUM — requires version-aware review |

### 2.3 Lockfile Review Requirements

For every PR that modifies `package-lock.json`:

1. **Verify `package.json` justifies the change** — if `package.json` is unchanged, the lockfile change is suspicious
2. **Check registry URLs** — all entries must point to `https://registry.npmjs.org/`
3. **Verify no new direct dependencies** without explicit approval
4. **Run `npm audit`** on the resulting lockfile
5. **Compare integrity hashes** — use `npm ci` which validates hashes
6. **Review total size delta** — large increases may indicate bundled malware

### 2.4 Required Controls

- [ ] Pre-commit hook that flags `package-lock.json` changes without corresponding `package.json` changes
- [ ] CI check that validates all registry URLs in lockfile
- [ ] CI check that runs `npm audit` and blocks on HIGH/CRITICAL findings
- [ ] Agent rule: agents MUST NOT modify `package-lock.json` directly
- [ ] Agent rule: `npm install <package>` requires explicit human approval

---

## 3. Python Packages

### 3.1 Current Python Dependency Profile

The `project_autopilot/` codebase uses **minimal external dependencies**:

| Dependency | Import | Type | Risk |
|-----------|--------|------|------|
| Python stdlib | `urllib`, `json`, `pathlib`, `subprocess`, `os`, `argparse` | Built-in | NONE |
| `anthropic` | Lazy import in `claude_analysis_call.py` | PyPI package | LOW — Anthropic-maintained |
| No `requirements.txt` | N/A | N/A | Dependencies not version-pinned |
| No `pyproject.toml` | N/A | N/A | No formal dependency management |

### 3.2 Python Supply Chain Risks

| Risk | Severity | Current Exposure |
|------|----------|-----------------|
| Typosquatting on PyPI | HIGH | LOW — few dependencies |
| `pip install` in agent-generated code | CRITICAL | POSSIBLE — no restriction on pip |
| No dependency pinning | MEDIUM | anthropic SDK version not locked |
| No integrity verification | MEDIUM | No hash pinning for pip packages |
| VPS `pip install` by agent | HIGH | Agent could install malicious packages |
| `requirements.txt` injection via PR | HIGH | No requirements.txt exists yet |

### 3.3 Python Risk Mitigations

- [ ] Create `requirements.txt` with pinned versions and hashes
- [ ] Use `pip install --require-hashes` in all environments
- [ ] VPS venv must be created by human, not agent
- [ ] Agent rule: agents MUST NOT run `pip install` or modify dependency files
- [ ] Scan for unexpected `import` statements in agent-generated Python code
- [ ] Use `pip audit` (or `safety check`) for vulnerability scanning
- [ ] Restrict PyPI access on VPS to allowlisted packages only

---

## 4. GitHub Actions

### 4.1 Current State

No GitHub Actions workflows exist yet. This section covers risks for when they are created.

### 4.2 GitHub Actions Supply Chain Risks

| Risk | Severity | Description |
|------|----------|-------------|
| Third-party action compromise | CRITICAL | Attacker pushes malicious update to popular action |
| Action pinned to mutable tag | HIGH | `uses: actions/checkout@v4` can change without warning |
| Workflow injection via PR | HIGH | PR modifies `.github/workflows/` |
| Secret exfiltration in action | CRITICAL | Malicious action reads `${{ secrets.* }}` |
| Self-hosted runner compromise | N/A | Not using self-hosted runners |
| Workflow dispatch parameter injection | MEDIUM | User input flows into shell commands |
| Fork PR workflow execution | HIGH | Fork PR triggers workflow with access to secrets |
| GITHUB_TOKEN scope too broad | MEDIUM | Default token has write access to repo |

### 4.3 GitHub Actions Security Requirements

#### Pin Actions to Full SHA (Not Tags)

```yaml
# BAD — mutable tag, can be changed by action maintainer
- uses: actions/checkout@v4

# GOOD — immutable commit SHA
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
```

#### Restrict GITHUB_TOKEN Permissions

```yaml
permissions:
  contents: read      # minimum needed
  pull-requests: write # only if PR comments needed
  # Never grant: packages, deployments, admin
```

#### Workflow Restrictions

- [ ] All third-party actions pinned to full commit SHA
- [ ] `GITHUB_TOKEN` permissions set to minimum required per workflow
- [ ] Fork PRs do not have access to secrets (`pull_request_target` used carefully)
- [ ] No `workflow_dispatch` parameters passed directly to shell commands
- [ ] Workflow files require human approval to modify (CODEOWNERS)
- [ ] No self-hosted runners (use GitHub-hosted only)
- [ ] Secret names do not reveal their purpose (e.g., `SECRET_1` not `SUPABASE_SERVICE_KEY`)
- [ ] All workflow runs produce artifacts for audit

### 4.4 Recommended Workflow Architecture

```yaml
# Safe workflow pattern for agent PRs
name: Agent PR Validation
on:
  pull_request:
    branches: [master]

permissions:
  contents: read
  checks: write

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<full-sha>
      - uses: actions/setup-node@<full-sha>
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm run build
      - run: npm audit --audit-level=high
```

---

## 5. Claude/Codex Generated Code

### 5.1 AI-Generated Code as Supply Chain Risk

AI-generated code is a unique supply chain vector because:
- The "supplier" (AI model) is a black box with training data from unknown sources
- Code may contain patterns learned from vulnerable or malicious code
- AI models can be manipulated via prompt injection to generate backdoors
- Generated code is not subject to the same review as human-authored OSS

### 5.2 AI-Generated Code Risk Scenarios

| Scenario | Severity | Likelihood |
|----------|----------|------------|
| Codex generates code with known vulnerability pattern | HIGH | MEDIUM |
| Codex generates backdoor via prompt injection | CRITICAL | LOW |
| Claude generates overly permissive security config | HIGH | MEDIUM |
| AI generates code that imports malicious package | HIGH | LOW |
| AI generates code with hardcoded credentials (hallucinated) | MEDIUM | LOW |
| AI generates code that disables security features | HIGH | LOW |
| AI generates code with subtle logic errors | MEDIUM | HIGH |
| AI generates test that always passes (false confidence) | HIGH | MEDIUM |

### 5.3 AI-Generated Code Review Requirements

All AI-generated code MUST be treated as **untrusted external contribution** and requires:

1. **Human review before merge** — no auto-merge of AI code
2. **Security scan** — automated scan for:
   - Known vulnerability patterns (OWASP Top 10)
   - Suspicious imports/requires
   - Hardcoded secrets or credentials
   - Shell command execution
   - Network operations (fetch, HTTP, socket)
   - File system operations outside expected scope
   - Eval/exec usage
3. **Test validation** — AI-generated tests must be reviewed for:
   - Assert statements that actually test something (not `assert true`)
   - No mocked-out security checks
   - Coverage of edge cases and error paths
4. **Dependency review** — any new `import`/`require` must be approved
5. **Diff size limit** — PRs over N lines should be split or manually reviewed with extra scrutiny

### 5.4 Required Controls

- [ ] All AI-generated PRs marked with `ai-generated` label
- [ ] CODEOWNERS file prevents AI from modifying security-critical files
- [ ] Pre-merge scan for patterns in Section 5.3
- [ ] AI-generated code must include provenance comment (which model, which prompt)
- [ ] Track AI-generated code percentage per file for audit

---

## 6. Dependency Approval Gates

### 6.1 Approval Workflow

```
Agent wants to add dependency
         │
         ▼
┌─────────────────────────┐
│ GATE 1: Is it needed?   │ → Reject if functionality exists in stdlib
│ (necessity check)       │   or current dependencies
└────────────┬────────────┘
             │ YES
             ▼
┌─────────────────────────┐
│ GATE 2: Is it safe?     │ → Check: maintainer reputation, download count,
│ (security check)        │   last publish date, known vulnerabilities,
└────────────┬────────────┘   license compatibility
             │ PASS
             ▼
┌─────────────────────────┐
│ GATE 3: Is it minimal?  │ → Check: transitive dependency count,
│ (scope check)           │   bundle size impact, install scripts
└────────────┬────────────┘
             │ PASS
             ▼
┌─────────────────────────┐
│ GATE 4: Human approval  │ → Human reviews the specific version,
│ (final decision)        │   lockfile diff, and justification
└────────────┬────────────┘
             │ APPROVED
             ▼
     Add to package.json
     Run npm install
     Commit lockfile
```

### 6.2 Dependency Assessment Criteria

| Criterion | Acceptable | Unacceptable |
|-----------|-----------|--------------|
| Maintainer | Known org (Vercel, Supabase, etc.) or established OSS maintainer | Anonymous, new account, single-person |
| Weekly downloads | >10,000 | <1,000 |
| Last publish | Within 12 months | >24 months ago |
| Known CVEs | None open, or patches available | Unpatched HIGH/CRITICAL |
| License | MIT, Apache-2.0, BSD | GPL (copyleft), unlicensed, custom |
| Transitive deps | <20 | >50 |
| Install scripts | None | postinstall, preinstall scripts |
| Bundle size | <100KB (minified) | >500KB without justification |

### 6.3 Emergency Dependency Updates

For security patches (CVE fix in existing dependency):

1. Create issue documenting the CVE
2. Update the specific package version
3. Run full test suite
4. Fast-track human review (same-day)
5. Deploy after verification

### 6.4 Required Controls

- [ ] `DEPENDENCY_APPROVALS.md` log of all approved dependencies with justification
- [ ] Agent rule: agents CANNOT add new dependencies without human pre-approval
- [ ] CI check that fails if `package.json` dependencies changed without approval entry
- [ ] Quarterly dependency audit (remove unused, update outdated, scan for CVEs)
- [ ] Dependabot or Renovate configured for automated security update PRs

---

## 7. Validation Requirements

### 7.1 Pre-Merge Validation Checklist

Every PR (human or agent) must pass these checks before merge:

| Check | Tool | Blocking? |
|-------|------|-----------|
| TypeScript type check | `npm run typecheck` | YES |
| ESLint | `npm run lint` | YES |
| Build succeeds | `npm run build` | YES |
| Python syntax check | `python -B -m compileall` | YES |
| npm audit (HIGH+) | `npm audit --audit-level=high` | YES |
| Git diff clean | `git diff --check` | YES (whitespace errors) |
| No secret patterns in diff | Custom scanner | YES |
| No `.env` files in diff | File check | YES |
| No lockfile-only changes | Lockfile validator | YES (if no package.json change) |
| Dependency approval | `DEPENDENCY_APPROVALS.md` | YES (if deps changed) |

### 7.2 Periodic Validation Schedule

| Validation | Frequency | Owner |
|-----------|-----------|-------|
| `npm audit` | Every PR + weekly | CI / Human |
| `pip audit` (when requirements.txt exists) | Every PR + weekly | CI / Human |
| GitHub Actions SHA verification | Monthly | Human |
| Dependency license scan | Quarterly | Human |
| Full dependency review (unused, outdated) | Quarterly | Human |
| Supply chain incident review (check for known compromises) | Monthly | Human |
| AI-generated code audit (review provenance, quality) | Monthly | Human |

### 7.3 Validation Failure Response

| Failure Type | Response | Escalation |
|-------------|----------|------------|
| `npm audit` HIGH/CRITICAL | Block merge, create issue, assess impact | If exploitable: emergency patch |
| New dependency without approval | Block merge, request justification | Human decides |
| Secret pattern detected in code | Block merge, alert human, rotate if exposed | Immediate rotation |
| Lockfile manipulation suspected | Block merge, investigate, full lockfile audit | Security review |
| AI-generated backdoor detected | Block merge, HALT all agents, full audit | Incident response |
| Build failure | Block merge, fix required | Standard dev workflow |

### 7.4 Supply Chain Incident Response Plan

If a supply chain compromise is detected:

1. **Identify:** Which package/action/dependency is affected
2. **Assess:** Is the compromised version in our lockfile/workflow?
3. **Contain:** Pin to last-known-good version, disable affected workflows
4. **Remediate:** Update to patched version, or replace dependency
5. **Verify:** Full build + test + audit cycle
6. **Post-mortem:** Document in `DEPENDENCY_APPROVALS.md`, add to monitoring

---

## Appendix: Supply Chain Risk Summary

```
RISK SOURCE          CURRENT EXPOSURE    PRIORITY
───────────────────  ─────────────────   ────────
npm dependencies     LOW (few, reputable) P2
package-lock.json    MEDIUM (no CI gate)  P1
Python packages      LOW (stdlib mostly)  P3
GitHub Actions       N/A (not created)    P1 (when created)
AI-generated code    HIGH (primary workflow) P0
Dependency approval  NONE (no process)    P1
Validation pipeline  PARTIAL (manual)     P1
```

**Top Priority:** Establish CI validation pipeline and dependency approval process before expanding agent autonomy.
