from __future__ import annotations

from fastapi import APIRouter, HTTPException
from app.agents.graph import agent_graph
from app.models.api_models import ChatRequest, ChatResponse
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        return agent_graph.invoke(request.messages)
    except Exception as exc:
        logger.exception("Chat request failed")
        raise HTTPException(status_code=500, detail="The recommender could not process this request safely.") from exc

