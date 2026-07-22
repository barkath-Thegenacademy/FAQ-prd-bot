from app.db import get_conn
from app.models import RetrievedChunk


def retrieve(cohort_id: str) -> list[RetrievedChunk]:
    """Structured lookup, not RAG: the cohort schedule is small enough that we hand
    the whole thing to the Synthesis Agent and let it pick/cite the relevant rows."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT title, item_type, starts_at, due_at, details, link
            FROM schedule_items
            WHERE cohort_id = %s
            ORDER BY COALESCE(due_at, starts_at) ASC NULLS LAST
            """,
            (cohort_id,),
        )
        rows = cur.fetchall()

    chunks = []
    for title, item_type, starts_at, due_at, details, link in rows:
        text = f"[{item_type}] {title} | starts_at={starts_at} | due_at={due_at} | {details or ''}"
        chunks.append(RetrievedChunk(text=text, source=link or title))
    return chunks
