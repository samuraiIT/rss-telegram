import re

COMPILED_PATTERNS = [
    re.compile(r"ignore\s+all\s+previous\s+instructions", re.I),
    re.compile(r"reveal\s+your\s+system\s+prompt", re.I),
    re.compile(r"DAN\s*mode", re.I),
    re.compile(r"jailbreak", re.I),
    re.compile(r"<\s*/?\s*system\s*>", re.I),
    re.compile(r"<\s*/?\s*assistant\s*>", re.I),
    re.compile(r"<\s*/?\s*user\s*>", re.I),
]


def sanitize_user_input(text: str, maxlen: int = 500) -> tuple[str, bool]:
    text = (text or "")[:maxlen]
    suspicious = any(pattern.search(text) for pattern in COMPILED_PATTERNS)
    sanitized = text.replace("\x00", " ").replace("\r", " ").strip()
    return sanitized, suspicious
