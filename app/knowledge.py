from functools import lru_cache

from app.config import get_config


@lru_cache
def load_knowledge_base_document() -> str:
    path = get_config().knowledge_base_path
    if not path.exists():
        return ""
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8").strip()
