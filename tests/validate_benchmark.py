import json
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

FILE = Path("benchmarks/questions.json")

ALLOWED_CATEGORIES = {
    "fact_verification",
    "source_reliability",
    "multi_hop_research",
    "conflicting_information",
    "temporal_accuracy",
    "answer_grounding",
    "insufficient_evidence"
}

ALLOWED_DIFFICULTIES = {"easy", "medium", "hard"}
ALLOWED_STATUSES = {"draft", "reviewed", "approved"}

REQUIRED_FIELDS = {
    "id",
    "category",
    "difficulty",
    "question",
    "expected_answer",
    "evidence",
    "evaluation_criteria",
    "created_at",
    "status"
}

SCORE_FIELDS = {
    "accuracy",
    "source_quality",
    "evidence_support",
    "reasoning"
}


def validate():
    errors = []

    if not FILE.exists():
        print("ERROR: Benchmark file not found.")
        sys.exit(1)

    try:
        questions = json.loads(FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: Invalid JSON: {exc}")
        sys.exit(1)

    if not isinstance(questions, list):
        print("ERROR: Questions must be a JSON list.")
        sys.exit(1)

    ids = [q.get("id") for q in questions if isinstance(q, dict)]

    if len(ids) != len(questions):
        errors.append("Every question must be a JSON object.")

    if len(ids) != len(set(ids)):
        errors.append("Duplicate question IDs found.")

    for index, q in enumerate(questions, start=1):
        if not isinstance(q, dict):
            continue

        prefix = f"Question {index} ({q.get('id', 'NO-ID')})"

        missing = REQUIRED_FIELDS - q.keys()
        if missing:
            errors.append(f"{prefix}: Missing fields: {sorted(missing)}")

        if q.get("category") not in ALLOWED_CATEGORIES:
            errors.append(f"{prefix}: Invalid category.")

        if q.get("difficulty") not in ALLOWED_DIFFICULTIES:
            errors.append(f"{prefix}: Invalid difficulty.")

        if q.get("status") not in ALLOWED_STATUSES:
            errors.append(f"{prefix}: Invalid status.")

        if not isinstance(q.get("question"), str) or not q["question"].strip():
            errors.append(f"{prefix}: Empty question.")

        if not isinstance(q.get("expected_answer"), str) or not q["expected_answer"].strip():
            errors.append(f"{prefix}: Empty expected answer.")

        evidence = q.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{prefix}: At least one evidence source is required.")
        else:
            for source in evidence:
                if not isinstance(source, dict):
                    errors.append(f"{prefix}: Evidence entry must be an object.")
                    continue

                url = source.get("url", "")
                parsed = urlparse(url)

                if parsed.scheme != "https" or not parsed.netloc:
                    errors.append(f"{prefix}: Invalid HTTPS source URL.")

                for field in ("source_title", "supporting_text", "source_type"):
                    if not source.get(field):
                        errors.append(f"{prefix}: Evidence missing {field}.")

        criteria = q.get("evaluation_criteria")
        if not isinstance(criteria, dict):
            errors.append(f"{prefix}: Evaluation criteria must be an object.")
        else:
            if set(criteria) != SCORE_FIELDS:
                errors.append(f"{prefix}: Incorrect evaluation criteria fields.")
            elif not all(
                isinstance(value, (int, float)) and 0 <= value <= 100
                for value in criteria.values()
            ):
                errors.append(f"{prefix}: Scores must be between 0 and 100.")
            elif sum(criteria.values()) != 100:
                errors.append(f"{prefix}: Evaluation scores must total 100.")

    print("\n========== AIREP BENCHMARK VALIDATION ==========")
    print(f"Total questions: {len(questions)}")
    print(f"Unique IDs: {len(set(ids))}")

    print("\nCategory distribution:")
    for category, count in sorted(
        Counter(
            q.get("category", "invalid")
            for q in questions if isinstance(q, dict)
        ).items()
    ):
        print(f"  {category}: {count}")

    if errors:
        print(f"\nVALIDATION FAILED: {len(errors)} issue(s)")
        for error in errors:
            print(f"[ERROR] {error}")
        sys.exit(1)

    print("\nVALIDATION PASSED")
    print("All structural checks passed.")


if __name__ == "__main__":
    validate()
