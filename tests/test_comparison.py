from app.agents.graph import agent_graph
from app.models.api_models import ChatMessage


def test_comparison_returns_no_recommendations():
    response = agent_graph.invoke([ChatMessage(role="user", content="What is the difference between OPQ and GSA?")])
    assert response.recommendations == []
    assert "Occupational Personality Questionnaire" in response.reply
    assert "General Ability Screen" in response.reply

