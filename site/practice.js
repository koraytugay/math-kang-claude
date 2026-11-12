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

// ------------------------------------------------------------------ choosing questions (personal)
// Every child has their own state per skill (generator), replayed from their answers in time order:
//  - box: a review schedule. Wrong -> box 1 (back tomorrow); right -> next box. Box n is due GAP[n] days
//    after the last answer, so known skills come back less and less often.
//  - level: which questions to give. 3 right in a row -> one level up (Part A -> B -> C -> harder numbers);
//    2 wrong in a row -> one level down.
const DAY = 864e5, GAP = [0, 1, 3, 7, 21];
const LEVELS = [[1, false], [2, false], [3, false], [3, true]];     // [difficulty, harder]

function skillStates(attempts) {
    const states = new Map();
    for (const a of attempts) {
        const s = states.get(a.gen) || { box: 0, level: 0, rightRun: 0, wrongRun: 0, last: 0, tries: 0 };
        s.tries++;
        s.last = new Date(a.at).getTime();
        if (a.correct) {
            s.box = Math.min(GAP.length - 1, s.box + 1);
            s.wrongRun = 0;
            if (++s.rightRun >= 3) { s.level = Math.min(LEVELS.length - 1, s.level + 1); s.rightRun = 0; }
        } else {
            s.box = 1;
            s.rightRun = 0;
            if (++s.wrongRun >= 2) { s.level = Math.max(0, s.level - 1); s.wrongRun = 0; }
        }
        s.due = s.last + GAP[s.box] * DAY;
        states.set(a.gen, s);
    }
    return states;
}

const shuffle = (xs) => { for (let i = xs.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [xs[i], xs[j]] = [xs[j], xs[i]]; } return xs; };

/** Which skills to practise now, most useful first: weak, due for review, new, then the rest. */
function planSkills(gens, states, n) {
    const now = Date.now(), st = (g) => states.get(g.key);
    const byDue = (a, b) => st(a).due - st(b).due;
    const weak = shuffle(gens.filter((g) => st(g) && st(g).box <= 1)).sort(byDue);
    const due = gens.filter((g) => st(g) && st(g).box >= 2 && st(g).due <= now).sort(byDue);
    const fresh = shuffle(gens.filter((g) => !st(g)));
    const later = gens.filter((g) => st(g) && st(g).box >= 2 && st(g).due > now).sort(byDue);

    const plan = [];
    const take = (list, k) => { for (const g of list) { if (k <= 0 || plan.length >= n) break; if (!plan.includes(g)) { plan.push(g); k--; } } };
    take(weak, 5);              // what they get wrong comes first
    take(due, 3);               // then what is due again
    take(fresh, 3);             // and a few skills they have not tried yet
    // A weak skill may come twice in one session (a second, different question).
    for (const g of weak) if (plan.length < n && plan.filter((x) => x === g).length < 2) plan.push(g);
    take(due, n); take(fresh, n); take(later, n); take(shuffle([...gens]), n);
    return plan.slice(0, n);
}

async function buildSession(profile) {
    const attempts = await store.attempts(profile.id);
    const states = skillStates(attempts);
    const seen = new Set(attempts.map((a) => a.id));
    const twoWeeks = Date.now() - 14 * DAY;
    const recent = new Set(attempts.filter((a) => new Date(a.at).getTime() > twoWeeks).map((a) => a.id));

    const qs = [];
    for (const g of planSkills(index.generators, states, SESSION)) {
        const bank = await bankFor(g);
        const [difficulty, harder] = LEVELS[states.get(g.key)?.level ?? 0];
        const free = (q) => !qs.some((x) => x.id === q.id);
        const atLevel = (q) => q.difficulty === difficulty && q.harder === harder;
        const tiers = [
            bank.filter((q) => free(q) && !seen.has(q.id) && atLevel(q)),      // new question, right level
            bank.filter((q) => free(q) && !seen.has(q.id) && q.difficulty === difficulty),
            bank.filter((q) => free(q) && !recent.has(q.id) && atLevel(q)),    // not in the last two weeks
            bank.filter((q) => free(q) && !seen.has(q.id)),
            bank.filter(free),
        ];
        const list = tiers.find((t) => t.length) || bank;
        qs.push({ ...list[Math.floor(Math.random() * list.length)], gen: g.key, teach: g.teach });
    }
    // Part A, then B, then C, like the contest; two questions of one skill are kept apart.
    qs.sort((a, b) => a.difficulty - b.difficulty);
    for (let k = 1; k < qs.length; k++) {
        if (qs[k].gen === qs[k - 1].gen) {
            const m = qs.findIndex((q, j) => j > k && q.gen !== qs[k].gen);
            if (m > 0) [qs[k], qs[m]] = [qs[m], qs[k]];
        }
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
    $("next").textContent = pos + 1 < session.length ? "Next question" : "Finish";
    $("teach-btn").hidden = correct || !q.teach;
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
$("quit").onclick = () => (results.length ? finish() : (show("who"), renderProfiles()));
$("again").onclick = () => start(profile);
$("switch").onclick = () => { show("who"); renderProfiles(); };
document.addEventListener("keydown", (e) => {
    if ($("play").hidden || $("teach").classList.contains("is-open")) return;
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
