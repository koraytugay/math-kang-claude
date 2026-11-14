// Parent view (parent.html, not linked anywhere): per child, the skill states from smart.js, what the next
// session focuses on, and the exact questions to study together (wrong first try or skipped).
"use strict";

const $ = (id) => document.getElementById(id);
const el = (tag, cls, text) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
};
const KIDS = [{ id: "deniz", name: "Deniz" }, { id: "toprak", name: "Toprak" }, { id: "koray", name: "Koray (test)" }];
const LEVEL_NAME = ["Part A", "Part B", "Part C", "Part C, harder"];
const LETTER = "ABCDE";

let secrets = null, index = null, kid = KIDS[0], showing = 0;
const banks = new Map();
const bankFor = (g) => {
    if (!banks.has(g.key)) banks.set(g.key, fetch(g.file).then((r) => r.json()));
    return banks.get(g.key);
};
const day = (t) => new Date(t).toLocaleDateString(undefined, { month: "short", day: "numeric" });
// Text only; a space where a paragraph, list item or line ends (so "rule.Next rule" stays apart).
const plain = (html) => { const d = el("div"); d.innerHTML = html.replace(/<\/(p|li)>|<br\s*\/?>/gi, " $&"); return d.textContent.replace(/\s+/g, " ").trim(); };

/** needs work / getting there / solid, from the score (smart.js). */
function status(s) {
    if (!s) return ["Not tried yet", "kt-badge"];
    if (s.status === "needs work") return ["Needs work", "kt-badge kt-badge--soft-danger"];
    if (s.status === "getting there") return ["Getting there", "kt-badge kt-badge--soft-warning"];
    return ["Solid", "kt-badge kt-badge--soft-success"];
}

async function show(k) {
    kid = k;
    document.querySelectorAll("#kids .kt-nav__link").forEach((b) => b.classList.toggle("is-active", b.dataset.id === k.id));
    $("loading").hidden = false;
    $("content").hidden = true;
    const ticket = ++showing;                   // a later click wins over a slower earlier one
    const attempts = await fetchAttempts(secrets.db, k.id);
    if (ticket !== showing) return;
    const real = attempts.filter((a) => !a.variant?.startsWith("warmup:"));
    const states = skillStates(attempts);
    const gens = index.generators;

    // summary (for the parent only)
    const counts = { "Needs work": 0, "Getting there": 0, Solid: 0, "Not tried yet": 0 };
    for (const g of gens) counts[status(states.get(g.key))[0]]++;
    const sum = $("summary");
    sum.innerHTML = "";
    for (const [label, n] of [["Answers", real.length], ...Object.entries(counts)]) {
        const s = el("div", "kt-stat");
        s.append(el("div", "kt-stat__value", String(n)), el("div", "kt-stat__label", label));
        sum.append(s);
    }

    // next session
    const focus = $("focus");
    focus.innerHTML = "";
    const seen = new Set();
    for (const g of planSkills(gens, states, 10)) {
        if (seen.has(g.key)) continue;
        seen.add(g.key);
        const s = states.get(g.key);
        focus.append(el("span", "kt-chip", `${g.label} · ${g.keywords[0] || ""} · ${s ? status(s)[0].toLowerCase() : "new"}`));
        // (in the order the session asks them: a confident start and finish)
    }

    // skills, weakest first
    const order = { "Needs work": 0, "Getting there": 1, Solid: 2, "Not tried yet": 3 };
    const rows = gens.map((g) => ({ g, s: states.get(g.key) }))
        .sort((a, b) => order[status(a.s)[0]] - order[status(b.s)[0]] || (a.s?.score ?? 0) - (b.s?.score ?? 0)
            || a.g.label.localeCompare(b.g.label));
    const body = $("skills");
    body.innerHTML = "";
    for (const { g, s } of rows) {
        const mine = real.filter((a) => a.gen === g.key);
        const right = mine.filter((a) => a.correct).length;
        const skipped = mine.filter((a) => a.chosen < 0).length;
        const tr = el("tr");
        const [label, cls] = status(s);
        const badge = el("span", cls, label);
        const cells = [
            el("td", null, `${g.label} · ${g.keywords[0] || ""}`), el("td", "kt-text-secondary", g.skill),
            el("td"), el("td", null, s ? LEVEL_NAME[s.level] : ""),
            el("td", "kt-num", mine.length ? String(mine.length) : ""),
            el("td", "kt-num", mine.length ? `${Math.round((100 * right) / mine.length)}%` : ""),
            el("td", "kt-num"),
            el("td", null, s ? day(s.last) : ""),
            el("td", "kt-num", s ? String(s.score) : ""),
        ];
        cells[2].append(badge);
        if (skipped) cells[6].append(el("span", "kt-badge kt-badge--orange", String(skipped)));
        tr.append(...cells);
        body.append(tr);
    }

    // the exact questions to study together: first try wrong or skipped, not yet marked as studied, and not
    // learned since (a later question of the same skill right on the first try, not a quick guess)
    const done = await studiedSet(k.id);
    if (ticket !== showing) return;
    const once = new Set();                     // the same exact question missed twice: one card (the newest)
    const wrong = real.filter((a) => !a.correct).reverse().filter((a) => !once.has(a.id) && once.add(a.id));
    const cards = [];
    for (const a of wrong) {
        const g = gens.find((x) => x.key === a.gen);
        const q = g ? (await bankFor(g)).find((x) => x.id === a.id) : null;
        if (ticket !== showing) return;
        const learned = real.find((b) => b.gen === a.gen && b.correct && new Date(b.at) > new Date(a.at)
            && !isGuess(b.difficulty, b.seconds));
        cards.push(studyCard(k, a, g, q, done.has(a.id), learned));
    }
    $("study").replaceChildren(...cards.filter((c) => !c.dataset.studied));
    $("studied").replaceChildren(...cards.filter((c) => c.dataset.studied));
    if (!$("study").children.length) $("study").append(el("div", "kt-text-secondary", "Nothing to study right now."));
    countStudy();
    $("loading").hidden = true;
    $("content").hidden = false;
}

