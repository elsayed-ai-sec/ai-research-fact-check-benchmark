import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

BENCHMARK_FILE = Path("benchmarks/questions.json")
RESULTS_DIR = Path("reports")

API_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "qwen2.5:1.5b"

BATCH_SIZE = 3


def load_questions():
    questions = json.loads(
        BENCHMARK_FILE.read_text(encoding="utf-8")
    )

    return questions[:BATCH_SIZE]


def build_prompt(question, mode):
    if mode == "closed_book_baseline":
        return f"""
Answer the following question using your existing knowledge.

If you are uncertain, clearly say so.
Do not invent facts or claim that you checked sources.
Give a concise answer.

Question:
{question["question"]}
"""

    evidence_text = []

    for index, source in enumerate(question["evidence"], start=1):
        evidence_text.append(
            f"""
Evidence {index}
Title: {source['source_title']}
URL: {source['url']}
Supporting text: {source['supporting_text']}
"""
        )

    evidence = "\n".join(evidence_text)

    return f"""
You are an AI research assistant.

Answer the question using only the supplied evidence.

Instructions:
1. Identify facts directly supported by the evidence.
2. Do not invent facts or dates.
3. If evidence is insufficient, clearly state what is missing.
4. Cite the evidence title supporting each important claim.
5. Do not claim that you opened or independently verified URLs.

Question:
{question["question"]}

Supplied evidence:
{evidence}

Provide:
- Answer
- Evidence used
- Any limitations
"""


def generate_answer(prompt, mode):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "num_ctx": 2048,
            "num_predict": 350
        }
    }

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=240) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result.get("response", "").strip()


def save_result(question, mode, answer):
    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )

    prefix = "BASELINE" if mode == "closed_book_baseline" else "EVIDENCE"

    record = {
        "evaluation_id": f"{prefix}-{question['id']}-{timestamp}",
        "benchmark_question_id": question["id"],
        "evaluation_mode": mode,
        "model": MODEL,
        "question": question["question"],
        "expected_answer": question["expected_answer"],
        "model_answer": answer,
        "automated_score": None,
        "review_status": "pending_human_review",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    if mode == "evidence_assisted":
        record["provided_evidence"] = question["evidence"]

    RESULTS_DIR.mkdir(exist_ok=True)

    output_file = RESULTS_DIR / f"{record['evaluation_id']}.json"

    output_file.write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

    return output_file


def main():
    questions = load_questions()

    print("Starting AIREP batch evaluation")
    print("Model:", MODEL)
    print("Questions:", len(questions))
    print("Modes: closed-book and evidence-assisted")
    print("Total planned evaluations:", len(questions) * 2)

    successful = 0
    failed = 0

    for question in questions:
        print("\n===================================")
        print("Question:", question["id"])
        print("Category:", question["category"])

        for mode in ("closed_book_baseline", "evidence_assisted"):
            print("\nMode:", mode)

            try:
                prompt = build_prompt(question, mode)
                answer = generate_answer(prompt, mode)
                output_file = save_result(question, mode, answer)

                successful += 1

                print("Answer:", answer)
                print("Saved:", output_file)

            except (urllib.error.URLError, TimeoutError, ValueError) as error:
                failed += 1
                print("Evaluation failed:", error)

            except Exception as error:
                failed += 1
                print("Unexpected error:", error)

    print("\n========== BATCH SUMMARY ==========")
    print("Successful:", successful)
    print("Failed:", failed)
    print("Total:", successful + failed)
    print("Human review required for successful evaluations.")


if __name__ == "__main__":
    main()
