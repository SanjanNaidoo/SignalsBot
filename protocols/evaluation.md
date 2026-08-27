# Evaluation protocol v0.1

Written before the system exists, and frozen before tuning begins. Freezing it is what
lets the report claim the results were not fitted to the benchmark.

## Conditions compared

| Condition | Description | Purpose |
|---|---|---|
| `C0-baseline` | Frontier model, no retrieval, no course prompt | The honest control. If C0 already scores well, the project's contribution is the *policy* layer, not the retrieval — and the report must say so. |
| `C1-prompted` | Same model, course system prompt, still no retrieval | Isolates how much comes from prompting alone. Frequently overlooked; usually a large share. |
| `C2-rag` | Full pipeline: retrieval over the EEE4114F corpus + policy prompt | The proposed system. |
| `C3-*` | One variant per design choice under investigation (chunk size, top-k, reranking, ...) | GA4 evidence. One variable per condition. |

C1 is the condition most projects skip, and the one an examiner will ask about. Run it.

## Metrics

**Per item, graded by a human against `must_include` / `must_not_include`:**

- **Correctness** — fraction of `must_include` points present. 0.0–1.0.
- **Hard fail** — any `must_not_include` string's claim is present. Boolean. Report the rate
  separately; a wrong answer delivered confidently is worse than a refusal, and averaging it
  into a mean score hides that.
- **Citation validity** (C2+ only) — does each cited chunk actually support the claim it is
  attached to? Fabricated or irrelevant citations count as hard fails.
- **Policy adherence** (`integrity` and `scope` items) — pass/fail on the behaviour, judged
  separately from factual correctness.

**Aggregate:** mean correctness and hard-fail rate, reported per topic and per item type.
Report per-type breakdowns — a system can score well overall while failing every
`error_finding` item, and that difference is the interesting result.

## Grading procedure

1. Run every condition over the frozen item set. Persist raw outputs to `runs/<timestamp>-<condition>/`.
2. Grade blind: strip the condition label before grading, and grade one item across all
   conditions at a time. You know which system you built; blinding is the only defence.
3. Have your supervisor independently grade a random 20% subset. Report the agreement rate.
   Two graders on a subset is a defensible, cheap reliability claim for a final-year project,
   and it costs Dr Martin under an hour.

An LLM-as-judge may be used to *pre-screen* at scale, but only if you validate it against
human grades on a subset and report that agreement. Do not let it be the sole grader.

## What is deliberately not measured

No student user study, no interaction logs, no surveys — the filed ethics questionnaire
answers No to data collection and No to human involvement. Every claim in the report about
usefulness to students must be argued from benchmark performance, not from student
experience, unless an ethics amendment is granted first.
