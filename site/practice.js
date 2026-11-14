// Practice page: the site password unlocks the database (secrets.js), a child picks their profile and
// solves 10 questions from the bank (bank/*.json, made by site/bank.py). Answers go to Postgres on Neon
// (DbStore). Answers that could not be saved, and Phase 1 answers kept in the browser (LocalStore), are
// uploaded the next time (see PLAN.md).
"use strict";

const $ = (id) => document.getElementById(id);
const el = (tag, cls, text) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
};

const PROFILES = [
    { id: "deniz", name: "Deniz" },
    { id: "toprak", name: "Toprak" },
    { id: "koray", name: "Koray", parent: true },   // the parent's test profile
];
const TEST_PROFILE = "koray";    // the parent's test profile opens each question with the right answer picked
const BATCH = 10;                // sessions are endless: the next BATCH questions are picked as they run out
const BREAK_EVERY = 15, BREAK_MINUTES = 25;   // then a soft "want a break?" (they can just go on)

// ------------------------------------------------------------------ store
class LocalStore {
    key(p) { return `mk.practice.${p}`; }
    read(p) {
        try { return JSON.parse(localStorage.getItem(this.key(p))) || { attempts: [] }; }
        catch { return { attempts: [] }; }
    }
    async attempts(p) { return this.read(p).attempts; }
    async recordAttempt(p, a) {
        const d = this.read(p);
        d.attempts.push(a);
        try { localStorage.setItem(this.key(p), JSON.stringify(d)); } catch { /* full or blocked */ }
    }
}
const local = new LocalStore();

const NEON = "https://cdn.jsdelivr.net/npm/@neondatabase/serverless@1.2.0/+esm";
class DbStore {
    constructor(url) {
        this.ready = import(NEON).then((m) => { this.sql = m.neon(url, { disableWarningInBrowsers: true }); });
    }
    async attempts(p) {
        await this.ready;
        await this.flush(p);
        return this.sql`select question_id as id, gen, variant, difficulty, harder, chosen, correct, second_try,
                               seconds, created_at as at
                        from attempts where profile_id = ${p} order by created_at, id`;
    }
    async insert(p, a) {
        await this.sql`insert into attempts (profile_id, question_id, gen, variant, difficulty, harder, chosen,
                                             correct, second_try, seconds, created_at)
                       values (${p}, ${a.id}, ${a.gen}, ${a.variant}, ${a.difficulty}, ${a.harder}, ${a.chosen},
                               ${a.correct}, ${a.second_try ?? null}, ${a.seconds}, ${a.at})`;
    }
    async recordAttempt(p, a) {
        await this.ready;
        try { await this.insert(p, a); } catch (e) { await local.recordAttempt(p, a); throw e; }
    }
    /** Upload answers that only exist in this browser (offline moments, Phase 1), then forget them. */
    async flush(p) {
        const waiting = await local.attempts(p);
        if (!waiting.length) return;
        for (const a of waiting) await this.insert(p, a);
        try { localStorage.removeItem(local.key(p)); } catch { /* blocked */ }
    }
}
let store = null;

// ------------------------------------------------------------------ bank
let index = null;
const files = new Map();
async function bankFor(gen) {
    if (!files.has(gen.key)) {
        // a failed download is not kept, so "Try again" really fetches it again
        const got = fetch(gen.file).then((r) => { if (!r.ok) throw new Error(`${gen.file}: ${r.status}`); return r.json(); });
        got.catch(() => files.delete(gen.key));
        files.set(gen.key, got);
    }
    return files.get(gen.key);
}

