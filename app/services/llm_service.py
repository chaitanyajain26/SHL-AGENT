from __future__ import annotations

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._llm = None
        if self.settings.groq_api_key:
            try:
                from langchain_groq import ChatGroq
                self._llm = ChatGroq(
                    api_key=self.settings.groq_api_key,
                    model=self.settings.model_name,
                    temperature=0.1,
                    max_tokens=500,
                )
            except Exception as exc:
                logger.warning("Groq LLM unavailable; deterministic responses remain active: %s", exc)

    def invoke(self, prompt: str) -> str | None:
        if self._llm is None:
            return None
        try:
            return str(self._llm.invoke(prompt).content)
        except Exception as exc:
            logger.warning("LLM call failed: %s", exc)
            return None

