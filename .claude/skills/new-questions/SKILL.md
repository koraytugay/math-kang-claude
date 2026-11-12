---
name: new-questions
description: Add the questions the kids got wrong in a past exam to the pool and write their generators, end to end (pool, generators, checks, catalog, commit, push, live site). Use when the parent says the kids solved an exam and struggled with some questions.
---

# New wrong questions from a past exam

The parent (Koray) and the kids (Deniz, Toprak, ~10, grade 3-4) solved a past Math Kangaroo exam. Turn the
questions they got wrong into generators so they show up in practice, personal PDFs and exams.
Do everything below without asking again, except step 1. Follow CLAUDE.md for how to write a generator.

## 1. Ask only this (one message, skip what the parent already said)
- Which exam: the set/contest and year, e.g. "Canada 2012" (set-03), "Austria 2011" (set-01), or a file.
- Which question numbers they struggled with.

## 2. Find the exam
- Exam PDFs: `set-03/by_level/Grade_03-04/` (Canada, CMKC_<year>_...), `set-01/by_level/Grade_03-04_Ecolier/`
  (Austrian Kangaroo_<year>_...), `set-02/by_level/Class_03-04_Ecolier/` (not used yet).
- Answers: `set-03/by_level/Answer_Keys/`, `set-01/by_level/Solutions/`, `set-02/by_level/Answer_Keys/`.
- Render each asked page to an image and look at the figure; `pdftotext -layout` may be missing - then use
  the Read tool on the PDF or pymupdf from `.venv` (`.venv/bin/python -m pip install pymupdf` if needed).
- Use the answer key; if there is none, solve it yourself and say so in the generator docstring.

## 3. Pool
- Add/merge the line in `question-pool.txt` (`<set>/by_level/<level>/<year>: n, n, n`), numbers sorted, no
  duplicates. A question that already has a generator: say so, skip it (maybe improve it instead).
- A new set (e.g. set-02) also needs an entry in `CONTESTS` in `check.py`.

## 4. Write one generator per question (`generators/<path>/y<YEAR>_q<NN>.py`)
Read `feedback.md` first. Everything in CLAUDE.md "How to write a generator" applies (4-6 variants,
difficulty 1/2/3, `harder`, answers computed, independent `check`, Fig drawings, bold key words, solutions
written to the kids). In addition, because the practice website uses them:
- `META["skill"]`: the **method**, never the answer - it is shown as the hint after a wrong first click.
- `META["keywords"]`: 2-3 plain words; the first one is shown to the kids ("You're getting stronger at: ...").
- **Mistake labels**: give wrong options as `(value, "what you did")` pairs in `numeric_choices` /
  `text_choices` - a verb phrase to the child that fits "Did you ...?" and "This is what you get if you ...",
  e.g. `(front, "count only the cubes you can see")`. Label every deliberate mistake.
- Keep the contest's wording when the "unclear" part is the trap the question teaches (do not add
  "different" to "How many common letters ...?").
- For questions the kids found very hard: `teach()` page (written to the kids) and 2-4 `@warmup`s - the
  website shows them after wrong answers and before a skill missed twice.

## 5. Verify (all must pass before committing)
- `.venv/bin/python check.py` (35+/N ok, stress test ok; takes ~10 min - run it in the background).
- `.venv/bin/python check.py --preview y<YEAR>_q<NN>` for each new generator and LOOK at every page.
- Second sweep: generate 40 seeds x every variant x normal/harder of each new generator, assert that
  `[i for i in range(5) if q.check(i)] == [q.answer]` for all, and read ~2 samples per variant (text,
  options, answer, solution) for wording that can be read two ways, singular/plural, a/an, units.
- `.venv/bin/python check.py --catalog` (rewrites QUESTIONS.md and the workflow checkboxes).

## 6. Ship
- Commit (message lists the new questions) and push to main; pull --rebase first if needed.
- The website redeploys by itself (`Publish website`, ~2 min). Check that `bank/index.json` on
  https://koraytugay.github.io/math-kang-claude/ lists the new skills. New skills come up about twice as
  often for 60 days automatically (from the generator's git date) - nothing to configure.
- Add a line to the Log in `PLAN.md`.

## 7. Report to the parent (short)
The new skills (question, keywords, what it practises), that they are live in practice and in the PDFs,
and anything that needs their eyes (e.g. a question solved without an answer key).
