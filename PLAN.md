# Plan: practice website (kids solve questions online, the site learns what they get wrong)

**Status: finished (2026-11-12).** All tasks are done; this file is now the record of the design and the
parent's decisions. New exam questions: use `/new-questions` (see CLAUDE.md).

**How it was resumed while in progress:** open Claude Code in this repo and say *"continue PLAN.md"*. The agent reads this file,
finds the first unchecked `[ ]` task, and goes on from there. Tick tasks `[x]` as they are done and add a
line to the **Log** at the bottom (date, what was done, what is next). Keep this file the single source of
truth for this project; decisions change here, not only in chat.

## Goal

Deniz and Toprak (about 10, grade 3-4) open the website on the family desktop, pick their profile, and
solve Math Kangaroo style questions on screen. Every answer is saved. The site is **personalized per child**:
it gives more of what each child gets wrong, adapts the difficulty, and explains mistakes.
The PDF exams (`make_exam.py`, the GitHub Actions workflow, the exam page) keep working unchanged.

## Decisions (made with the parent, 2026-11-11)

- **Profiles:** `Deniz`, `Toprak`, `Koray`. Koray is the parent; **always test with Koray**, never with the
  kids' profiles. No passwords for the kids; just their names, **no emojis/avatars** ("Who's practising?").
- **Desktop only.** No phone/tablet work. Style with kt-styles (see CLAUDE.md / `~/github/koraytugay/kt-styles`);
  missing UI elements are added to kt-styles first.
- **Generators stay Python; no rewrite to JS.** One source, two outputs: PDF (as now) and a pre-generated
  **question bank** (JSON + SVG figures) built in GitHub Actions and published with the site.
- **Database: Postgres on Neon** (the parent already has an account), used **directly from the browser** with
  Neon's serverless driver (`@neondatabase/serverless`, SQL over HTTPS). The connection string is **locked with
  the site password** exactly like the GitHub token (PBKDF2 + AES-GCM, `site/lock-token.mjs`), in the same
  locked file: one password unlocks both. The site asks for the password when it opens ("Remember on this
  device"), so the kids don't type it. Safety: the site uses a **limited Postgres role** (only
  SELECT/INSERT/UPDATE on our tables, no DDL/DELETE), a strong passphrase, and Neon's point-in-time restore.
  (Earlier idea, not needed now: Neon Data API + Neon Auth, or a Cloudflare Worker proxy.)
- **Write the website text to the kids** ("you"), never about them (see feedback memory / CLAUDE.md).
- **No gamification and no counts** (parent, 2026-11-12): no points, scores, totals, "today" counters,
  streaks or badges anywhere the kids see them; they can be discouraging. Feedback is right/wrong + the
  solution, and the summary shows only "Look at these once more". Effort goes into personalization.
  Updated 2026-11-14 (parent): **encouraging words only** - "Three in a row!", "Good comeback!", "Part C -
  brilliant!" - still no points, totals or badges, nothing the brothers can compare. Sessions are endless
  (batches of 10 picked as they go) with a soft "want a break?" every 15 questions or 25 minutes.

## Architecture

```
generators/*.py ──► site/bank.py (GitHub Actions) ──► _site/bank/<generator>.json  (questions + SVG)
                                                     _site/bank/index.json        (skills, counts)
_site/practice.html + practice.js  ── reads the bank, shows questions, records answers ──► Store
Store = LocalStore (Phase 1, browser only)  →  DbStore (Phase 2, Neon)   — same interface
```

Bank entry (one question):
`{id, gen, variant, seed, harder, difficulty, text, after, figure(svg|null), choices[5], choice_figures[5]|null,
answer, solution}` — `id = "<gen>|<variant>|<seed>|<h0/h1>"`, so the same id always rebuilds the same question.
Per generator in index.json: `{key, label, contest, keywords, skill, topics, counts}`.

Store interface (JS): `attempts(profile)`, `recordAttempt(profile, attempt)`; Phase 3 adds
`skillState(profile)`, `saveSkillState(profile, gen, state)`.

Database tables (Phase 2):
- `profiles(id, name, avatar, is_parent)`
- `attempts(id, profile_id, question_id, gen, variant, difficulty, chosen, correct, seconds, created_at)`
- `skill_state(profile_id, gen, level, box, due_at, streak, updated_at)` — primary key (profile_id, gen)
- `achievements(profile_id, code, earned_at)`

## Phases and tasks

