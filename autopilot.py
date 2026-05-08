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


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python autopilot.py <command> [options]")
        print()
        print("Commands:")
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

    if command == "scan":
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
