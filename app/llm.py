from google import genai
from google.genai import types

from app.config import get_config
from app.models import KnowledgeDocument

SYSTEM_PROMPT = """You answer Gen Academy cohort FAQ questions.

Rules:
- Use only the provided approved course material.
- Do not use outside knowledge.
- Keep the answer concise.
- Cite source titles in the answer.
- If the material is insufficient, say exactly: I couldn't find this information in the current course material.
"""


def synthesize_with_llm(question: str, documents: list[KnowledgeDocument]) -> str | None:
    config = get_config()
    if not config.gemini_api_key:
        return None

    context = "\n\n".join(
        f"Title: {doc.title}\nSource: {doc.source}\nContent: {doc.content}" for doc in documents
    )
    client = genai.Client(api_key=config.gemini_api_key)
    response = client.models.generate_content(
        model=config.gemini_model,
        contents=f"Question: {question}\n\nApproved material:\n{context}",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0,
        ),
    )
    return response.text
