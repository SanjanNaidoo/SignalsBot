## Design stance

Retrieval-augmented generation (RAG) over the EEE4114F course corpus, on top of a
frontier model — *not* fine-tuning since the course is way too small for that. Maybe we could do this with all the signal processing courses?

## Repository layout

| Path | Contents |
|---|---|
| `corpus/raw/` | Source course materials, as supplied. **Never committed.** |
| `corpus/processed/` | Extracted + chunked text with provenance metadata. Generated. |
| `configs/` | Per-course configuration. `eee4114f.yaml` is the target course. |
| `bench/` | Benchmark items — the evaluation set the report is built on. |
| `protocols/` | Written evaluation protocols: what is measured, how, and by whom. |
| `runs/` | Timestamped run outputs. Generated, gitignored, regenerable. |
| `grades/` | Human grades. **Committed** — this is expensive human labour, not output. |
| `src/ym07/` | The harness package. |

## Build order

The report is marked on GA1 (justified design choices),
GA4 (investigation and analysis) and GA5 (tool use and benchmarking) — so it's clear that all three need a
measuring instrument that exists before the thing being measured.

1. **Corpus.** Collect and catalogue EEE4114F materials; get the convener's permission in writing.
2. **Benchmark set.** Write the evaluation items and the grading protocol. Freeze them.
3. **Baseline.** Ungrounded model, no retrieval. Score it. This is the number every later
   design choice has to beat, and it is the honest control condition.
4. **RAG v1.** Ingest → chunk → embed → retrieve → answer with citations. Score it.
5. **Iterate on measured weaknesses only.** Each change gets a run directory and a delta.
6. **Interface.** Last. It carries no marks that the pipeline does not already carry.

## Running the harness

`make demo` is the whole thing. It installs on first use, so there is nothing to set
up first.

```bash
make demo        # narrated walkthrough — no API calls, nothing spent
make help        # every other target
```

Common targets:

| Target | Does | Costs money |
|---|---|---|
| `make demo` | Narrated walkthrough of the whole pipeline | no |
| `make items` | Validate the item set, show coverage gaps | no |
| `make conditions` | What each condition varies, and why | no |
| `make dry` | Dry-run C0, C1 and C2 | no |
| `make baseline` | **Real run** of C0 and C1 | yes |
| `make rag` | **Real run** of C2 | yes |
| `make sweep` | **Real run** of every condition | yes |
| `make variance` | **Real run** of C0 three times, for run-to-run spread | yes |
| `make grade` | Blind grading, interactive and resumable | no |
| `make report` | Aggregate graded runs into tables | no |
| `make clean` | Delete run outputs (grades are kept) | no |

Real runs need `ANTHROPIC_API_KEY` in the environment. Everything else works offline.

Dry runs exercise every stage — prompting, retrieval, run directories, grading,
reporting — without calling a model. They produce obviously-fake text, and grading
refuses to touch them unless you pass `--allow-dry-run`.

The underlying CLI is `ym07 items | conditions | run | grade | report`; run
`.venv/bin/ym07 --help` for the full flag set.

### What each run records

Every run writes `runs/<timestamp>-<condition>/` containing `responses.jsonl`, the
resolved `system_prompt.txt`, and a `manifest.json` recording the config digest, the
item-set digest, the model, the effort level and the token cost. The digests are what
let you prove two runs are comparable, and what make the "frozen benchmark" claim in
`protocols/evaluation.md` checkable rather than asserted.

### Deliberate choices worth defending in the report

- **No server-side refusal fallback.** If a request is refused, that is recorded as a
  refusal rather than silently retried on another model. Fallbacks are right for a
  product and wrong for a benchmark: every recorded answer must be attributable to one
  known model.
- **No temperature control.** It is not available on the current models, so runs are not
  bit-identical. Measure that variance instead of assuming it away: `--repeats 3`.
- **Retrieval is lexical (TF-IDF) in v0.** No embedding model needed, so C2 runs the day
  a corpus exists — and lexical becomes the comparison arm when dense retrieval lands.
