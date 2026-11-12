# Plan: practice website (kids solve questions online, the site learns what they get wrong)

**How to resume:** open Claude Code in this repo and say *"continue PLAN.md"*. The agent reads this file,
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
