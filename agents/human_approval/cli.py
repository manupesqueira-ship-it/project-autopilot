"""CLI entry point for Human Approval agent.

Supports two modes:
1. Interactive: shows each content piece, asks for decision (default)
2. Auto-approve: approves compliance-passing items, rejects blocked (--auto-approve)
"""

from __future__ import annotations

import argparse
import io
import json
import logging
import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from agents.human_approval.agent import HumanApprovalAgent
from agents.human_approval.schemas import ApprovalOutput, Decision


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _run_interactive(agent: HumanApprovalAgent) -> ApprovalOutput:
    """Interactive approval flow — prompts user for each item."""
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    from rich.console import Console
    from rich.panel import Panel

    console = Console()

    compliance_data = agent._load_compliance_output()
    compliance_run = compliance_data.get("run_id", "unknown")
    results = compliance_data.get("results", [])

    # Also load composer content for preview
    composer_data = agent._load_composer_output_for_compliance(compliance_data)
    content_by_slug: dict[str, dict] = {}
    for c in composer_data.get("content", []):
        content_by_slug[c.get("brief_slug", "")] = c

    console.print()
    console.print(Panel(
        f"[bold]Human Approval[/bold]\n"
        f"Property: [cyan]{agent.property_name}[/cyan]  |  "
        f"Compliance run: [dim]{compliance_run}[/dim]\n"
        f"Items to review: {len(results)}",
        style="blue",
    ))

    from agents.human_approval.schemas import ContentDecision
    decisions = []

    for i, result in enumerate(results, 1):
        slug = result.get("brief_slug", "unknown")
        title = result.get("brief_title", "unknown")
        content_type = result.get("content_type", "unknown")
        verdict = result.get("verdict", "blocked")
        summary = result.get("summary", "")
        blocks = result.get("blocks", [])
        warnings = result.get("warnings", [])

        # Verdict color
        if verdict == "approved":
            v_style = "bold green"
        elif verdict == "approved_with_warnings":
            v_style = "yellow"
        else:
            v_style = "bold red"

        console.print()
        console.print(f"  [{v_style}]#{i} {verdict.upper()}[/{v_style}] "
                       f"[cyan]{content_type}[/cyan] — {title}")
        console.print(f"  [italic]{summary}[/italic]")

        if blocks:
            for b in blocks:
                console.print(f"    [red]BLOCK:[/red] {b}")
        if warnings:
            for w in warnings:
                console.print(f"    [yellow]WARN:[/yellow] {w}")

        # Show content preview
        content = content_by_slug.get(slug, {})
        if content_type == "carousel_caption":
            preview = content.get("carousel", {}).get("caption", {}).get("full_text", "")
        elif content_type == "newsletter":
            preview = content.get("newsletter", {}).get("full_text", "")[:300]
        elif content_type == "reel_script":
            rs = content.get("reel_script", {})
            preview = f"HOOK: {rs.get('hook', '')}\nCTA: {rs.get('cta', '')}" if rs else ""
        else:
            preview = ""

        if preview:
            console.print(Panel(preview[:250], title="[dim]Preview[/dim]", style="dim"))

        # Prompt for decision
        console.print("  [bold]Decision:[/bold] (a)pprove  (r)eject  (d)efer  (q)uit")
        try:
            choice = input("  > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            choice = "q"

        if choice == "q":
            # Defer remaining
            for remaining in results[i:]:
                decisions.append(ContentDecision(
                    brief_slug=remaining.get("brief_slug", ""),
                    brief_title=remaining.get("brief_title", ""),
                    content_type=remaining.get("content_type", ""),
                    decision=Decision.DEFERRED,
                    notes="Session ended by user",
                ))
            break

        decision_map = {
            "a": Decision.APPROVED,
            "r": Decision.REJECTED,
            "d": Decision.DEFERRED,
        }
        decision = decision_map.get(choice, Decision.DEFERRED)

        notes = ""
        if decision == Decision.REJECTED:
            console.print("  [dim]Reason (optional, enter to skip):[/dim]")
            try:
                notes = input("  > ").strip()
            except (EOFError, KeyboardInterrupt):
                notes = ""

        decisions.append(ContentDecision(
            brief_slug=slug,
            brief_title=title,
            content_type=content_type,
            decision=decision,
            notes=notes or f"Interactive decision: {decision.value}",
        ))

    from agents.human_approval.schemas import ApprovalStats
    from datetime import datetime, timezone
    stats = ApprovalStats(
        items_reviewed=len(decisions),
        items_approved=sum(1 for d in decisions if d.decision == Decision.APPROVED),
        items_rejected=sum(1 for d in decisions if d.decision == Decision.REJECTED),
        items_deferred=sum(1 for d in decisions if d.decision == Decision.DEFERRED),
    )

    output = ApprovalOutput(
        run_id=agent._generate_run_id(),
        compliance_run_id=compliance_run,
        property=agent.property_name,
        decisions=decisions,
        stats=stats,
    )

    agent._save_output(output)
    _print_summary(output, console)
    return output


def _print_summary(output: ApprovalOutput, console=None) -> None:
    if console is None:
        from rich.console import Console
        console = Console()

    s = output.stats
    console.print()
    console.print(
        f"  [bold]Done:[/bold] "
        f"[green]{s.items_approved} approved[/green]  |  "
        f"[red]{s.items_rejected} rejected[/red]  |  "
        f"[dim]{s.items_deferred} deferred[/dim]"
    )


def _print_auto_result(output: ApprovalOutput) -> None:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    from rich.console import Console
    from rich.panel import Panel

    console = Console()
    console.print()

    s = output.stats
    console.print(Panel(
        f"[bold]Human Approval (auto-mode)[/bold]\n"
        f"Property: [cyan]{output.property}[/cyan]\n"
        f"[green]Approved: {s.items_approved}[/green]  |  "
        f"[red]Rejected: {s.items_rejected}[/red]  |  "
        f"[dim]Deferred: {s.items_deferred}[/dim]",
        style="blue",
    ))

    for d in output.decisions:
        if d.decision == Decision.APPROVED:
            style = "green"
        elif d.decision == Decision.REJECTED:
            style = "red"
        else:
            style = "dim"
        console.print(f"  [{style}]{d.decision.value.upper()}[/{style}] "
                       f"[cyan]{d.content_type}[/cyan] — {d.brief_title[:50]}")
        if d.notes and d.decision == Decision.REJECTED:
            console.print(f"    [dim]{d.notes[:80]}[/dim]")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="human_approval",
        description="Review and approve/reject content before publication.",
    )
    parser.add_argument("--property", "-p", required=True)
    parser.add_argument("--auto-approve", action="store_true",
                        help="Auto-approve compliance-passing items, reject blocked")
    parser.add_argument("--run-id", default=None, help="Compliance run ID")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--log-level", default="WARNING",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--config-dir", type=Path, default=None)

    args = parser.parse_args(argv)
    _setup_logging(args.log_level)

    try:
        agent = HumanApprovalAgent(property_name=args.property, config_dir=args.config_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.auto_approve or args.json_output:
        output = agent.run(compliance_run_id=args.run_id, auto_approve=args.auto_approve)
        if args.json_output:
            print(output.model_dump_json(indent=2))
        else:
            _print_auto_result(output)
    else:
        output = _run_interactive(agent)

    return 0


if __name__ == "__main__":
    sys.exit(main())
