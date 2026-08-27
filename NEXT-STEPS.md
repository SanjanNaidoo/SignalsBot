# Next steps

## This week

1. **Email Dr Martin** and settle three things in one message:
   - permission to use EEE4114F notes, tutorials, past tests and memos as the corpus, and
     how that should be characterised against ethics Q8 ("open source" — course notes are not);
   - whether any student-facing evaluation is wanted, since that needs an ethics amendment
     started now, not in September;
   - whether he will grade a 20% subset of the benchmark as a second marker.
2. **Collect the corpus** into `corpus/raw/`. Everything: lecture slides, notes, tutorial
   sheets and memos, past papers and memos, prescribed textbook chapter references, MATLAB
   or Python lab handouts. Keep original filenames; write down where each came from.
3. **Fix the syllabus** in `configs/eee4114f.yaml`. The topic list there is a placeholder
   I inferred, not the real course outline. Replace it from the course handbook — the topic
   ids tag both corpus chunks and benchmark items, so changing them later means re-tagging.
4. **Write benchmark items.** Target ~120, from tutorials and past papers you already have
   worked solutions for. `items/eee4114f.seed.jsonl` has 7 to show the shape. This is the
   single highest-value thing you can do before writing any pipeline code, and it is the
   part that cannot be automated.

## Then

5. Ingestion: PDF → text → chunks with provenance. Slide decks and scanned notes will need
   different handling; equations are the hard part and worth a paragraph in the report.
6. Run `C0-baseline` against the frozen items. Do this before building retrieval — the
   number is more interesting than you expect, and it sets the bar.
7. Build `C2-rag`.

## Open questions to resolve before writing pipeline code

- What form are the EEE4114F materials in? Native-text PDFs, scanned images, PowerPoint,
  handwritten notes? This determines the whole ingestion design.
- Is there a hard requirement that this run offline / on UCT infrastructure / at zero cost?
  If a hosted API is unacceptable to the department, the architecture changes substantially
  and that constraint should be captured now rather than discovered in October.
