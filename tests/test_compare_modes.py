import pytest

from evaluation.compare_modes import get_review, common_score, score_value, criterion_notes


def test_get_review_reads_current_review_format():
    result = {
        "review_status": "reviewed",
        "human_review": {
            "accuracy": 35,
            "reasoning": 10,
            "reviewer_notes": "Good answer"
        }
    }

    review = get_review(result)

    assert review["accuracy"] == 35
    assert review["reasoning"] == 10


def test_get_review_rejects_pending_review():
    result = {
        "review_status": "pending_human_review",
        "human_review": {}
    }

    with pytest.raises(ValueError):
        get_review(result)


def test_common_score_calculates_shared_score():
    review = {
        "accuracy": 35,
        "reasoning": 10
    }

    earned, maximum, percentage = common_score(review)

    assert earned == 45
    assert maximum == 55
    assert percentage == pytest.approx(81.818, rel=1e-3)


def test_common_score_rejects_missing_criteria():
    review = {"accuracy": 35}

    with pytest.raises(ValueError):
        common_score(review)


def test_get_review_accepts_legacy_completed_review():
    result = {
        "review_status": "pending_human_review",
        "human_review": {
            "review_status": "reviewed",
            "accuracy": {"score": 10, "max_score": 40, "notes": "Old format"},
            "reasoning": {"score": 4, "max_score": 15, "notes": "Old format"}
        }
    }

    review = get_review(result)

    assert review["accuracy"]["score"] == 10


def test_common_score_calculates_legacy_review_format():
    review = {
        "accuracy": {"score": 10, "max_score": 40},
        "reasoning": {"score": 4, "max_score": 15}
    }

    earned, maximum, percentage = common_score(review)

    assert earned == 14
    assert maximum == 55
    assert percentage == pytest.approx(25.4545, rel=1e-3)



def test_score_value_reads_legacy_additional_criteria():
    review = {
        "source_quality": {"score": 20, "max_score": 20}
    }
    assert score_value(review, "source_quality") == 20


def test_score_value_reads_current_additional_criteria():
    review = {"evidence_support": 20}
    assert score_value(review, "evidence_support") == 20


def test_criterion_notes_supports_both_formats():
    legacy = {
        "accuracy": {"score": 35, "notes": "Legacy note"}
    }
    current = {"reviewer_notes": "Current note"}

    assert criterion_notes(legacy, "accuracy") == "Legacy note"
    assert criterion_notes(current, "accuracy") == "Current note"


def test_common_score_rejects_out_of_range_score():
    review = {"accuracy": 41, "reasoning": 10}

    with pytest.raises(ValueError):
        common_score(review)
