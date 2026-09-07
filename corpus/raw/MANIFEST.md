# Corpus manifest — EEE4114F

The provenance and permission trail for everything in `corpus/raw/`. This file **is**
committed; the materials it describes are not.

## Permission

| | |
|---|---|
| Granted by | Dr Yaaseen Martin — course convener, EEE4114F, and project supervisor |
| Covers | EEE4114F course materials as training/retrieval data: notes, tutorials, problem sets, class tests, exams and their memos |
| Granted on | 2026-09-07 |
| Form | Informal written approval by email. No formal permissions document was issued; the supervisor judged one unnecessary |
| Evidence | Email from Dr Martin, 2026-09-07 — "I think it should be okay to go ahead without formal permission… we won't be publishing your thesis anyway, so should be good to go" |
| Stated rationale | Precedent from a previous supervisee (Rifuwo); the supervisor's view that the course materials carry no meaningful copyright restriction; and that the thesis will not be published |
| Restrictions | Not to be redistributed. Course materials are never committed to the repository — see the gitignore rules |

**Status: GRANTED (informal).** Sufficient to proceed with graded runs.

Two things worth keeping visible, neither of which blocks the work:

1. **The rationale is scoped to non-publication.** The supervisor's reasoning rests partly
   on the thesis not being published. The GitHub repository is public, so the gitignore
   rules that keep `corpus/raw/` and `corpus/processed/` out of version control are what
   keep that reasoning true. Never commit course materials, and never use `git add -f`
   here.
2. **Ethics questionnaire Q8** (`YM07.pdf`) states the third-party data is open source.
   That is not accurate for UCT course notes, and this email does not change the wording
   on the form. It is a documentation inconsistency rather than a permissions problem —
   worth a sentence to Dr Martin at the next meeting so the record is straight.

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
