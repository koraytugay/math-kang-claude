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
- 2026-11-14: End summary buttons: "Keep practising" (back to the same session and its circles, next question) and "Start over" (a new session); "Switch profile" removed (the start page still has the profiles).
- 2026-11-14: One text size (fs-lg) for everything the kids read on the practice page (question, messages, end summary), no bold except headings. kt-styles alerts now inherit the surrounding text size (they were always fs-sm).
- 2026-11-14: Parent page: "Sessions" table (last 10, newest first): when, minutes, questions, right first try, right second try, wrong, skipped, skills. No session column in the database: answers less than 30 minutes apart are one session; "now" badge when the last answer is under 10 minutes old. Only this table reloads every minute (and when the tab comes back), so study cards in use are not reset.
- 2026-11-14: Parent Sessions table: the Skills column (no use to the parent) replaced by one column per level (0 Part A, 1 Part B, 2 Part C, 3 Part C harder): questions answered at that level, right first try in brackets.
- 2026-11-14: countdown.html (parent asked for a page to hype the kids): days to the contest (March 21, 2027) with a ticking clock, both kids **combined** (never per child, nothing to compare): questions answered, right first try, mistakes turned into learning (same rule as the parent page), days practised; next goal (25 ... 5000) with a bar and "about N a day until the contest"; a sticker book (19 stickers, locked ones show how to earn them, confetti for new ones - remembered per browser). Not linked anywhere yet. A deliberate exception to "no counts" for this page only: the parent asked for it, and it is shared, not a comparison.
- 2026-11-14: Countdown goals set with the parent: ~12 study weekends x ~75 questions together + the first 100 = **1,000 on contest day (contest goal)**, **1,250 the ultimate goal**. Flags every 100 up to there in one row (100 ... 1,000, 1,250), normal spacing; a 🍔 (McDonald's treat) on 300, 600, 900 and 1,250. New "Weekend goal" bar: 75 together per weekend (Sat+Sun; on weekdays it shows the last weekend). New stickers: Weekend warrior (75 in a weekend), Super weekend (100), Five great weekends.
- 2026-11-14: Countdown goal flags, the goal bar and the 1,000 / 1,250 stickers now count answers **right on the first try** (not a quick guess), not all answers: answers alone filled the flags too fast (parent). The "right on the first try" card uses the same number. The weekend goal (75) still counts answers.
- 2026-11-14: Ultimate goal is now **1,500 right on the first try = a real Pokémon booster pack** (the kids agreed and were hyped). Flags 100 ... 1,000 (contest goal), 1,250 🍔, 1,500 🎴; the 1,250 sticker became "Booster pack!" at 1,500. 🍔 = a McDonald's treat at 300, 600, 900, 1,250.
- 2026-11-14: Practice: the row of answer circles (mk-dots) removed - distracting (parent). Only the Stop button is left in that row.
- 2026-11-14: Countdown: 1,500 is no longer a small pill; it has its own big shiny pill under the flags ("1,500 ⚡ POKÉMON BOOSTER PACK! ⚡ N to go", yellow/blue, glowing, a shine sweeping across; "YOU DID IT!" when reached).
- 2026-11-14: Countdown goals lowered (they count right-first-try answers now): flags 100 ... 1,000 (**ultimate goal**), then the big **Pokémon booster pack pill at 1,250**; 🍔 McDonald's treat at 200, 400, 600, 800 and 1,000. The "88 / 100 right on the first try" text next to the goal title removed.
- 2026-11-14: Countdown goals count **right answers: first try (not a quick guess) or second try** (a son: a right second try is right too). The booster pack is back in the flag row as its last pill ("⚡ 1,250 POKÉMON PACK! ⚡"): same height, it fills the rest of the row, yellow with a blue edge and a shine sweeping across.
- 2026-11-14: Countdown: weekend goal removed completely (section and its 3 stickers; nobody cared). Smaller header: one line "127 days to go!" and the cheer, no date line, no hours/minutes clock.
- 2026-11-14: Pokémon pill text: "1,250 4 Pokémon Packs!" (no emojis); the reward is 4 packs (note line and sticker say so too).
- 2026-11-14: Sticker book grown from 20 to 71 stickers in 9 groups with headings and "N of M" each: Questions, Right answers, Learning from mistakes (second tries, learned, warm-ups), Tough ones (Part B/C, hardest numbers, 2+ minutes of thinking), In a row (right first try in a row per child, practice days in a row), Practice time (days, big days, total thinking time, before 9 am), Skills (tried, solid, "gym badge" = every question of one past exam solid), Topics (25 right in logic/spatial/counting/arithmetic/geometry/patterns), On the way to March 21 (100/50/10 days left, winter holidays, Jan 1, March 20, contest day). All both kids together.
- 2026-11-14: Stickers moved to site/stickers.js (shared). Practice page: when a child unlocks a sticker with an answer (worked out from **their own** answers, so it shows even if the brother has it already), a big "You unlocked a sticker!!!" pop-up with the sticker and confetti; Enter / Escape / "Awesome!" closes it. The countdown page stays the team's book (both kids together). Nothing is saved for stickers anywhere (always worked out from the answers). Test profile Koray: also a random sticker after 25% of the answers, to see the pop-up; Koray's answers never count on the countdown page. A deliberate exception to "no counts or badges for the kids" on the practice page: the parent asked for it.
- 2026-11-15: 53 new stickers (124 in all). **One per skill**: `META["sticker"] = (emoji, name)` in every generator, exported in bank/index.json, grouped by exam in the sticker book ("Skills from Austrian Kangaroo 2023"), earned when the skill is solid once; `check.py` fails a pool question without a sticker or with a name used twice, so new questions bring their own. **Level up**: Part C right (not a guess) in 1/5/10/20 skills, hardest numbers in 1/5/10. **Turnarounds**: a skill that was "needs work" once becomes solid (1/3/5/10). smart.js skillStates keeps `everSolid` and `turned`; the solid-skill stickers (Skill star, gym badges) now use "solid once" too, so no sticker is lost when a score fades (and none pops up twice).
- 2026-11-16: New question Austrian Kangaroo 2022 Q16 (which postcard is whose: start with the clue that fits only one card). Simple icon cards (sun, moon, star, heart, flower; `kangaroo.pictures.picture_card`) instead of the contest's photos, at the parent's request. Sticker 📮 "Postcard sorter". The parent decided: no more teaching pages or warm-ups for new questions (the kids don't use them); removed from CLAUDE.md and the new-questions skill.
- 2026-11-17: New question Austrian Kangaroo 2022 Q24 (coloured cards hide numbers, row sums: put two rows together or compare rows; twist: missing column sum = all rows − other columns). Sticker 🟫 "Colour code breaker". `kangaroo.solve.linear_value` (exact elimination) for the answer checks.
- 2026-11-17: New question Austrian Kangaroo 2022 Q17 (fewest shapes for several "exactly" rules: one shape counts for two rules; also the largest number and which shape is surely chosen). Sticker 🔺 "Shape picker".
- 2026-11-17: New question Austrian Kangaroo 2022 Q19 (ant crawling over a pyramid of cubes, drawn from the front: add all ups, all downs, all flat pieces; stairs, towers with dips, how much longer than the floor, find the cube side). Sticker 🐜 "Ant trail".
- 2026-11-17: New question Austrian Kangaroo 2022 Q20 (road tiles in a hexagon between six houses: follow the roads that meet, check every rule incl. the "not"; our own tiles, never turned, roads that meet have one meeting point). Sticker 🛣️ "Road tiler".
- 2026-11-17: y2022_q17 v2: the "largest number" solution now explains why (shapes that break no rule + at most the rule numbers, and which rule has no shape that fits it alone), after the parent found the old one made no sense.
- 2026-11-17: y2022_q17 v3: removed the "largest number" variant - "I have chosen exactly ..." describes the whole choice, so adding shapes that fit no rule makes no sense (parent). New variant which_group: five chosen groups in numbered boxes, only one matches every "exactly" (the others are one shape off in one rule).
- 2026-11-19: New question Canada 2026 Q7 (cutting a stack of overlapping paper squares on a grid: cut each sheet on its own, also the hidden parts, a line along an edge does not cut; how many squares / pieces / not squares / squares of one colour, 3 sheets or 4, 2 or 3 cuts). Solved without an answer key (answer 5). Sticker 🥞 "Stack slicer".
- 2026-11-19: New question Canada 2026 Q9 (picture puzzle on a grid, four of five pieces fill the white squares: all pieces minus the empty squares is the piece left over; two pieces of that size, a lost piece, two of six left out, all pieces the same size). Solved without an answer key (answer A). Sticker 💝 "Heart puzzler". New kangaroo.polyomino.place_inside.
- 2026-11-21: New question Canada 2026 Q14 (towers of cubes seen from the front: look along each line from your end, a tower is seen only if taller than all in front; how many seen / hidden, from another side, cube faces seen, seen from front or back). Answer D from our own key (UNOFFICIAL). Sticker 🔭 "Tower spotter".
- 2026-11-21: New question Canada 2026 Q16 (coloured paper strip folded in half, cut, folded again: matching squares share a colour, link the pairs of every fold and count the groups; most colours, bigger cut, squares with the colour of square 1, two cuts, how many squares were cut off). Answer B (1) from our own key (UNOFFICIAL). Sticker 🎀 "Ribbon folder".
- 2026-11-21: y2026_q16 v2: the strip question was too hard for the kids (parent). Three easier difficulty-1 variants: one_fold (only one fold, how many colours), which_square (which square matches square k), short_strip (4 or 6 squares, one cut).
- 2026-11-21: New question Canada 2026 Q22 (big 3x3x3 cube of black and white cubes, three faces drawn: copy the cubes you can already see, turn the picture for the new side, then use the colour totals for the hidden cubes; how many cubes are hidden, how many hidden are black/white, what she sees when the hidden cubes are all one colour, what she could see from the left / from behind). Answer B from our own key (UNOFFICIAL), confirmed by trying every filling of the 8 hidden cubes. Sticker 👀 "Side peeker".
- 2026-11-21: New questions Canada 2026 Q23 (sweets in a grid, numbers = sweets of the neighbours: add the neighbours of a square, rows of 3-4, 2x3 grid, one hidden square, the 3x3 total; sticker 🍬 "Sweet solver") and Q24 (drawing balls, how many to be SURE: worst luck = all the other colours first, then one more; pictured boxes with 2-3 colours, reverse with one unknown colour, two clues, all colours, the three-clue contest question; sticker 🎩 "Sure-draw wizard"). Parent asked for easy versions: 2 easy variants for Q23, 3 for Q24. Both answers from our own key (UNOFFICIAL): A (16) and C (7), confirmed by brute force.
- 2026-11-21: Exam page (index.html): the contest pills are now one row per set ("All" on its own row, then Set 01 ..., Set 03 ...), parent request.
- 2026-11-21: Exam page: no more 12px jump when switching contests (the space between contests is now only between visible ones: a hidden contest left a margin on the next one, so only the first, 2002, sat higher); pill rows closer together. Checked in headless Chrome: content top is the same for every pill.
- 2026-11-23: **Harder practice, rungs.** Parent: the kids say practice starts too easy. The log (Deniz and Toprak, 11-22 Nov, ~120 answers each): 82-83% right, about half of all questions Part A style, level 3 answered right as often as level 1. Reading the 10 newest generators against their contest originals showed our "Part A/B/C" levels are only steps inside a skill, not the contest parts: for a Part C original (Q17-24) step 1 is much easier than the contest question, for a Part A original it is aligned. So: (1) each generator rates its four steps with `META["rungs"]` = easier / aligned / harder compared with the original (default from the contest part; the 10 newest are rated by hand; `python check.py --rungs`). (2) smart.js: a skill's level is now a rung (0 easier, 1 aligned, 2 harder); every skill starts at aligned, right = one rung up, wrong = one down; a question is picked on the rung, else the nearest one with fresh questions, and 15% of the time from another rung (nothing disappears). Parent page and study cards show Easier / Aligned / Harder instead of Part A/B/C. (3) Weight = 0.4 + (100 - score) / 9 (a mastered skill ~30 times rarer than a weak one, never zero) + 1 review place per 8 questions for a solid skill. (4) New-in-pool boost 3x fading over 21 days (was 2x over 60), and up to 2 untried new skills get a place in every session. (5) "Skip question" is now "Skip - Study with Dad". The attempts table is unchanged (difficulty + harder are steps; rungs are mapped with the generator's rungs). Open: 19 skills have only one aligned variant (`check.py --rungs`), so aligned questions run out sooner there; add variants over time. The PDFs still print "Part A/B/C" headers (steps).
- 2026-11-23 (later): Rungs per variant. `@variant(difficulty=N, rungs=(normal, harder))` rates one variant (the step rating stays the default); bank/index.json carries `vr` {variant: [rung, rung with harder numbers]} so the site and the parent page use it (the exam page sends `key@r<rung>`, make_exam.py picks a variant on that rung). Rated by hand, from the wording and the sizes: the 19 skills that had one aligned variant (y2007_q24's "which design cannot be made" is the contest question, so it is aligned; harder=True often lands on the contest's own size). Three skills still had one aligned variant, so new ones: y2026_q23 one_row (how many sweets in a row; a middle-square question was dropped, its answer was almost always 1), y2026_q24 three_clues_total (the contest clues, all balls in the box), y2003_q18 two_of_five (five pieces, which two cover the hole). Every skill now has 2+ aligned variants. The other 35 skills use the step ratings by contest part (not reviewed variant by variant).
- 2026-11-23 (later still): **Studied together -> retry early.** New table `study_notes` (db/003_study_notes.sql, created by the parent in the Neon editor; mk_site has select/insert/update; the 14 old `studied:` rows of the achievements table were copied over, achievements is no longer used). Clicking "Studied together" stores the question (kind 'studied') and a note to retry its skill (kind 'retry'); undo sets done_at (and the retry, if no other question of that skill is still marked). The child's next session (first batch) puts every owed skill in the first 3 questions: places 2 and 3 (place 1 stays a confident skill), or from place 1 when 3+ are owed (smart.js planSkills `retries`); the question is a new one of that skill, on the aligned rung at most; it stays owed until the child answers one question of it (a skip does not count), then done_at is set. The swap after two misses in a row leaves it in place. Checked with the real table (profile koray) and a 400-plan simulation.
- 2026-11-23 (later still): the 14 questions studied before this feature got retry notes too (7 skills each for Deniz and Toprak); at most 3 owed skills go into one session, the rest follow in the next ones until each has been answered once.
- 2026-11-24: Review follow-ups. (1) Time per answer is saved as at most 300 s (practice.js MAX_SECONDS): three of the 383 logged answers were 5-7 minutes (idle tabs); only the "too fast = guess" rule reads seconds, so scoring is unchanged. (2) New tests for smart.js: `node --test tests/smart.test.mjs` (scoring, rungs, fade, status, planSkills incl. owed skills in the first 3 places). (3) Checked and left alone: seed 0 is not favoured by the retry flow (the 23 variants with only 1-2 distinct questions always keep seed 0; the bank is otherwise uniform); repo size is not a CI problem (checkout 10 s of a 3 min build, 115 s is bank.py).