### Phase 1 — Question bank + practice page (no database; answers kept in the browser)
- [x] 1.1 `site/bank.py`: export every generator × variant × seeds (normal + harder) to `_site/bank/*.json`;
      figures and choice figures as inline SVG; reportlab markup (`<b> <i> <br/> <sup> <font>`) passed as HTML.
      Seeds per variant configurable (start 20). Check the answer with `Question.check` while exporting.
- [x] 1.2 Run bank export in `.github/workflows/pages.yml` (after `site/build.py`).
- [x] 1.3 `site/practice.html` + `site/practice.js`: "Who's practising?" (Deniz, Toprak, Koray),
      a session of 10 questions, click an option → right/wrong + solution, end-of-session summary.
- [x] 1.4 `LocalStore` (localStorage) behind the Store interface; per profile attempts + skill state.
- [x] 1.5 Simple choice of questions: weak skills first (most wrong recently), then unseen skills.
- [x] 1.6 Link between the exam page (`index.html`) and the practice page.
- [x] 1.7 Test with the Koray profile (screenshots), commit, push, check the live site.

### Phase 2 — Postgres on Neon
- [x] 2.1 Parent: Neon project/database for this site. Replace CHANGE_ME in `db/001_init.sql` (already
      written) with a strong password and run it in the Neon SQL editor: tables + limited role `mk_site`.
- [x] 2.2 Lock file holds several secrets: extend `site/lock-token.mjs` + the page to `{github, db}`
      (keep reading the old one-secret file). Parent runs it locally with `MK_TOKEN`, `MK_DB` (the
      `mk_site` connection string) and `MK_PASSWORD`, so the secrets never go through chat.
- [x] 2.3 Unlock on page open (one password for exams + practice), then the profile picker.
- [x] 2.4 `DbStore` implementing the Store interface; switch practice.js to it; keep LocalStore as offline fallback.
- [x] 2.5 One-time import of any LocalStore data from Phase 1 into the database.

### Phase 3 — Smart practice
- [x] 3.1 Per kid per skill (generator): Leitner box + due date. Wrong → box 1 (due tomorrow);
      right → next box (1, 3, 7, 21 days).
- [x] 3.2 Adaptive difficulty per skill: level A→B→C→C harder; **each right answer = one level up, each wrong
      = one level down** (parent, 2026-11-12: "harder ones once the easy one is solved"); also inside a session.
- [x] 3.3 Session builder: ~60% due/weak skills, ~25% review, ~15% new or maintenance; never the same
      question id twice in a row; avoid repeats seen in the last 2 weeks.
- [x] 3.4 After a wrong answer: show the solution, offer the generator's "How to think about it" page
      (`teach()`, export it to the bank) and its warm-ups.

### Phase 4 — Learning from mistakes (parent picked these on 2026-11-12)
- [x] 4.1 **One more try + hint.** First wrong click: "Not quite, try once more" + a hint (first sentence of
      the solution, or `Question.hint` when a generator sets one). Second wrong click: show the answer.
      Only the first click counts (`correct`); store `second_try` too (new nullable column, `db/002_*.sql`).
- [x] 4.2 **Guessing does not level up.** A right first answer faster than a minimum time (Part A 4 s, B 6 s,
      C 8 s) keeps the level (box still moves). Applies in smart.js, so PDFs follow too.
- [x] 4.3 **Warm-ups for a stuck skill.** When a child missed a skill twice in a row, the next session starts
      that skill with 1-2 warm-ups (export `@warmup` questions to the bank: `bank/<key>.warmup.json`).
      Warm-ups are recorded with `variant = "warmup:<name>"` and do not change the level.
- [x] 4.4 **Mistake labels.** Wrong options carry the mistake they stand for. Extend `numeric_choices` /
      `text_choices` (backwards compatible) to accept labels, add them to `Question.meta["mistakes"]`
      (index -> short text), export to the bank, show "This is what you get if you <mistake>" after a wrong
      answer, and store `chosen` (already there) so the parent page can group mistakes. Add labels to
      generators gradually, most-missed skills first.
- [x] 4.5 **Hidden parent page** `parent.html` (not linked anywhere; needs the site password like the rest):
      per child each skill as *needs work / getting there / solid* (from smart.js states), recent mistakes
      with the option picked (and its mistake label), and what the next session will focus on.

