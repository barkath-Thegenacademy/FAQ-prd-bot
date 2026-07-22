from app.llm import complete_json

SYSTEM = """You split an incoming student message into a list of discrete questions or requests.
Rules:
- If the message contains multiple distinct asks, return each as a separate string.
- If it's a single ask, return a list with one string.
- Preserve the student's original wording as closely as possible; do not answer or editorialize.
- Output ONLY a JSON array of strings, nothing else.
"""


def parse_questions(message_text: str) -> list[str]:
    questions = complete_json(SYSTEM, message_text, max_tokens=512)
    if not isinstance(questions, list) or not questions:
        return [message_text.strip()]
    return [str(q).strip() for q in questions if str(q).strip()]
