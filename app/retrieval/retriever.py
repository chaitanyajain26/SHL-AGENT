from __future__ import annotations

from functools import lru_cache
from app.models.catalog_models import CatalogItem
from app.retrieval.ranking import rerank
from app.retrieval.vector_store import VectorStore, load_catalog


@lru_cache
def get_vector_store() -> VectorStore:
    return VectorStore()


def retrieve(query: str, top_k: int = 10) -> list[CatalogItem]:
    scored = get_vector_store().search(query, top_k=max(top_k * 2, 10))
    return rerank(query, scored)[:top_k]


def catalog_items() -> list[CatalogItem]:
    return load_catalog()

