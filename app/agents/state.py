from __future__ import annotations

from typing import Literal, TypedDict
from app.models.api_models import ChatMessage, ChatResponse
from app.models.catalog_models import CatalogItem

Intent = Literal["clarify", "recommend", "refine", "compare", "refuse"]


class AgentState(TypedDict, total=False):
    messages: list[ChatMessage]
    query: str
    intent: Intent
    retrieved: list[CatalogItem]
    reply: str
    response: ChatResponse

