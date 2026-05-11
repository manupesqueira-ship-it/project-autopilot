"""Editorial agent — Capa 2, Fase 4.

Converts high-scoring items into full editorial briefs following
the Anexo A template and brand voice rules.
"""

from agents.editorial.agent import EditorialAgent
from agents.editorial.schemas import EditorialBrief, EditorialResult

__all__ = ["EditorialAgent", "EditorialBrief", "EditorialResult"]
