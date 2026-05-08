"""CLI entry point for Compliance agent."""

from __future__ import annotations

import argparse
import io
import logging
import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from agents.compliance.agent import ComplianceAgent
from agents.compliance.schemas import ComplianceOutput, ComplianceVerdict, CheckSeverity


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _print_result(output: ComplianceOutput) -> None:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()
    console.print()

    s = output.stats
    console.print(Panel(
        f"[bold]Compliance Review[/bold]\n"
        f"Property: [cyan]{output.property}[/cyan]  |  "
        f"Composer run: [dim]{output.composer_run_id}[/dim]\n"
        f"Items: {s.items_checked}  |  "
        f"[green]Approved: {s.items_approved}[/green]  |  "
        f"[yellow]Warnings: {s.items_approved_with_warnings}[/yellow]  |  "
        f"[red]Blocked: {s.items_blocked}[/red]  |  "
        f"Checks: {s.checks_passed}/{s.total_checks} passed  |  "
        f"Tokens: {s.total_input_tokens + s.total_output_tokens:,}",
        style="blue",
    ))

    for result in output.results:
        verdict_styles = {
            ComplianceVerdict.APPROVED: ("bold green", "APPROVED"),
            ComplianceVerdict.APPROVED_WITH_WARNINGS: ("yellow", "WARNINGS"),
            ComplianceVerdict.BLOCKED: ("bold red", "BLOCKED"),
        }
        style, label = verdict_styles.get(result.verdict, ("white", "UNKNOWN"))

        console.print()
        console.print(
            f"  [{style}]{label}[/{style}] "
            f"[cyan]{result.content_type}[/cyan] — {result.brief_title[:50]}"
        )
        console.print(f"  [italic]{result.summary}[/italic]")

        # Show failed checks
        failed = [c for c in result.checks if not c.passed]
        if failed:
            for c in failed:
                sev_style = {"block": "bold red", "warning": "yellow", "info": "dim"}.get(
                    c.severity.value, "white"
                )
                console.print(
                    f"    [{sev_style}]{c.severity.value.upper()}[/{sev_style}] "
                    f"{c.rule}: {c.detail[:60]}"
                )
                if c.suggested_fix:
                    console.print(f"      Fix: {c.suggested_fix[:80]}")

        if result.blocks:
            for b in result.blocks:
                console.print(f"    [bold red]BLOCK:[/bold red] {b}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="compliance",
        description="Review content for platform and brand compliance.",
    )
    parser.add_argument("--property", "-p", required=True)
    parser.add_argument("--run-id", default=None, help="Composer run ID")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--log-level", default="WARNING",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--config-dir", type=Path, default=None)

    args = parser.parse_args(argv)
    _setup_logging(args.log_level)

    try:
        agent = ComplianceAgent(property_name=args.property, config_dir=args.config_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    output = agent.run(composer_run_id=args.run_id)

    if args.json_output:
        print(output.model_dump_json(indent=2))
    else:
        _print_result(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
