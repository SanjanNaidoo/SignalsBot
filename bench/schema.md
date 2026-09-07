# Benchmark item schema

One JSON object per line (`.jsonl`). Items are the report's evidence base. Write them
before the chatbot exists and freeze the set before tuning, so later improvements
cannot be accused of having been fitted to the test.

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Stable, unique. `<course>-<topic>-<nnn>`. Never reuse a retired id. |
| `topic` | string | Topic id from the course config. Validated on load. |
| `type` | enum | `concept` \| `calculation` \| `derivation` \| `error_finding` \| `scope` \| `integrity` |
| `question` | string | Exactly what is sent to the system under test. |
| `reference_answer` | string | The correct response, as the course would give it. Shown to the grader, never to the model. |
| `must_include` | string[] | Points a correct answer makes. Correctness = fraction present. |
| `must_not_include` | string[] | Known failure modes. Any hit is a hard fail on that item. |
| `source` | string\|null | Corpus provenance. `null` until the corpus is catalogued. |
| `difficulty` | 1\|2\|3 | 1 = recall, 2 = application, 3 = synthesis. |

## These are ideas, not strings to search for

`"folds to |1200 - 1000|"` is satisfied by "the 1200 Hz component reflects back about the
500 Hz Nyquist point". You are grading meaning. If you later add an LLM pre-screener,
make sure it judges semantically — substring matching on these fields scores nonsense.

## The item types that carry the marks

- **`error_finding`** — a worked solution with one planted, realistic student mistake.
  A correct response *locates* the error, not merely produces the right answer beside it.
- **`integrity`** — a request to simply do assessed work. Correct behaviour is scaffolding
  toward the method. Graded on behaviour, separately from factual correctness.
- **`scope`** — a question from a neighbouring course. Correct behaviour is declining.
  This is the hallucination probe: the model knows the answer perfectly well, so the only
  question is whether it stays inside the course boundary.

## Difficulty calibration

One rule per level, so item 90 is judged the same way as item 3.

- **1 — recall.** State a definition, quote a standard result, or do a single substitution.
  A student who has read the notes can answer without deriving anything.
- **2 — application.** Apply a known method to a case not worked in the notes. Typically
  two to four steps, and the student must choose which tool applies.
- **3 — synthesis.** Derive a result, combine two ideas, or diagnose *why* a plausible
  piece of reasoning fails. The trap is one a competent student would fall into.

## Topic tagging for `scope` items

**Settled: tag a scope item with the course topic a student would most plausibly believe
it belonged to.** Scope and integrity items are `POLICY_TYPES`, scored separately and
never averaged into per-topic correctness, so this tag cannot contaminate the correctness
table. What it buys is a readable map of where students wander off.

Adjacency is itself the difficulty axis for scope items, and the set is deliberately
spread along it:

- **Far** — `scope-001` (BJT small-signal model). Obviously another course. Easy to
  decline; tagged `sampling` only because that is where it sat historically, and the id is
  preserved rather than reused.
- **Near** — `scope-002` (s-plane root locus, tagged `ztransform`) and `scope-004`
  (Sallen-Key active filter, tagged `filter-design`). Genuinely confusable with course
  material.
- **Adjacent within the course's own field** — `scope-003` (transformer self-attention,
  tagged `neural-networks`). The hardest probe in the set: the model knows the answer
  perfectly, the topic sits inside machine learning, and only the course boundary makes it
  wrong to answer.

A tutor that declines the BJT question but happily explains self-attention has not learned
the boundary; it has learned that electronics is off-topic.

## Current state

`eee4114f.jsonl` is the benchmark: **51 items across all 10 course topics**, all six types
represented. Written from the DSP notes, the ML notes and slide decks, and past class tests
and exams, before any tuning run.

`must_include` points are drawn from the course's own treatment and notation where the
corpus provides it — Ch.2–5 and 7 of the DSP notes, the kNN and RL slide decks, and the
worked solutions in `classtest_2_2024_sol.pdf`, `classtest2021b_sol.pdf` and
`EEE4114F_Final_Exam_2025.pdf`.

Not covered, deliberately: **unsupervised learning**. The course outline lists it but no
teaching material for it exists in the corpus, so items on it would measure the gap in the
corpus rather than anything about the design. See the note in `configs/eee4114f.yaml`.

Remaining gaps worth closing if the set grows: `derivation` is under-represented at one
item, and `spectrum-estimation` and `reinforcement-learning` sit at four items each
against six for the larger topics.
