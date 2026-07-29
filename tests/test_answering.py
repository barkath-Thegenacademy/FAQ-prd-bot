import asyncio

import app.answering as answering
from app.answering import ChatRequest, NO_MATCH_TEXT, answer_chat
from app.llm import clean_answer


async def _fake_escalate(*args, **kwargs):
    return True


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


def test_declines_and_escalates_career_questions(monkeypatch):
    monkeypatch.setattr(answering, "escalate", _fake_escalate)

    response = asyncio.run(answer_chat(ChatRequest(message="Can you help me with recruiter outreach?")))

    assert response.route == "declined"
    assert response.escalated is True


def test_escalates_action_requests(monkeypatch):
    monkeypatch.setattr(answering, "escalate", _fake_escalate)

    response = asyncio.run(answer_chat(ChatRequest(message="My Pinecone promo code isn't working, can you help?")))

    assert response.route == "action_request"
    assert response.escalated is True


def test_escalates_unknown_content(monkeypatch):
    monkeypatch.setattr(answering, "escalate", _fake_escalate)
    monkeypatch.setattr(
        answering,
        "synthesize_with_llm",
        lambda question, knowledge_base_document: NO_MATCH_TEXT,
    )

    response = asyncio.run(answer_chat(ChatRequest(message="Where is the capstone deployment rubric?")))

    assert response.route == "content"
    assert response.escalated is True
    assert response.answer == NO_MATCH_TEXT


def test_clean_answer_removes_markdown_emphasis():
    answer = clean_answer("Use the **Recording Index** from *the KB*.")

    assert answer == "Use the Recording Index from the KB."
