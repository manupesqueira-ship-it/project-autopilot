# Claude Manual Handoff Protocol

Status: active, manual-only

Purpose: define how a human can use Claude Code inside a Project Autopilot-approved sandbox worktree without Project Autopilot executing Claude automatically.

## Commands

Dry-run packet only:

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-manual-handoff-dry-run --task "<task>"
```

Create one approved sandbox worktree and handoff packet:

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-manual-handoff-create-approved --task "<task>"
```

Post-builder intake after the human saves Claude's report:

```bash
python -B project_autopilot/agent_loop.py --project mira --post-builder <path_to_claude_builder_report>
```

Cleanup:

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-worktree-cleanup-approved --task-id "<task_id>"
```

Direct module commands:

```bash
python -B project_autopilot/claude_manual_handoff.py --project mira --task "<task>" --dry-run
python -B project_autopilot/claude_manual_handoff.py --project mira --task "<task>" --create-worktree-approved
```

## Human Steps

1. Generate the create-approved handoff packet.
2. Open Claude Code manually in the sandbox worktree path from the packet.
3. Paste `logs/claude_sandbox/<project_id>/latest/manual_handoff_packet.md` into Claude Code.
4. Keep Claude inside the sandbox worktree and within the file/command allowlists.
5. Save Claude's final report as markdown.
6. Run `--post-builder <report>` from the main repo.
7. Cleanup the sandbox worktree only after evidence is preserved.

## Allowed

- Manual human paste into Claude Code.
- Work inside the approved sandbox worktree.
- Allowed files and commands listed in the handoff packet.
- Validation commands listed in the packet.
- Builder report generation.

## Forbidden

- Project Autopilot executing Claude.
- Automatic Claude execution.
- Anthropic/OpenAI calls by Project Autopilot.
- Env/secrets reads or secret printing.
- SQL/RLS, deploy, paid APIs, scheduler changes.
- Auto-merge, force-push, or git history rewriting.
- Product code changes unless explicitly allowed by the packet.

## Required Builder Report

Claude must return a markdown report containing task, files created, files modified, commands run, validation results, evidence captured, blockers, risks, git status, and the post-builder return command.

## Packet Evidence

The packet and metadata are written under ignored logs:

```text
logs/claude_sandbox/<project_id>/latest/manual_handoff_packet.md
logs/claude_sandbox/<project_id>/latest/manual_handoff_metadata.json
```

The metadata must show that Project Autopilot did not execute Claude, did not call Anthropic/OpenAI, did not enable automatic Claude execution, and did not touch product code.

## Difference From Automatic Execution

This protocol creates a packet and optionally a sandbox worktree. It does not run Claude, does not pass tool access to Claude, and does not accept builder output without Project Autopilot post-builder policy review.
