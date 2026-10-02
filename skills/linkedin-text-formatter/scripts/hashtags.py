"""Rule-based LinkedIn hashtag suggestions from post content."""

from __future__ import annotations

import re

# (regex, hashtag, priority) — higher priority wins when trimming to max count
HASHTAG_RULES: list[tuple[str, str, int]] = [
    (r"\baccountant|\baccounting\b|\bauditors?\b|\bbookkeeping\b|\bworkpapers?\b", "#Accounting", 10),
    (r"\bfinance teams?\b|\bfinancial\b|\bERP\b|\btax research\b", "#Finance", 9),
    (r"\bAI tools?\b|\bartificial intelligence\b|\bAI fits\b|\bgenerative AI\b|\bAI products?\b", "#AI", 10),
    (r"\bworkflow fragmentation\b|\bworkflow\b|\bcontext-switching\b|\binformation retrieval\b", "#WorkflowAutomation", 8),
    (r"\bprofessional services\b|\bconsultants?\b", "#ProfessionalServices", 8),
    (r"\bproduct manager\b|\bPM at\b|\bPM\b|\bproduct management\b", "#ProductManagement", 8),
    (r"\boperations professional|\boperations teams?\b", "#Operations", 7),
    (r"\bSaaS\b|\bB2B\b|\benterprise software\b", "#SaaS", 6),
    (r"\bstartup\b|\bfounder\b|\bbuild in public\b", "#Startup", 6),
    (r"\bproductivity\b|\befficiency\b", "#Productivity", 5),
    # Example product-brand rule: replace "ExampleProduct" with your own product name.
    (r"\bExampleProduct\b", "#ExampleProduct", 4),
    (r"\bmarketing\b|\bgrowth\b|\bcontent strategy\b", "#Marketing", 5),
    (r"\bsales\b|\brevenue\b|\bpipeline\b", "#Sales", 5),
    (r"\bengineering\b|\bdeveloper\b|\bsoftware\b", "#Engineering", 5),
    (r"\bdesign\b|\bUX\b|\buser experience\b", "#Design", 5),
    (r"\bdata\b|\banalytics\b|\binsights\b", "#DataAnalytics", 5),
    (r"\bleadership\b|\bmanagement\b|\bexecutive\b", "#Leadership", 4),
    (r"\bhiring\b|\bcareer\b|\bjob search\b", "#Careers", 4),
    (r"\bremote work\b|\bhybrid work\b", "#FutureOfWork", 4),
]

FALLBACK_TAGS = ["#FutureOfWork", "#Innovation", "#Leadership"]


def _normalize_tag(tag: str) -> str:
    tag = tag.strip()
    if not tag.startswith("#"):
        tag = f"#{tag}"
    # LinkedIn tags: strip spaces, keep letters/numbers/underscore
    body = re.sub(r"[^\w]", "", tag[1:], flags=re.UNICODE)
    return f"#{body}" if body else ""


def suggest_hashtags(text: str, existing: list[str] | None = None, *, max_count: int = 5) -> list[str]:
    """Return up to max_count hashtags: user-provided first, then content-based suggestions."""
    if max_count <= 0:
        return []

    existing = existing or []
    result: list[str] = []
    seen: set[str] = set()

    for raw in existing:
        tag = _normalize_tag(raw)
        key = tag.lower()
        if tag and key not in seen:
            seen.add(key)
            result.append(tag)

    lower = text.lower()
    scored: dict[str, int] = {}
    for pattern, tag, priority in HASHTAG_RULES:
        if re.search(pattern, lower, re.I):
            norm = _normalize_tag(tag)
            key = norm.lower()
            scored[key] = max(scored.get(key, 0), priority)

    for tag_key in sorted(scored, key=lambda k: (-scored[k], k)):
        if len(result) >= max_count:
            break
        if tag_key not in seen:
            seen.add(tag_key)
            # recover proper casing from rules
            display = tag_key if tag_key.startswith("#") else f"#{tag_key}"
            for _, rule_tag, _ in HASHTAG_RULES:
                if _normalize_tag(rule_tag).lower() == tag_key:
                    display = _normalize_tag(rule_tag)
                    break
            result.append(display)

    if len(result) < min(3, max_count):
        for fb in FALLBACK_TAGS:
            if len(result) >= max_count:
                break
            key = fb.lower()
            if key not in seen:
                seen.add(key)
                result.append(fb)

    return result[:max_count]
