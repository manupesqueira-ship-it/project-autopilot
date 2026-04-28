# Human Questions

Non-blocking questions go here so the agent can keep working while preserving context for later review.

## Open Questions

### 2026-04-28 05:10 UTC - OpenAI API budget for Project Autopilot

Status: open
Severity: non-blocking
Source: agent

Question:
What monthly OpenAI API budget should Project Autopilot use by default? Currently set to $100/month in mira.yaml.

Why it matters:
The budget controls whether `--cycle` can run and how many supervisor calls are allowed per day. Too low and cycles are blocked frequently. Too high and costs accumulate without oversight.

### 2026-04-28 05:10 UTC - Should Project Autopilot live in its own repo?

Status: open
Severity: non-blocking
Source: agent

Question:
Should Project Autopilot eventually be extracted to its own repository, separate from MIRA?

Why it matters:
Currently Project Autopilot lives under `project_autopilot/` inside the MIRA repo. This works for now but means every project that uses it would need a copy or a git submodule. A standalone repo would allow independent versioning and reuse.

### 2026-04-28 05:10 UTC - Scheduler execution environment

Status: open
Severity: non-blocking
Source: agent

Question:
Should the future scheduler run locally (cron on dev machine), on a VPS, or not at all yet?

Why it matters:
The scheduler is listed as a future task but the execution environment affects design decisions (e.g., local cron vs. systemd timer vs. cloud function). No scheduler is needed until the manual workflow is proven reliable.

## Format

```md
### YYYY-MM-DD HH:MM - Short title

Status: open
Severity: non-blocking
Source: agent | builder | qa | human

Question:
...

Why it matters:
...
```
