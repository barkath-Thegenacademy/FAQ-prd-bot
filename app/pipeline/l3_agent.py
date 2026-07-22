from app.db import get_conn
from app.embeddings import embed_query
from app.models import RetrievedChunk

TOP_K = 5


def retrieve(question: str, cohort_id: str) -> list[RetrievedChunk]:
    vector = embed_query(question)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT chunk_text, source_url
            FROM session_content
            WHERE cohort_id = %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (cohort_id, vector, TOP_K),
        )
        rows = cur.fetchall()
    return [RetrievedChunk(text=text, source=source or "session_content") for text, source in rows]
