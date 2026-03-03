import re
import config


def matches_keywords(text: str) -> bool:
    """Check if text contains any of the configured keywords (case-insensitive)."""
    text_lower = text.lower()
    for keyword in config.KEYWORDS:
        if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
            return True
    return False
