from __future__ import annotations

import re
from app.models.api_models import ChatMessage, ChatResponse
from app.models.catalog_models import CatalogItem
from app.retrieval.retriever import catalog_items, retrieve
from app.utils.helpers import latest_user_text, normalize_text


def _mentioned_items(text: str, catalog: list[CatalogItem]) -> list[CatalogItem]:
    lower = normalize_text(text)
    matches: list[CatalogItem] = []
    for item in catalog:
        name = normalize_text(item.name)
        initials = "".join(part[0] for part in re.findall(r"[A-Za-z0-9]+", item.name) if part)
        keyword_match = any(normalize_text(keyword) in lower for keyword in item.keywords if len(keyword) >= 3)
        if name in lower or (initials and initials.lower() in lower.split()) or keyword_match:
            matches.append(item)
    return matches


def compare(messages: list[ChatMessage]) -> ChatResponse:
    text = latest_user_text(messages)
    catalog = catalog_items()
    items = _mentioned_items(text, catalog)
    if len(items) < 2:
        retrieved = retrieve(text, top_k=6)
        for item in retrieved:
            if item.name not in {existing.name for existing in items}:
                items.append(item)
            if len(items) >= 2:
                break
    if len(items) < 2:
        return ChatResponse(
            reply="I need two SHL assessment names from the catalog to compare them accurately.",
            recommendations=[],
            end_of_conversation=False,
        )
    left, right = items[0], items[1]
    reply = (
        f"{left.name} is a {left.category or left.test_type} assessment focused on {left.description} "
        f"Duration: {left.duration or 'not specified in the local catalog'}. "
        f"{right.name} is a {right.category or right.test_type} assessment focused on {right.description} "
        f"Duration: {right.duration or 'not specified in the local catalog'}. "
        "Use the first when its measured capability matches the role requirements; use the second when that catalog purpose is the stronger fit."
    )
    return ChatResponse(reply=reply, recommendations=[], end_of_conversation=False)
