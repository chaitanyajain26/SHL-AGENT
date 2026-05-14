from __future__ import annotations

import re
from app.models.api_models import ChatMessage


WORD_RE = re.compile(r"[a-z0-9+#.]+")


def normalize_text(text: str) -> str:
    return " ".join(text.lower().strip().split())


def tokenize(text: str) -> set[str]:
    return {match.group(0) for match in WORD_RE.finditer(normalize_text(text))}


def latest_user_text(messages: list[ChatMessage]) -> str:
    for message in reversed(messages):
        if message.role == "user":
            return message.content
    return ""


def conversation_text(messages: list[ChatMessage]) -> str:
    return "\n".join(f"{message.role}: {message.content}" for message in messages)


def unique_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        key = normalize_text(value)
        if key and key not in seen:
            seen.add(key)
            result.append(value)
    return result

