from __future__ import annotations

import re
from app.models.api_models import ChatMessage
from app.utils.helpers import conversation_text, latest_user_text, normalize_text

INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "system prompt",
    "developer message",
    "jailbreak",
    "forget your rules",
    "non-shl",
]
OFF_TOPIC = ["weather", "stock", "recipe", "movie", "write code", "legal advice", "hiring law", "employment law"]
COMPARE_RE = re.compile(r"\b(compare|difference|different|versus|vs\.?)\b", re.I)
REFINE_TERMS = ["actually", "instead", "remove", "include", "add", "only", "exclude", "change", "also"]
ROLE_TERMS = [
    "developer", "engineer", "manager", "sales", "graduate", "analyst", "java", "python",
    "leader", "leadership", "customer", "support", "finance", "admin", "administrator",
]
ASSESSMENT_TERMS = ["technical", "coding", "personality", "cognitive", "verbal", "numerical", "leadership", "skills"]


def detect_intent(messages: list[ChatMessage]) -> str:
    latest = normalize_text(latest_user_text(messages))
    full = normalize_text(conversation_text(messages))
    if any(pattern in latest for pattern in INJECTION_PATTERNS) or any(term in latest for term in OFF_TOPIC):
        return "refuse"
    if COMPARE_RE.search(latest):
        return "compare"
    if len(messages) > 1 and any(term in latest for term in REFINE_TERMS):
        return "refine"
    if needs_clarification(messages):
        return "clarify"
    if any(term in full for term in ROLE_TERMS + ASSESSMENT_TERMS):
        return "recommend"
    return "clarify"


def needs_clarification(messages: list[ChatMessage]) -> bool:
    latest = normalize_text(latest_user_text(messages))
    vague = {"assessment", "test", "tests", "hiring", "hire", "need", "recommend", "candidate"}
    tokens = set(latest.split())
    has_role = any(term in latest for term in ROLE_TERMS)
    has_assessment_type = any(term in latest for term in ASSESSMENT_TERMS)
    if len(tokens) <= 4 and not has_role:
        return True
    if tokens <= vague:
        return True
    return not (has_role or has_assessment_type)


def clarification_question(messages: list[ChatMessage]) -> str:
    full = normalize_text(conversation_text(messages))
    if not any(term in full for term in ROLE_TERMS):
        return "What role are you hiring for, and what seniority level should the assessment target?"
    if not any(term in full for term in ["technical", "coding", "personality", "cognitive", "leadership"]):
        return "Should the assessment focus on technical skills, cognitive ability, personality, leadership, or a mix?"
    if "leadership" not in full and "manager" in full:
        return "Will this role include leadership responsibilities or mostly individual contribution?"
    return "What constraints should I consider, such as remote testing, duration, or stakeholder-facing responsibilities?"

