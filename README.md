# SHL Conversational Assessment Recommender

Production-ready FastAPI backend for a stateless conversational agent that recommends SHL assessments from the official SHL product catalog.

## What It Does

- Asks clarification questions for vague hiring needs.
- Recommends 1-10 grounded SHL catalog assessments.
- Refines recommendations from the full `messages` history.
- Compares SHL assessments using local catalog records only.
- Refuses prompt injection, legal advice, hiring law advice, unrelated requests, and non-SHL recommendations.
- Keeps `/chat` responses schema-stable with Pydantic validation.

## Architecture

```text
FastAPI
  -> LangGraph agent
  -> intent detection
  -> clarify / recommend / refine / compare / refuse nodes
  -> FAISS or local deterministic vector retrieval
  -> metadata reranking
  -> Pydantic response validation
```

The API is stateless. Each `/chat` request sends the full conversation history, and the agent reconstructs context from that array.

## Project Structure

```text
app/
  agents/       LangGraph state, routing, nodes, prompts
  models/       Strict API and catalog Pydantic models
  retrieval/    Embeddings, FAISS persistence, retrieval, ranking
  routes/       FastAPI route modules
  scraper/      SHL catalog scraper and parser
  services/     Recommendation, comparison, refusal, LLM wrapper
  utils/        Logging, validation, helper utilities
data/
  catalog.json  Bootstrap SHL catalog records
  faiss_index/  Generated vector index
tests/          Pytest coverage for API and behaviors
```

## API

### `GET /health`

```json
{"status": "ok"}
```

### `POST /chat`

Request:

```json
{
  "messages": [
    {"role": "user", "content": "Hiring a Java developer"}
  ]
}
```

Response:

```json
{
  "reply": "Here are SHL catalog assessments that best match the hiring context: Java 8 (New).",
  "recommendations": [
    {
      "name": "Java 8 (New)",
      "url": "https://www.shl.com/products/product-catalog/view/java-8-new/",
      "test_type": "K"
    }
  ],
  "end_of_conversation": true
}
```

## Windows PowerShell Commands

```powershell
cd "C:\Users\Chait\Documents\New project\shl-assessment-agent"
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m app.scraper.scrape_catalog
python -m app.retrieval.vector_store
uvicorn app.main:app --host 0.0.0.0 --port 10000
pytest
```

Endpoint checks:

```powershell
Invoke-RestMethod http://localhost:10000/health
Invoke-RestMethod http://localhost:10000/chat -Method Post -ContentType "application/json" -Body '{"messages":[{"role":"user","content":"Hiring a Java developer"}]}'
```

## Git Bash Commands

```bash
cd "/c/Users/Chait/Documents/New project/shl-assessment-agent"
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m app.scraper.scrape_catalog
python -m app.retrieval.vector_store
uvicorn app.main:app --host 0.0.0.0 --port 10000
pytest
```

Endpoint checks:

```bash
curl http://localhost:10000/health
curl -X POST http://localhost:10000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hiring a Java developer"}]}'
```

## Linux/macOS Commands

```bash
cd shl-assessment-agent
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m app.scraper.scrape_catalog
python -m app.retrieval.vector_store
uvicorn app.main:app --host 0.0.0.0 --port 10000
pytest
```

## Environment Variables

Copy `.env.example` to `.env` and set:

```bash
GROQ_API_KEY=your_groq_key
MODEL_NAME=llama-3.3-70b-versatile
ALLOW_MODEL_DOWNLOAD=false
```

`ALLOW_MODEL_DOWNLOAD=false` keeps deployment startup predictable. Set it to `true` when you want `sentence-transformers/all-MiniLM-L6-v2` downloaded while building the FAISS index.

## Render Deployment

1. Push this folder to GitHub.
2. In Render, create a new Blueprint from `render.yaml`.
3. Add `GROQ_API_KEY` as a secret environment variable.
4. Render runs:

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

Render CLI-style flow:

```bash
git init
git add .
git commit -m "Build SHL assessment recommender"
git branch -M main
git remote add origin https://github.com/<your-user>/shl-assessment-agent.git
git push -u origin main
```

## Troubleshooting

- If FAISS is unavailable, the app automatically uses a NumPy/deterministic retrieval fallback.
- If the sentence-transformer model is not cached and downloads are disabled, the app uses deterministic local embeddings.
- If the Groq key is missing, the deterministic grounded response path still works and preserves schema.
- If scraper output changes because SHL updates markup, the parser still writes only normalized `CatalogItem` records and fails loudly when no catalog links are found.

## Limitations

The included `data/catalog.json` is a bootstrap catalog so the assignment runs immediately. For maximum coverage, run the scraper on a network-enabled machine and rebuild the FAISS index before final deployment.