Not now (parent's choice): recording paper-exam results, more teach pages, a "report a question" button
(the kids will tell the parent instead), new token/password, backups (Neon keeps data permanently; the
restore window of the free plan is 6 hours, and mk_site cannot delete anything).

### Phase 5 — Quality
- [x] 5.1 **Wording sweep** of every generator variant: things that can be read two ways (like "exactly 2
      wagons"), unclear counting rules (ends included? start counted?), options/units that do not match the
      question. Method: dump one question per variant (`scratch dump`), read all, fix generators (bump
      version), `python check.py`, look at previews. Progress per contest in the Log.

## What the parent needs to provide
- Phase 1: nothing.
- Phase 2: done (Neon project `math-kang` / `morning-glitter-66992696`, database `neondb`, limited role
  `mk_site`; site password unlocks both secrets). To redo the lock: `MK_TOKEN=... MK_DB=... MK_PASSWORD=...
  node site/lock-token.mjs` (the mk_site connection string is only in the parent's Neon account / the lock).

## Log
- 2026-11-11: Plan written. Exam website (site/index.html) already live with password-locked token.
  Next: Phase 1, task 1.1.
- 2026-11-11: Decided: Neon used from the browser with the connection string locked by the site password
  (no Neon Auth / proxy). Started Phase 1.
- 2026-11-11: Phase 1 tasks 1.1-1.6 done: site/bank.py (5,635 questions, 20 seeds/variant, ~30 MB, gzip
  ~150 KB for the largest file), site/practice.html + practice.js (profiles Deniz/Toprak/Koray, 10-question
  sessions, feedback + solution, summary with pictures), LocalStore, weak-skill weighting, links between the
  exam and practice pages. kt-styles got card tones (.kt-card--success/--danger).
  Next: 1.7 check the live site with the Koray profile, then Phase 2 (needs the parent: Neon, see 2.1).
- 2026-11-11: 1.7 done, practice page live (35 skills, 5,635 questions). db/001_init.sql written.
  Next: Phase 2, waiting for the parent (task 2.1).
- 2026-11-12: Phase 2 done. Neon via CLI login: tables from db/001_init.sql; mk_site created with one
  standalone SQL statement (roles made in the Neon console/CLI join neon_superuser - don't). mk_site can
  select/insert (update on skill_state, achievements), cannot delete/create/drop (tested). token.json v2 =
  {github, db} locked with the site password; secrets.js shared by both pages; practice page asks for the
  password first, saves answers to Neon, keeps unsaved ones locally and uploads them later. Tested end to end
  with Koray (Chrome via puppeteer-core in the scratchpad, not in the repo).
- 2026-11-12: Parent: remove counts/points, drop gamification, focus on personalization. Done on the page;
  plan updated (Phase 4 = parent view only). Next: Phase 3 (smart practice), task 3.1.
- 2026-11-12: Phase 3 done (3.4 without warm-ups: only the teach page). The per-skill state is replayed from
  the attempts table on every session (practice.js skillStates: Leitner box with GAP 0/1/3/7/21 days, level
  A/B/C/harder: 3 right in a row up, 2 wrong down); the skill_state table is not used yet. planSkills: up to
  5 weak, 3 due, 3 new, weak skills twice, then the rest; questions never seen first. Teaching pages exported
  to bank/*.teach.json (5 generators have one) and shown after a wrong answer.
  Next: Phase 4 parent view (4.1), or more teach() pages / warm-ups for skills the kids miss most.
- 2026-11-12: Personal PDF exams (4.2) added; planning code moved to site/smart.js (shared by both pages).
  Emojis removed from the profiles. Next: 4.1 parent view, or more teach() pages for the most-missed skills.
- 2026-11-12: Levels now move one step per answer (right up, wrong down), also for a skill's second question
  in the same session (practice.js adaptLater). Personal PDF exams use the same levels.
- 2026-11-12: GitHub Pages source set to "GitHub Actions" (it was "Deploy from a branch", which served the
  README). If the README ever shows again, check Settings -> Pages -> Source, then re-run "Publish website".
- 2026-11-12: New Phase 4 (learning from mistakes) planned with the parent: 4.1 try again + hint, 4.2 guesses
  do not level up, 4.3 warm-ups, 4.4 mistake labels, 4.5 hidden parent page. Old Phase 5 folded into 4.4.
- 2026-11-12: 4.1 + 4.2 done. Hint = the generator's META["skill"] (the method, never the answer).
  db/002_second_try.sql applied. Guess thresholds in smart.js MIN_SECONDS. Next: 4.3 warm-ups.
- 2026-11-12: 4.3 done: bank/<key>.warmup.json (5 generators have warm-ups); smart.js counts `stuck` (wrong
  first tries in a row, warm-ups ignored); stuck >= 2 -> up to 2 warm-ups right before that skill's question.
  Next: 4.5 hidden parent page, then 4.4 mistake labels.
- 2026-11-12: 4.5 done: site/parent.html + parent.js (not linked; password like the rest; noindex). Shows per
  child: summary, next-session focus, skills table (status from the review box), recent mistakes with the
  picked option. Next: 4.4 mistake labels (generators + kangaroo/choices.py).
- 2026-11-12: 4.4 done (mechanism + first generators). kangaroo.choices: mistakes may be (value, "what you
  did") pairs -> Choices list with .mistakes -> Question.meta["mistakes"] (registry) -> bank "mistakes".
  Practice: first wrong click hint "Did you ...?", final feedback "X is what you get if you ...";
  parent page shows it. Labelled so far: y2007_q04 (digit sum), y2025_q10 (runners). Label more
  generators gradually, most-missed first (see the parent page). Phase 4 complete.
- 2026-11-12: New algorithm in smart.js (parent: "1 easy right is not strong; 2 rights should already show it
  less; don't discourage"). Score 0-100 per skill: right A/B/C/C+ +15/20/25/30, quick guess or right on 2nd
  try +5, wrong -20; fades 10%/week after a week without practice. Status (parent page only): needs work
  (<15 with a real mistake) / getting there / solid (>=60 and 3+ rights). Weight = 1 + (100-score)/10
  (+ up to 2 when long unseen), untried 6, x up to 2 for skills added to the pool in the last 60 days
  (bank index "added" from git; pages.yml checks out full history). Sessions: max 3 weak skills, never two
  in a row, start and end with a strong skill; after 2 misses in a row the next question is a strong or
  untried one. End screen: "You're getting stronger at" / "You tried something new" first, then
  "Worth another look". Never the exact same question again (seen ones only if a skill runs out).
- 2026-11-12: 5.1 wording sweep: read one question per variant of all 35 generators (~175). No wrong answers.
  Fixed two-way readings: 2003 Q9 ("outside is red" -> every cube you can see, also below and behind),
  2007 Q3 ("letters in common" -> "different letters in common"). Fixed unclear solutions: 2003 Q10,
  2002 Q1, 2003 Q18, 2007 Q21 (a/an), 2007 Q23, 2024 Q24 and 2007 Q3 (singular/plural). Versions bumped.
  Only seed 11 per variant was read; plural/grammar slips in other seeds are still possible.
- 2026-11-12: Second sweep (parent asked to double-check): 3,040 generated questions of the 8 changed
  generators, every one re-checked with its independent answer check: 0 mismatches; only text was changed
  (git diff). It caught two of my own slips (2003 Q10 solution rounded mm away; "a 8 x 8") and three older
  ones (1 layers / they are in A / only 1 are) - all fixed. 2007 Q3 wording reverted to the contest's
  "How many common letters ...?": noticing that a repeated letter counts once IS the skill, so the question
  must not say "different". Rule: keep the contest's wording when the "ambiguity" is the trap being taught.
- 2026-11-12: Parent: a second session right after the first should practise other skills. smart.js: skills
  answered in the last 30 minutes are left out of the plan (weak ones too) and only fill up when there are
  not enough others (also for personal PDFs). Found and fixed a real bug on the way: answers came back in row
  order, not time order (answers uploaded later from the browser's offline queue looked like the newest), so
  "last practised", scores and levels could be replayed in the wrong order. Now sorted by created_at (SQL)
  and by time in skillStates. Browser test: two sessions back to back, 5 runs, 0 repeated skills.
- 2026-11-12: New pool question Austria 2023 Q12 (houses and streets: north + south = east + west), with teach page and warm-ups.
- 2026-11-12: New pool question Austria 2023 Q15 (fewest colours for circles joined by lines), teach page + warm-ups; shared solver kangaroo/solve.py colourings/min_colours and pictures.node_graph.
- 2026-11-12: New pool question Austria 2023 Q9 (fill a shape with pieces: which piece is on the dot), warm-ups; new shared module kangaroo/halfsquares.py (shapes of squares and half squares, tiling solver).
- 2026-11-12: New pool question Austria 2023 Q19 (count the orders that keep 'not first' rules), teach page + warm-ups.
- 2026-11-12: New pool question Austria 2023 Q22 (turning machine and printing machine: which order), teach page + warm-ups.
- 2026-11-12: New pool question Austria 2023 Q23 (sums of neighbours in a ring: guess and go around), teach page + warm-ups.
- 2026-11-12: New pool question Austria 2023 Q24 (one guess is right, the others have all but one right), teach page + warm-ups.
- 2026-11-13: Question layout (site + PDF): question text may use blank lines (paragraphs) and "- " lines (bullets), see kangaroo/layout.py; the final question sentence gets its own paragraph automatically. Rules/clues turned into bullet lists in 12 generators (cookies, pets, orders, houses, caterpillar, T-shirts, machines, digit cards, guesses, frogs, flag, thick wall).
- 2026-11-13: Removed the "Make a PDF exam instead" link from the practice page.
- 2026-11-13: Practice: "I'm not sure - skip this question" button. A skip is saved as chosen = -1, correct = false (counts like a wrong answer for the skill: score, level down, same skill easier later in the session, "worth another look"). Parent page: orange "Skipped - not sure" badge in "Recent mistakes and skips" and a Skipped count per skill.
- 2026-11-13: Practice answers use the new kt-styles choices (.kt-choice: letter key, no corner mark): pictures and short answers in a row, long answers one per line.
- 2026-11-13: Skip now simply moves on: no answer or solution is shown (also not in the end summary, which says "You skipped this one"). Still saved as a skip (counts like not knowing it).
- 2026-11-14: Kids misclicked while scrolling, so answering is two steps: a click (or a letter key) only picks an option, "Check my answer" (or Enter) locks it in. Kept the start at Part A: levels are per question and already move up after each right answer. Figures were cut slightly at the sides: bank.py now writes the exact SVG size (reportlab rounded it down) with a 2pt margin, and drops the shared id="clip" clip path.
- 2026-11-14: Practice got stuck on "Getting your questions ready…" after Stop and picking the profile again. Any error while building a session now shows "Could not get the questions ready" with a Try again button (20 s timeout), failed bank downloads are no longer cached, and a newer profile click wins. Also: the practice page did not load second_try, so a right second try counted like a wrong answer in its scoring (the parent page was right).
- 2026-11-14: Endless practice sessions: the next 10 are picked in the background 3 questions before the end (skills from the last 30 minutes wait, as before; warm-ups once per session). No progress bar, "Question N". Soft break hint every 15 questions / 25 minutes with "Stop for now". Encouraging words in the feedback title (streak of 3/5/8+, back on track after two misses, a skill missed before now right, Part C right, second-try comeback); no numbers or points.
- 2026-11-14: Test profile Koray: each question opens with the right answer already picked (one click on Check to test a right answer, pick another to test a wrong one).
- 2026-11-14: Parent page: "Recent mistakes and skips" table replaced by "To study together": every exact question answered wrong on the first try or skipped (newest first, one card per question), shown in full (text, figure, options with the pick in red and the answer in green, mistake label, skill, solution behind a toggle). "Studied together" moves it to a collapsed "Studied together" list (undo there). Saved in the unused achievements table as studied:<question id> (undo renames it to unstudied:<id>:<time>; the site cannot delete). Does not change what the kids are asked.
- 2026-11-14: Practice: no "Question N" in the header; the skip button is now "Skip question", large like "Check my answer", on the right of the same row.
- 2026-11-14: Parent "To study together": no answer and no pick shown; options are clickable with "Check answer" (wrong: "Not quite - try again" + the mistake hint) and "Show answer", then the solution. A question also moves to "Done" by itself when a later question of the same skill was right on the first try (not a quick guess), badge "Got a similar one right on <date>".
- 2026-11-14: Practice header: no name or Part badge; a row of circles instead (right green, right on the 2nd try light green, wrong an empty ring - "a learning opportunity", never red - skipped grey). ?profile=Deniz in the URL (set when a profile starts, opens it straight away). Feedback: a big cheer only (no solution after a right answer, it was never read); after a wrong answer neither the answer nor the solution is shown (it would be memorised), only what the picked option stands for; the end summary no longer shows answers either.
- 2026-11-14: Feedback text the same size as the question text (cheer semibold, not big and bold).
- 2026-11-14: Kid messages ("Not quite. Try once more!" + hint, feedback, break hint) at question-text size, no bold.
