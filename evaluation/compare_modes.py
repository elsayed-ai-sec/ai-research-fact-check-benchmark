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

    if not isinstance(review, dict):
        raise ValueError(
            f"Human review missing in {data.get('evaluation_id')}"
        )

    outer_status = data.get("review_status")
    inner_status = review.get("review_status")

    if outer_status != "reviewed" and inner_status != "reviewed":
        raise ValueError(
            f"Completed human review missing in {data.get('evaluation_id')}"
        )

    return review


def score_value(review, criterion):
    value = review.get(criterion)

    if isinstance(value, dict):
        value = value.get("score")

    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"Invalid or missing score: {criterion}")

    return value


def criterion_notes(review, criterion):
    value = review.get(criterion)

    if isinstance(value, dict):
        return value.get("notes", "No notes provided.")

    return review.get("reviewer_notes", "No notes provided.")


def common_score(review):
    maxima = {"accuracy": 40, "reasoning": 15}

    earned = 0

    for criterion, maximum in maxima.items():
        score = score_value(review, criterion)

        if not 0 <= score <= maximum:
            raise ValueError(f"Score out of range: {criterion}")

        earned += score

    maximum = sum(maxima.values())

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
| Accuracy | {score_value(baseline_review, 'accuracy')}/{40} | {score_value(evidence_review, 'accuracy')}/{40} |
| Reasoning | {score_value(baseline_review, 'reasoning')}/{15} | {score_value(evidence_review, 'reasoning')}/{15} |
| Combined | {baseline_score[0]}/{baseline_score[1]} ({baseline_score[2]:.2f}%) | {evidence_score[0]}/{evidence_score[1]} ({evidence_score[2]:.2f}%) |

## Difference

- Score change: {improvement:+.2f} percentage points.

## Additional Evidence-assisted Criteria

- Source Quality: {score_value(evidence_review, 'source_quality')}/{20}
- Evidence Support: {score_value(evidence_review, 'evidence_support')}/{25}

These criteria are excluded from the direct comparison because
they were not assessed in the closed-book evaluation.

## Failure Analysis

### Closed-book

{criterion_notes(baseline_review, 'accuracy')}

{criterion_notes(baseline_review, 'reasoning')}

### Evidence-assisted

{criterion_notes(evidence_review, 'accuracy')}

{criterion_notes(evidence_review, 'reasoning')}

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
