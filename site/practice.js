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
    { id: "deniz", name: "Deniz", avatar: "🦘" },
    { id: "toprak", name: "Toprak", avatar: "🐨" },
    { id: "koray", name: "Koray", avatar: "🧪", parent: true },   // the parent's test profile
];
const SESSION = 10;
const PART = { 1: "Part A", 2: "Part B", 3: "Part C" };

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
        return this.sql`select question_id as id, gen, variant, difficulty, harder, chosen, correct, seconds,
                               created_at as at
                        from attempts where profile_id = ${p} order by id`;
    }
    async insert(p, a) {
        await this.sql`insert into attempts (profile_id, question_id, gen, variant, difficulty, harder, chosen,
                                             correct, seconds, created_at)
                       values (${p}, ${a.id}, ${a.gen}, ${a.variant}, ${a.difficulty}, ${a.harder}, ${a.chosen},
                               ${a.correct}, ${a.seconds}, ${a.at})`;
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
    if (!files.has(gen.key)) files.set(gen.key, fetch(gen.file).then((r) => r.json()));
    return files.get(gen.key);
}

// ------------------------------------------------------------------ choosing questions
// Per skill (generator): the last 5 answers decide how weak it is; right answers in a row raise the level.
function skillStats(attempts) {
    const by = new Map();
    for (const a of attempts) {
        if (!by.has(a.gen)) by.set(a.gen, []);
        by.get(a.gen).push(a);
    }
    const out = new Map();
    for (const [gen, list] of by) {
        const recent = list.slice(-5);
        let streak = 0;
        for (let i = list.length - 1; i >= 0 && list[i].correct; i--) streak++;
        out.set(gen, { tries: list.length, wrongRate: recent.filter((a) => !a.correct).length / recent.length, streak });
    }
    return out;
}

function weightedPick(items, weight, n) {
    const pool = items.map((x) => ({ x, w: weight(x) })), out = [];
    while (out.length < n && pool.length) {
        let r = Math.random() * pool.reduce((s, p) => s + p.w, 0);
        const i = pool.findIndex((p) => (r -= p.w) <= 0);
        out.push(pool.splice(i < 0 ? pool.length - 1 : i, 1)[0].x);
    }
    return out;
}

async function buildSession(profile) {
    const attempts = await store.attempts(profile.id);
    const stats = skillStats(attempts);
    const recentIds = new Set(attempts.slice(-300).map((a) => a.id));
    // Weak skills come first, skills never tried next, well-known skills now and then.
    const weight = (g) => {
        const s = stats.get(g.key);
        return !s ? 3 : 1 + 6 * s.wrongRate + (s.streak >= 4 ? -0.6 : 0);
    };
    let gens = weightedPick(index.generators, weight, SESSION);
    while (gens.length < SESSION) gens.push(index.generators[Math.floor(Math.random() * index.generators.length)]);

    const qs = [];
    for (const g of gens) {
        const bank = await bankFor(g);
        const s = stats.get(g.key) || { streak: 0, wrongRate: 0 };
        const level = s.wrongRate > 0.5 ? 1 : Math.min(3, 1 + Math.floor(s.streak / 2));
        const harder = s.streak >= 6;
        const fresh = (q) => !recentIds.has(q.id) && !qs.some((x) => x.id === q.id);
        const tiers = [
            bank.filter((q) => fresh(q) && q.difficulty === level && q.harder === harder),
            bank.filter((q) => fresh(q) && q.difficulty === level),
            bank.filter(fresh),
            bank,
        ];
        const list = tiers.find((t) => t.length);
        qs.push({ ...list[Math.floor(Math.random() * list.length)], gen: g.key });
    }
    return qs.sort((a, b) => a.difficulty - b.difficulty);    // Part A, then B, then C, like the contest
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
        body.append(el("div", "mk-avatar", p.avatar), el("div", "kt-card__title", p.name),
            el("div", "kt-card__subtitle", "Start practising"));
        b.append(body);
        b.onclick = () => start(p);
        box.append(b);
    }
}

let profile = null, session = [], pos = 0, shownAt = 0, results = [];

async function start(p) {
    profile = p;
    $("play-who").textContent = `${p.avatar} ${p.name}`;
    show("play");
    $("q-text").textContent = "Getting your questions ready…";
    $("q-fig").innerHTML = ""; $("q-after").textContent = ""; $("q-options").innerHTML = "";
    $("feedback").hidden = true;
    session = await buildSession(p);
    pos = 0; results = [];
    renderQuestion();
}

function bigger(container, factor) {
    container.querySelectorAll("svg").forEach((s) => {
        const w = parseFloat(s.getAttribute("width")), h = parseFloat(s.getAttribute("height"));
        if (w && h) { s.setAttribute("width", w * factor); s.setAttribute("height", h * factor); }
    });
}

