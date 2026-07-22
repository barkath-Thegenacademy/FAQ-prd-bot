import json

from anthropic import Anthropic

from app.config import get_config

_client: Anthropic | None = None


def get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=get_config().anthropic_api_key)
    return _client


def complete(system: str, user: str, max_tokens: int = 1024) -> str:
    response = get_client().messages.create(
        model=get_config().anthropic_model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return response.content[0].text


def complete_json(system: str, user: str, max_tokens: int = 1024):
    text = complete(system, user, max_tokens=max_tokens).strip()
    if text.startswith("```"):
        text = text.strip("`")
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1 :]
    return json.loads(text)
