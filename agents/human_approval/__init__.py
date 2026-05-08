"""Human Approval agent — Capa 2, Fase 4.

Interactive CLI for reviewing, approving, or rejecting content
before publication. Human-in-the-loop step, no LLM.
"""

from agents.human_approval.agent import HumanApprovalAgent
from agents.human_approval.schemas import ApprovalOutput, ContentDecision

__all__ = ["HumanApprovalAgent", "ApprovalOutput", "ContentDecision"]
