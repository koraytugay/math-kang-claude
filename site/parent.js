// Parent view (parent.html, not linked anywhere): per child, the skill states from smart.js, what the next
// session focuses on, and the recent mistakes with the option that was picked.
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
const plain = (html) => { const d = el("div"); d.innerHTML = html; return d.textContent; };

/** needs work / getting there / solid, from the review box (smart.js). */
function status(s) {
    if (!s) return ["Not tried yet", "kt-badge"];
    if (s.box <= 1) return ["Needs work", "kt-badge kt-badge--soft-danger"];
    if (s.box <= 3) return ["Getting there", "kt-badge kt-badge--soft-warning"];
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
    }

    // skills, weakest first
    const order = { "Needs work": 0, "Getting there": 1, Solid: 2, "Not tried yet": 3 };
    const rows = gens.map((g) => ({ g, s: states.get(g.key) }))
        .sort((a, b) => order[status(a.s)[0]] - order[status(b.s)[0]] || a.g.label.localeCompare(b.g.label));
    const body = $("skills");
    body.innerHTML = "";
    for (const { g, s } of rows) {
        const mine = real.filter((a) => a.gen === g.key);
        const right = mine.filter((a) => a.correct).length;
        const tr = el("tr");
        const [label, cls] = status(s);
        const badge = el("span", cls, label);
        const cells = [
            el("td", null, `${g.label} · ${g.keywords[0] || ""}`), el("td", "kt-text-secondary", g.skill),
            el("td"), el("td", null, s ? LEVEL_NAME[s.level] : ""),
            el("td", "kt-num", mine.length ? String(mine.length) : ""),
            el("td", "kt-num", mine.length ? `${Math.round((100 * right) / mine.length)}%` : ""),
            el("td", null, s ? day(s.last) : ""),
            el("td", null, s ? (s.due <= Date.now() ? "now" : day(s.due)) : ""),
        ];
        cells[2].append(badge);
        tr.append(...cells);
        body.append(tr);
    }

    // recent mistakes (first try wrong), newest first
    const mb = $("mistakes");
    mb.innerHTML = "";
    const wrong = real.filter((a) => !a.correct).slice(-20).reverse();
    if (!wrong.length) { const tr = el("tr"); const td = el("td", "kt-text-secondary", "No mistakes yet."); td.colSpan = 7; tr.append(td); mb.append(tr); }
    for (const a of wrong) {
        const g = gens.find((x) => x.key === a.gen);
        const q = g ? (await bankFor(g)).find((x) => x.id === a.id) : null;
        if (ticket !== showing) return;
        const opt = (i) => q ? `${LETTER[i]} (${q.choice_figures ? "picture" : plain(q.choices[i])})` : LETTER[i] ?? "";
        const tr = el("tr");
        tr.append(
            el("td", null, day(a.at)), el("td", null, g ? `${g.label} · ${g.keywords[0] || ""}` : a.gen),
            el("td", "mk-q", q ? plain(q.text).slice(0, 160) + (plain(q.text).length > 160 ? "…" : "") : ""),
            el("td", null, opt(a.chosen) + (q?.mistakes?.[a.chosen] ? ` - ${q.mistakes[a.chosen]}` : "")),
            el("td", null, q ? opt(q.answer) : ""),
            el("td", null, a.second_try == null ? "" : a.second_try ? "right" : "wrong"),
            el("td", "kt-num", String(a.seconds ?? "")),
        );
        mb.append(tr);
    }
    $("loading").hidden = true;
    $("content").hidden = false;
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
