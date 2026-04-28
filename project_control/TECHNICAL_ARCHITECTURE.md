# Technical Architecture

## Application Stack

- Next.js 14 App Router.
- React 18.
- TypeScript.
- Tailwind CSS.
- next-intl for localized routes and messages.
- Motion for UI transitions.
- Supabase client and SQL schema scaffolding.
- Mocked provider modules for image and video generation.

## Agent Control Layer

The control layer is intentionally separate from the product app:

- `project_control/` contains durable project state, rules, blockers, decisions, and task queue.
- `agent/` contains Python orchestration modules.
- `config/agent.config.example.yaml` documents default operating configuration.
- `logs/` stores iteration logs and generated prompts.
- `screenshots/` stores future visual evidence.

## Operating Model

1. Read all project control files.
2. Collect evidence from safe commands and repository state.
3. Ask OpenAI for next-task planning in supervised mode.
4. Generate a builder prompt for Codex or Claude.
5. Do not execute the builder prompt automatically.
6. Collect QA evidence after builder work is manually completed.
7. Ask OpenAI for QA review and correction prompt generation.
8. Escalate blockers through markdown state files and Telegram when enabled.
