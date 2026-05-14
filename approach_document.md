# Approach Document

## Design Decisions

The system is a stateless conversational retrieval backend. FastAPI owns request validation, LangGraph owns orchestration, and retrieval is isolated behind a service boundary so recommendation, refinement, and comparison logic can remain grounded in catalog data. Each request receives the full `messages` array; no server-side conversation memory is required.

The graph uses five business states: clarification, recommendation, refinement, comparison, and refusal. Intent detection is deterministic because schema-sensitive evaluators reward predictable behavior. Groq/LangChain integration is present as an optional service, but the response path is intentionally safe without an API key so deployment and tests do not fail.

## Retrieval Strategy

Catalog records are represented as strict Pydantic `CatalogItem` objects. The searchable text combines name, description, duration, type, keywords, category, job levels, language support, and remote testing support. The vector layer uses `sentence-transformers/all-MiniLM-L6-v2` when locally available and persists vectors in FAISS. If FAISS or the model is unavailable, deterministic vectors and token overlap keep the API functional.

Ranking combines semantic similarity, keyword overlap, and role-aware boosts. This helps queries like "Hiring a Java developer" prioritize Java and coding assessments, while refinements like "include personality and leadership" prioritize OPQ and leadership-oriented records.

## Prompt Engineering And Guardrails

Prompts are written as reusable policy strings, and the deterministic router enforces the key constraints before generation:

- SHL-only recommendations.
- No hallucinated names or URLs.
- Empty recommendations during clarification, comparison, and refusal.
- Refusal for prompt injection, legal advice, hiring law advice, unrelated topics, and non-SHL requests.

The final response is always reconstructed from catalog objects, not from raw model text, which prevents invented assessment names from entering the API payload.

## Evaluation Methodology

The test suite checks:

- `/health` response shape.
- `/chat` schema stability.
- Clarification returns no recommendations.
- Recommendations are SHL catalog URLs.
- Refinement can add personality or leadership assessments.
- Comparison returns grounded text without recommendation payload pollution.
- Prompt injection and legal requests are refused.

Every response passes through Pydantic `ChatResponse` validation before being returned by FastAPI.

## Tradeoffs

The included bootstrap catalog is intentionally compact so the project runs immediately in a local evaluator. The scraper can refresh the catalog from SHL when network access is available. The production recommendation path does not depend on LLM generation for the structured payload because reliability and hallucination resistance matter more than stylistic variety for this assignment.

## Failure Cases And Mitigations

If SHL changes catalog markup, the scraper logs skipped pages and fails if no records are produced. If vector dependencies are missing, retrieval falls back to deterministic local scoring. If the user provides contradictory requirements, refinement reranks from the full conversation history and returns the most relevant grounded shortlist rather than fabricating a new assessment.

## AI Tools Used

The implementation was generated and verified with an AI coding assistant inside Cursor/Codex-style local workspace tooling. The architecture follows production backend patterns: strict models, dependency isolation, graceful fallback, deterministic validation, and automated tests.
