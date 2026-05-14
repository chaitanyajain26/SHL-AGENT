from __future__ import annotations

from app.models.api_models import ChatResponse


def refuse() -> ChatResponse:
    return ChatResponse(
        reply="I can help only with SHL assessment discovery, comparison, and refinement using the SHL catalog. Please share the role, skills, or assessment constraints you want to evaluate.",
        recommendations=[],
        end_of_conversation=False,
    )

