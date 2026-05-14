from __future__ import annotations

from app.agents.router import clarification_question, detect_intent
from app.agents.state import AgentState
from app.models.api_models import ChatResponse
from app.retrieval.retriever import retrieve
from app.services.comparison_service import compare
from app.services.recommendation_service import recommend, refine
from app.services.refusal_service import refuse
from app.utils.helpers import conversation_text


OFFTOPIC_KEYWORDS = [
    "legal",
    "lawsuit",
    "politics",
    "medical",
    "investment",
    "crypto",
    "religion",
    "dating",
]


IMPORTANT_ROLE_KEYWORDS = [
    "developer",
    "engineer",
    "manager",
    "analyst",
    "sales",
    "marketing",
    "java",
    "python",
    "sql",
    "frontend",
    "backend",
    "fullstack",
]


IMPORTANT_CONTEXT_KEYWORDS = [
    "senior",
    "junior",
    "mid",
    "experience",
    "years",
    "personality",
    "cognitive",
    "communication",
    "leadership",
]


def latest_user_message(messages):
    user_messages = [
        m.content for m in messages
        if m.role == "user"
    ]

    return user_messages[-1] if user_messages else ""


def needs_clarification(query: str) -> bool:
    """
    Detects whether user query is too vague.
    """

    role_matches = sum(
        1 for keyword in IMPORTANT_ROLE_KEYWORDS if keyword in query
    )

    context_matches = sum(
        1 for keyword in IMPORTANT_CONTEXT_KEYWORDS if keyword in query
    )

    # If role is missing OR context is missing -> clarify
    if role_matches == 0:
        return True

    if context_matches == 0:
        return True

    return False


def is_offtopic(query: str) -> bool:
    """
    Detect unsupported queries.
    """
    return any(keyword in query for keyword in OFFTOPIC_KEYWORDS)


def is_comparison(query: str) -> bool:
    """
    Detect comparison requests.
    """
    comparison_terms = [
        "compare",
        "difference between",
        "vs",
        "versus",
    ]

    return any(term in query for term in comparison_terms)


def analyze_node(state: AgentState) -> AgentState:
    state["query"] = conversation_text(state["messages"])
    return state


def route_node(state: AgentState) -> AgentState:
    """
    Enhanced intelligent routing.
    """

    latest_query = latest_user_message(state["messages"])

    # Refusal
    if is_offtopic(latest_query):
        state["intent"] = "refuse"
        return state

    # Comparison
    if is_comparison(latest_query):
        state["intent"] = "compare"
        return state

    # Refinement
    refinement_terms = [
        "also",
        "add",
        "include",
        "instead",
        "change",
        "update",
        "remove",
    ]

    if any(term in latest_query for term in refinement_terms):
        state["intent"] = "refine"
        return state

    # Clarification
    if needs_clarification(latest_query):
        state["intent"] = "clarify"
        return state

    # Recommendation
    state["intent"] = "recommend"
    return state


def clarify_node(state: AgentState) -> AgentState:
    """
    Ask intelligent clarification questions.
    """

    custom_question = (
        "Could you share the role seniority level, "
        "required skills, and whether you also want "
        "personality or cognitive assessments?"
    )

    state["response"] = ChatResponse(
        reply=custom_question,
        recommendations=[],
        end_of_conversation=False,
    )

    return state


def retrieve_node(state: AgentState) -> AgentState:
    """
    Retrieve relevant catalog records.
    """

    state["retrieved"] = retrieve(
        state.get("query", ""),
        top_k=10,
    )

    return state


def recommend_node(state: AgentState) -> AgentState:
    """
    Generate recommendation response.
    """

    state["response"] = recommend(state["messages"])

    return state


def refine_node(state: AgentState) -> AgentState:
    """
    Refine recommendations when constraints change.
    """

    state["response"] = refine(state["messages"])

    return state


def compare_node(state: AgentState) -> AgentState:
    """
    Compare SHL assessments.
    """

    state["response"] = compare(state["messages"])

    return state


def refuse_node(state: AgentState) -> AgentState:
    """
    Refuse unsupported requests.
    """

    state["response"] = ChatResponse(
        reply=(
            "I can only help with SHL assessment "
            "recommendations, refinements, and comparisons."
        ),
        recommendations=[],
        end_of_conversation=True,
    )

    return state


def formatter_node(state: AgentState) -> AgentState:
    """
    Ensure schema-safe response.
    """

    response = state.get("response")

    if response is None:
        response = ChatResponse(
            reply=(
                "Please share the hiring role, "
                "required skills, and assessment needs."
            ),
            recommendations=[],
            end_of_conversation=False,
        )

    state["response"] = ChatResponse.model_validate(response)

    return state