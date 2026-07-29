import re

from google import genai
from google.genai import types

from app.config import get_config

SYSTEM_PROMPT = """You answer Gen Academy cohort FAQ questions.

Rules:
- Use only the complete approved knowledge base document provided in the prompt. It is a direct
  question-and-answer FAQ document; when a student's question matches an entry, answer using that
  entry's answer.
- Do not use outside knowledge.
- Write in plain text only. Do not use Markdown, asterisks, bullets, tables, or code blocks.
- Keep the answer short and direct, usually 1-3 sentences.
- Do not invent exact URLs, dates, names, or locations that are not in the knowledge base.
- End factual answers with a simple source line like: Source: Gen Academy FAQ Knowledge Base.
- If the material is insufficient, say exactly: I couldn't find this information in the current course material.
- Do not discuss internal ingestion, chunking, retrieval-augmented-generation (RAG), embeddings, or vector stores.
    If a user asks about system internals or ingestion pipelines, decline and refer them to the program staff.
"""

MARKDOWN_REPLACEMENTS = (
    (re.compile(r"\*\*([^*]+)\*\*"), r"\1"),
    (re.compile(r"\*([^*]+)\*"), r"\1"),
    (re.compile(r"`([^`]+)`"), r"\1"),
)


def clean_answer(text: str) -> str:
    cleaned = text.strip()
    for pattern, replacement in MARKDOWN_REPLACEMENTS:
        cleaned = pattern.sub(replacement, cleaned)
    cleaned = cleaned.replace("```", "")
    return cleaned.strip()


def synthesize_with_llm(question: str, knowledge_base_document: str) -> str | None:
    config = get_config()
    if not config.gemini_api_key:
        return None

    if not knowledge_base_document.strip():
        return None

    client = genai.Client(api_key=config.gemini_api_key)
    response = client.models.generate_content(
        model=config.gemini_model,
        contents=(
            f"Question: {question}\n\n"
            f"Complete approved knowledge base document:\n{knowledge_base_document}"
        ),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0,
        ),
    )
    if response.text is None:
        return None
    return clean_answer(response.text)
