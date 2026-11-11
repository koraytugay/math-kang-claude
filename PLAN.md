# Plan: practice website (kids solve questions online, the site learns what they get wrong)

**How to resume:** open Claude Code in this repo and say *"continue PLAN.md"*. The agent reads this file,
finds the first unchecked `[ ]` task, and goes on from there. Tick tasks `[x]` as they are done and add a
line to the **Log** at the bottom (date, what was done, what is next). Keep this file the single source of
truth for this project; decisions change here, not only in chat.

## Goal

Deniz and Toprak (about 10, grade 3-4) open the website on the family desktop, pick their profile, and
solve Math Kangaroo style questions on screen. Every answer is saved. The site gives more of what each child
gets wrong, adapts the difficulty, explains mistakes, and rewards progress (points, streaks, badges).
The PDF exams (`make_exam.py`, the GitHub Actions workflow, the exam page) keep working unchanged.

## Decisions (made with the parent, 2026-11-11)

- **Profiles:** `Deniz`, `Toprak`, `Koray`. Koray is the parent; **always test with Koray**, never with the
  kids' profiles. No passwords for the kids (pick an avatar, "Who's practising?").
- **Desktop only.** No phone/tablet work. Style with kt-styles (see CLAUDE.md / `~/github/koraytugay/kt-styles`);
  missing UI elements are added to kt-styles first.
- **Generators stay Python; no rewrite to JS.** One source, two outputs: PDF (as now) and a pre-generated
  **question bank** (JSON + SVG figures) built in GitHub Actions and published with the site.
- **Database: Postgres on Neon** (the parent already has an account). The browser must never hold the
  database connection string. Preferred: **Neon Data API + Neon Auth** (browser calls an HTTPS API with a
  login, row-level security in Postgres). Fallback: a tiny free proxy (Cloudflare Worker) holding the
  connection string. Verify Neon's current docs before Phase 2.
- **Write the website text to the kids** ("you"), never about them (see feedback memory / CLAUDE.md).
- Siblings: no head-to-head leaderboard; personal goals + one shared family goal.

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

Store interface (JS): `profiles()`, `recordAttempt(profile, attempt)`, `attempts(profile)`,
`skillState(profile)`, `saveSkillState(profile, gen, state)`, `achievements(profile)`, `award(profile, code)`.

Database tables (Phase 2):
- `profiles(id, name, avatar, is_parent)`
- `attempts(id, profile_id, question_id, gen, variant, difficulty, chosen, correct, seconds, created_at)`
- `skill_state(profile_id, gen, level, box, due_at, streak, updated_at)` — primary key (profile_id, gen)
- `achievements(profile_id, code, earned_at)`

## Phases and tasks

### Phase 1 — Question bank + practice page (no database; answers kept in the browser)
- [ ] 1.1 `site/bank.py`: export every generator × variant × seeds (normal + harder) to `_site/bank/*.json`;
      figures and choice figures as inline SVG; reportlab markup (`<b> <i> <br/> <sup> <font>`) passed as HTML.
      Seeds per variant configurable (start 20). Check the answer with `Question.check` while exporting.
- [ ] 1.2 Run bank export in `.github/workflows/pages.yml` (after `site/build.py`).
- [ ] 1.3 `site/practice.html` + `site/practice.js`: "Who's practising?" (Deniz, Toprak, Koray),
      a session of 10 questions, click an option → right/wrong + solution, end-of-session summary.
- [ ] 1.4 `LocalStore` (localStorage) behind the Store interface; per profile attempts + skill state.
- [ ] 1.5 Simple choice of questions: weak skills first (most wrong recently), then unseen skills.
- [ ] 1.6 Link between the exam page (`index.html`) and the practice page.
- [ ] 1.7 Test with the Koray profile (screenshots), commit, push, check the live site.

### Phase 2 — Postgres on Neon
- [ ] 2.1 Parent: Neon project for this site; enable Data API + Neon Auth (or decide on the proxy fallback).
      Give the agent: the Data API URL and the auth settings (NOT the database password in chat if avoidable).
- [ ] 2.2 SQL migration file `db/001_init.sql` (tables above + row-level security: only the family login).
- [ ] 2.3 Family login on the site (parent signs in once per computer), then the profile picker.
- [ ] 2.4 `DbStore` implementing the Store interface; switch practice.js to it; keep LocalStore as offline fallback.
- [ ] 2.5 One-time import of any LocalStore data from Phase 1 into the database.

### Phase 3 — Smart practice
- [ ] 3.1 Per kid per skill (generator): Leitner box + due date. Wrong → box 1 (due tomorrow);
      right → next box (1, 3, 7, 21 days).
- [ ] 3.2 Adaptive difficulty per skill: level 1→2→3, then `harder`; 3 right in a row up, 2 wrong down.
- [ ] 3.3 Session builder: ~60% due/weak skills, ~25% review, ~15% new or maintenance; never the same
      question id twice in a row; avoid repeats seen in the last 2 weeks.
- [ ] 3.4 After a wrong answer: show the solution, offer the generator's "How to think about it" page
      (`teach()`, export it to the bank) and its warm-ups.

### Phase 4 — Gamification + parent view
- [ ] 4.1 Points = contest points (3/4/5), daily streak, levels.
- [ ] 4.2 Badges: per skill mastered, milestones (first Part C, 100 questions, 7-day streak).
- [ ] 4.3 Kangaroo avatar that unlocks accessories with levels.
- [ ] 4.4 Mock contest mode: timed, real Kangaroo scoring, personal best.
- [ ] 4.5 Family goal: questions together per week.
- [ ] 4.6 Parent view (Koray): skill table per kid, recent mistakes, "print PDF of weak spots"
      (fills the exam workflow's `website` input with the weak generators).

### Phase 5 — Explaining mistakes (later)
- [ ] 5.1 Label wrong options in generators with the mistake they represent (extend `numeric_choices`
      to accept labels, backwards compatible), export to the bank, show "you often ...".

## What the parent needs to provide
- Phase 1: nothing.
- Phase 2: Neon project with Data API + Neon Auth enabled (or OK for a Cloudflare account for the proxy),
  and the Data API URL / auth config. The agent will give exact click-by-click steps at that point.

## Log
- 2026-11-11: Plan written. Exam website (site/index.html) already live with password-locked token.
  Next: Phase 1, task 1.1.
