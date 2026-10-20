# Math Kangaroo practice generator — instructions for the AI agent

This project turns questions the kids struggled with into **question generators**
(plain Python, no AI at run time). A strong model writes/improves generators; making
an exam is just `python make_exam.py`.

## Layout
- `sample-tests/<YEAR>.pdf` — original contests (Grade 3-4).
- `question-pool.txt` — `YEAR: n, n, n` lines; the questions the kids got wrong.
- `generators/y<YEAR>_q<NN>.py` — one generator per pool question (e.g. `y2002_q06.py`).
- `kangaroo/` — shared library: `Question`, `numeric_choices`/`text_choices`, `Fig` (drawing), `render.py` (PDF), `registry.py`.
- `feedback.md` — the parent's notes on generated questions. **Read it before touching a generator.**
- `make_exam.py`, `check.py` — the two commands.

## Typical requests
- **"Sync generators"** → run `python check.py`, pick MISSING entries (a few at a time unless told otherwise), write them.
- **"Improve y2002_q06"** / feedback in `feedback.md` → edit that generator, bump `META["version"]`, mark the feedback item done.

## How to write a generator
1. Read the original question (render the PDF page to an image and look at the figure; `pdftotext -layout` for text). Put the original question + answer in the module docstring.
2. Name the **core skill** (why it is hard for an 8–10 year old), put it in `META["skill"]`, and pick `topics` (reuse existing topic words: geometry, perimeter, area, counting, logic, patterns, arithmetic, time, spatial, ...).
3. Write **4–6 variants** with `@variant(difficulty=1|2|3)` — each a function `(rng, harder) -> Question`:
   - difficulty 1 ≈ Part A (close to the original), 2 ≈ Part B, 3 ≈ Part C (reverse the question, add a twist, combine steps).
   - Be creative: different stories/contexts, asking for a different unknown, a counter-intuitive twist (e.g. "the perimeter doesn't change"). Keep the same underlying skill and grade 3–4 language.
   - `harder=True` → bigger numbers / more steps within the same variant.
   - Compute the answer from the parameters; never hard-code it.
   - Wrong options = plausible mistakes (forgot to double, used the wrong piece, ...), via `numeric_choices(correct, mistakes, rng, unit=...)`.
   - Draw figures with `kangaroo.Fig` (vector, Times font, `max_px` ~90–120). Figures must be unambiguous and roughly to scale.
   - Solutions: 1–3 short sentences a parent can explain from.
   - **Answer check (required):** set `Question.check` — a function `i -> bool` saying whether option
     `i` is correct, worked out *independently* from how the answer was built (brute force, simulate,
     count cell by cell, re-solve from the drawn data). Numbers: `check=value_check(choices, value)`.
     Shared solvers live in `kangaroo/solve.py`, `polyomino.covers`, `cubes.buried`/`exposed_faces`,
     `numbers.written`. `validate()` demands exactly one passing option, and it must be the answer.
   - Emphasise the key word of a reversed question in **bold**: `<b>not</b>`, `<b>cannot</b>`.
4. If several generators need the same machinery (e.g. balance scales, cube nets), put it in `kangaroo/` rather than copying it.
5. Verify: `python check.py` (stress test must be `ok`; it fails a variant with no answer check), then `python check.py --preview y<YEAR>_q<NN>` and **look at the rendered pages** — check every figure, the wording, and that exactly one option is correct.

## Conventions
- One file per pool question, even if two questions share a skill (share code via `kangaroo/`).
- Don't change `kangaroo/` APIs in ways that break existing generators; run `check.py` after any library change.
- Exams and previews go to `output/`, which is committed to git (keep generated PDFs there).
