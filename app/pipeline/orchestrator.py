from app.models import AgentAnswer
from app.pipeline import action_request, l3_agent, l4_agent, router_agent, synthesis_agent, verification_gate
from app.pipeline.parse_questions import parse_questions

DECLINE_TEXT = (
    "That's a career/job-transition question -- outside what this bot is set up to advise on. "
    "Please reach out to your program mentor for that conversation."
)
UNVERIFIED_TEXT = (
    "I can't find you as an enrolled student for this cohort. Please verify your enrollment "
    "before I can answer content questions -- reach out to your program coordinator to get set up."
)


def process_question(question: str, *, student_identity: str, thread_id: str | None) -> AgentAnswer:
    decision = router_agent.classify(question)

    if decision.route == "action_request":
        text = action_request.handle(decision.target_human)
        synthesis_agent.log_question(
            student_identity=student_identity,
            cohort_id=None,
            thread_id=thread_id,
            question_text=question,
            route="action_request",
            verified=False,
            outcome="routed_to_human",
            answer_text=text,
        )
        return AgentAnswer(question=question, route="action_request", outcome="routed_to_human", text=text)

    if decision.route == "declined":
        synthesis_agent.log_question(
            student_identity=student_identity,
            cohort_id=None,
            thread_id=thread_id,
            question_text=question,
            route="declined",
            verified=False,
            outcome="declined",
            answer_text=DECLINE_TEXT,
        )
        return AgentAnswer(question=question, route="declined", outcome="declined", text=DECLINE_TEXT)

    verification = verification_gate.verify(student_identity, thread_id)
    if not verification.verified:
        synthesis_agent.log_question(
            student_identity=student_identity,
            cohort_id=None,
            thread_id=thread_id,
            question_text=question,
            route=decision.route,
            verified=False,
            outcome="escalated",
            answer_text=UNVERIFIED_TEXT,
        )
        return AgentAnswer(question=question, route=decision.route, outcome="escalated", text=UNVERIFIED_TEXT)

    if decision.route == "l3":
        chunks = l3_agent.retrieve(question, verification.cohort_id)
    else:
        chunks = l4_agent.retrieve(verification.cohort_id)

    answer_text = synthesis_agent.synthesize(question, chunks)
    synthesis_agent.log_question(
        student_identity=student_identity,
        cohort_id=verification.cohort_id,
        thread_id=thread_id,
        question_text=question,
        route=decision.route,
        verified=True,
        outcome="answered",
        answer_text=answer_text,
    )
    return AgentAnswer(question=question, route=decision.route, outcome="answered", text=answer_text)


def process_message(
    message_text: str, *, student_identity: str, thread_id: str | None = None
) -> list[AgentAnswer]:
    questions = parse_questions(message_text)
    return [process_question(q, student_identity=student_identity, thread_id=thread_id) for q in questions]
