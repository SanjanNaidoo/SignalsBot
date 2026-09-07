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

## Current state

`eee4114f.seed.jsonl` holds 8 seed items covering the three topics currently in
`configs/eee4114f.yaml`, with all six types represented. **This is a demonstration set,
not the benchmark.** Target is ~15 items per topic, roughly 120 total, written from
tutorials and past papers with worked solutions.

Two conventions to settle before the set grows:

1. **Topic tagging for `scope` items.** `eee4114f-scope-001` asks a BJT question but is
   tagged `sampling`, which is not true of the question. Either give scope items their own
   tag or tag them by the topic the student believed they were asking about — but decide
   now, because it determines whether the per-topic table means anything.
2. **Difficulty calibration.** Write a one-line rule per level so item 90 is judged the
   same way as item 3.