// ------------------------------------------------------------------ choosing questions: see smart.js
// exclude: ids already in this session. The first batch also keeps the states for the summary.
async function buildSession(profile, exclude = [], first = true) {
    const attempts = await store.attempts(profile.id);
    const states = skillStates(attempts);
    if (first) sessionStates = states;
    const seen = new Set([...attempts.map((a) => a.id), ...exclude]);

    const qs = [];
    for (const g of planSkills(index.generators, states, BATCH)) {
        const bank = await bankFor(g);
        const [difficulty, harder] = LEVELS[states.get(g.key)?.level ?? 0];
        const free = (q) => !qs.some((x) => x.id === q.id);
        const atLevel = (q) => q.difficulty === difficulty && q.harder === harder;
        const tiers = [
            bank.filter((q) => free(q) && !seen.has(q.id) && atLevel(q)),      // new question, right level
            bank.filter((q) => free(q) && !seen.has(q.id) && q.difficulty === difficulty),
            bank.filter((q) => free(q) && !seen.has(q.id)),
            bank.filter(free),                                                 // only if the skill ran out
        ];
        const list = tiers.find((t) => t.length) || bank;
        qs.push({ ...list[Math.floor(Math.random() * list.length)], gen: g.key, teach: g.teach });
    }
    // Keep the plan's encouraging order (smart.js): a confident start and finish, weak skills spread out.
    // A skill missed twice in a row starts with up to 2 warm-ups (small steps), right before its question.
    for (const g of index.generators) {
        if (!g.warmup || (states.get(g.key)?.stuck ?? 0) < 2) continue;
        if (!first && session.some((q) => q.isWarmup && q.gen === g.key)) continue;   // once per session
        const k = qs.findIndex((q) => q.gen === g.key);
        if (k < 0) continue;
        const warm = await fetch(g.warmup).then((r) => r.json());
        const picks = [];
        for (const v of shuffle([...new Set(warm.map((w) => w.variant))]).slice(0, 2)) {
            const list = warm.filter((w) => w.variant === v && !seen.has(w.id));
            const pool = list.length ? list : warm.filter((w) => w.variant === v);
            picks.push({ ...pool[Math.floor(Math.random() * pool.length)], gen: g.key, isWarmup: true });
        }
        qs.splice(k, 0, ...picks);
    }
    return qs;
}

// ------------------------------------------------------------------ screens
function show(id) { for (const s of ["who", "play", "done"]) $(s).hidden = s !== id; window.scrollTo(0, 0); }

async function renderProfiles() {
    const box = $("profiles");
    box.innerHTML = "";
    for (const p of PROFILES) {
        const b = el("button", "kt-card kt-card--selectable");
        b.type = "button";
        b.setAttribute("aria-pressed", "false");
        const body = el("div", "kt-card__body kt-stack");
        body.append(el("div", "kt-card__title", p.name),
            el("div", "kt-card__subtitle", "Start practising"));
        b.append(body);
        b.onclick = () => start(p);
        box.append(b);
    }
}

let profile = null, session = [], pos = 0, shownAt = 0, results = [], sessionStates = new Map();

async function start(p) {
    profile = p;
    try { history.replaceState(null, "", `?profile=${encodeURIComponent(p.name)}`); } catch { /* file:// */ }
    $("dots").replaceChildren();
    show("play");
    $("q-text").textContent = "Getting your questions ready…";
    $("q-fig").innerHTML = ""; $("q-after").textContent = ""; $("q-options").innerHTML = "";
    $("feedback").hidden = true;
    $("retry").hidden = true;
    $("skip-row").hidden = true;
    const mine = ++starting;                       // a later click on a profile wins
    try {
        const built = await withTimeout(buildSession(p), 20000);
        if (mine !== starting) return;
        session = built;
    } catch (e) {
        if (mine !== starting) return;
        console.error(e);
        $("q-text").innerHTML = "";
        const box = el("div", "kt-alert kt-alert--danger");
        box.append(el("div", "kt-alert__title", "Could not get the questions ready."),
            el("div", "kt-mb-2", "Check the internet connection and try again."));
        const again = el("button", "kt-btn kt-btn--primary", "Try again");
        again.type = "button";
        again.onclick = () => start(p);
        box.append(again);
        $("q-text").append(box);
        return;
    }
    $("skip-row").hidden = false;
    pos = 0; results = []; refill = null; startedAt = Date.now(); lastBreak = { at: startedAt, n: 0 };
    renderQuestion();
}
let refill = null, startedAt = 0, lastBreak = { at: 0, n: 0 };
/** The next batch, picked in the background a few questions before the session runs out. */
function refillSoon() {
    if (refill || session.length - pos > 3) return;
    const who = profile;
    refill = buildSession(who, session.map((q) => q.id), false)
        .then((more) => { if (who === profile) session.push(...more); })
        .catch((e) => console.error(e))
        .finally(() => { refill = null; });
}
let starting = 0;
const withTimeout = (promise, ms) => Promise.race([promise,
    new Promise((_, reject) => setTimeout(() => reject(new Error("timed out")), ms))]);

function bigger(container, factor) {
    container.querySelectorAll("svg").forEach((s) => {
        const w = parseFloat(s.getAttribute("width")), h = parseFloat(s.getAttribute("height"));
        if (w && h) { s.setAttribute("width", w * factor); s.setAttribute("height", h * factor); }
    });
}

