"""Content Composer agent — Capa 2, Fase 4.

Generates publishable content (carousel, caption, newsletter, reel script)
from editorial briefs.
"""

from agents.content_composer.agent import ContentComposerAgent
from agents.content_composer.schemas import ComposedContent, ComposerOutput

__all__ = ["ContentComposerAgent", "ComposedContent", "ComposerOutput"]
