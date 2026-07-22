import voyageai

from app.config import get_config

_client: voyageai.Client | None = None


def get_client() -> voyageai.Client:
    global _client
    if _client is None:
        _client = voyageai.Client(api_key=get_config().voyage_api_key)
    return _client


def embed_query(text: str) -> list[float]:
    result = get_client().embed([text], model=get_config().voyage_model, input_type="query")
    return result.embeddings[0]


def embed_documents(texts: list[str]) -> list[list[float]]:
    result = get_client().embed(texts, model=get_config().voyage_model, input_type="document")
    return result.embeddings
