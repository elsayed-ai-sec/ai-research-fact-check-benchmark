import json
import tempfile
import unittest
from pathlib import Path

from evaluation.aggregate_report import (
    discover_latest_results,
    reviewed_result,
    shared_score,
    build_report
)


class TestAggregateReport(unittest.TestCase):

    def test_latest_result_is_selected(self):
        with tempfile.TemporaryDirectory() as temp:
            for filename, timestamp in [
                ("BASELINE-AIREP-001-old.json", "2026-10-30T10:00:00+00:00"),
                ("BASELINE-AIREP-001-new.json", "2026-10-31T10:00:00+00:00")
            ]:
                data = {
                    "benchmark_question_id": "AIREP-001",
                    "evaluation_mode": "closed_book_baseline",
                    "created_at": timestamp
                }
                Path(temp, filename).write_text(json.dumps(data))

            results, superseded = discover_latest_results(Path(temp))

            self.assertEqual(len(results), 1)
            self.assertEqual(superseded, 1)
            self.assertIn("2026-10-31", results[0]["created_at"])

    def test_shared_score_calculation(self):
        review = {"accuracy": 35, "reasoning": 10}
        self.assertEqual(shared_score(review), 45)

    def test_pending_result_is_not_reviewed(self):
        result = {
            "review_status": "pending_human_review",
            "human_review": {}
        }
        self.assertFalse(reviewed_result(result))

    def test_report_uses_comparable_scores(self):
        results = [
            {
                "benchmark_question_id": "AIREP-001",
                "evaluation_mode": "closed_book_baseline",
                "review_status": "reviewed",
                "human_review": {"accuracy": 0, "reasoning": 0}
            },
            {
                "benchmark_question_id": "AIREP-001",
                "evaluation_mode": "evidence_assisted",
                "review_status": "reviewed",
                "human_review": {
                    "accuracy": 35,
                    "reasoning": 10,
                    "source_quality": 20,
                    "evidence_support": 20,
                    "applicable_score": 85,
                    "applicable_max_score": 100
                }
            }
        ]

        report = build_report(results, 0)

        self.assertIn("0/55", report)
        self.assertIn("45/55", report)
        self.assertIn("85/100", report)

    def test_corrupted_json_is_skipped(self):
        with tempfile.TemporaryDirectory() as temp:
            Path(temp, "BASELINE-AIREP-001-broken.json").write_text(
                "{invalid json",
                encoding="utf-8"
            )

            results, superseded = discover_latest_results(Path(temp))

            self.assertEqual(results, [])
            self.assertEqual(superseded, 0)

    def test_report_handles_no_completed_reviews(self):
        results = [{
            "benchmark_question_id": "AIREP-001",
            "evaluation_mode": "closed_book_baseline",
            "review_status": "pending_human_review",
            "human_review": {}
        }]

        report = build_report(results, 0)

        self.assertIn("Reviewed: 0", report)
        self.assertIn("Pending: 1", report)
        self.assertNotIn("nan", report.lower())


if __name__ == "__main__":
    unittest.main()