// ------------------------------------------------------------------ studying together
// "Studied together" is saved in the achievements table (unused since badges were dropped; the site may
// insert and update there, not delete): code "studied:<question id>". Undo renames the row to
// "unstudied:<question id>:<time>", so it can be marked again later.
let sqlFn = null;
async function sql() {
    if (!sqlFn) {
        const m = await import("https://cdn.jsdelivr.net/npm/@neondatabase/serverless@1.2.0/+esm");
        sqlFn = m.neon(secrets.db, { disableWarningInBrowsers: true });
    }
    return sqlFn;
}
async function studiedSet(profileId) {
    const db = await sql();
    const rows = await db`select code from achievements where profile_id = ${profileId} and code like 'studied:%'`;
    return new Set(rows.map((r) => r.code.slice("studied:".length)));
}
async function markStudied(profileId, qid, on) {
    const db = await sql();
    if (on) await db`insert into achievements (profile_id, code) values (${profileId}, ${"studied:" + qid})
                     on conflict (profile_id, code) do nothing`;
    else await db`update achievements set code = ${`unstudied:${qid}:${Date.now()}`}
                  where profile_id = ${profileId} and code = ${"studied:" + qid}`;
}
function countStudy() {
    const open = $("study").querySelectorAll(".mk-card").length, closed = $("studied").children.length;
    $("study-title").textContent = `To study together (${open})`;
    $("studied-title").textContent = `Done (${closed})`;
    $("studied-box").hidden = !closed;
}

function bigger(container, factor) {
    container.querySelectorAll("svg").forEach((s) => {
        const w = parseFloat(s.getAttribute("width")), h = parseFloat(s.getAttribute("height"));
        if (w && h) { s.setAttribute("width", w * factor); s.setAttribute("height", h * factor); }
    });
}

/**
 * One question as the child saw it, to solve together: no answer and no pick shown. Pick an option and
 * "Check", or "Show answer"; then the solution. learned: a later right answer of the same skill.
 */