function renderQuestion() {
    const q = session[pos];
    refillSoon();
    $("q-text").innerHTML = q.text;
    $("q-fig").innerHTML = q.figure || "";
    $("q-fig").hidden = !q.figure;
    bigger($("q-fig"), 2);
    $("q-after").innerHTML = q.after;
    $("feedback").hidden = true;
    $("retry").hidden = true;
    $("skip").hidden = false;
    $("check").hidden = false;
    firstChoice = null;
    selected = null;
    $("check").disabled = true;

    // kt-choices: pictures in a row (key on top), short answers in a row, long answers one per line.
    const opts = $("q-options");
    const plainLen = (c) => c.replace(/<[^>]*>/g, "").length;
    const row = q.choice_figures || Math.max(...q.choices.map(plainLen)) <= 14;
    opts.className = `kt-choices kt-mt-4${row ? " kt-choices--row" : ""}`;
    opts.innerHTML = "";
    q.choices.forEach((c, i) => {
        const b = el("button", `kt-choice${q.choice_figures ? " kt-choice--stacked" : ""}`);
        b.type = "button";
        b.append(el("span", "kt-choice__key", "ABCDE"[i]));
        const content = el("span", "kt-choice__label mk-opt-text");
        if (q.choice_figures) { content.innerHTML = q.choice_figures[i]; bigger(content, 1.6); } else content.innerHTML = c;
        b.append(content);
        b.onclick = () => select(i);
        opts.append(b);
    });
    shownAt = Date.now();
    if (profile.id === TEST_PROFILE) select(q.answer);   // the parent's test account: right answer picked
}

let firstChoice = null;          // the wrong first answer of the current question, or null
let selected = null;             // the option picked but not checked yet, or null

// Two steps, so a click while scrolling never counts: a click only picks an option (it can be changed),
// "Check my answer" locks it in.
function select(i) {
    if (!$("feedback").hidden) return;
    const buttons = [...$("q-options").children];
    if (buttons[i].disabled) return;
    selected = i;
    buttons.forEach((b, j) => { if (!b.disabled) b.setAttribute("aria-pressed", String(j === i)); });
    $("check").disabled = false;
}

function check() {
    if (selected === null) return;
    const i = selected;
    selected = null;
    $("check").disabled = true;
    answer(i);
}

async function answer(i) {
    const q = session[pos];
    if (!$("feedback").hidden) return;                // already answered
    const buttons = [...$("q-options").children];
    if (buttons[i].disabled) return;
    const right = i === q.answer;

    // First wrong click: one more try, with a hint about the method (never the answer itself).
    if (!right && firstChoice === null) {
        firstChoice = i;
        buttons[i].disabled = true;
        buttons[i].setAttribute("aria-pressed", "true");
        buttons[i].classList.add("kt-choice--danger");
        // Hint: the mistake this option stands for when the generator knows it, else the skill's method.
        const skill = index.generators.find((g) => g.key === q.gen)?.skill;
        const mistake = q.mistakes?.[i];
        $("retry").innerHTML = `<div class="kt-alert__title">Not quite. Try once more!</div>` +
            (mistake ? `Did you ${mistake}?` : skill ? `Hint: ${skill}.` : "");
        $("retry").hidden = false;
        return;
    }

    const correct = firstChoice === null && right;     // only the first try counts
    const secondTry = firstChoice === null ? null : right;
    await settle(q, firstChoice ?? i, correct, secondTry, i, right);
}

// "Skip question": counts as not knowing it - for the skill it is the same as a wrong answer.
// Saved as chosen = SKIPPED and correct = false, so the parent page can show it as "Skipped".
// It just moves on: no answer, no solution (also not in the summary at the end).
const SKIPPED = -1;
let skipping = false;
async function skip() {
    const q = session[pos];
    if (!$("feedback").hidden || skipping) return;
    skipping = true;
    $("skip").disabled = true;
    $("check").disabled = true;
    selected = null;
    [...$("q-options").children].forEach((b) => { b.disabled = true; });
    const seconds = Math.round((Date.now() - shownAt) / 1000);
    results.push({ q, chosen: SKIPPED, correct: false });
    dot("skip");
    await adaptLater(q, false, seconds);
    try {
        await store.recordAttempt(profile.id, {
            id: q.id, gen: q.gen, variant: q.variant, difficulty: q.difficulty, harder: q.harder,
            chosen: SKIPPED, correct: false, second_try: null, seconds, at: new Date().toISOString(),
        });
    } catch { /* kept in this browser, saved next time */ }
    skipping = false;
    $("skip").disabled = false;
    next();
}

