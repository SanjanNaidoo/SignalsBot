# Where the project is — 9 September 2026

A snapshot for picking the work up on another machine. Update it or delete it;
it is a lab-notebook entry, not a spec, and it will go stale.

## Done

- **Corpus.** 118 files, convener's permission recorded. Ingested to 335 chunks
  with page-level provenance. *Not in git* — see "What git does not carry".
- **Benchmark.** 47 items across 9 topics, arithmetic verified, frozen.
  Digest `020975b2ecf884f4`. Protocol and H1 written before any results.
- **Harness.** `ym07 items | conditions | ingest | chat | run | grade | report`,
  14 conditions defined, hosted and open arms.
- **Six runs, 282 responses, $6.16, zero errors:** C0 for Claude, GPT, Gemini,
  Grok and DeepSeek, plus C1-prompted on Claude. All committed.
- **`ym07 chat`.** The interactive tutor — the working chatbot the brief asks
  for. Same config, prompt, retriever and clients as the benchmark, so the demo
  is the measured system rather than a lookalike.
- **Report statistics.** 95% intervals on correctness, and a paired comparison
  against a reference condition (default C1-prompted, the bar H1 names).
  Verified end to end against synthetic grades; the real grades file is empty.

## In flight

- **C1-oss** on the GPU machine. First attempt failed: the default four workers
  each began loading their own copy of the model. Fixed in `6078edc` — pull
  before re-running.

## Next, in order

1. **Grade the 282 responses.** `ym07 grade`. Blind and resumable. Nothing
   produces a single number until this is done, and it needs no money, no GPU
   and no decision from anyone. This is the bottleneck.
2. **C0-oss**, the other free local run.
3. **Fine-tuning**: generate training data, train, run C2-oss-tuned. The
   headline claim. Blocked on the holdout decision below.
4. **The report.** Not begun.
5. **C2 retrieval conditions.** Waiting on the supervisor.
6. **Rotate the five API keys.**

## Open decisions

- **Contamination holdout is too coarse.** The rule says a file used to write a
  benchmark item is excluded from fine-tuning data. `EEE4114F DSP Notes.pdf`
  alone is the source of 16 items, so file-level exclusion discards the best
  teaching material in the corpus. Hold out at *page* level instead — the
  chunks carry page numbers already. Decide before generating training data.

## Measured weaknesses — findings, not bugs to quietly fix

- **Retrieval favours past papers over notes on concept questions.**
  "What is aliasing?" returns 7 past papers and 0 pages of notes; "explain
  overfitting" returns 6 and 1. Past papers are 181 of 335 chunks, and exam text
  repeats a term densely in little prose, which is what TF-IDF rewards. This is
  the motivation for a dense-retrieval comparison arm, and it belongs in the
  report as measured-then-addressed rather than tuned away.

## What git does not carry

- `corpus/raw/` and `corpus/processed/` are gitignored: the convener's
  permission covers use, not republication. Copy them to a new machine by hand,
  or re-run `ym07 ingest` against a hand-copied `corpus/raw/`.
- Without a corpus, `ym07 chat` still runs ungrounded (that is condition C1) and
  says so on startup. C0 and C1 runs need no corpus; C2 refuses without one.
- API keys are environment variables and are in no file here.

## Gotchas already paid for

- `torch` must be `<2.11`, pinned in `pyproject.toml`: 2.11 removed a symbol
  transformers still imports, and pip resolves the broken pair without
  complaint.
- On a 50-series card torch must come from the CUDA 12.8 index or it has no
  kernels for the GPU.
- Dry runs are indistinguishable from real ones by directory name — only
  `manifest.json` records `dry_run`. Check before committing run output:
  `grep -l '"dry_run": true' runs/*/manifest.json`
- Local conditions now force one worker. Concurrency helps network latency, not
  a single GPU.
