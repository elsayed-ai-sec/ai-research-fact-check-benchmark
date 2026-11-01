import json
from pathlib import Path
from datetime import datetime, timezone

BASELINE_FILE = Path("reports/BASELINE-20261031T165836Z.json")
EVIDENCE_FILE = Path("reports/EVIDENCE-20261031T170820Z.json")
OUTPUT_FILE = Path("reports/failure-analysis-AIREP-011.json")


def load_json(path):
    if not path.exists():
        raise FileNotFoundError(path)

    return json.loads(path.read_text(encoding="utf-8"))


def main():
    baseline = load_json(BASELINE_FILE)
    evidence = load_json(EVIDENCE_FILE)

    analysis = {
        "benchmark_question_id": "AIREP-011",
        "model": baseline["model"],
        "analysis_type": "human_review_based",
        "failures": [
            {
                "evaluation_mode": "closed_book_baseline",
                "failure_types": [
                    "factual_error",
                    "incomplete_answer",
                    "reasoning_error"
                ],
                "observations": [
                    "Both report numbers were incorrect.",
                    "The relationship between the reports was inaccurately described."
                ]
            },
            {
                "evaluation_mode": "evidence_assisted",
                "failure_types": [
                    "incomplete_answer",
                    "false_abstention",
                    "citation_failure"
                ],
                "observations": [
                    "Both report numbers were correct.",
                    "The model did not explicitly identify Generative AI.",
                    "The model claimed the supplied evidence did not specify the technology.",
                    "The answer did not cite the supplied source titles."
                ]
            }
        ],
        "overall_finding": (
            "Providing evidence improved factual accuracy on this question, "
            "but did not guarantee answer completeness or correct evidence use."
        ),
        "limitations": [
            "Analysis is based on one benchmark question.",
            "Failure labels were assigned through human review.",
            "Results do not establish general model performance."
        ],
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    OUTPUT_FILE.parent.mkdir(exist_ok=True)

    OUTPUT_FILE.write_text(
        json.dumps(analysis, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

    print("Failure analysis saved:", OUTPUT_FILE)
    print("Analysis type:", analysis["analysis_type"])
    print("Evaluations analyzed:", len(analysis["failures"]))


if __name__ == "__main__":
    main()
