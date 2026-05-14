from __future__ import annotations

from app.models.api_models import ChatResponse, Recommendation
from app.models.catalog_models import CatalogItem


def catalog_lookup(catalog: list[CatalogItem]) -> dict[str, CatalogItem]:
    return {item.name.casefold(): item for item in catalog}


def recommendations_from_catalog(items: list[CatalogItem], limit: int = 10) -> list[Recommendation]:
    recommendations: list[Recommendation] = []
    seen: set[str] = set()
    for item in items:
        key = item.name.casefold()
        if key in seen:
            continue
        seen.add(key)
        recommendations.append(Recommendation(name=item.name, url=item.url, test_type=item.test_type))
        if len(recommendations) >= limit:
            break
    return recommendations


def safe_response(reply: str, items: list[CatalogItem] | None = None, done: bool = False) -> ChatResponse:
    recommendations = recommendations_from_catalog(items or [])
    return ChatResponse(reply=reply, recommendations=recommendations, end_of_conversation=bool(done and recommendations))

