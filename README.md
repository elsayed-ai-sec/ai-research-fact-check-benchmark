# AI Research & Fact-Checking Benchmark

A Python-based evaluation project that checks structured fact-checking tasks, retrieves source pages, compares expected answers with extracted page text, and generates JSON and Markdown reports.

## Project Goals

- Validate benchmark task structure and required fields.
- Check source URL format.
- Retrieve publicly accessible source pages.
- Extract visible page text and perform preliminary exact-text matching.
- Record source-access and evidence-matching outcomes.
- Generate machine-readable JSON results and human-readable Markdown reports.
- Run automated tests with pytest.

## Current Scope

The current benchmark includes two questions about the NIST AI Risk Management Framework (AI RMF 1.0).

The source checker reports:
- `EVIDENCE_MATCH`: the normalized expected answer appears in extracted page text.
- `EVIDENCE_NOT_FOUND`: the expected text was not found.
- `SOURCE_ACCESS_BLOCKED`: the server rejected the request.
- `SOURCE_ERROR`: a network or retrieval error occurred.

These are preliminary source-checking results. Exact-text matching does **not** prove that a claim is true, that the source context supports it, or that the source is authoritative. Fact verification is not yet automated.

## Requirements

- Python 3.13 or compatible Python 3
- pytest 9.x for running tests
- Internet access for live source checks

The source checker currently uses Python's standard library; no third-party HTTP library is required.

## Project Structure

```text
.
├── README.md
├── run_benchmark.py
├── verify_sources.py
├── tasks/
│   ├── benchmark_tasks.json
│   └── sources/
├── tests/
│   ├── test_benchmark.py
│   └── test_verify_sources.py
├── results/
├── reports/
└── docs/
```

## Run the Benchmark

```bash
python3 -m py_compile run_benchmark.py verify_sources.py
python3 -m pytest -v
python3 run_benchmark.py
```

Run source checks directly:

```bash
python3 verify_sources.py
```

The benchmark writes timestamped JSON results under `results/` and Markdown reports under `reports/`.

## Test Coverage

Current tests cover:
- Task loading and structural validation
- Missing required fields
- Invalid source URL formats
- Unknown verification states
- Text normalization
- Extraction of visible page text
- Preliminary text matching behavior

## Limitations and Next Steps

- Exact-text matching can miss paraphrases and may match text without sufficient context.
- A successful HTTP response does not establish factual correctness.
- Live source access can vary because of server policies, network failures, or timeouts.
- The benchmark currently contains only two tasks.

Planned improvements:
1. Add more verified benchmark cases from authoritative sources.
2. Record evidence snippets and page metadata.
3. Add offline tests for source retrieval outcomes.
4. Improve claim-to-evidence comparison beyond exact-text matching.
5. Keep source accessibility, evidence matching, and factual verification as separate outcomes.

## Responsible Evaluation

This project is intended for educational and quality-assurance use. Reports should clearly distinguish observed evidence from conclusions and should not label claims as verified without adequate supporting evidence.
