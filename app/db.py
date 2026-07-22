from contextlib import contextmanager

from psycopg_pool import ConnectionPool

from app.config import get_config

_pool: ConnectionPool | None = None


def get_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        _pool = ConnectionPool(get_config().database_url, min_size=1, max_size=5)
    return _pool


@contextmanager
def get_conn():
    with get_pool().connection() as conn:
        yield conn