/** Show the answer, save the attempt and the feedback. picked: the option clicked last. */
async function settle(q, chosen, correct, secondTry, picked, right) {
    const buttons = [...$("q-options").children];
    const seconds = Math.round((Date.now() - shownAt) / 1000);
    $("retry").hidden = true;
    $("skip").hidden = true;
    $("check").hidden = true;
    buttons.forEach((b, j) => {
        b.disabled = true;
        if (j === q.answer && right) b.classList.add("kt-choice--success");   // wrong: the answer stays hidden
        if (j === picked) { b.setAttribute("aria-pressed", "true"); if (!right) b.classList.add("kt-choice--danger"); }
    });
    results.push({ q, chosen, correct });
    dot(correct ? "right" : right ? "second" : "learn");
    // The same skill later in this session: next level up after a right answer, down after a wrong one.
    await adaptLater(q, correct, seconds);
    let saveNote = "";
    try {
        await store.recordAttempt(profile.id, {
            id: q.id, gen: q.gen, variant: q.variant, difficulty: q.difficulty, harder: q.harder,
            chosen, correct, second_try: secondTry, seconds, at: new Date().toISOString(),
        });
    } catch {
        saveNote = '<div class="kt-mt-2 kt-fs-xs">(Could not save this answer right now; it will be saved next time.)</div>';
    }
    const fb = $("feedback-text");
    fb.className = `kt-alert ${right ? "kt-alert--success" : "kt-alert--danger"}`;
    const title = cheer(q, correct, right);
    // Right: just the cheer (the solution was never read). Wrong: no answer and no solution (it would be
    // memorised), only what the picked option stands for; the same skill comes back later.
    const why = !right && q.mistakes?.[picked] ? `<div>${"ABCDE"[picked]} is what you get if you ${q.mistakes[picked]}.</div>` : "";
    fb.innerHTML = `<div class="mk-cheer">${title}</div>${why}${saveNote}`;
    $("next").textContent = "Next question";
    $("teach-btn").hidden = correct || !q.teach;
    // A soft break hint every BREAK_EVERY questions or BREAK_MINUTES minutes; they can just go on.
    const breakTime = results.length - lastBreak.n >= BREAK_EVERY || Date.now() - lastBreak.at >= BREAK_MINUTES * 60e3;
    $("break").hidden = !breakTime;
    if (breakTime) lastBreak = { at: Date.now(), n: results.length };
    $("feedback").hidden = false;
    $("next").focus();
}

async function adaptLater(q, correct, seconds) {
    if (q.isWarmup) return;
    const k = session.findIndex((x, j) => j > pos && x.gen === q.gen && !x.isWarmup);
    if (k < 0) return;
    const cur = LEVELS.findIndex(([d, h]) => d === q.difficulty && h === q.harder);
    const step = correct ? (isGuess(q.difficulty, seconds) ? 0 : 1) : -1;
    const [difficulty, harder] = LEVELS[Math.max(0, Math.min(LEVELS.length - 1, (cur < 0 ? 0 : cur) + step))];
    const bank = await bankFor(index.generators.find((g) => g.key === q.gen));
    const used = new Set(session.map((x) => x.id));
    const list = bank.filter((x) => !used.has(x.id) && x.difficulty === difficulty && x.harder === harder);
    if (list.length) session[k] = { ...list[Math.floor(Math.random() * list.length)], gen: q.gen, teach: session[k].teach };
}

// Encouraging words, never numbers or points (parent, 2026-11-14): streaks of right answers, a hard part,
// a comeback after misses, a skill that was tricky before. Warm-ups only get a plain "Right!".
const pick = (xs) => xs[Math.floor(Math.random() * xs.length)];
function cheer(q, correct, right) {
    if (!right) return pick(["Not this time - a learning opportunity!", "Not this one - you'll meet it again and get it!",
        "Mistakes help you learn!"]);
    if (!correct) return pick(["Right, on the second try - good comeback!", "Right, on the second try! You didn't give up."]);
    if (q.isWarmup) return "Right!";
    const real = results.filter((r) => !r.q.isWarmup);
    let streak = 0;
    for (let k = real.length - 1; k >= 0 && real[k].correct; k--) streak++;   // includes this answer
    const before = real.slice(0, -1);
    if (streak === 3) return "Three in a row!";
    if (streak === 5) return "Five in a row - you're on fire!";
    if (streak >= 8 && streak % 4 === 0) return "Unstoppable! Keep it going!";
    if (before.length >= 2 && before.slice(-2).every((r) => !r.correct)) return "Back on track - well done!";
    if ((sessionStates.get(q.gen)?.wrongs ?? 0) > 0 && !before.some((r) => r.q.gen === q.gen))
        return pick(["This one was tricky before - now you've got it!", "You beat a tricky one!"]);
    if (q.difficulty === 3) return pick(["Part C - the hard one. Brilliant!", "A Part C question - great thinking!"]);
    return pick(["Right!", "Well done!", "Nice!", "Correct - good thinking!"]);
}

