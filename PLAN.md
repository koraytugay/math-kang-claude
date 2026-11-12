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
  kids' profiles. No passwords for the kids (pick an avatar, "Who's practising?").
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
- [x] 3.2 Adaptive difficulty per skill: level 1→2→3, then `harder`; 3 right in a row up, 2 wrong down.
- [x] 3.3 Session builder: ~60% due/weak skills, ~25% review, ~15% new or maintenance; never the same
      question id twice in a row; avoid repeats seen in the last 2 weeks.
- [x] 3.4 After a wrong answer: show the solution, offer the generator's "How to think about it" page
      (`teach()`, export it to the bank) and its warm-ups.

### Phase 4 — Parent view (only Koray sees it)
- [ ] 4.1 Parent view: skill table per kid (weak / getting there / strong), recent mistakes.
- [ ] 4.2 "Print a PDF of the weak spots" (fills the exam workflow's `website` input with the weak generators).
- (Gamification — points, streaks, badges, avatars, family goal — dropped by the parent on 2026-11-12.)

### Phase 5 — Explaining mistakes (later)
- [ ] 5.1 Label wrong options in generators with the mistake they represent (extend `numeric_choices`
      to accept labels, backwards compatible), export to the bank, show "you often ...".

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
