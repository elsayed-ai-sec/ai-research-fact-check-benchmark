import json
from pathlib import Path
import run_benchmark


def test_load_tasks_returns_two_tasks():
    tasks = run_benchmark.load_tasks()
    assert isinstance(tasks, list)
    assert len(tasks) == 2


def test_all_tasks_have_valid_structure():
    tasks = run_benchmark.load_tasks()
    for task in tasks:
        valid, message = run_benchmark.validate_task(task)
        assert valid, f"{task.get('id', 'UNKNOWN')}: {message}"


def test_missing_required_field_is_rejected():
    task = {
        "id": "TEST-001",
        "question": "Test question?",
        "source_name": "Example",
        "source_url": "https://example.com",
        "category": "test",
        "verification_status": "verified",
    }
    valid, message = run_benchmark.validate_task(task)
    assert not valid
    assert "expected_answer" in message


def test_invalid_source_url_is_rejected():
    task = {
        "id": "TEST-002",
        "question": "Test question?",
        "expected_answer": "Test answer",
        "source_name": "Example",
        "source_url": "ftp://example.com",
        "category": "test",
        "verification_status": "verified",
    }
    valid, message = run_benchmark.validate_task(task)
    assert not valid
    assert "Source URL" in message


def test_invalid_url_without_hostname_is_rejected():
    task = {
        "id": "TEST-003",
        "question": "Test question?",
        "expected_answer": "Test answer",
        "source_name": "Example",
        "source_url": "https://",
        "category": "test",
        "verification_status": "verified",
    }
    valid, message = run_benchmark.validate_task(task)
    assert not valid
    assert "valid HTTP or HTTPS URL" in message


def test_unknown_verification_status_is_rejected():
    task = {
        "id": "TEST-004",
        "question": "Test question?",
        "expected_answer": "Test answer",
        "source_name": "Example",
        "source_url": "https://example.com",
        "category": "test",
        "verification_status": "maybe",
    }
    valid, message = run_benchmark.validate_task(task)
    assert not valid
    assert "Unknown verification_status" in message