function studyCard(k, a, g, q, studied, learned) {
    const card = el("div", "kt-card kt-card--padded kt-stack mk-card");
    if (studied || learned) card.dataset.studied = "1";
    const head = el("div", "kt-cluster");
    head.append(el("span", "kt-fw-bold", `${day(a.at)} · ${g ? `${g.label} · ${g.keywords[0] || ""}` : a.gen}`),
        el("span", "kt-badge kt-badge--soft-info", LEVEL_NAME[[1, 2, 3].indexOf(a.difficulty) + (a.harder ? 1 : 0)] || ""));
    if (a.chosen < 0) head.append(el("span", "kt-badge kt-badge--orange", "Skipped"));
    else head.append(el("span", a.second_try ? "kt-badge kt-badge--soft-warning" : "kt-badge kt-badge--soft-danger",
        a.second_try ? "Wrong, then right on the second try" : a.second_try === false ? "Wrong twice" : "Wrong"));
    if (learned) head.append(el("span", "kt-badge kt-badge--soft-success", `Got a similar one right on ${day(learned.at)}`));
    card.append(head);
    if (!q) {
        card.append(el("div", "kt-text-secondary", "This question is no longer in the question bank (the generator changed)."));
    } else {
        const t = el("div", "mk-qtext mk-rich"); t.innerHTML = q.text; card.append(t);
        if (q.figure) { const f = el("div", "mk-fig"); f.innerHTML = q.figure; bigger(f, 1.6); card.append(f); }
        if (q.after) { const t2 = el("div", "mk-qtext mk-rich"); t2.innerHTML = q.after; card.append(t2); }
        const row = q.choice_figures || Math.max(...q.choices.map((c) => plain(c).length)) <= 14;
        const opts = el("div", `kt-choices${row ? " kt-choices--row" : ""}`);
        const buttons = [];
        let selected = null, over = false;
        q.choices.forEach((c, i) => {
            const b = el("button", `kt-choice${q.choice_figures ? " kt-choice--stacked" : ""}`);
            b.type = "button";
            b.setAttribute("aria-pressed", "false");
            b.append(el("span", "kt-choice__key", LETTER[i]));
            const lab = el("span", "kt-choice__label");
            if (q.choice_figures) { lab.innerHTML = q.choice_figures[i]; bigger(lab, 1.3); } else lab.innerHTML = c;
            b.append(lab);
            b.onclick = () => {
                if (over || b.disabled) return;
                selected = i;
                buttons.forEach((x, j) => { if (!x.disabled) x.setAttribute("aria-pressed", String(j === i)); });
                check.disabled = false;
            };
            buttons.push(b);
            opts.append(b);
        });
        card.append(opts);
        const note = el("div", "kt-alert");
        note.hidden = true;
        const check = el("button", "kt-btn kt-btn--primary", "Check answer");
        check.type = "button"; check.disabled = true;
        const reveal = el("button", "kt-btn kt-ml-auto", "Show answer");
        reveal.type = "button";
        const finish = (title, cls) => {
            over = true;
            buttons.forEach((x, j) => { x.disabled = true; if (j === q.answer) x.classList.add("kt-choice--success"); });
            note.className = `kt-alert ${cls}`;
            note.innerHTML = `<div class="kt-alert__title">${title}</div>${q.solution}`;
            note.hidden = false;
            check.hidden = true; reveal.hidden = true;
        };
        check.onclick = () => {
            if (selected === null) return;
            const i = selected;
            selected = null; check.disabled = true;
            if (i === q.answer) return finish("Right!", "kt-alert--success");
            buttons[i].disabled = true;
            buttons[i].classList.add("kt-choice--danger");
            note.className = "kt-alert kt-alert--warning";
            note.innerHTML = `<div class="kt-alert__title">Not quite - try again.</div>`
                + (q.mistakes?.[i] ? `Did you ${q.mistakes[i]}?` : g?.skill ? `Hint: ${g.skill}.` : "");
            note.hidden = false;
        };
        reveal.onclick = () => finish(`The answer is ${LETTER[q.answer]}.`, "kt-alert--info");
        const tools = el("div", "kt-cluster");
        tools.append(check, reveal);
        card.append(tools, note);
    }
    if (learned) return card;                   // done by itself, nothing to undo
    const btn = el("button", studied ? "kt-btn" : "kt-btn", studied ? "Undo - study again" : "Studied together");
    btn.type = "button";
    btn.onclick = async () => {
        btn.disabled = true;
        try {
            await markStudied(k.id, a.id, !card.dataset.studied);
            if (card.dataset.studied) { delete card.dataset.studied; btn.className = "kt-btn"; btn.textContent = "Studied together"; $("study").querySelector(":scope > .kt-text-secondary")?.remove(); $("study").prepend(card); }
            else { card.dataset.studied = "1"; btn.className = "kt-btn"; btn.textContent = "Undo - study again"; $("studied").prepend(card); }
            if (!$("study").children.length) $("study").append(el("div", "kt-text-secondary", "Nothing to study right now."));
            countStudy();
        } catch (e) { alert(`Could not save: ${e.message}`); }
        btn.disabled = false;
    };
    const foot = el("div", "kt-mt-2"); foot.append(btn); card.append(foot);
    return card;
}

function start(s) {
    secrets = s;
    $("lock").hidden = true;
    $("view").hidden = false;
    const nav = $("kids");
    for (const k of KIDS) {
        const b = el("button", "kt-nav__link", k.name);
        b.type = "button";
        b.dataset.id = k.id;
        b.onclick = () => show(k).catch(fail);
        nav.append(b);
    }
    show(kid).catch(fail);
}
function fail(e) {
    $("loading").hidden = true;
    $("content").hidden = true;
    const a = el("div", "kt-alert kt-alert--danger", `Could not load: ${e.message}`);
    $("view").append(a);
}

$("lock-form").onsubmit = async (e) => {
    e.preventDefault();
    $("lock-error").hidden = true;
    try {
        const s = await Secrets.unlock($("lock-password").value);
        if (!s.db) throw new Error("The locked file has no database yet.");
        if ($("lock-remember").checked) Secrets.save(s);
        start(s);
    } catch (x) {
        $("lock-error").textContent = x.message;
        $("lock-error").hidden = false;
    }
};

fetch("bank/index.json", { cache: "no-store" }).then((r) => r.json()).then((j) => {
    index = j;
    const s = Secrets.saved();
    if (s?.db) start(s); else { $("lock").hidden = false; $("lock-password").focus(); }
});
