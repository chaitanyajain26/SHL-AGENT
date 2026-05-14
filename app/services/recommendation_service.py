from __future__ import annotations

from app.models.api_models import ChatMessage, ChatResponse
from app.retrieval.retriever import retrieve
from app.utils.helpers import conversation_text
from app.utils.validation import safe_response


def recommend(messages: list[ChatMessage], query_override: str | None = None) -> ChatResponse:
    query = query_override or conversation_text(messages)
    items = retrieve(query, top_k=10)
    if not items:
        return ChatResponse(
            reply="I could not find a grounded SHL catalog match. Please add the role, skills, or assessment type.",
            recommendations=[],
            end_of_conversation=False,
        )
    names = ", ".join(item.name for item in items[:5])
    reply = f"Here are SHL catalog assessments that best match the hiring context: {names}."
    return safe_response(reply, items[:10], done=True)


def refine(messages: list[ChatMessage]) -> ChatResponse:
    response = recommend(messages)
    if response.recommendations:
        return ChatResponse(
            reply=f"I refined the shortlist using your updated constraints. {response.reply}",
            recommendations=response.recommendations,
            end_of_conversation=True,
        )
    return response

