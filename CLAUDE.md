# Math Kangaroo practice generator — instructions for the AI agent

This project turns questions the kids struggled with into **question generators**
(plain Python, no AI at run time). A strong model writes/improves generators; making
an exam is just `python make_exam.py`.

## Layout
- Contest PDFs are organized by set and level, e.g. `set-03/by_level/Grade_03-04/` (Canada Math Kangaroo Grade 3-4), `set-01/by_level/...`, etc.
- `question-pool.txt` — `<PATH>/<YEAR>: n, n, n` lines (e.g. `set-03/by_level/Grade_03-04/2002: 1, 6, 7`); the questions the kids got wrong.
- `generators/<PATH>/y<YEAR>_q<NN>.py` — one generator per pool question (e.g. `generators/set-03/by_level/Grade_03-04/y2002_q06.py`).
- `kangaroo/` — shared library: `Question`, `numeric_choices`/`text_choices`, `Fig` (drawing), `render.py` (PDF), `registry.py`.
- `cemc-potw/level-A/` — University of Waterloo (CEMC) Problem of the Week, Grade 3/4 booklets with solutions (see its README).
- `feedback.md` — the parent's notes on generated questions. **Read it before touching a generator.**
- `make_exam.py`, `check.py` — the two commands.

## Menu (show this when the parent says hi, "what can I do?", "help" or seems unsure)
Answer with this short list, in plain words:
- **`/new-questions`** - "we solved a past exam and the kids struggled with some questions": tell me the exam
  and the question numbers, I add them to practice, PDFs and exams.
- **"Improve <question>"** or a note in `feedback.md` - fix or improve one question.
- **"Make an exam"** - a PDF exam (or use the website: https://koraytugay.github.io/math-kang-claude/).
- Websites: practice https://koraytugay.github.io/math-kang-claude/practice.html, parent view
  https://koraytugay.github.io/math-kang-claude/parent.html.

## Typical requests
- **"Sync generators"** → run `python check.py`, pick MISSING entries (a few at a time unless told otherwise), write them.
- **"We solved an exam" / `/new-questions`** → follow `.claude/skills/new-questions/SKILL.md`: ask only which
  exam and which questions, then pool, generators (with mistake labels), checks, catalog, push.
- **"Improve y2002_q06"** / feedback in `feedback.md` → edit that generator, bump `META["version"]`, mark the feedback item done.

## How to write a generator
1. Read the original question (find the contest PDF in e.g. `set-03/by_level/Grade_03-04/`; render the PDF page to an image and look at the figure; `pdftotext -layout` for text). Put the original question + answer in the module docstring.
2. Give `META["keywords"]`: 2-3 short plain words a parent would type to pick this question
   ("cube counting", "hiding digits"); the first one is shown in the GitHub Actions form.
   Give `META["sticker"] = ("<emoji>", "<name>")`: the skill's own sticker on the practice website
   (unlocked when the skill is solid), e.g. `("🍕", "Pizza slicer")` - a fun name for a 10-year-old, an emoji
   and a name no other generator or fixed sticker in `site/stickers.js` uses (`check.py` checks).
   Name the **core skill** (why it is hard for an 8–10 year old), put it in `META["skill"]`, and pick `topics` (reuse existing topic words: geometry, perimeter, area, counting, logic, patterns, arithmetic, time, spatial, ...).
3. Write **4–6 variants** with `@variant(difficulty=1|2|3)` — each a function `(rng, harder) -> Question`.
   `difficulty` is only the order of our steps inside one skill: 1 = closest to the original, 2 = a step on,
   3 = a twist (reverse the question, add a step, combine steps); `harder=True` on a difficulty-3 variant is
   the fourth step. **What matters for practice is how hard each step is compared with the ORIGINAL contest
   question**: `META["rungs"] = (step1, step2, step3, step3_harder)`, each `"easier"`, `"aligned"` or
   `"harder"`. Rate them honestly, by reading the original and the variant side by side:
   - **aligned** = the same number of steps, the same kind of numbers and the same trap as the original;
   - **easier** = fewer steps or a simpler set-up (count what is pictured, one clue instead of three, a smaller grid);
   - **harder** = an extra step, a twist, bigger numbers, or the question reversed.
   The practice site starts every skill at *aligned*, moves one rung up after a right answer and one down
   after a wrong one, and now and then shows a question from another rung. Without `META["rungs"]` the
   default follows the original's contest part (Q17-24: easier, easier, aligned, harder; Q9-16: aligned,
   aligned, harder, harder; Q1-8: aligned, harder, harder, harder): fine for a first draft, rate them yourself
   for new generators. Each rung the skill needs must have **real variants**: aim for **at least 2 aligned
   variants** (one variant gives only ~20 questions, then practice runs out of fresh aligned ones).
   `python check.py --rungs` lists the counts and `python check.py` notes skills with fewer than 2 aligned.
   Part C originals (Q17-24) are hard: their "close to the original" variant is already *easier* - do not call
   it aligned; add the genuinely aligned variants (the original wording, a different figure or numbers).
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
   - Layout (`kangaroo/layout.py`, PDF and website): a blank line (`"\n\n"`) starts a paragraph, a line
     starting `"- "` is a bullet. Put rules/clues the kids must keep in mind (3+ facts) in a bulleted list after
     a lead sentence (never start the text with a bullet). The last question sentence is put on its own line
     automatically.
   - Don't add a `teach()` page or `@warmup` questions to new generators: the kids don't use them (parent,
     2026-11-16). Older generators still have some; leave them unless asked.
4. If several generators need the same machinery (e.g. balance scales, cube nets), put it in `kangaroo/` rather than copying it.
5. Verify: `python check.py` (stress test must be `ok`; it fails a variant with no answer check), then `python check.py --preview y<YEAR>_q<NN>` (or `python check.py --preview-all`) and **look at the rendered pages** — check every figure, the wording, and that exactly one option is correct.

## Conventions
- One file per pool question, even if two questions share a skill (share code via `kangaroo/`).
- Don't change `kangaroo/` APIs in ways that break existing generators; run `check.py` after any library change.
- When `question-pool.txt` or any `META["keywords"]` changes, run `python check.py --catalog`: it rewrites
  `QUESTIONS.md` and the contest checkboxes in `.github/workflows/generate-exam.yml` (between the BEGIN/END
  markers - never edit those by hand). New sets need an entry in `CONTESTS` in `check.py`.
- Exams go to `output/exams/` (e.g. `001.pdf`) and previews to `output/previews/`, which are committed to git.

## Practice website (ongoing project)
The practice website is finished (all tasks in `PLAN.md` are done). `PLAN.md` stays as the record of its
design and the parent's decisions (no points or counts for the kids, no exact repeats, keep contest traps,
the scoring in site/smart.js). Read it before changing the website; add a Log line for changes.
