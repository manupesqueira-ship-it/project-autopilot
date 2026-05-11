"""CLI entry point for Fact-Checker agent."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from agents.fact_checker.agent import FactCheckerAgent
from agents.fact_checker.schemas import BriefVerdict, FactCheckerOutput


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _print_result(output: FactCheckerOutput) -> None:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()
    console.print()

    s = output.stats
    console.print(Panel(
        f"[bold]Fact-Checker[/bold]\n"
        f"Property: [cyan]{output.property}[/cyan]  |  "
        f"Editorial run: [dim]{output.editorial_run_id}[/dim]\n"
        f"Briefs: {s.briefs_checked}  |  Claims: {s.claims_total}  |  "
        f"[green]Verified: {s.claims_verified}[/green]  |  "
        f"[red]Disputed: {s.claims_disputed}[/red]  |  "
        f"[yellow]Unverified: {s.claims_unverified}[/yellow]  |  "
        f"Tokens: {s.total_input_tokens + s.total_output_tokens:,}",
        style="blue",
    ))

    for result in output.results:
        # Verdict coloring
        verdict_colors = {
            BriefVerdict.PASS: "bold green",
            BriefVerdict.PASS_WITH_EDITS: "yellow",
            BriefVerdict.NEEDS_REVIEW: "bold yellow",
            BriefVerdict.FAIL: "bold red",
        }
        v_style = verdict_colors.get(result.verdict, "white")

        console.print()
        console.print(f"  [{v_style}]{result.verdict.value.upper()}[/{v_style}] — {result.brief_title}")
        console.print(f"  [italic]{result.summary}[/italic]")

        if result.claims:
            table = Table(show_header=True, pad_edge=False, box=None)
            table.add_column("Status", width=12)
            table.add_column("Sev", width=8)
            table.add_column("Claim", min_width=40)
            table.add_column("Notes", min_width=20)

            status_colors = {
                "verified": "green",
                "partially_verified": "yellow",
                "unverified": "red",
                "disputed": "bold red",
                "unable_to_verify": "dim",
            }
            for c in result.claims:
                sc = status_colors.get(c.status.value, "white")
                table.add_row(
                    f"[{sc}]{c.status.value}[/{sc}]",
                    c.severity.value,
                    c.claim[:60],
                    c.notes[:40],
                )
            console.print(table)

        if result.recommended_edits:
            console.print(f"  [yellow]Edits sugeridas:[/yellow]")
            for edit in result.recommended_edits:
                console.print(f"    - {edit}")

        if result.critical_issues:
            console.print(f"  [red]Issues críticos:[/red]")
            for issue in result.critical_issues:
                console.print(f"    [red]![/red] {issue}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="fact_checker",
        description="Verify claims in editorial briefs before publication.",
    )
    parser.add_argument("--property", "-p", required=True)
    parser.add_argument("--run-id", default=None, help="Editorial run ID to check")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--log-level", default="WARNING",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--config-dir", type=Path, default=None)

    args = parser.parse_args(argv)
    _setup_logging(args.log_level)

    try:
        agent = FactCheckerAgent(
            property_name=args.property,
            config_dir=args.config_dir,
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    output = agent.run(editorial_run_id=args.run_id)

    if args.json_output:
        print(output.model_dump_json(indent=2))
    else:
        _print_result(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
