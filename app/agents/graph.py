from __future__ import annotations

from app.agents.nodes import (
    analyze_node,
    clarify_node,
    compare_node,
    formatter_node,
    recommend_node,
    refine_node,
    refuse_node,
    route_node,
)
from app.agents.state import AgentState
from app.models.api_models import ChatMessage, ChatResponse


def _next_node(state: AgentState) -> str:
    return {
        "clarify": "clarify",
        "recommend": "recommend",
        "refine": "refine",
        "compare": "compare",
        "refuse": "refuse",
    }.get(state.get("intent", "clarify"), "clarify")


class AgentGraph:
    def __init__(self) -> None:
        self._graph = None
        try:
            from langgraph.graph import END, START, StateGraph
            graph = StateGraph(AgentState)
            graph.add_node("analyze", analyze_node)
            graph.add_node("route", route_node)
            graph.add_node("clarify", clarify_node)
            graph.add_node("recommend", recommend_node)
            graph.add_node("refine", refine_node)
            graph.add_node("compare", compare_node)
            graph.add_node("refuse", refuse_node)
            graph.add_node("format", formatter_node)
            graph.add_edge(START, "analyze")
            graph.add_edge("analyze", "route")
            graph.add_conditional_edges("route", _next_node)
            for node in ["clarify", "recommend", "refine", "compare", "refuse"]:
                graph.add_edge(node, "format")
            graph.add_edge("format", END)
            self._graph = graph.compile()
        except Exception:
            self._graph = None

    def invoke(self, messages: list[ChatMessage]) -> ChatResponse:
        state: AgentState = {"messages": messages}
        if self._graph is not None:
            result = self._graph.invoke(state)
            return ChatResponse.model_validate(result["response"])
        state = analyze_node(state)
        state = route_node(state)
        intent = state["intent"]
        state = {
            "clarify": clarify_node,
            "recommend": recommend_node,
            "refine": refine_node,
            "compare": compare_node,
            "refuse": refuse_node,
        }[intent](state)
        state = formatter_node(state)
        return ChatResponse.model_validate(state["response"])


agent_graph = AgentGraph()

