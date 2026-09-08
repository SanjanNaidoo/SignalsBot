# Evaluation protocol v0.1

Written before the system exists, and frozen before tuning begins. Freezing it is what is gonna let the report claim the results were not fitted to the benchmark.

## Hypothesis

Stated before any training run, so the result cannot be a story fitted afterwards.

> **H1 (primary).** A fine-tuned open-weights 7B with retrieval over the EEE4114F
> corpus (`C2-oss-tuned`) scores higher on correctness than a frontier model with the
> course prompt but no corpus (`C1-prompted`).

The claim being tested is that **access to the course's own material is worth more than
raw model capability**, on questions about that course. That is the question a department
actually faces when deciding what to deploy, and it is winnable on a student GPU.

`C2-rag` is deliberately **not** the bar. It is the ceiling reference — the same pipeline
with an unlimited model budget — and it bounds how much of the gap is the corpus versus
the model. H1 failing is a reportable result; it would mean the corpus does not carry
enough of the load on this course, which is a finding about DSP tutoring, not a failure of
method.

## Conditions compared

Two arms. Read **down** an arm for the effect of retrieval; read **across** the arms for
the effect of the model. Everything else — items, corpus, prompt, policy — is held equal.

**Hosted arm** (frontier, Claude)

`C0-baseline` — no retrieval, no course prompt
`C1-prompted` — course system prompt, still no retrieval — **the bar for H1**
`C2-rag` — full pipeline: retrieval over the EEE4114F corpus + policy prompt
`C3-money` / `C3-effort-low` / `C3-topk-3` — one variable each away from C2-rag: cheaper
model tier, lower thinking effort, fewer retrieved chunks

**Open arm** (Qwen2.5-7B-Instruct, self-hosted)

`C0-oss` — no retrieval, no course prompt
`C1-oss` — course system prompt, no retrieval
`C2-oss` — full pipeline, model **not** fine-tuned
`C2-oss-tuned` — full pipeline, fine-tuned on the corpus — **the proposed system**

`C2-oss` exists so that any gain from `C2-oss-tuned` can be attributed to the fine-tuning
rather than to the retrieval. Without it the headline number is uninterpretable.

**Cross-model ungrounded baseline** (`C0-gpt`, `C0-gemini`, `C0-grok`, `C0-deepseek`)

The same bare question — no system prompt, no retrieval — sent to other frontier models at
each provider's *default* settings, via their APIs. This is what a student gets by pasting
the question into a chat box. It is run through the API rather than the web interface
because every web interface wraps the question in the vendor's own hidden system prompt
and may invoke tools; only the API call is unprompted, and only the API call can be
recorded exactly.

It answers a question the single-model `C0-baseline` cannot: which frontier model is the
strongest ungrounded baseline. That bounds how much of the C1/C2 gap is the course prompt
and the corpus, versus simply the choice of model. If another model's bare answer already
beats the grounded Claude pipeline, the project's contribution is smaller than it looks,
and the report must say so.

The open arm is greedy-decoded with a fixed seed, so it is exactly reproducible. The
hosted arm is not — those models expose no temperature — so its run-to-run spread is
measured with `--repeats 3` instead of assumed away.

## Contamination rule

Any corpus file used to write a benchmark item is recorded in `corpus/raw/MANIFEST.md`
under *Held out of training* and **must not** appear in the fine-tuning set. Training on
benchmark material would invalidate every claim in this document.

## Metrics

- **Correctness** — fraction of `must_include` points present. 0.0–1.0.
- **Hard fail** — any `must_not_include` string's claim is present. Boolean. Report the rate
  separately; a wrong answer delivered confidently is worse than a refusal, and averaging it into a mean score hides that.
- **Citation validity** (C2+ exclusive) — does each cited chunk actually support the claim it is attached to? Fabricated or irrelevant citations count as hard fails.
- **Policy adherence** pass/fail on the behaviour, judged separately from factual correctness.

