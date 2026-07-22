# FAQ-BOT — L3/L4 Basic Agent

Cohort-only support pipeline: Router Agent splits action requests (billing, credits,
drops) from content questions; content questions pass a Verification Gate before
reaching L3 (session content, pgvector RAG) or L4 (schedule/deadlines, structured
lookup); Synthesis Agent writes the cited answer and logs every question to Postgres.

Out of scope for this build: L1/L2 (public prospect FAQ) and L5 (live systems
integration).

## Layout

```
db/schema.sql         students, verification_cache, question_log, session_content, schedule_items
app/config.py         env-backed config
app/db.py             Postgres connection pool
app/llm.py            Anthropic client wrapper (plain + JSON completions)
app/embeddings.py      Voyage AI client wrapper (query/document embedding)
app/models.py         RouteDecision / VerificationResult / RetrievedChunk / AgentAnswer
app/pipeline/
  parse_questions.py   LLM splits a message into discrete questions
  router_agent.py       classifies: l3 / l4 / action_request / declined
  verification_gate.py  roster check + 24h session cache
  l3_agent.py            pgvector similarity search over session_content
  l4_agent.py            full cohort schedule_items lookup (small table, no RAG)
  synthesis_agent.py     drafts the cited answer; logs every question to question_log
  action_request.py      routes billing/credits/drops straight to a human, no draft
  compose_reply.py       merges per-question answers back in order
  orchestrator.py        the Loop -- ties all of the above together per message
app/main.py            CLI entrypoint: run the pipeline on one message
```

## Setup

1. `python -m venv .venv && .venv\Scripts\activate` (Windows) then `pip install -r requirements.txt`.
2. Create a Postgres database with the `pgvector` extension available, then run `db/schema.sql` against it.
3. Copy `.env.example` to `.env` and fill in `ANTHROPIC_API_KEY`, `VOYAGE_API_KEY`, `DATABASE_URL`.
4. Seed `students` (roster) and `schedule_items` for at least one cohort, and ingest some
   `session_content` rows with embeddings (chunk + embed via `app/embeddings.py`) so L3/L4 have
   something to retrieve.
5. Run: `python -m app.main "when does the certificate get issued?" --identity discord:12345`

## Build sequence status (see plan, Section 6)

- [x] 1. Postgres schema
- [x] 2. L4 agent (structured schedule lookup)
- [x] 3. L3 agent (pgvector RAG) -- retrieval wired; session content still needs to be ingested
- [x] 4. Router Agent -- prompted against the real question categories from the plan
- [x] 5. Verification Gate + Postgres wiring, including the question-log write
- [ ] 6. Pilot in approval mode -- `app/main.py` only prints the draft today; wiring an actual
      human approve/edit/reject step (Discord/WhatsApp/email delivery) and override-rate tracking
      is the next piece of work before this can run live.

## Notes / open decisions

- Anthropic doesn't provide an embeddings API, so L3 uses Voyage AI (their recommended
  embedding partner). `session_content.embedding` is `VECTOR(1024)` to match `voyage-3` --
  change both together if you pick a different model.
- `router_agent.classify` decides L3 vs. L4 directly (not a separate step), since the plan's
  diagrams don't show a distinct L3/L4 selector ahead of the Verification Gate.
- Unverified content questions and declined (career) questions are still written to
  `question_log` (per Section 5: "every question that reaches Synthesis... gets written"),
  just with `verified=false` / route `declined` and no L3/L4 lookup performed.
# FAQ-BOT-
