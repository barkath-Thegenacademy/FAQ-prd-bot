import argparse

from app.pipeline import compose_reply
from app.pipeline.orchestrator import process_message


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the FAQ bot pipeline on a single message.")
    parser.add_argument("message", help="The incoming student message text.")
    parser.add_argument("--identity", required=True, help="Discord ID / WhatsApp number / email.")
    parser.add_argument("--thread-id", default=None, help="Thread/conversation identifier.")
    args = parser.parse_args()

    answers = process_message(args.message, student_identity=args.identity, thread_id=args.thread_id)
    draft = compose_reply.compose(answers)

    print("\n--- Draft reply (pending human approval) ---\n")
    print(draft)
    print("\n--- Per-question routing ---")
    for a in answers:
        print(f"[{a.route} / {a.outcome}] {a.question}")


if __name__ == "__main__":
    main()
