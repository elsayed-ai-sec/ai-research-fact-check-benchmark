import json
import re
import urllib.request
import urllib.error
from html.parser import HTMLParser
from pathlib import Path

TASKS_FILE = Path("tasks/benchmark_tasks.json")


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data):
        if not self.skip_depth:
            self.parts.append(data)


def normalize(text):
    return re.sub(r"\s+", " ", text).strip().casefold()


def check_source(task):
    request = urllib.request.Request(
        task["source_url"],
        headers={"User-Agent": "Mozilla/5.0 (compatible; FactCheckBenchmark/1.0)"}
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            html = response.read().decode("utf-8", errors="replace")
            status_code = response.status

        parser = TextExtractor()
        parser.feed(html)
        page_text = normalize(" ".join(parser.parts))
        expected = normalize(task["expected_answer"])

        if expected in page_text:
            result = "EVIDENCE_MATCH"
        else:
            result = "EVIDENCE_NOT_FOUND"

        return {
            "task_id": task["id"],
            "source_check": result,
            "http_status": status_code,
            "fact_verification": "NOT_AUTOMATICALLY_VERIFIED",
            "detail": "Text matching is preliminary evidence only.",
        }

    except urllib.error.HTTPError as error:
        return {
            "task_id": task["id"],
            "source_check": "SOURCE_ACCESS_BLOCKED",
            "http_status": error.code,
            "fact_verification": "NOT_AUTOMATICALLY_VERIFIED",
            "detail": str(error),
        }
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return {
            "task_id": task["id"],
            "source_check": "SOURCE_ERROR",
            "http_status": None,
            "fact_verification": "NOT_AUTOMATICALLY_VERIFIED",
            "detail": str(error),
        }


def main():
    tasks = json.loads(TASKS_FILE.read_text(encoding="utf-8"))

    for task in tasks:
        result = check_source(task)
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
