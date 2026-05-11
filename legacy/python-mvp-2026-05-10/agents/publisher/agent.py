"""Publisher Agent — prepares approved content for publication.

Takes approved content and exports it as ready-to-publish files:
- Instagram: caption.txt + slides.md (copy-paste to Canva/Buffer)
- Newsletter: newsletter.md (copy-paste to Beehiiv)
- Reel: reel_script.md (for recording)

In Fase 4, publishing is "assisted" — the agent prepares files,
the human does the actual posting. Direct API publishing (Meta Graph,
Beehiiv API) comes later when business accounts are set up.

Usage:
    autopilot publish --property ai-brief-latam
"""

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from agents.publisher.schemas import (
    PublishableItem,
    PublishChannel,
    PublisherOutput,
    PublisherStats,
    PublishStatus,
)

logger = logging.getLogger(__name__)


class PublisherAgent:
    """Exports approved content as ready-to-publish files."""

    def __init__(self, property_name: str, config_dir: Path | None = None):
        self.property_name = property_name
        self.config_dir = config_dir or self._find_project_root()
        self.agent_config = self._load_agent_config()

    def run(self, approval_run_id: str | None = None) -> PublisherOutput:
        """Export approved content to publish-ready files.

        Args:
            approval_run_id: Specific Approval run. If None, uses latest.
        """
        run_id = self._generate_run_id()

        approval_data = self._load_approval_output(approval_run_id)
        approval_run = approval_data.get("run_id", "unknown")
        decisions = approval_data.get("decisions", [])

        # Find the composer output to get actual content
        composer_data = self._find_composer_output(approval_data)

        # Filter to approved items only
        approved = [d for d in decisions if d.get("decision") == "approved"]
        logger.info(f"Publishing {len(approved)} approved items from '{approval_run}'")

        # Group by brief slug
        approved_slugs = {d.get("brief_slug") for d in approved}
        approved_types = {}
        for d in approved:
            slug = d.get("brief_slug", "")
            approved_types.setdefault(slug, set()).add(d.get("content_type", ""))

        # Export
        export_dir = self.config_dir / "agents" / "publisher" / "export" / run_id
        export_dir.mkdir(parents=True, exist_ok=True)

        items: list[PublishableItem] = []
        files_exported = 0
        errors: list[str] = []

        content_list = composer_data.get("content", [])
        for content in content_list:
            slug = content.get("brief_slug", "")
            if slug not in approved_slugs:
                continue

            title = content.get("brief_title", "unknown")
            types = approved_types.get(slug, set())
            slug_dir = export_dir / slug
            slug_dir.mkdir(parents=True, exist_ok=True)

            has_ig = False
            has_nl = False

            # Export caption
            if "carousel_caption" in types:
                caption = content.get("carousel", {}).get("caption", {}).get("full_text", "")
                if caption:
                    (slug_dir / "caption.txt").write_text(caption, encoding="utf-8")
                    files_exported += 1
                    has_ig = True

                # Export slides
                slides = content.get("carousel", {}).get("slides", [])
                if slides:
                    slides_text = "\n\n---\n\n".join(
                        f"SLIDE {s.get('slide_number', i+1)}\n"
                        f"{s.get('headline', '')}\n\n"
                        f"{s.get('body', '')}\n\n"
                        f"[Visual: {s.get('visual_direction', '')}]"
                        for i, s in enumerate(slides)
                    )
                    (slug_dir / "slides.md").write_text(slides_text, encoding="utf-8")
                    files_exported += 1

            # Export newsletter
            if "newsletter" in types:
                nl_text = content.get("newsletter", {}).get("full_text", "")
                if nl_text:
                    (slug_dir / "newsletter.md").write_text(nl_text, encoding="utf-8")
                    files_exported += 1
                    has_nl = True

            # Export reel script
            if "reel_script" in types:
                rs = content.get("reel_script")
                if rs and isinstance(rs, dict):
                    script = (
                        f"REEL SCRIPT ({rs.get('estimated_duration_seconds', 30)}s)\n\n"
                        f"[HOOK · 0-3s]\n{rs.get('hook', '')}\n\n"
                        f"[BODY · 3-22s]\n{rs.get('body', '')}\n\n"
                        f"POR QUÉ IMPORTA:\n{rs.get('por_que_importa', '')}\n\n"
                        f"[CLOSE · 22-30s]\n{rs.get('close', '')}\n\n"
                        f"CTA: {rs.get('cta', '')}\n\n"
                        f"ON-SCREEN TEXT:\n" +
                        "\n".join(f"  - {t}" for t in rs.get("on_screen_text", []))
                    )
                    (slug_dir / "reel_script.md").write_text(script, encoding="utf-8")
                    files_exported += 1
                    has_ig = True

            # Determine channel
            if has_ig and has_nl:
                channel = PublishChannel.BOTH
            elif has_nl:
                channel = PublishChannel.NEWSLETTER
            else:
                channel = PublishChannel.INSTAGRAM

            items.append(PublishableItem(
                brief_slug=slug,
                brief_title=title,
                channel=channel,
                status=PublishStatus.READY,
                caption_file=f"{slug}/caption.txt" if has_ig else "",
                slides_file=f"{slug}/slides.md" if has_ig else "",
                newsletter_file=f"{slug}/newsletter.md" if has_nl else "",
                reel_file=f"{slug}/reel_script.md" if "reel_script" in types else "",
            ))

        stats = PublisherStats(
            items_processed=len(approved),
            items_ready=len(items),
            items_instagram=sum(1 for i in items if i.channel in (PublishChannel.INSTAGRAM, PublishChannel.BOTH)),
            items_newsletter=sum(1 for i in items if i.channel in (PublishChannel.NEWSLETTER, PublishChannel.BOTH)),
            files_exported=files_exported,
        )

        output = PublisherOutput(
            run_id=run_id,
            approval_run_id=approval_run,
            property=self.property_name,
            items=items,
            stats=stats,
            export_dir=str(export_dir),
            errors=errors,
        )

        self._save_output(output, export_dir)
        logger.info(f"Exported {files_exported} files for {len(items)} items to {export_dir}")
        return output

    def _load_approval_output(self, run_id: str | None = None) -> dict:
        evidence_dir = self.config_dir / "agents" / "human_approval" / "evidence"
        if not evidence_dir.exists():
            raise FileNotFoundError(f"No Approval evidence at {evidence_dir}.")
        if run_id:
            run_dir = evidence_dir / run_id
        else:
            runs = sorted([r for r in evidence_dir.iterdir() if r.is_dir()], reverse=True)
            if not runs:
                raise FileNotFoundError("No Approval runs found.")
            run_dir = runs[0]
        output_file = run_dir / "approval_output.json"
        if not output_file.exists():
            raise FileNotFoundError(f"Approval output not found: {output_file}")
        with open(output_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _find_composer_output(self, approval_data: dict) -> dict:
        """Walk back through the chain to find the composer output."""
        # approval -> compliance -> composer
        compliance_run = approval_data.get("compliance_run_id", "")
        if not compliance_run:
            return {}

        comp_file = (
            self.config_dir / "agents" / "compliance" / "evidence"
            / compliance_run / "compliance_output.json"
        )
        if not comp_file.exists():
            return {}

        with open(comp_file, "r", encoding="utf-8") as f:
            compliance_data = json.load(f)

        composer_run = compliance_data.get("composer_run_id", "")
        if not composer_run:
            return {}

        composer_file = (
            self.config_dir / "agents" / "content_composer" / "evidence"
            / composer_run / "composer_output.json"
        )
        if not composer_file.exists():
            return {}

        with open(composer_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_output(self, output: PublisherOutput, export_dir: Path) -> None:
        output_path = export_dir / "publisher_output.json"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output.model_dump_json(indent=2))
        logger.info(f"Saved manifest to {output_path}")

    def _load_agent_config(self) -> dict[str, Any]:
        config_path = self.config_dir / "agents" / "publisher" / "config.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Agent config not found: {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _generate_run_id(self) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        return f"{ts}_{self.property_name}_publish"

    @staticmethod
    def _find_project_root() -> Path:
        current = Path(__file__).resolve().parent
        for _ in range(10):
            if (current / "MASTER_PLAN.md").exists():
                return current
            parent = current.parent
            if parent == current:
                break
            current = parent
        raise FileNotFoundError("Could not find project root.")
