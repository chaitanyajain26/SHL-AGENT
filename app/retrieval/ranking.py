from __future__ import annotations

from app.models.catalog_models import CatalogItem
from app.utils.helpers import tokenize


ROLE_BOOSTS = {
    "developer": {"java", "python", "coding", "software", "sql", "javascript"},
    "engineer": {"java", "python", "coding", "software", "sql", "javascript"},
    "manager": {"leadership", "manager", "personality", "opq"},
    "sales": {"sales", "customer", "stakeholder"},
    "graduate": {"graduate", "cognitive", "numerical", "verbal", "inductive"},
}


def keyword_overlap_score(query: str, item: CatalogItem) -> float:
    q_tokens = tokenize(query)
    item_tokens = tokenize(item.search_text)
    if not q_tokens or not item_tokens:
        return 0.0
    return len(q_tokens & item_tokens) / max(len(q_tokens), 1)


def role_relevance_score(query: str, item: CatalogItem) -> float:
    q_tokens = tokenize(query)
    item_tokens = tokenize(item.search_text)
    score = 0.0
    for role, boosts in ROLE_BOOSTS.items():
        if role in q_tokens:
            score += len(boosts & item_tokens) * 0.08
    if "personality" in q_tokens and item.test_type.upper().startswith("P"):
        score += 0.35
    if ("coding" in q_tokens or "developer" in q_tokens) and item.test_type.upper().startswith("K"):
        score += 0.25
    if "leadership" in q_tokens and ("leadership" in item_tokens or item.test_type.upper().startswith("P")):
        score += 0.25
    return score


def rerank(query: str, scored_items: list[tuple[CatalogItem, float]]) -> list[CatalogItem]:
    ranked = sorted(
        scored_items,
        key=lambda pair: pair[1] + keyword_overlap_score(query, pair[0]) + role_relevance_score(query, pair[0]),
        reverse=True,
    )
    return [item for item, _ in ranked]

