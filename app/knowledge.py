import json
from functools import lru_cache
from pathlib import Path

from app.config import get_config
from app.models import KnowledgeDocument


def _load_json(path: Path) -> list[KnowledgeDocument]:
    data = json.loads(path.read_text(encoding="utf-8"))
    records = data if isinstance(data, list) else data.get("documents", [])
    return [KnowledgeDocument(**record) for record in records]


def _load_markdown(path: Path) -> list[KnowledgeDocument]:
    content = path.read_text(encoding="utf-8").strip()
    title = path.stem.replace("-", " ").replace("_", " ").title()
    return [
        KnowledgeDocument(
            id=path.stem,
            title=title,
            source=str(path),
            content=content,
        )
    ]


@lru_cache
def load_documents() -> list[KnowledgeDocument]:
    root = get_config().knowledge_base_path
    if not root.exists():
        return []

    documents: list[KnowledgeDocument] = []
    for path in sorted(root.rglob("*")):
        if path.suffix.lower() == ".json":
            documents.extend(_load_json(path))
        elif path.suffix.lower() in {".md", ".markdown"}:
            documents.extend(_load_markdown(path))
    return documents
