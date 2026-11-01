# AIREP - AI Research & Evaluation Platform

## Project Goals

AIREP evaluates how language models answer research questions using either internal knowledge or supplied evidence.

The platform aims to:

- Build a structured research benchmark.
- Compare closed-book and evidence-assisted answers.
- Evaluate factual accuracy, source quality, evidence support, and reasoning.
- Support human review and failure analysis.
- Generate JSON and Markdown reports.
- Distinguish source accessibility from factual verification.

## Current Implementation

The current benchmark contains 11 draft questions across five categories:

| Category | Questions |
|---|---:|
| Fact verification | 5 |
| Source reliability | 2 |
| Multi-hop research | 2 |
| Temporal accuracy | 1 |
| Answer grounding | 1 |
| **Total** | **11** |

The long-term target is 100 questions. The current benchmark is not yet complete.

## Evaluation Methodology

AIREP uses four evaluation dimensions:

| Dimension | Weight |
|---|---:|
| Accuracy | 40% |
| Source quality | 20% |
| Evidence support | 25% |
| Reasoning | 15% |
| **Total** | **100%** |

The platform compares two answer modes:

1. **Closed-book:** The model answers without supplied evidence.
2. **Evidence-assisted:** The model answers using supplied research evidence.

Evaluation results can be reviewed by a human evaluator. Automated checks and source accessibility checks do not independently prove that an answer is factually correct.

## Project Limitations

- The benchmark currently contains only 11 draft questions.
- Results from a small number of questions or models are preliminary.
- Human review is important when judging answer quality and evidence support.
- An accessible source URL does not necessarily support the answer.
- AIREP is a research and evaluation platform, not an automated fact-checking authority.

## Installation

1. Clone the repository using: git clone git@github.com:elsayed-ai-sec/ai-research-fact-check-benchmark.git
2. Enter the project directory: cd ai-research-fact-check-benchmark
3. Create a virtual environment: python3 -m venv venv
4. Activate it: source venv/bin/activate
5. Install dependencies: pip install -r requirements.txt

## Run Tests

Run the automated test suite:

    python -m pytest -v

Validate the benchmark structure:

    python tests/validate_benchmark.py
