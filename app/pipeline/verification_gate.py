from datetime import datetime, timedelta, timezone

from app.db import get_conn
from app.models import VerificationResult

CACHE_TTL = timedelta(hours=24)


def verify(identity: str, thread_id: str | None) -> VerificationResult:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT cohort_id, thread_id, expires_at
            FROM verification_cache
            JOIN students USING (identity)
            WHERE identity = %s
            """,
            (identity,),
        )
        row = cur.fetchone()
        now = datetime.now(timezone.utc)
        if row:
            cohort_id, cached_thread_id, expires_at = row
            same_thread = thread_id is None or cached_thread_id == thread_id
            if same_thread and expires_at > now:
                return VerificationResult(verified=True, cohort_id=cohort_id, reason="cache_hit")

        cur.execute(
            "SELECT cohort_id FROM students WHERE identity = %s AND active = true",
            (identity,),
        )
        student_row = cur.fetchone()
        if not student_row:
            return VerificationResult(verified=False, reason="not_enrolled")

        cohort_id = student_row[0]
        expires_at = now + CACHE_TTL
        cur.execute(
            """
            INSERT INTO verification_cache (identity, thread_id, verified_at, expires_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (identity) DO UPDATE
            SET thread_id = EXCLUDED.thread_id,
                verified_at = EXCLUDED.verified_at,
                expires_at = EXCLUDED.expires_at
            """,
            (identity, thread_id, now, expires_at),
        )
        conn.commit()
        return VerificationResult(verified=True, cohort_id=cohort_id, reason="roster_match")
