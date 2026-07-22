-- Section 1 of the build sequence: roster, verification cache, question log,
-- plus the two content stores (L3 pgvector chunks, L4 structured schedule).

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    identity TEXT NOT NULL UNIQUE,             -- discord id / whatsapp number / email
    channel TEXT NOT NULL CHECK (channel IN ('discord', 'whatsapp', 'email')),
    full_name TEXT,
    cohort_id TEXT NOT NULL,
    enrolled_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    active BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE verification_cache (
    identity TEXT PRIMARY KEY REFERENCES students(identity),
    thread_id TEXT,
    verified_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE question_log (
    id SERIAL PRIMARY KEY,
    student_identity TEXT NOT NULL,
    cohort_id TEXT,
    thread_id TEXT,
    question_text TEXT NOT NULL,
    route TEXT NOT NULL CHECK (route IN ('l3', 'l4', 'action_request', 'declined')),
    verified BOOLEAN NOT NULL,
    outcome TEXT NOT NULL CHECK (outcome IN ('answered', 'escalated', 'routed_to_human', 'declined')),
    answer_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- L3: session content, chunked and tagged by session/week, embedded for pgvector RAG.
-- embedding dimension must match whatever VOYAGE_MODEL is configured (voyage-3 = 1024).
CREATE TABLE session_content (
    id SERIAL PRIMARY KEY,
    cohort_id TEXT NOT NULL,
    session_week INTEGER,
    session_title TEXT,
    source_url TEXT,
    chunk_text TEXT NOT NULL,
    embedding VECTOR(1024),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX session_content_embedding_idx ON session_content USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX session_content_cohort_idx ON session_content (cohort_id);

-- L4: structured schedule/deadline facts. Small table, no RAG -- Synthesis Agent
-- is handed the full cohort schedule and picks/cites the relevant rows.
CREATE TABLE schedule_items (
    id SERIAL PRIMARY KEY,
    cohort_id TEXT NOT NULL,
    item_type TEXT NOT NULL CHECK (item_type IN ('session', 'deadline', 'assessment', 'certificate')),
    title TEXT NOT NULL,
    starts_at TIMESTAMPTZ,
    due_at TIMESTAMPTZ,
    details TEXT,
    link TEXT
);

CREATE INDEX schedule_items_cohort_idx ON schedule_items (cohort_id);