function renderQuestion() {
    const q = session[pos];
    $("play-count").textContent = `Question ${pos + 1} of ${session.length}`;
    $("play-part").textContent = PART[q.difficulty];
    $("play-bar").style.width = `${(100 * pos) / session.length}%`;
    $("q-text").innerHTML = q.text;
    $("q-fig").innerHTML = q.figure || "";
    $("q-fig").hidden = !q.figure;
    bigger($("q-fig"), 2);
    $("q-after").innerHTML = q.after;
    $("feedback").hidden = true;

    const opts = $("q-options");
    opts.innerHTML = "";
    q.choices.forEach((c, i) => {
        const b = el("button", "kt-card kt-card--selectable mk-opt");
        b.type = "button";
        b.setAttribute("aria-pressed", "false");
        const body = el("div", "kt-card__body");
        body.append(el("span", "kt-fw-bold mk-opt-text", "ABCDE"[i] + "."));
        const content = el("span", "mk-opt-text");
        if (q.choice_figures) { content.innerHTML = q.choice_figures[i]; bigger(content, 1.6); } else content.innerHTML = c;
        body.append(content);
        b.append(body);
        b.onclick = () => answer(i);
        opts.append(b);
    });
    shownAt = Date.now();
}

async function answer(i) {
    const q = session[pos];
    if (!$("feedback").hidden) return;                // already answered
    const correct = i === q.answer;
    const seconds = Math.round((Date.now() - shownAt) / 1000);
    [...$("q-options").children].forEach((b, j) => {
        b.disabled = true;
        if (j === q.answer) b.classList.add("kt-card--success");
        if (j === i) { b.setAttribute("aria-pressed", "true"); if (!correct) b.classList.add("kt-card--danger"); }
    });
    results.push({ q, chosen: i, correct });
    let saveNote = "";
    try {
        await store.recordAttempt(profile.id, {
            id: q.id, gen: q.gen, variant: q.variant, difficulty: q.difficulty, harder: q.harder,
            chosen: i, correct, seconds, at: new Date().toISOString(),
        });
    } catch {
        saveNote = '<div class="kt-mt-2 kt-fs-xs">(Could not save this answer right now; it will be saved next time.)</div>';
    }
    const fb = $("feedback-text");
    fb.className = `kt-alert ${correct ? "kt-alert--success" : "kt-alert--danger"}`;
    fb.innerHTML = `<div class="kt-alert__title">${correct ? "Right!" :
        `Not this time. The answer is ${"ABCDE"[q.answer]}.`}</div>${q.solution}${saveNote}`;
    $("next").textContent = pos + 1 < session.length ? "Next question" : "See your result";
    $("feedback").hidden = false;
    $("next").focus();
}

function next() {
    pos++;
    if (pos < session.length) { renderQuestion(); return; }
    finish();
}

function finish() {
    $("done-title").textContent = `Nice work, ${profile.name}!`;
    const box = $("done-mistakes");
    box.innerHTML = "";
    const wrong = results.filter((r) => !r.correct);
    if (wrong.length) box.append(el("h3", "kt-section-title", "Look at these once more"));
    for (const r of wrong) {
        const c = el("div", "kt-card kt-card--padded");
        const t = el("div"); t.innerHTML = r.q.text;
        if (r.q.figure) { const f = el("div", "mk-fig"); f.innerHTML = r.q.figure; c.append(t, f); }
        if (r.q.after) { const a = el("div"); a.innerHTML = r.q.after; c.append(a); }
        const s = el("div", "kt-mt-2 kt-text-secondary");
        s.innerHTML = `You chose ${"ABCDE"[r.chosen]}, the answer is ${"ABCDE"[r.q.answer]}. ${r.q.solution}`;
        if (!c.contains(t)) c.append(t);
        c.append(s);
        box.append(c);
    }
    show("done");
}

// ------------------------------------------------------------------ start
$("next").onclick = next;
$("quit").onclick = () => (results.length ? finish() : (show("who"), renderProfiles()));
$("again").onclick = () => start(profile);
$("switch").onclick = () => { show("who"); renderProfiles(); };
document.addEventListener("keydown", (e) => {
    if ($("play").hidden) return;
    const k = e.key.toUpperCase();
    if ($("feedback").hidden && "ABCDE".includes(k) && k.length === 1) answer("ABCDE".indexOf(k));
    else if (!$("feedback").hidden && e.key === "Enter" && document.activeElement !== $("next")) next();
});

// The password comes first; after that the device remembers it (unless "Remember" was unticked).
function connect(secrets) {
    store = new DbStore(secrets.db);
    $("lock").hidden = true;
    $("who").hidden = false;
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
