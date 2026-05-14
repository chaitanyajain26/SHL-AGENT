from __future__ import annotations

import json
import pickle
from pathlib import Path
import numpy as np

from app.config import get_settings
from app.models.catalog_models import CatalogItem
from app.retrieval.embeddings import EmbeddingModel
from app.utils.helpers import tokenize
from app.utils.logger import get_logger

logger = get_logger(__name__)


def load_catalog(path: Path | None = None) -> list[CatalogItem]:
    catalog_path = path or get_settings().catalog_path
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    return [CatalogItem.model_validate(item) for item in data]


class VectorStore:
    def __init__(self, catalog: list[CatalogItem] | None = None) -> None:
        self.settings = get_settings()
        self.catalog = catalog or load_catalog()
        self.embedder = EmbeddingModel()
        self.index = None
        self.matrix: np.ndarray | None = None
        self._load_or_build()

    def _load_or_build(self) -> None:
        try:
            self._load()
        except Exception as exc:
            logger.warning("Vector index unavailable, rebuilding: %s", exc)
            self.build()

    def _load(self) -> None:
        meta_path = self.settings.faiss_dir / "catalog.pkl"
        if not meta_path.exists():
            raise FileNotFoundError(meta_path)
        with meta_path.open("rb") as handle:
            self.catalog = pickle.load(handle)
        try:
            import faiss
            self.index = faiss.read_index(str(self.settings.faiss_dir / "index.faiss"))
        except Exception:
            matrix_path = self.settings.faiss_dir / "matrix.npy"
            self.matrix = np.load(matrix_path)

    def build(self) -> None:
        self.settings.faiss_dir.mkdir(parents=True, exist_ok=True)
        texts = [item.search_text for item in self.catalog]
        vectors = self.embedder.encode(texts)
        try:
            import faiss
            index = faiss.IndexFlatIP(vectors.shape[1])
            index.add(vectors)
            faiss.write_index(index, str(self.settings.faiss_dir / "index.faiss"))
            self.index = index
            self.matrix = None
        except Exception as exc:
            logger.warning("FAISS unavailable, storing numpy matrix fallback: %s", exc)
            self.matrix = vectors
            np.save(self.settings.faiss_dir / "matrix.npy", vectors)
        with (self.settings.faiss_dir / "catalog.pkl").open("wb") as handle:
            pickle.dump(self.catalog, handle)

    def search(self, query: str, top_k: int = 10) -> list[tuple[CatalogItem, float]]:
        if not query.strip():
            return []
        query_vector = self.embedder.encode([query])
        if self.index is not None:
            scores, indices = self.index.search(query_vector, min(top_k, len(self.catalog)))
            return [(self.catalog[int(idx)], float(score)) for idx, score in zip(indices[0], scores[0]) if idx >= 0]
        if self.matrix is not None:
            scores = self.matrix @ query_vector[0]
            order = np.argsort(scores)[::-1][:top_k]
            return [(self.catalog[int(idx)], float(scores[int(idx)])) for idx in order]
        query_tokens = tokenize(query)
        scored = []
        for item in self.catalog:
            item_tokens = tokenize(item.search_text)
            score = len(query_tokens & item_tokens) / max(len(query_tokens), 1)
            scored.append((item, score))
        return sorted(scored, key=lambda pair: pair[1], reverse=True)[:top_k]


def build_index() -> None:
    store = VectorStore(load_catalog())
    store.build()
    logger.info("Built vector index with %d catalog records", len(store.catalog))


if __name__ == "__main__":
    build_index()

