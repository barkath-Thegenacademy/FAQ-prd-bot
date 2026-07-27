# Gen Academy FAQ Bot POC

A web-based FAQ bot for Gen Academy cohort-content questions. It answers only from
the local approved knowledge base and escalates unsupported or human-action questions
through Discord and email when those integrations are configured.

## What It Does

- Serves a browser chat UI at `/`.
- Exposes `POST /api/chat` for web, Discord, or email adapters.
- Passes the complete approved knowledge base document to Gemini on every content question.
- Includes source citations in every factual answer.
- Keeps short follow-up context during the active in-memory session.
- Refuses career/job-transition coaching questions.
- Escalates unsupported questions with the exact fallback text required by the SRS:
  `I couldn't find this information in the current course material.`
- Sends escalation notifications to Discord webhook and SMTP email when configured.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Fill in `.env` if you want escalation delivery:

- `DISCORD_WEBHOOK_URL`
- `ESCALATION_EMAIL_TO`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `EMAIL_FROM`

The app still runs without these values; escalation attempts are simply skipped.

## Run

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Open `http://127.0.0.1:8000`.

## API Example

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/chat `
  -ContentType application/json `
  -Body '{"message":"Where was chunking discussed?","student_identity":"discord:123","channel":"discord"}'
```

## Knowledge Base

Set `KNOWLEDGE_BASE_PATH` to the single approved knowledge base document. The default is
`knowledge_base/cohort_questions_full_list_with_resources.md`, extracted from
`Cohort_Questions_Full_List_With_Resources (1).docx`. The app sends that full document to
the LLM for every content question.

This POC intentionally does not use document chunking, embeddings, vector databases, semantic
search, Pinecone, FAISS, ChromaDB, or a RAG pipeline.