// Two misses in a row: the next question is one from a skill the child is good at (if one is left).
function next() {
    const recentRes = results.filter((r) => !r.q.isWarmup).slice(-2);
    if (recentRes.length === 2 && recentRes.every((r) => !r.correct)) {
        // a skill the child is good at, or an untried one (those start at Part A, the easy level)
        const good = (q) => !q.isWarmup && (!sessionStates.has(q.gen) || sessionStates.get(q.gen).score >= 30);
        const k = session.findIndex((q, j) => j > pos + 1 && good(q));
        if (k > 0 && !good(session[pos + 1] || {})) [session[pos + 1], session[k]] = [session[k], session[pos + 1]];
    }
    pos++;
    if (pos < session.length) { renderQuestion(); return; }
    // ran out before the background batch arrived: wait for it (or pick one now)
    $("feedback").hidden = true;
    $("q-text").textContent = "Getting more questions ready…";
    $("q-fig").innerHTML = ""; $("q-after").textContent = ""; $("q-options").innerHTML = "";
    $("skip-row").hidden = true;
    refillSoon();
    Promise.resolve(refill).then(() => {
        $("skip-row").hidden = false;
        if (pos < session.length) renderQuestion(); else finish();
    });
}

function finish() {
    $("done-title").textContent = `Nice work, ${profile.name}!`;
    const box = $("done-mistakes");
    box.innerHTML = "";
    // The good news first: skills that went up a level today, and skills tried for the first time.
    const name = (gen) => index.generators.find((g) => g.key === gen)?.keywords?.[0] || "";
    const real = results.filter((r) => !r.q.isWarmup);
    const stronger = [...new Set(real.filter((r) => r.correct).map((r) => name(r.q.gen)))].filter(Boolean);
    const fresh = [...new Set(real.filter((r) => !sessionStates.has(r.q.gen)).map((r) => name(r.q.gen)))]
        .filter((n) => n && !stronger.includes(n));
    const good = [];
    if (stronger.length) good.push(`<div><b>You're getting stronger at:</b> ${stronger.join(", ")}.</div>`);
    if (fresh.length) good.push(`<div><b>You tried something new:</b> ${fresh.join(", ")}.</div>`);
    if (good.length) { const g = el("div", "kt-alert kt-alert--success"); g.innerHTML = good.join(""); box.append(g); }
    const wrong = results.filter((r) => !r.correct);
    if (wrong.length) box.append(el("h3", "kt-section-title", "Worth another look"));
    for (const r of wrong) {
        const c = el("div", "kt-card kt-card--padded");
        const t = el("div", "mk-rich"); t.innerHTML = r.q.text;
        if (r.q.figure) { const f = el("div", "mk-fig"); f.innerHTML = r.q.figure; c.append(t, f); }
        if (r.q.after) { const a = el("div", "mk-rich"); a.innerHTML = r.q.after; c.append(a); }
        const s = el("div", "kt-mt-2 kt-text-secondary");
        s.innerHTML = r.chosen === SKIPPED ? "You skipped this one. Try it again another time!"
            : "A learning opportunity - one like it will come back, so you can try again!";
        if (!c.contains(t)) c.append(t);
        c.append(s);
        box.append(c);
    }
    show("done");
}

