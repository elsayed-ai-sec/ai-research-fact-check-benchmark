import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

BENCHMARK_FILE = Path("benchmarks/questions.json")
RESULTS_DIR = Path("reports")
API_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "qwen2.5:1.5b"
QUESTION_ID = "AIREP-011"


def main():
    questions = json.loads(
        BENCHMARK_FILE.read_text(encoding="utf-8")
    )

    question = next(
        (q for q in questions if q["id"] == QUESTION_ID),
        None
    )

    if question is None:
        raise ValueError(f"Question not found: {QUESTION_ID}")

    prompt = f"""
Answer the following question using your existing knowledge.

If you are uncertain, clearly say so.
Do not invent facts or claim that you checked sources.
Give a concise answer.

Question:
{question["question"]}
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0
        }
    }

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    print("Running model evaluation...")
    print("Model:", MODEL)
    print("Question:", QUESTION_ID)

    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))
    except Exception as error:
        print("ERROR:", error)
        return

    model_answer = result.get("response", "").strip()

    record = {
        "evaluation_id": "BASELINE-" + datetime.now(
            timezone.utc
        ).strftime("%Y%m%dT%H%M%SZ"),
        "benchmark_question_id": QUESTION_ID,
        "evaluation_mode": "closed_book_baseline",
        "model": MODEL,
        "question": question["question"],
        "expected_answer": question["expected_answer"],
        "model_answer": model_answer,
        "automated_score": None,
        "review_status": "pending_human_review",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    RESULTS_DIR.mkdir(exist_ok=True)

    output_file = RESULTS_DIR / (
        record["evaluation_id"] + ".json"
    )

    output_file.write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

    print("\n========== MODEL ANSWER ==========")
    print(model_answer)

    print("\n========== RESULT ==========")
    print("Saved to:", output_file)
    print("Review status: pending_human_review")
    print("No automatic score was assigned.")


if __name__ == "__main__":
    main()
