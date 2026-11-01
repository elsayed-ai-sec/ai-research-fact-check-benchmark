import json
import urllib.request
import urllib.error
from collections import Counter

BENCHMARK_FILE = "benchmarks/questions.json"
TIMEOUT = 15


def check_url(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "AIREP-Research-Evaluation/1.0"},
        method="HEAD"
    )

    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return response.status, "Reachable"

    except urllib.error.HTTPError as error:
        if error.code in (403, 405, 501):
            try:
                request = urllib.request.Request(
                    url,
                    headers={
                        "User-Agent": "AIREP-Research-Evaluation/1.0",
                        "Range": "bytes=0-0"
                    },
                    method="GET"
                )
                with urllib.request.urlopen(
                    request, timeout=TIMEOUT
                ) as response:
                    return response.status, "Reachable"

            except Exception as retry_error:
                return error.code, str(retry_error)

        return error.code, str(error)

    except Exception as error:
        return None, str(error)


def main():
    with open(BENCHMARK_FILE, encoding="utf-8") as file:
        questions = json.load(file)

    checked_urls = {}

    for question in questions:
        for source in question.get("evidence", []):
            url = source.get("url")

            if url and url not in checked_urls:
                checked_urls[url] = check_url(url)

    print("\n========== AIREP SOURCE CHECKER ==========")

    reachable = 0
    failed = 0

    for url, (status, message) in checked_urls.items():
        if status is not None and 200 <= status < 400:
            reachable += 1
            result = "REACHABLE"
        else:
            failed += 1
            result = "CHECK NEEDED"

        print(f"\n[{result}] {url}")
        print(f"Status: {status}")
        if result == "CHECK NEEDED":
            print(f"Details: {message}")

    print("\n========== SUMMARY ==========")
    print(f"Unique URLs: {len(checked_urls)}")
    print(f"Reachable: {reachable}")
    print(f"Need checking: {failed}")

    print("\nNote: Reachability does not prove that a source")
    print("supports the answer. Evidence must be reviewed separately.")


if __name__ == "__main__":
    main()
