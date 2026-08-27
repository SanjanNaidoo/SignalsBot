# Benchmark item schema

One JSON object per line (`.jsonl`). Items are the report's evidence base — write them
before the chatbot exists, and freeze the set before you start tuning, so that later
improvements cannot be accused of having been fitted to the test.

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Stable, unique. `<course>-<topic>-<nnn>`. Never reuse. |
| `topic` | string | Topic id from the course config. |
| `type` | enum | `concept` \| `calculation` \| `derivation` \| `error_finding` \| `scope` \| `integrity` |
| `question` | string | Exactly what is sent to the system under test. |
| `reference_answer` | string | The correct response, as the course would give it. |
| `must_include` | string[] | Substantive points a correct answer contains. Graded per point. |
| `must_not_include` | string[] | Known failure modes. Any hit is an automatic fail on that item. |
| `source` | string\|null | Corpus provenance. `null` until the corpus is catalogued. |
| `difficulty` | 1\|2\|3 | 1 = recall, 2 = application, 3 = synthesis. |

## The item types that carry the marks

`error_finding` and `integrity` are the two the brief explicitly calls for and the two a
generic chatbot handles worst — they are where your results will differentiate.

- **`error_finding`** — the brief asks for "identifying errors in calculations". Give the
  system a worked solution containing one planted, realistic student mistake. A correct
  response locates the error, not merely produces the right answer alongside it.
- **`integrity`** — a request to simply do assessed work. Correct behaviour is scaffolding
  toward the method, not supplying the answer. Grade this explicitly; a tutor that does a
  student's assignment is a project failure regardless of its accuracy score.
- **`scope`** — a question from a neighbouring course. Correct behaviour is declining and
  saying so, not answering fluently from general knowledge. This is your hallucination probe.

## Coverage target

Aim for ≥ 15 items per topic, with every type represented in each topic, before you run
anything. Roughly 120 items. That is enough to see a real difference between conditions
and small enough to grade by hand in an afternoon.
