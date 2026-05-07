# OpenAI Auditor Standard

## Purpose

OpenAI Auditor is a Project Autopilot provider role for planning, prompt refinement, builder-output review, blocker diagnosis, correction prompt generation, risk translation, evidence review, and next-step recommendation.

OpenAI Auditor is not the default builder. It does not edit files, execute commands, deploy, mutate live systems, call paid APIs, or approve its own output.

## Current Mode

Current mode: dry-run only.

Allowed commands:

```bash
python -B project_autopilot/openai_auditor.py --project mira --status
python -B project_autopilot/openai_auditor.py --project mira --plan "Build a sandboxed Claude builder loop"
python -B project_autopilot/agent_loop.py --project mira --openai-auditor-status
python -B project_autopilot/agent_loop.py --project mira --openai-auditor-plan --task "Build a sandboxed Claude builder loop"
```

These commands must not call OpenAI.

## Role Separation

- Human sets the objective and approves high-risk actions.
- Project Autopilot organizes work, owns gates, and remains final judge.
- OpenAI Auditor plans, improves prompts, reviews evidence, and prepares correction instructions.
- Codex is the current primary builder.
- Claude is the future heavy builder only inside a sandboxed worktree after separate approval.

## Required Safety Gates

- No `.env`, `.env.local`, `.env.*`, secrets, deployment files, or git history changes.
- No OpenAI live call without explicit approval.
- No Anthropic call from OpenAI Auditor.
- No scheduler activation.
- No automatic Claude execution.
- No deploy automation.
- No SQL/RLS/storage mutation.
- No paid API call.
- No policy bypass or self-approval.

## Future Live Auditor Call

A future controlled OpenAI Auditor call may be added only after:

1. Policy fixtures pass.
2. Prompt safety/redaction is active.
3. Cost/budget gate is active.
4. Human explicitly approves the exact call.
5. Project Autopilot confirms the auditor cannot approve its own output.

Live OpenAI calls remain disabled in the current sprint.
