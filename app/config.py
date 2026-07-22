import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    anthropic_api_key: str
    anthropic_model: str
    voyage_api_key: str
    voyage_model: str
    database_url: str
    action_request_human: str


@lru_cache
def get_config() -> Config:
    return Config(
        anthropic_api_key=os.environ["ANTHROPIC_API_KEY"],
        anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5"),
        voyage_api_key=os.environ["VOYAGE_API_KEY"],
        voyage_model=os.getenv("VOYAGE_MODEL", "voyage-3"),
        database_url=os.environ["DATABASE_URL"],
        action_request_human=os.getenv("ACTION_REQUEST_HUMAN", "Arvind"),
    )
