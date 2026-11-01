import json
from pathlib import Path
from datetime import datetime, timezone

BASELINE_FILE = Path("reports/BASELINE-20261031T165836Z.json")
EVIDENCE_FILE = Path("reports/EVIDENCE-20261031T170820Z.json")
REPORT_DIR = Path("reports")


def load_result(path):
    if not path.exists():
        raise FileNotFoundError(f"Result file not found: {path}")

    return json.loads(path.read_text(encoding="utf-8"))


def get_review(data):
    review = data.get("human_review")

    if not review:
        raise ValueError(
            f"Human review missing in {data.get('evaluation_id')}"
        )

    return review


def common_score(review):
    criteria = ["accuracy", "reasoning"]

    earned = sum(review[c]["score"] for c in criteria)
    maximum = sum(review[c]["max_score"] for c in criteria)

    return earned, maximum, (earned / maximum) * 100


def main():
    baseline = load_result(BASELINE_FILE)
    evidence = load_result(EVIDENCE_FILE)

    if baseline["benchmark_question_id"] != evidence["benchmark_question_id"]:
        raise ValueError("Cannot compare different benchmark questions.")

    baseline_review = get_review(baseline)
    evidence_review = get_review(evidence)

    baseline_score = common_score(baseline_review)
    evidence_score = common_score(evidence_review)

    improvement = evidence_score[2] - baseline_score[2]

    report = f"""# AIREP Evaluation Comparison

## Evaluation Details

- Question ID: {baseline['benchmark_question_id']}
- Model: {baseline['model']}
- Baseline mode: {baseline['evaluation_mode']}
- Evidence mode: {evidence['evaluation_mode']}

## Comparable Criteria

Only Accuracy and Reasoning are compared because both evaluations
have scores for these criteria.

| Criterion | Closed-book | Evidence-assisted |
|---|---:|---:|
| Accuracy | {baseline_review['accuracy']['score']}/{baseline_review['accuracy']['max_score']} | {evidence_review['accuracy']['score']}/{evidence_review['accuracy']['max_score']} |
| Reasoning | {baseline_review['reasoning']['score']}/{baseline_review['reasoning']['max_score']} | {evidence_review['reasoning']['score']}/{evidence_review['reasoning']['max_score']} |
| Combined | {baseline_score[0]}/{baseline_score[1]} ({baseline_score[2]:.2f}%) | {evidence_score[0]}/{evidence_score[1]} ({evidence_score[2]:.2f}%) |

## Difference

- Score change: {improvement:+.2f} percentage points.

## Additional Evidence-assisted Criteria

- Source Quality: {evidence_review['source_quality']['score']}/{evidence_review['source_quality']['max_score']}
- Evidence Support: {evidence_review['evidence_support']['score']}/{evidence_review['evidence_support']['max_score']}

These criteria are excluded from the direct comparison because
they were not assessed in the closed-book evaluation.

## Failure Analysis

### Closed-book

{baseline_review['accuracy']['notes']}

{baseline_review['reasoning']['notes']}

### Evidence-assisted

{evidence_review['accuracy']['notes']}

{evidence_review['reasoning']['notes']}

## Limitations

This comparison covers one benchmark question and one model.
The results are preliminary and do not establish general model performance.

Generated at: {datetime.now(timezone.utc).isoformat()}
"""

    REPORT_DIR.mkdir(exist_ok=True)

    output = REPORT_DIR / "comparison-AIREP-011.md"
    output.write_text(report, encoding="utf-8")

    print("Comparison completed.")
    print(f"Closed-book: {baseline_score[0]}/{baseline_score[1]} ({baseline_score[2]:.2f}%)")
    print(f"Evidence-assisted: {evidence_score[0]}/{evidence_score[1]} ({evidence_score[2]:.2f}%)")
    print(f"Difference: {improvement:+.2f} percentage points")
    print("Report saved to:", output)


if __name__ == "__main__":
    main()
