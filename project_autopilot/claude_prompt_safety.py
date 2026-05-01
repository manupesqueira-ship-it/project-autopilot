from __future__ import annotations

import re
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class PromptSafetyResult:
    sanitized_text: str
    redaction_count: int
    blocked_reason: str
    findings: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


SECRET_PATTERNS: list[tuple[str, str]] = [
    ("anthropic_key", r"\bsk-ant-[A-Za-z0-9_\-]{10,}\b"),
    ("generic_openai_style_key", r"\bsk-[A-Za-z0-9_\-]{12,}\b"),
    ("supabase_secret", r"\bsb_secret_[A-Za-z0-9_\-]{8,}\b"),
    ("supabase_publishable", r"\bsb_publishable_[A-Za-z0-9_\-]{8,}\b"),
    ("supabase_service_role_assignment", r"\bSUPABASE_SERVICE_ROLE_KEY\s*=\s*[^\s]+"),
    ("anthropic_assignment", r"\bANTHROPIC_API_KEY\s*=\s*[^\s]+"),
    ("openai_assignment", r"\bOPENAI_API_KEY\s*=\s*[^\s]+"),
    ("service_role_assignment", r"\bservice_role\s*[:=]\s*[^\s]+"),
    ("access_token", r"\baccess_token\s*[:=]\s*[^\s]+"),
    ("refresh_token", r"\brefresh_token\s*[:=]\s*[^\s]+"),
    ("jwt_like_token", r"\beyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{10,}\b"),
]


def sanitize_prompt_text(text: str, max_redactions: int = 50) -> PromptSafetyResult:
    sanitized = text
    redactions = 0
    findings: list[str] = []
    for label, pattern in SECRET_PATTERNS:
        sanitized, count = re.subn(pattern, f"[REDACTED:{label}]", sanitized, flags=re.IGNORECASE)
        if count:
            redactions += count
            findings.append(label)

    blocked_reason = ""
    if redactions > max_redactions:
        blocked_reason = "Too many secret-like values were present to safely send this prompt."

    return PromptSafetyResult(
        sanitized_text=sanitized,
        redaction_count=redactions,
        blocked_reason=blocked_reason,
        findings=sorted(set(findings)),
    )


def self_test() -> bool:
    sample = (
        "ANTHROPIC_API_KEY=sk-ant-exampleSecretValue access_token=abc123 "
        "jwt eyJabcdefghijklmnopqrstuvwxyz.ABCDEFGHIJKLMNOPQRSTUVWXYZ.1234567890"
    )
    result = sanitize_prompt_text(sample)
    return result.redaction_count >= 2 and "sk-ant-exampleSecretValue" not in result.sanitized_text
