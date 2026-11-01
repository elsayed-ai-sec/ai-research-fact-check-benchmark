import json
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict


REPORTS_DIR = Path("reports")
OUTPUT_FILE = REPORTS_DIR / "aggregate-report.md"

VALID_MODES = {
    "closed_book_baseline",
    "evidence_assisted"
}


def read_timestamp(result):
    value = result.get("created_at")

    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)


def discover_latest_results(reports_dir=REPORTS_DIR):
    grouped = defaultdict(list)

    for path in reports_dir.glob("*.json"):
        if not (
            path.name.startswith("BASELINE-AIREP-")
            or path.name.startswith("EVIDENCE-AIREP-")
        ):
            continue

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            print(f"Warning: Skipping unreadable file: {path}")
            continue

        question_id = data.get("benchmark_question_id")
        mode = data.get("evaluation_mode")

        if not question_id or mode not in VALID_MODES:
            continue

        key = (question_id, mode)
        grouped[key].append((read_timestamp(data), path, data))

    latest = []
    superseded_count = 0

    for records in grouped.values():
        records.sort(key=lambda item: (item[0], item[1].name))
        latest.append(records[-1][2])
        superseded_count += len(records) - 1

    latest.sort(
        key=lambda item: (
            item.get("benchmark_question_id", ""),
            item.get("evaluation_mode", "")
        )
    )

    return latest, superseded_count


def reviewed_result(result):
    return (
        result.get("review_status") == "reviewed"
        and isinstance(result.get("human_review"), dict)
    )


def shared_score(review):
    return (
        review.get("accuracy", 0)
        + review.get("reasoning", 0)
    )


def build_report(results, superseded_count):
    lines = [
        "# AIREP Aggregate Evaluation Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Evaluation Overview",
        "",
        f"- Latest evaluation records: {len(results)}",
        f"- Superseded historical records excluded: {superseded_count}",
        f"- Questions evaluated: {len(set(r.get('benchmark_question_id') for r in results))}",
        ""
    ]

    modes = {
        "closed_book_baseline": [],
        "evidence_assisted": []
    }

    for result in results:
        modes[result["evaluation_mode"]].append(result)

    for mode, records in modes.items():
        completed = [r for r in records if reviewed_result(r)]
        pending = len(records) - len(completed)

        lines.extend([
            f"## {mode.replace('_', ' ').title()}",
            "",
            f"- Reviewed: {len(completed)}",
            f"- Pending: {pending}"
        ])

        if completed:
            reviews = [r["human_review"] for r in completed]

            common_earned = sum(shared_score(r) for r in reviews)
            common_possible = 55 * len(reviews)

            lines.append(
                f"- Average comparable score (Accuracy + Reasoning): "
                f"{common_earned}/{common_possible} "
                f"({common_earned / common_possible * 100:.2f}%)"
            )

            if mode == "evidence_assisted":
                total_earned = sum(
                    r.get("applicable_score", 0) for r in reviews
                )
                total_possible = sum(
                    r.get("applicable_max_score", 0) for r in reviews
                )

                if total_possible:
                    lines.append(
                        f"- Overall reviewed score: {total_earned}/"
                        f"{total_possible} "
                        f"({total_earned / total_possible * 100:.2f}%)"
                    )

        lines.append("")

    lines.extend([
        "## Per-question Comparison",
        "",
        "| Question | Closed-book (Accuracy + Reasoning) | Evidence-assisted (Accuracy + Reasoning) | Evidence-assisted (Total) |",
        "|---|---:|---:|---:|"
    ])

    question_ids = sorted({
        r.get("benchmark_question_id") for r in results
    })

    lookup = {
        (r.get("benchmark_question_id"), r.get("evaluation_mode")): r
        for r in results
    }

    for question_id in question_ids:
        baseline = lookup.get((question_id, "closed_book_baseline"))
        evidence = lookup.get((question_id, "evidence_assisted"))

        baseline_text = "Pending"
        evidence_shared_text = "Pending"
        evidence_total_text = "Pending"

        if baseline and reviewed_result(baseline):
            review = baseline["human_review"]
            baseline_text = f"{shared_score(review)}/55"

        if evidence and reviewed_result(evidence):
            review = evidence["human_review"]
            evidence_shared_text = f"{shared_score(review)}/55"
            evidence_total_text = (
                f"{review.get('applicable_score', 0)}/"
                f"{review.get('applicable_max_score', 0)}"
            )

        lines.append(
            f"| {question_id} | {baseline_text} | "
            f"{evidence_shared_text} | {evidence_total_text} |"
        )

    lines.extend([
        "",
        "## Methodology and Limitations",
        "",
        "- The report selects the latest saved result for each question and evaluation mode.",
        "- Older records are preserved but excluded when superseded by a newer run.",
        "- Human review scores are used; model responses are not treated as self-validated.",
        "- Cross-mode comparison uses Accuracy and Reasoning only (maximum 55 points).",
        "- Evidence-assisted total scores use all four criteria (maximum 100 points).",
        "- This preliminary batch contains only three questions and one model.",
        "- Results should not be generalized to other models or larger benchmarks.",
        ""
    ])

    return "\n".join(lines)


def main():
    results, superseded_count = discover_latest_results()

    if not results:
        print("No AIREP batch result files found.")
        return

    report = build_report(results, superseded_count)
    OUTPUT_FILE.write_text(report, encoding="utf-8")

    print("Aggregate report generated.")
    print(f"Latest records: {len(results)}")
    print(f"Superseded records excluded: {superseded_count}")
    print(f"Report: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
