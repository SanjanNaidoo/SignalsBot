# YM-07 — Course-specific Chatbot for Student Support (EEE4114F)

Final-year project, UCT EE. Supervisor: Dr Yaaseen Martin.
Target course: **EEE4114F — Digital Signal Processing**.

## Design stance

Retrieval-augmented generation (RAG) over the EEE4114F course corpus, on top of a
frontier model — *not* fine-tuning. Justification (this argument belongs in the report):

1. The corpus is one course. That is far too little data to fine-tune facts into a model;
   fine-tuning teaches style and format, not content.
2. Students must be able to check the tutor. Retrieval gives citations back to a specific
   lecture note / tutorial; a fine-tuned model gives an unattributable assertion.
3. The brief requires the chatbot be "easily adaptable to new courses". With RAG that is a
   corpus swap plus a config file. With fine-tuning it is a retraining run per course.

The word "train" in the project brief is satisfied by grounding the model on course material;
say so explicitly in the report and defend it.

## Repository layout

| Path | Contents |
|---|---|
| `corpus/raw/` | Source course materials, as supplied. **Never committed.** |
| `corpus/processed/` | Extracted + chunked text with provenance metadata. Generated. |
| `configs/` | Per-course configuration. `eee4114f.yaml` is the target course. |
| `items/` | Benchmark items — the evaluation set the report is built on. |
| `protocols/` | Written evaluation protocols: what is measured, how, and by whom. |
| `runs/` | Timestamped benchmark run outputs. Generated. |
| `src/ym07/` | The package. |

## Build order

Deliberately not "chatbot first". The report is marked on GA1 (justified design choices),
GA4 (investigation and analysis) and GA5 (tool use and benchmarking) — all three need a
measuring instrument that exists *before* the thing being measured.

1. **Corpus.** Collect and catalogue EEE4114F materials; get the convener's permission in writing.
2. **Benchmark set.** Write the evaluation items and the grading protocol. Freeze them.
3. **Baseline.** Ungrounded model, no retrieval. Score it. This is the number every later
   design choice has to beat, and it is the honest control condition.
4. **RAG v1.** Ingest → chunk → embed → retrieve → answer with citations. Score it.
5. **Iterate on measured weaknesses only.** Each change gets a run directory and a delta.
6. **Interface.** Last. It carries no marks that the pipeline does not already carry.

## Ethics constraint (read before planning evaluation)

The submitted ethics questionnaire answers **No** to data collection and **No** to human
involvement. That means: **no student user study, no surveys, no interaction logs from real
students** without first filing an ethics amendment. All evidence in the report must therefore
come from the benchmark set in `items/`, graded by you and/or your supervisor.

If you want student feedback in the report, start the amendment now — it is slow.

Q8 was answered "third-party data is open source". Course notes are not open-source; they are
copyright UCT. Confirm with Dr Martin how to characterise this, and keep the corpus out of git.
