import json
import sys
from pathlib import Path
from datetime import datetime, timezone


def get_score(label, maximum):
    while True:
        try:
            score = int(input(f"{label} (0-{maximum}): "))
            if 0 <= score <= maximum:
                return score
            print(f"Enter a value between 0 and {maximum}.")
        except ValueError:
            print("Please enter a valid integer.")


def review_result(file_path):
    path = Path(file_path)

    if not path.exists():
        print(f"File not found: {path}")
        return

    with path.open("r", encoding="utf-8") as file:
        result = json.load(file)

    if result.get("review_status") == "reviewed":
        print("This result has already been reviewed.")
        return

    print("\nAIREP Human Review")
    print("=" * 50)
    print("Question ID:", result.get("benchmark_question_id"))
    print("Mode:", result.get("evaluation_mode"))
    print("Model:", result.get("model"))

    print("\nQuestion:")
    print(result.get("question"))

    print("\nExpected answer:")
    print(result.get("expected_answer"))

    print("\nModel answer:")
    print(result.get("model_answer"))

    accuracy = get_score("Accuracy", 40)
    reasoning = get_score("Reasoning", 15)

    if result.get("evaluation_mode") == "evidence_assisted":
        source_quality = get_score("Source Quality", 20)
        evidence_support = get_score("Evidence Support", 25)
    else:
        source_quality = None
        evidence_support = None

    notes = input("\nReviewer notes: ").strip()

    applicable_score = accuracy + reasoning
    applicable_max = 55

    if source_quality is not None:
        applicable_score += source_quality + evidence_support
        applicable_max += 45

    result["human_review"] = {
        "accuracy": accuracy,
        "reasoning": reasoning,
        "source_quality": source_quality,
        "evidence_support": evidence_support,
        "applicable_score": applicable_score,
        "applicable_max_score": applicable_max,
        "reviewer_notes": notes,
        "reviewed_at": datetime.now(timezone.utc).isoformat()
    }

    result["review_status"] = "reviewed"

    with path.open("w", encoding="utf-8") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)

    print("\nReview saved successfully.")
    print(f"Score: {applicable_score}/{applicable_max}")
    print(f"Updated file: {path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python evaluation/review_result.py <result.json>")
        sys.exit(1)

    review_result(sys.argv[1])
