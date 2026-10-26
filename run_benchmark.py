import json
from pathlib import Path
from datetime import datetime, timezone
from verify_sources import check_source
from urllib.parse import urlparse

TASKS_FILE = Path("tasks/benchmark_tasks.json")
RESULTS_DIR = Path("results")
REPORTS_DIR = Path("reports")

REQUIRED_FIELDS = [
    "id",
    "question",
    "expected_answer",
    "source_name",
    "source_url",
    "category",
    "verification_status",
]

ALLOWED_VERIFICATION_STATUSES = {
    "verified",
    "needs_verification",
}


def load_tasks():
    with TASKS_FILE.open("r", encoding="utf-8") as file:
        tasks = json.load(file)

    if not isinstance(tasks, list):
        raise ValueError("The benchmark file must contain a JSON list.")

    return tasks


def validate_task(task):
    if not isinstance(task, dict):
        return False, "Task must be a JSON object."

    missing = [
        field for field in REQUIRED_FIELDS
        if not task.get(field)
    ]

    if missing:
        return False, f"Missing fields: {', '.join(missing)}"

    parsed_url = urlparse(task["source_url"])

    if (
        parsed_url.scheme not in ("http", "https")
        or not parsed_url.hostname
    ):
        return False, "Source URL must be a valid HTTP or HTTPS URL."

    if task["verification_status"] not in ALLOWED_VERIFICATION_STATUSES:
        return False, "Unknown verification_status."

    return True, "Task structure is valid."


def run_benchmark():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    tasks = load_tasks()
    results = []

    for task in tasks:
        valid, message = validate_task(task)

        if not valid:
            status = "ERROR"
        elif task["verification_status"] == "verified":
            status = "SOURCE_CHECK_COMPLETED"
        else:
            status = "NEEDS_VERIFICATION"

        source_result = check_source(task) if valid else {
            "source_check": "NOT_RUN_INVALID_TASK",
            "fact_verification": "NOT_AUTOMATICALLY_VERIFIED",
            "detail": message,
        }

        results.append({
            "source_result": source_result,
            "id": task.get("id", "UNKNOWN") if isinstance(task, dict) else "UNKNOWN",
            "question": task.get("question", "") if isinstance(task, dict) else "",
            "status": status,
            "validation_message": message,
            "source_name": task.get("source_name", "") if isinstance(task, dict) else "",
            "source_url": task.get("source_url", "") if isinstance(task, dict) else "",
            "expected_answer": task.get("expected_answer", "") if isinstance(task, dict) else "",
        })

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    results_file = RESULTS_DIR / f"benchmark_{timestamp}.json"
    report_file = REPORTS_DIR / f"benchmark_{timestamp}.md"

    with results_file.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)

    counts = {}
    for result in results:
        status = result["status"]
        counts[status] = counts.get(status, 0) + 1

    lines = [
        "# Fact-Checking Benchmark Report",
        "",
        f"- Generated at: {timestamp}",
        f"- Total tasks: {len(results)}",
        "",
        "## Summary",
        "",
    ]

    for status, count in sorted(counts.items()):
        lines.append(f"- {status}: {count}")

    lines.extend(["", "## Task Results", ""])

    for result in results:
        lines.extend([
            f"### {result['id']}",
            f"- Status: {result['status']}",
            f"- Question: {result['question']}",
            f"- Validation: {result['validation_message']}",
            f"- Source: {result['source_name']}",
            f"- URL: {result['source_url']}",
            f"- Source check: {result['source_result'].get('source_check', 'UNKNOWN')}",
            f"- Fact verification: {result['source_result'].get('fact_verification', 'NOT_AUTOMATICALLY_VERIFIED')}",
            f"- Source detail: {result['source_result'].get('detail', '')}",
            "",
        ])

    report_file.write_text("\n".join(lines), encoding="utf-8")

    print(f"Tasks loaded: {len(tasks)}")
    print(f"Results saved to: {results_file}")
    print(f"Report saved to: {report_file}")
    print("\nStatus summary:")

    for status, count in sorted(counts.items()):
        print(f"  {status}: {count}")


if __name__ == "__main__":
    try:
        run_benchmark()
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"Benchmark failed: {error}")
        raise SystemExit(1)