// ------------------------------------------------------------------ teaching page
const teachPages = new Map();
async function openTeach() {
    const q = session[pos];
    if (!teachPages.has(q.teach)) teachPages.set(q.teach, fetch(q.teach).then((r) => r.json()));
    const body = $("teach-body");
    body.innerHTML = "";
    let list = null;
    for (const it of await teachPages.get(q.teach)) {
        if (it.li != null) {
            if (!list) { list = el("ul", "kt-list"); body.append(list); }
            const li = el("li"); li.innerHTML = it.li; list.append(li);
            continue;
        }
        list = null;
        if (it.h != null) { if (body.children.length) { const h = el("h3", "kt-section-title"); h.innerHTML = it.h; body.append(h); } else $("teach-title").innerHTML = it.h; }
        else if (it.p != null) { const p = el("p"); p.innerHTML = it.p; body.append(p); }
        else if (it.tip != null) { const t = el("div", "kt-alert kt-alert--info"); t.innerHTML = it.tip; body.append(t); }
        else if (it.svg != null) { const f = el("div", "mk-fig"); f.innerHTML = it.svg; bigger(f, 1.3); body.append(f); }
        else if (it.table) {
            const wrap = el("div", "kt-table-wrap"), t = el("table", "kt-table");
            it.table.forEach((row, r) => {
                const tr = el("tr");
                row.forEach((c) => { const td = el(r ? "td" : "th"); td.innerHTML = c; tr.append(td); });
                t.append(tr);
            });
            wrap.append(t); body.append(wrap);
        }
    }
    $("teach").classList.add("is-open");
}
$("teach").addEventListener("click", (e) => {
    if (e.target === $("teach") || e.target.closest(".kt-modal__close")) $("teach").classList.remove("is-open");
});
document.addEventListener("keydown", (e) => { if (e.key === "Escape") $("teach").classList.remove("is-open"); });

// ------------------------------------------------------------------ start
$("teach-btn").onclick = openTeach;
$("next").onclick = next;
$("break-stop").onclick = finish;
$("skip").onclick = skip;
$("check").onclick = check;
$("quit").onclick = () => (results.length ? finish() : (show("who"), renderProfiles(), clearProfileUrl()));
$("again").onclick = () => start(profile);
// Keep practising: back to the same session (its circles too), at the next question if this one was answered.
$("keep").onclick = () => { show("play"); if (!$("feedback").hidden) next(); };
function clearProfileUrl() { try { history.replaceState(null, "", location.pathname); } catch { /* file:// */ } }
/** One circle per answer in the top row (no numbers): right, second, learn (wrong), skip. */
function dot(kind) { $("dots").append(el("span", `mk-dot mk-dot--${kind}`)); }
document.addEventListener("keydown", (e) => {
    if ($("play").hidden || $("teach").classList.contains("is-open")) return;
    const k = e.key.toUpperCase();
    const onButton = document.activeElement?.tagName === "BUTTON";   // Enter on a button clicks it already
    if ($("feedback").hidden && "ABCDE".includes(k) && k.length === 1) {
        const i = "ABCDE".indexOf(k);
        if (i < $("q-options").children.length) select(i);
    } else if ($("feedback").hidden && e.key === "Enter" && !onButton) check();
    else if (!$("feedback").hidden && e.key === "Enter" && document.activeElement !== $("next")) next();
});

// The password comes first; after that the device remembers it (unless "Remember" was unticked).
function connect(secrets) {
    store = new DbStore(secrets.db);
    $("lock").hidden = true;
    $("who").hidden = false;
    // ?profile=Deniz opens that child's practice straight away
    const wanted = new URLSearchParams(location.search).get("profile")?.toLowerCase();
    const p = PROFILES.find((x) => x.name.toLowerCase() === wanted || x.id === wanted);
    if (p && index) { start(p); return; }
    renderProfiles().catch((e) => {
        $("profiles").innerHTML = "";
        const a = el("div", "kt-alert kt-alert--danger", `Could not reach the database: ${e.message}`);
        $("profiles").append(a);
    });
}

$("lock-form").onsubmit = async (e) => {
    e.preventDefault();
    $("lock-error").hidden = true;
    $("lock-btn").disabled = true;
    try {
        const secrets = await Secrets.unlock($("lock-password").value);
        if (!secrets.db) throw new Error("The locked file has no database yet.");
        if ($("lock-remember").checked) Secrets.save(secrets);
        connect(secrets);
    } catch (x) {
        $("lock-error").textContent = x.message;
        $("lock-error").hidden = false;
        $("lock-password").select();
    } finally {
        $("lock-btn").disabled = false;
    }
};

fetch("bank/index.json", { cache: "no-store" })
    .then((r) => r.json())
    .then((j) => {
        index = j;
        const saved = Secrets.saved();
        if (saved?.db) connect(saved);
        else { $("lock").hidden = false; $("lock-password").focus(); }
    })
    .catch(() => { $("lock").hidden = false; $("lock-error").textContent = "Could not load the questions."; $("lock-error").hidden = false; });
