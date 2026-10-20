# Math Kangaroo practice exams

Generates printable Math Kangaroo-style practice exams (Grade 3–4) built from the
questions the kids struggled with. Each missed question gets its own **generator**: a
small Python file that makes endless new questions that test the same skill,
with new numbers, new stories and new twists. Making an exam is a plain script with no
AI involved; a strong AI model is only needed to write or improve generators.

## Setup (once)

```
cd ~/mathkang-claude
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

This creates a private Python environment in `.venv/` (not committed), so nothing is
installed system-wide. Optional: run `source .venv/bin/activate` once per Terminal
window, and then `python3 make_exam.py` uses it. Without activating, write
`.venv/bin/python make_exam.py` instead of `python3 make_exam.py`.

## 1. Make an exam (no AI needed)

The commands below assume `source .venv/bin/activate` was run in this Terminal window
(otherwise replace `python3` with `.venv/bin/python`).

```
python3 make_exam.py                  # 20 questions
python3 make_exam.py -n 24 --harder   # more Part C questions, bigger numbers
python3 make_exam.py --from 2002      # only questions based on the 2002 test
python3 make_exam.py --topic perimeter
python3 make_exam.py --seed 2026      # re-create an exact exam (seed is printed under the title)
python3 make_exam.py --hide-sources   # answer key without the [2002 Q7 · ...] tags
```

The PDF goes to `output/`. Each run produces a different exam unless you pass `--seed`.
It contains:

- the questions, ordered into Part A (3 points), Part B (4 points) and Part C (5 points), each with 5 options (A–E);
- an **answer key** with a short solution for every question.

Each solution ends with a tag such as `[2002 Q6 · notch]`, which names the generator and
the variant that made it. If the kids keep missing the same tag, that skill needs more
practice.

## 2. Check / review generators

```
python3 check.py                       # coverage: which pool questions have generators; runs self-tests
python3 check.py --preview y2002_q07   # PDF showing every variant of one generator, for review
```

## 3. Report a bad question

Add a line to `feedback.md` using the tag from the answer key:

```
- [ ] y2002_q07 · how_many_fit — too hard to compare, make the pieces bigger
```

The next time the AI agent works on the project, it applies the feedback and ticks the item.

## 4. Grow it (with a strong model, e.g. Claude Code in this folder)

1. Drop the new contest PDF into `sample-tests/` (e.g. `2008.pdf`).
2. Add the missed questions to `question-pool.txt`, e.g. `2008: 3, 7, 15`.
3. Ask the agent things like:
   - "sync generators, next 3"
   - "add a generator for 2002 Q9"
   - "apply feedback.md"
   - "improve y2002_q06: add a variant about area"

The agent follows the rules in `CLAUDE.md`: one generator per pool question, 4–6
variants across Parts A–C, answers computed in code, wrong options based on likely
mistakes, a self-test, and a visual review of the preview PDF.

## Saving changes to GitHub

The project lives at https://github.com/koraytugay/math-kang-claude. After adding tests,
editing `question-pool.txt` or `feedback.md`, or after the agent adds or improves
generators:

```
git add .
git commit -m "Describe what changed"
git push
```

Generated exams in `output/` are committed too; only the Python environment (`.venv/`) is ignored by git.

## Troubleshooting

**`ModuleNotFoundError: No module named 'reportlab'`** (or the message
"reportlab is not installed"): the one-time setup hasn't been done, or you ran plain
`python3` without the environment. Run the setup steps above, then use
`.venv/bin/python make_exam.py ...` (or `source .venv/bin/activate` first).

**`pip install` says "externally-managed-environment"**: macOS/Homebrew Python blocks
system-wide installs. Use the `.venv` setup above instead of `pip install` directly.

**`git push` is rejected** (the remote has commits you don't have):
`git pull --rebase origin main`, then `git push`.

## Project layout

| Path | What it is |
|---|---|
| `sample-tests/` | Original contest PDFs |
| `question-pool.txt` | The questions the kids struggled with (`YEAR: n, n, n`) |
| `generators/yYEAR_qNN.py` | One generator per pool question |
| `kangaroo/` | Shared library: question format, answer options, drawing, PDF layout |
| `make_exam.py` | Makes an exam |
| `check.py` | Coverage report, self-tests, previews |
| `feedback.md` | Notes on generated questions, for the agent to act on |
| `CLAUDE.md` | Instructions for the AI agent that writes generators |
| `output/` | Generated PDFs (committed) |

## Status

| Pool question | Generator | Variants |
|---|---|---|
| 2002 Q6 — perimeter of a rectangle cut from a square | `y2002_q06.py` | square_minus_strip, pieces_total, corner_cut, notch, strips_to_square, two_perimeters |
| 2002 Q7 — which piece cannot belong to the skyline | `y2002_q07.py` | cannot_belong, can_belong, how_many_fit |
| 2002 Q9 — balance: oranges and melons | `y2002_q09.py` | one_more_balances, both_sides, chain, grams, what_to_add |
| 2002 Q11 — cracked clock with consecutive sums | `y2002_q11.py` | biggest_piece, which_picture, largest_sum, straight_crack, count_ways |
| 2002 Q15 — flag silhouette | `y2002_q15.py` | torn_flag, door, too_wide, count_possible, only_one_right. Wrong pictures only ever break one of two clear-cut rules (part of the pole edge is bare, or wider than the flag), so no cloth-folding judgement is needed. |
| 2002 Q18 — who has which pet (logic) | `y2002_q18.py` | who_has, which_true, which_not_true |
| 2002 Q20 — tunnel of cubes rebuilt as a pyramid | `y2002_q20.py` | count_tunnel, tunnel_to_pyramid, count_pyramid, fill_the_hole, not_enough, longer_tunnel |
| 2002 Q21 — who cannot make 20 from three cards | `y2002_q21.py` | who_cannot, which_can, which_cannot, hidden_card, biggest |
| 2002 Q22 — ways to sit at a table, one seat fixed | `y2002_q22.py` | fixed_seat, photo_line, ends_fixed, outfits, side_by_side, stripes |
| 2002 Q24 — odometer: next number with all different digits | `y2002_q24.py` | all_different, next_palindrome, last_time, same_digits, going_up |
| 2003 Q9 — blue cubes inside a red brick | `y2003_q09.py` | blue_inside, red_outside, painted, how_deep, thick_wall |
| 2003 Q10 — 50 dm 50 cm 50 mm + 123 cm | `y2003_q10.py` | jump, longest, how_much_longer, pieces, not_equal |
| 2003 Q16 — 35 digits for the page numbers | `y2003_q16.py` | pages_from_digits, digits_for_pages, count_one_digit, from_page, three_digit_pages |
| 2003 Q17 — bar code with wide and narrow bars | `y2003_q17.py` | narrow_bars, fence, wide_bars, necklace, ends_differ |
| 2003 Q18 — which two pieces cover the empty area | `y2003_q18.py` | one_piece, two_pieces, two_copies, three_pieces |
| 2007 Q1 — numbers along a forking road | `y2007_q01.py` | which_group, how_many_routes, largest_sum, impossible_total, which_branch |
| 2007 Q3 — common letters of KANGAROO and PROBLEM | `y2007_q03.py` | common_letters, different_letters, only_in_first, which_word, letter_cards |
| 2007 Q4 — next number after 2007 with the same digit sum | `y2007_q04.py` | next_same_sum, which_same_sum, smallest_with_sum, before_same_sum, count_with_sum |
| 2007 Q5 — work backwards through a chain of calculations | `y2007_q05.py` | favourite_number, forwards, think_of_a_number, missing_number, which_operation |
| 2007 Q8 — which piece completes the rectangle | `y2007_q08.py` | complete_rectangle, squares_missing, two_make_rectangle, two_copies |
| 2007 Q12 — older by one year and one day | `y2007_q12.py` | younger_birthday, older_birthday, days_between, age_on_day, new_year_twins |
| 2007 Q14 — how many more cubes fit in the aquarium | `y2007_q14.py` | how_many_more, count_inside, long_box, bottom_layer, two_layers |

Run `python3 check.py` for the full, current list.
