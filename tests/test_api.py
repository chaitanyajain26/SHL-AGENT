from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_clarification_has_empty_recommendations():
    response = client.post("/chat", json={"messages": [{"role": "user", "content": "I need a test"}]})
    assert response.status_code == 200
    body = response.json()
    assert body["recommendations"] == []
    assert body["end_of_conversation"] is False


def test_recommendation_schema_and_catalog_grounding():
    response = client.post("/chat", json={"messages": [{"role": "user", "content": "Hiring a Java developer"}]})
    assert response.status_code == 200
    body = response.json()
    assert 1 <= len(body["recommendations"]) <= 10
    assert all(item["url"].startswith("https://www.shl.com/products/product-catalog/") for item in body["recommendations"])
    assert any("Java" in item["name"] for item in body["recommendations"])

