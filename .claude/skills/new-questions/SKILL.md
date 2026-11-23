---
name: new-questions
description: Add the questions the kids got wrong in a past exam to the pool and write their generators, end to end (pool, generators, stickers, checks, previews, catalog, website bank, commit, push, live site). Use when the parent says the kids solved an exam and struggled with some questions.
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
  (Austrian Kangaroo_<year>_...), `set-02/by_level/Class_03-04_Ecolier/` (IKMC_<year>_..., not used yet).
- Answers: `set-03/by_level/Answer_Keys/`, `set-01/by_level/Solutions/`, `set-02/by_level/Answer_Keys/`.
- Render each asked page to an image and look at the figure; `pdftotext -layout` may be missing - then use
  the Read tool on the PDF or pymupdf from `.venv` (`.venv/bin/python -m pip install pymupdf` if needed).
- Use the answer key; if there is none, solve it yourself and say so in the generator docstring.

## 3. Pool, and what already exists
- Add/merge the line in `question-pool.txt` (`<set>/by_level/<level>/<year>: n, n, n`), numbers sorted, no
  duplicates. A question that already has a generator: say so, skip it (maybe improve it instead).
- A new set (e.g. set-02) also needs an entry in `CONTESTS` in `check.py` (id, contest name shown on the
  website: "Skills from <name> <year>" sticker group, "Set NN · year" pill, exam form checkbox).
- Look at the existing generators (`QUESTIONS.md` lists skills and keywords) for the same skill. If one is close,
  share code via `kangaroo/` and give the new one a different angle, a first keyword and a sticker of its own.
- Read `feedback.md` for open items that apply (same skill, same kind of figure).

## 4. Write one generator per question (`generators/<path>/y<YEAR>_q<NN>.py`)
Everything in CLAUDE.md "How to write a generator" applies (4-6 variants, difficulty 1/2/3, `harder`, `META["rungs"]`, answers
computed, independent `check`, Fig drawings, bold key words, solutions written to the kids). In addition,
because the practice website uses them:
- `META["skill"]`: the **method**, never the answer - it is shown as the hint after a wrong first click.
- `META["keywords"]`: 2-3 plain words. The first one is shown to the kids ("You're getting stronger at: ..."),
  in the sticker ("Master <first keyword>") and in the exam form, so make it one no other generator starts with.
- `META["sticker"] = ("<emoji>", "<name>")`: the skill's own sticker (unlocked on the practice page when the
  skill is solid; grouped by exam in the sticker book). The site tracks earned stickers by **name**, so name and
  emoji must not be used by another generator or by the fixed stickers in `site/stickers.js` (`check.py` fails
  a missing sticker, a reused name or emoji, or a clash with `stickers.js`).
- **Mistake labels**: give wrong options as `(value, "what you did")` pairs in `numeric_choices` /
  `text_choices` - a verb phrase to the child that fits "Did you ...?" and "This is what you get if you ...",
  e.g. `(front, "count only the cubes you can see")`. Label every deliberate mistake.
- Keep the contest's wording when the "unclear" part is the trap the question teaches (do not add
  "different" to "How many common letters ...?").
- No `teach()` page and no `@warmup`s: the kids don't use them (parent, 2026-11-16).
- `META["rungs"] = (step1, step2, step3, step3_harder)`: each `"easier"`, `"aligned"` or `"harder"` than the
  ORIGINAL contest question (CLAUDE.md has the rubric). Rate it by reading the original next to each variant. A Part C
  original (Q17-24) is hard: its close-to-original variant is *easier*; write at least **2 aligned variants** (the
  practice site starts every skill at aligned). Rate single variants with `@variant(difficulty=N, rungs=(normal, harder))` when they differ from their step.
  Check with `python check.py --rungs`.
- `META["version"] = 1`.

## 5. Verify (all must pass before committing)
- `.venv/bin/python check.py` - every pool line `ok`, `Failing: 0`, no `note: same first keyword` and no
  `note: ... aligned variant(s)` naming a new generator. It takes ~10 min: run it in the background and do the next steps meanwhile.
- `.venv/bin/python check.py --preview y<YEAR>_q<NN>` for each new generator and LOOK at every page.
- Second sweep: generate 40 seeds x every variant x normal/harder of each new generator, assert that
  `[i for i in range(5) if q.check(i)] == [q.answer]` for all, that every wrong option a variant means as a
  mistake has a label in `q.meta["mistakes"]`, and read ~2 samples per variant (text, options, answer,
  solution) for wording that can be read two ways, singular/plural, a/an, units.
- `.venv/bin/python check.py --catalog` (rewrites QUESTIONS.md and the exam form checkboxes in
  `.github/workflows/generate-exam.yml`); check the diff shows the new questions and a new contest checkbox
  when the exam is new.
- Website bank, as the Publish workflow builds it (~10 s): `BANK_SEEDS=2 .venv/bin/python site/bank.py`.
  In `_site/bank/index.json` each new generator must have its `contest`, `level` (e.g. "Grade 3-4", not a
  folder name), `keywords`, `skill` and `sticker`. `_site/` is not
  committed.

## 6. Ship
- Add a line to the Log in `PLAN.md` (the new questions and their stickers).
- Commit: the pool, the new generators, any `kangaroo/` or `check.py` change, `QUESTIONS.md`, the workflow,
  `PLAN.md`, `feedback.md` if items were ticked, and the **preview PDFs of the new generators**
  (`output/previews/...`, QUESTIONS.md links to them). Leave out other preview PDFs that changed only because
  they were rebuilt (the PDF date changes every time). The message lists the new questions.
- Pull --rebase if needed, push to main.
- Stop after the push: no deploy watch, no live-site check (parent, 2026-11-16). New skills come up about
  3 times as often for 21 days and get a guaranteed place in each child's next sessions until tried (from the
  generator's git date) - nothing to configure.

## 7. Report to the parent (short)
The new skills (question, first keyword, what it practises, its sticker), that they will be in practice (after the ~2 min deploy) and
in the PDFs, and anything that needs their eyes (e.g. a question solved without an answer key, or a contest
wording kept on purpose). Offer to make a PDF exam from just this exam's questions
(`make_exam.py --from <year>`).
