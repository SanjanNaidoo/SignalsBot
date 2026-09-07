# Corpus manifest — EEE4114F

The provenance and permission trail for everything in `corpus/raw/`. This file **is**
committed; the materials it describes are not.

## Permission

| | |
|---|---|
| Granted by | *(name, role — e.g. Dr Yaaseen Martin, supervisor)* |
| Covers | *(which materials, which years)* |
| Granted on | *(date)* |
| Evidence | *(email thread subject / date, or file in the project drive)* |
| Restrictions | *(e.g. not to be redistributed, not to be published in the repo)* |

**Status: NOT YET OBTAINED.** No graded run may use this corpus until this table is filled
in and the evidence exists in writing.

## Inventory

Add a row per file as you collect. `Text layer` is yes/no/partial — whether text can be
selected in a PDF viewer (no = needs OCR, may not be ingestible).

| File | Type | Year | Source | Supplied by | Text layer | Notes |
|---|---|---|---|---|---|---|
| *(example)* `Lecture03_Sampling.pdf` | slides | 2025 | Amathuba → Lectures | course site | yes | equation-heavy |
|  |  |  |  |  |  |  |

## Held out of training

Files whose contents were used to write benchmark items. Anything listed here is corpus
material for retrieval but **must not** appear in the fine-tuning set — training on it
would contaminate the frozen benchmark and invalidate the central claim in
`protocols/evaluation.md`.

| File | Item ids derived from it |
|---|---|
|  |  |
