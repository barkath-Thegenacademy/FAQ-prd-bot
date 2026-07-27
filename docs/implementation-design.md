# FAQ Bot POC - Implementation Design

## Architecture

The POC is a FastAPI application with three layers:

- Web/API layer: `app/main.py` serves the chat UI and `POST /api/chat`.
- Bot layer: `app/answering.py` handles routing, citations, context, and escalation.
- Knowledge layer: `app/knowledge.py` loads approved JSON and Markdown files from `knowledge_base/`.
- LLM layer: `app/llm.py` calls Gemini (`google-genai`) with the full knowledge base as context.

This is an **LLM + full-document context** architecture, not a Retrieval-Augmented Generation (RAG)
pipeline — there is no chunking, embedding generation, or vector database. The entire approved
knowledge base is passed to the LLM on every content question (see requirements-spec.md, Section 7.1).

No answer is produced from model memory or internet search. The bot either cites approved course
material or returns the required fallback text.

## Request Flow

1. Student sends a message through the web UI or any adapter that calls `POST /api/chat`.
2. The active `session_id` is loaded from in-memory session state.
3. Follow-up wording is expanded with the previous content question when needed.
4. The router classifies the message as content, action request, declined, or not a question.
5. Content questions are answered by loading every document in the knowledge base and sending
   them, verbatim, as context to Gemini alongside the question.
6. The LLM is instructed to answer only from that context and to reply with the exact fallback
   phrase when the material is insufficient.
7. If the reply is the fallback phrase (or the LLM is unavailable, e.g. no `GEMINI_API_KEY`),
   the bot returns the fallback text and escalates. Otherwise the LLM's answer — including its
   inline source citations — is returned as-is.

## Discord Integration

Discord escalation uses `DISCORD_WEBHOOK_URL`. The payload includes:

- Student identity
- Question
- UTC timestamp
- Escalation reason

This satisfies the POC requirement for unanswered-question review.

## Email Integration

Email escalation uses SMTP settings from `.env`:

- `ESCALATION_EMAIL_TO`
- `EMAIL_FROM`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `SMTP_USE_TLS`

Email is optional. If SMTP is not configured, the application still returns a stable answer.

## Knowledge Base Format

The approved knowledge base lives in `knowledge_base/` and supports:

- `.json` document arrays
- `.md` / `.markdown` files

Each JSON document should include `id`, `title`, `source`, `content`, optional `url`, and optional
`tags`. The seed file currently contains placeholder URLs and should be replaced with approved
Gen Academy resource links before a live demo.

## Testing Strategy

The focused tests cover:

- Known cohort-content answer includes citations.
- Career questions are declined without escalation.
- Unsupported questions return the exact SRS fallback and trigger escalation state.

Once Python dependencies are installed, run:

```powershell
python -m pytest -q
```
