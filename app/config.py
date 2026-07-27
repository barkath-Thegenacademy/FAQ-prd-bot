import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    app_name: str
    knowledge_base_path: Path
    gemini_api_key: str | None
    gemini_model: str


@lru_cache
def get_config() -> Config:
    return Config(
        app_name=os.getenv("APP_NAME", "Gen Academy FAQ Bot"),
        knowledge_base_path=Path(
            os.getenv("KNOWLEDGE_BASE_PATH", "knowledge_base/cohort_questions_full_list_with_resources.md")
        ),
        gemini_api_key=os.getenv("GEMINI_API_KEY") or None,
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-flash-latest"),
    )
