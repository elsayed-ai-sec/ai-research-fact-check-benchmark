# AIREP Evaluation Comparison

## Evaluation Details

- Question ID: AIREP-011
- Model: qwen2.5:1.5b
- Baseline mode: closed_book_baseline
- Evidence mode: evidence_assisted

## Comparable Criteria

Only Accuracy and Reasoning are compared because both evaluations
have scores for these criteria.

| Criterion | Closed-book | Evidence-assisted |
|---|---:|---:|
| Accuracy | 10/40 | 35/40 |
| Reasoning | 4/15 | 11/15 |
| Combined | 14/55 (25.45%) | 46/55 (83.64%) |

## Difference

- Score change: +58.18 percentage points.

## Additional Evidence-assisted Criteria

- Source Quality: 20/20
- Evidence Support: 20/25

These criteria are excluded from the direct comparison because
they were not assessed in the closed-book evaluation.

## Failure Analysis

### Closed-book

Correctly identified Generative AI, but both report numbers were incorrect.

Attempted to explain the relationship, but described it inaccurately.

### Evidence-assisted

Both report numbers are correct. The relationship is partially explained, but the technology is not explicitly identified.

The model identifies the relationship but fails to explicitly extract Generative AI as the technology.

## Limitations

This comparison covers one benchmark question and one model.
The results are preliminary and do not establish general model performance.

Generated at: 2026-10-31T17:12:06.920344+00:00
