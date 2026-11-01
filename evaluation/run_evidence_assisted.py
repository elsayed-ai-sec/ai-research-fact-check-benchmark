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


def load_question():
    questions = json.loads(
        BENCHMARK_FILE.read_text(encoding="utf-8")
    )

    for question in questions:
        if question["id"] == QUESTION_ID:
            return question

    raise ValueError(f"Question not found: {QUESTION_ID}")


def build_prompt(question):
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
1. Identify the facts directly supported by the evidence.
2. Do not invent report numbers or dates.
3. If evidence is insufficient, clearly state what is missing.
4. Cite the evidence title supporting each important claim.
5. Do not claim that you opened or independently verified the URLs.

Question:
{question["question"]}

Supplied evidence:
{evidence}

Provide:
- Answer
- Evidence used
- Any limitations
"""


def generate_answer(prompt):
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
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(request, timeout=240) as response:
            result = json.loads(response.read().decode("utf-8"))

        return result.get("response", "").strip()

    except urllib.error.HTTPError as error:
        error_body = error.read().decode("utf-8", errors="replace")
        print("\\nOllama HTTP Error:", error.code)
        print("Error details:", error_body)
        raise

    except urllib.error.URLError as error:
        print("\\nOllama connection error:", error.reason)
        raise


def main():
    question = load_question()
    prompt = build_prompt(question)

    print("Running evidence-assisted evaluation...")
    print("Model:", MODEL)
    print("Question:", QUESTION_ID)

    answer = generate_answer(prompt)

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    record = {
        "evaluation_id": f"EVIDENCE-{timestamp}",
        "benchmark_question_id": QUESTION_ID,
        "evaluation_mode": "evidence_assisted",
        "model": MODEL,
        "question": question["question"],
        "expected_answer": question["expected_answer"],
        "provided_evidence": question["evidence"],
        "model_answer": answer,
        "automated_score": None,
        "review_status": "pending_human_review",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    RESULTS_DIR.mkdir(exist_ok=True)

    output_file = RESULTS_DIR / f"{record['evaluation_id']}.json"

    output_file.write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

    print("\n========== EVIDENCE-ASSISTED ANSWER ==========")
    print(answer)

    print("\n========== RESULT ==========")
    print("Saved to:", output_file)
    print("Review status: pending_human_review")
    print("No automatic score was assigned.")


if __name__ == "__main__":
    main()
