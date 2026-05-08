"""CLI entry point for Editorial agent.

Usage:
    python -m agents.editorial.cli --property ai-brief-latam
    python -m agents.editorial.cli --property ai-brief-latam --items 3
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from agents.editorial.agent import EditorialAgent
from agents.editorial.schemas import EditorialResult


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _print_result(result: EditorialResult) -> None:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown

    console = Console()
    console.print()

    s = result.stats
    console.print(Panel(
        f"[bold]Editorial Agent[/bold]\n"
        f"Property: [cyan]{result.property}[/cyan]  |  "
        f"Score run: [dim]{result.score_run_id}[/dim]\n"
        f"Briefs: [bold green]{s.briefs_generated}[/bold green]/{s.items_processed}  |  "
        f"Tokens: {s.total_input_tokens + s.total_output_tokens:,}",
        style="blue",
    ))

    if result.errors:
        console.print(f"\n  [red]Errors ({len(result.errors)}):[/red]")
        for err in result.errors[:3]:
            console.print(f"    [red]x[/red] {err[:80]}")

    for i, brief in enumerate(result.briefs, 1):
        console.print()
        console.print(Panel(
            f"[bold]{brief.title}[/bold]\n\n"
            f"[bold]Qué pasó:[/bold] {brief.que_paso[:200]}...\n\n"
            f"[bold]Por qué importa:[/bold] {brief.por_que_importa[:200]}...\n\n"
            f"[bold]Ángulo LATAM:[/bold] {brief.angulo_latam[:150]}\n\n"
            f"[bold]Hook:[/bold] [italic]\"{brief.hook_tentativo}\"[/italic]\n\n"
            f"[bold]Formato:[/bold] {brief.formato_recomendado.value}  |  "
            f"[bold]CTA:[/bold] {brief.cta_tentativo.value}\n\n"
            f"[bold]Datos clave:[/bold]\n" +
            "\n".join(f"  - {d}" for d in brief.datos_clave[:4]) + "\n\n"
            f"[dim]Slug: {brief.slug}[/dim]",
            title=f"[green]Brief #{i} — Score {brief.signal_score:.0f}[/green]",
            style="green",
        ))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="editorial",
        description="Generate editorial briefs from scored items.",
    )
    parser.add_argument("--property", "-p", required=True)
    parser.add_argument("--items", "-n", type=int, default=None, help="Max briefs to generate")
    parser.add_argument("--min-score", type=float, default=None, help="Min signal score")
    parser.add_argument("--run-id", default=None, help="Signal Scorer run ID")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--log-level", default="WARNING",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--config-dir", type=Path, default=None)

    args = parser.parse_args(argv)
    _setup_logging(args.log_level)

    try:
        agent = EditorialAgent(
            property_name=args.property,
            config_dir=args.config_dir,
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    result = agent.run(
        score_run_id=args.run_id,
        max_items=args.items,
        min_signal_score=args.min_score,
    )

    if args.json_output:
        print(result.model_dump_json(indent=2))
    else:
        _print_result(result)

    return 0


if __name__ == "__main__":
    sys.exit(main())
