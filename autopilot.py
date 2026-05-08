#!/usr/bin/env python3
"""Project Autopilot — CLI dispatcher.

Top-level entry point that routes subcommands to the appropriate agent.

Usage:
    python autopilot.py scan --property ai-brief-latam
    python autopilot.py scan --property ai-brief-latam --top 10
    python autopilot.py scan --property ai-brief-latam --json
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
_root = Path(__file__).resolve().parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


def run_all(argv: list[str]) -> int:
    """Run the full pipeline: scan → score → brief → check → compose → comply → approve → publish."""
    import argparse
    parser = argparse.ArgumentParser(prog="autopilot run-all")
    parser.add_argument("--property", "-p", required=True)
    parser.add_argument("--max-score-items", type=int, default=10, help="Max items to LLM-score")
    parser.add_argument("--max-briefs", type=int, default=3, help="Max briefs to generate")
    parser.add_argument("--auto-approve", action="store_true", help="Auto-approve compliance-passing items")
    parser.add_argument("--log-level", default="WARNING", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args(argv)

    import logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.WARNING),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    import io
    if sys.platform == "win32" and hasattr(sys.stdout, "buffer") and sys.stdout.encoding != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    from rich.console import Console
    console = Console()

    prop = args.property
    steps = [
        ("scan", f"scan -p {prop}"),
        ("score", f"score -p {prop} --max-items {args.max_score_items}"),
        ("brief", f"brief -p {prop} --items {args.max_briefs}"),
        ("check", f"check -p {prop}"),
        ("compose", f"compose -p {prop}"),
        ("comply", f"comply -p {prop}"),
        ("approve", f"approve -p {prop}" + (" --auto-approve" if args.auto_approve else " --auto-approve")),
        ("publish", f"publish -p {prop}"),
    ]

    console.print()
    console.print(f"[bold blue]AUTOPILOT RUN-ALL[/bold blue] — {prop}")
    console.print(f"[dim]Steps: {' → '.join(s[0] for s in steps)}[/dim]")
    console.print()

    for i, (name, cmd_args) in enumerate(steps, 1):
        console.print(f"[bold]Step {i}/8: {name}[/bold]", end=" ")

        # Import and run each agent's CLI main
        try:
            if name == "scan":
                from agents.source_monitor.cli import main as step_main
            elif name == "score":
                from agents.signal_scorer.cli import main as step_main
            elif name == "brief":
                from agents.editorial.cli import main as step_main
            elif name == "check":
                from agents.fact_checker.cli import main as step_main
            elif name == "compose":
                from agents.content_composer.cli import main as step_main
            elif name == "comply":
                from agents.compliance.cli import main as step_main
            elif name == "approve":
                from agents.human_approval.cli import main as step_main
            elif name == "publish":
                from agents.publisher.cli import main as step_main
            else:
                continue

            # Suppress rich output — run with --json and discard, or just run quietly
            step_argv = cmd_args.split()[1:]  # Remove the command name
            step_argv.extend(["--log-level", args.log_level])
            result = step_main(step_argv)
            if result == 0:
                console.print("[green]OK[/green]")
            else:
                console.print("[red]FAILED[/red]")
                console.print(f"  [red]Step '{name}' failed. Stopping pipeline.[/red]")
                return result
        except Exception as e:
            console.print(f"[red]ERROR: {e}[/red]")
            return 1

    console.print()
    console.print("[bold green]Pipeline complete.[/bold green]")

    # Run analytics at the end
    console.print()
    from agents.analytics.cli import main as analytics_main
    analytics_main(["-p", prop, "--log-level", args.log_level])

    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python autopilot.py <command> [options]")
        print()
        print("Commands:")
        print("  run-all Full pipeline: scan → score → brief → check → compose → comply → approve → publish")
        print()
        print("  scan    Run Source Monitor to discover and rank new items")
        print("  score   Run Signal Scorer on Source Monitor output (requires ANTHROPIC_API_KEY)")
        print("  brief   Generate editorial briefs from scored items (requires ANTHROPIC_API_KEY)")
        print("  check   Fact-check claims in editorial briefs (requires ANTHROPIC_API_KEY)")
        print("  compose Generate publishable content from briefs (requires ANTHROPIC_API_KEY)")
        print("  comply  Review content for platform and brand compliance (requires ANTHROPIC_API_KEY)")
        print("  approve Interactive content approval (or --auto-approve for batch)")
        print("  publish Export approved content as ready-to-publish files")
        print("  analytics View pipeline metrics, API costs, and performance")
        return 1

    command = sys.argv[1]

    if command == "run-all":
        return run_all(sys.argv[2:])
    elif command == "scan":
        from agents.source_monitor.cli import main as scan_main
        return scan_main(sys.argv[2:])
    elif command == "score":
        from agents.signal_scorer.cli import main as score_main
        return score_main(sys.argv[2:])
    elif command == "brief":
        from agents.editorial.cli import main as brief_main
        return brief_main(sys.argv[2:])
    elif command == "check":
        from agents.fact_checker.cli import main as check_main
        return check_main(sys.argv[2:])
    elif command == "compose":
        from agents.content_composer.cli import main as compose_main
        return compose_main(sys.argv[2:])
    elif command == "comply":
        from agents.compliance.cli import main as comply_main
        return comply_main(sys.argv[2:])
    elif command == "approve":
        from agents.human_approval.cli import main as approve_main
        return approve_main(sys.argv[2:])
    elif command == "publish":
        from agents.publisher.cli import main as publish_main
        return publish_main(sys.argv[2:])
    elif command == "analytics":
        from agents.analytics.cli import main as analytics_main
        return analytics_main(sys.argv[2:])
    else:
        print(f"Unknown command: {command}")
        print("Available: scan, score, brief, check, compose, comply, approve, publish, analytics")
        return 1


if __name__ == "__main__":
    sys.exit(main())
