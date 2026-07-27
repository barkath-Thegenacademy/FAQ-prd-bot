import asyncio

import app.answering as answering
from app.answering import ChatRequest, NO_MATCH_TEXT, answer_chat


def test_answers_known_content_with_source(monkeypatch):
    monkeypatch.setattr(
        answering,
        "synthesize_with_llm",
        lambda question, knowledge_base_document: (
            "Chunking was covered in Week 3.\n\nSources:\n- Session Notes: Week 3"
        ),
    )

    response = asyncio.run(answer_chat(ChatRequest(message="Where was chunking discussed?")))

    assert response.route == "content"
    assert response.escalated is False
    assert "Sources:" in response.answer


def test_declines_career_questions_without_escalation():
    response = asyncio.run(answer_chat(ChatRequest(message="Can you help me with recruiter outreach?")))

    assert response.route == "declined"
    assert response.escalated is False


def test_escalates_unknown_content(monkeypatch):
    monkeypatch.setattr(
        answering,
        "synthesize_with_llm",
        lambda question, knowledge_base_document: NO_MATCH_TEXT,
    )

    response = asyncio.run(answer_chat(ChatRequest(message="Where is the capstone deployment rubric?")))

    assert response.route == "content"
    assert response.escalated is True
    assert response.answer == NO_MATCH_TEXT
