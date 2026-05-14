from __future__ import annotations

import hashlib
import numpy as np
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingModel:
    def __init__(self) -> None:
        self.model_name = get_settings().embedding_model
        self._model = None
        try:
            from sentence_transformers import SentenceTransformer
            kwargs = {} if get_settings().allow_model_download else {"local_files_only": True}
            self._model = SentenceTransformer(self.model_name, **kwargs)
            self.dimension = int(self._model.get_sentence_embedding_dimension())
        except Exception as exc:
            logger.warning("SentenceTransformer unavailable, using deterministic fallback embeddings: %s", exc)
            self.dimension = 384

    def encode(self, texts: list[str]) -> np.ndarray:
        if self._model is not None:
            vectors = self._model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
            return np.asarray(vectors, dtype="float32")
        return np.vstack([self._fallback_vector(text) for text in texts]).astype("float32")

    def _fallback_vector(self, text: str) -> np.ndarray:
        vector = np.zeros(self.dimension, dtype="float32")
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimension
            vector[index] += 1.0
        norm = np.linalg.norm(vector)
        return vector / norm if norm else vector
