from app.agents.graph import agent_graph
from app.models.api_models import ChatMessage


def test_refinement_includes_personality_when_requested():
    response = agent_graph.invoke(
        [
            ChatMessage(role="user", content="Hiring a software engineering manager"),
            ChatMessage(role="assistant", content="Here are SHL catalog assessments."),
            ChatMessage(role="user", content="Actually include personality and leadership tests"),
        ]
    )
    assert response.recommendations
    assert any(item.test_type == "P" for item in response.recommendations)

