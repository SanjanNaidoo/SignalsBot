# Raw corpus — not committed

Drop EEE4114F source materials here. Everything in this directory except this README and
`MANIFEST.md` is gitignored: the notes are copyright UCT and used with the convener's
permission, and that permission does not extend to publishing them in a repository.

Keep `MANIFEST.md` up to date as you add files. It records, for each item: original
filename, where it came from, who supplied it, and what year it is from. The report needs
that trail, and so does anyone adapting the tool to another course later.

## What to collect

| Material | Why it matters |
|---|---|
| Lecture notes and slide decks | The bulk of the retrievable corpus. |
| Tutorials **with** solutions | Solutions carry the course's worked-answer style. |
| Past tests and exams **with** memos | The benchmark items are written from these. |
| Course outline / handbook page | Fixes the topic list in `configs/eee4114f.yaml`. |

Tutorials and past papers do double duty: they are corpus material *and* the source of
benchmark items. Anything that becomes a benchmark item must be held out of the
fine-tuning set — see `protocols/evaluation.md`.

## How to save it

**Keep the original files.** Do not convert, rename, flatten or "tidy" them.

- **Keep PDFs as PDFs.** Ingestion records a page number per chunk (`page` in the chunk
  schema) so a citation can say *which page*. Converting to `.txt` first destroys that.
- **Keep original filenames.** They usually carry the year, week or topic, which is
  provenance the manifest would otherwise have to reconstruct by hand.
- **Preserve the site's folder structure** if there is one — it is a free topic labelling.
- **Flag scanned vs native PDFs** in the manifest. A native PDF has a text layer and
  extracts cleanly; a scan of handwritten notes needs OCR and may not be worth ingesting.
  Test: try selecting text in a viewer. If you cannot, it is a scan.
- **Note anything equation-heavy.** Maths is the hard part of ingestion — LaTeX in a PDF
  extracts as mangled symbols. These files may need manual handling.

## What not to put here

Textbook PDFs and other third-party copyrighted material. The permission trail covers
course materials produced for EEE4114F, not a scanned Oppenheim. The ethics questionnaire
(`YM07.pdf`, Q8) currently claims the third-party data is open source, which is not true of
UCT course notes — that needs resolving with Dr Martin before this directory is used in a
graded run.
