from app.db import get_conn
from app.llm import complete
from app.models import Outcome, RetrievedChunk, Route

SYSTEM = """You are the synthesis agent for a cohort support bot. You are given a student's question and
retrieved source material. Write a short, direct answer grounded ONLY in the provided material, and cite
the source for each fact you state. If the material does not answer the question, say so plainly instead
of guessing.
"""


def synthesize(question: str, chunks: list[RetrievedChunk]) -> str:
    context = "\n\n".join(f"Source: {c.source}\n{c.text}" for c in chunks)
    user = f"Question: {question}\n\nRetrieved material:\n{context}"
    return complete(SYSTEM, user, max_tokens=512)


def log_question(
    *,
    student_identity: str,
    cohort_id: str | None,
    thread_id: str | None,
    question_text: str,
    route: Route,
    verified: bool,
    outcome: Outcome,
    answer_text: str | None,
) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO question_log
                (student_identity, cohort_id, thread_id, question_text, route, verified, outcome, answer_text)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (student_identity, cohort_id, thread_id, question_text, route, verified, outcome, answer_text),
        )
        conn.commit()
