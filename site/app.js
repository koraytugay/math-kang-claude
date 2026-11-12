// Exam website: pick questions, unlock the GitHub token with a password, run the
// "Generate Practice Exam" workflow and open the PDF it commits to output/exams/.
"use strict";

const $ = (id) => document.getElementById(id);
const store = {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch { /* private mode */ } },
    del(k) { try { localStorage.removeItem(k); } catch { /* private mode */ } },
};
const PICK_KEY = "mk.picked", SHOW_KEY = "mk.show";

let cfg = null;              // questions.json
let picked = new Set(JSON.parse(store.get(PICK_KEY) || "[]"));
let token = Secrets.saved()?.github || null;   // secrets.js
let show = Number(store.get(SHOW_KEY) ?? 0);   // index of the contest shown, -1 = all

// ------------------------------------------------------------------ gallery
function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
}

function card(q) {
    const b = el("button", "kt-card kt-card--selectable");
    b.type = "button";
    b.dataset.key = q.key;
    const head = el("div", "kt-card__header mk-card-head");
    const lines = el("div", "kt-stack");
    lines.style.setProperty("--kt-gap", "var(--kt-space-2)");
    const chips = el("div", "kt-cluster");
    for (const k of q.keywords) chips.append(el("span", "kt-chip", k));
    lines.append(el("div", "kt-card__title", q.label), chips);
    head.append(lines);
    const body = el("div", "kt-card__body");
    const img = el("img", "mk-card-img");
    img.src = q.img; img.alt = `Example: ${q.label}`; img.loading = "lazy";
    body.append(img);
    const foot = el("div", "kt-card__footer", q.skill);
    b.append(head, body, foot);
    b.addEventListener("click", () => toggle([q.key], !picked.has(q.key)));
    return b;
}

function pill(label, idx) {
    const b = el("button", "kt-nav__link");
    b.type = "button";
    b.dataset.idx = idx;
    b.append(el("span", null, label), el("span", "kt-badge kt-badge--pill"));
    b.onclick = () => { show = idx; store.set(SHOW_KEY, String(idx)); refresh(); };
    return b;
}

function render() {
    if (!(show >= -1 && show < cfg.contests.length)) show = 0;
    const nav = $("pills");
    nav.innerHTML = "";
    nav.append(pill("All", -1));
    cfg.contests.forEach((c, i) => nav.append(pill(c.pill, i)));

    const root = $("contests");
    root.innerHTML = "";
    for (const [i, c] of cfg.contests.entries()) {
        const sec = el("section", "mk-contest");
        sec.dataset.idx = i;
        const top = el("div", "kt-split kt-mb-3");
        const t = el("div");
        t.append(el("h2", "kt-section-title kt-m-0", c.name), el("div", "kt-caption", c.level));
        const btns = el("div", "kt-cluster");
        const keys = c.questions.map((q) => q.key);
        const all = el("button", "kt-btn", "All");
        all.type = "button"; all.onclick = () => toggle(keys, true);
        const none = el("button", "kt-btn kt-btn--ghost", "None");
        none.type = "button"; none.onclick = () => toggle(keys, false);
        btns.append(all, none);
        top.append(t, btns);
        const grid = el("div", "kt-grid");
        grid.style.setProperty("--kt-grid-min", "480px");
        for (const q of c.questions) grid.append(card(q));
        sec.append(top, grid);
        root.append(sec);
    }
    refresh();
}

function allKeys() { return cfg.contests.flatMap((c) => c.questions.map((q) => q.key)); }

function toggle(keys, on) {
    for (const k of keys) on ? picked.add(k) : picked.delete(k);
    store.set(PICK_KEY, JSON.stringify([...picked]));
    refresh();
}

// Number of questions typed in the box, or null when it is not a whole number from 1 to 60.
function count() {
    const v = $("count").value.trim();
    const n = /^\d+$/.test(v) ? Number(v) : NaN;
    return n >= 1 && n <= 60 ? n : null;
}

function refresh() {
    const valid = new Set(allKeys());
    picked = new Set([...picked].filter((k) => valid.has(k)));
    document.querySelectorAll(".kt-card--selectable").forEach((b) =>
        b.setAttribute("aria-pressed", picked.has(b.dataset.key) ? "true" : "false"));
    document.querySelectorAll(".mk-contest").forEach((s) => { s.hidden = show !== -1 && Number(s.dataset.idx) !== show; });
    document.querySelectorAll("#pills .kt-nav__link").forEach((b) => {
        const i = Number(b.dataset.idx);
        const keys = i === -1 ? allKeys() : cfg.contests[i].questions.map((q) => q.key);
        const n = keys.filter((k) => picked.has(k)).length;
        const badge = b.querySelector(".kt-badge");
        badge.textContent = n;
        badge.hidden = n === 0;
        b.classList.toggle("is-active", i === show);
        b.setAttribute("aria-pressed", String(i === show));
    });
    const n = picked.size, oneEach = $("one-each").checked;
    $("picked").textContent = `${n} question${n === 1 ? "" : "s"} picked`;
    $("picked-hint").textContent = n === 0 ? "Click a question to pick it."
        : oneEach ? `The exam will have ${n} question${n === 1 ? "" : "s"}, one of each.`
        : count() === null ? "Type a number of questions from 1 to 60."
        : `The exam will have ${count()} questions.`;
    $("count").classList.toggle("is-invalid", !oneEach && count() === null);
    $("make").disabled = n === 0 || (!oneEach && count() === null);
}

// ------------------------------------------------------------------ modals
let opener = null;
function openModal(m) {
    if (!m.classList.contains("is-open")) opener = document.activeElement;
    m.classList.add("is-open");
}
function closeModal(m) {
    m.classList.remove("is-open");
    if (opener && document.contains(opener)) opener.focus();
    opener = null;
}
document.querySelectorAll(".kt-modal").forEach((m) => {
    // Close on the backdrop only when the press also started there (not when a text selection ends outside).
    let downOnBackdrop = false;
    m.addEventListener("mousedown", (e) => { downOnBackdrop = e.target === m; });
    m.addEventListener("click", (e) => {
        if ((e.target === m && downOnBackdrop) || e.target.closest(".kt-modal__close")) closeModal(m);
    });
});
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") document.querySelectorAll(".kt-modal.is-open").forEach(closeModal);
});

// ------------------------------------------------------------------ password -> token (secrets.js)
function askPassword() {
    return new Promise((resolve) => {
        const m = $("unlock"), err = $("unlock-error");
        err.hidden = true;
        $("password").value = "";
        openModal(m);
        setTimeout(() => $("password").focus(), 50);   // after the open transition starts
        const done = (v) => { obs.disconnect(); $("unlock-form").onsubmit = null; resolve(v); };
        const obs = new MutationObserver(() => { if (!m.classList.contains("is-open")) done(null); });
        obs.observe(m, { attributes: true, attributeFilter: ["class"] });
        $("unlock-form").onsubmit = async (e) => {
            e.preventDefault();
            $("unlock-btn").disabled = true;
            err.hidden = true;
            try {
                const secrets = await Secrets.unlock($("password").value);
                if ($("remember").checked) Secrets.save(secrets);
                obs.disconnect();
                closeModal(m);
                done(secrets);
            } catch (x) {
                err.textContent = x.message;
                err.hidden = false;
                $("password").select();
            } finally {
                $("unlock-btn").disabled = false;
            }
        };
    });
}

// ------------------------------------------------------------------ GitHub
class AuthError extends Error {}

async function gh(path, opts = {}) {
    const r = await fetch(`https://api.github.com/repos/${cfg.repo}${path}`, {
        ...opts,
        cache: "no-store",
        headers: {
            Authorization: `Bearer ${token}`,
            Accept: "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            ...(opts.headers || {}),
        },
    });
    if (r.status === 401) throw new AuthError("GitHub did not accept the token (expired or deleted?).");
    if (!r.ok) throw new Error(`GitHub answered ${r.status}: ${(await r.text()).slice(0, 200)}`);
    return r;
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function examNames() {
    const r = await gh("/contents/output/exams");
    return (await r.json()).map((f) => f.name).filter((n) => n.endsWith(".pdf"));
}

async function latestRunId() {
    const r = await gh(`/actions/workflows/${cfg.workflow}/runs?per_page=1`);
    const runs = (await r.json()).workflow_runs;
    return runs.length ? runs[0].id : 0;
}

function status(text) { $("progress-text").textContent = text; }

let running = false, pdfUrl = null;

/** plan: null for the picked questions, or {name, items} for a personal exam ("key@level,..."). */
async function makeExam(plan = null) {
    if (running) { openModal($("progress")); return; }
    if (!token) token = (await askPassword())?.github || null;
    if (!token) return;
    running = true;
    $("make").textContent = "Making exam…";

    const m = $("progress");
    $("progress-title").textContent = "Making your exam";
    $("progress-busy").hidden = false;
    $("progress-error").hidden = true;
    $("progress-done").hidden = true;
    $("run-link").hidden = true;
    openModal(m);
    const t0 = Date.now();
    const secs = () => Math.round((Date.now() - t0) / 1000);

    try {
        status("Asking GitHub to start…");
        const before = new Set(await examNames());
        const lastRun = await latestRunId();
        await gh(`/actions/workflows/${cfg.workflow}/dispatches`, {
            method: "POST",
            body: JSON.stringify({
                ref: "main",
                inputs: {
                    questions: String(count() ?? 20),
                    harder: String(!plan && $("harder").checked),
                    one_each: String(!plan && $("one-each").checked),
                    website: plan ? `plan:${plan.name}:${plan.items}` : [...picked].join(","),
                },
            }),
        });

        let run = null;
        while (!run) {
            if (secs() > 90) throw new Error("GitHub did not start the run. Try again in a minute.");
            await sleep(3000);
            status(`Waiting for GitHub to start… (${secs()} s)`);
            const r = await gh(`/actions/workflows/${cfg.workflow}/runs?event=workflow_dispatch&per_page=5`);
            run = (await r.json()).workflow_runs.filter((x) => x.id > lastRun).pop() || null;
        }
        $("run-link").href = run.html_url;
        $("run-link").hidden = false;

        while (run.status !== "completed") {
            if (secs() > 600) throw new Error("This is taking too long. Check the run on GitHub.");
            status(`Making the exam… (${secs()} s, usually about a minute)`);
            await sleep(4000);
            run = await (await gh(`/actions/runs/${run.id}`)).json();
        }
        if (run.conclusion !== "success") throw new Error(`The run ended with “${run.conclusion}”. See the run on GitHub.`);

        status("Fetching the PDF…");
        let name = null;
        for (let i = 0; i < 10 && !name; i++) {
            name = (await examNames()).filter((n) => !before.has(n)).sort().pop() || null;
            if (!name) await sleep(2000);
        }
        if (!name) throw new Error("The run finished, but no new PDF showed up in output/exams.");
        const pdf = await gh(`/contents/output/exams/${name}`, { headers: { Accept: "application/vnd.github.raw" } });
        if (pdfUrl) URL.revokeObjectURL(pdfUrl);
        const url = pdfUrl = URL.createObjectURL(new Blob([await pdf.arrayBuffer()], { type: "application/pdf" }));

        $("progress-title").textContent = "Your exam is ready";
        $("done-text").textContent = `${name} is ready (${secs()} s).`;
        $("open-pdf").href = url;
        $("save-pdf").href = url;
        $("save-pdf").download = name;
        $("progress-busy").hidden = true;
        $("progress-done").hidden = false;
    } catch (x) {
        if (x instanceof AuthError) { Secrets.forget(); token = null; }
        $("progress-title").textContent = "Something went wrong";
        $("progress-busy").hidden = true;
        $("progress-error").textContent = x.message +
            (x instanceof AuthError ? " The saved password was forgotten; try again." : "");
        $("progress-error").hidden = false;
    } finally {
        running = false;
        $("make").textContent = "Make exam";
        openModal(m);   // the dialog may have been closed while waiting: show how it ended
    }
}

// ------------------------------------------------------------------ start
$("all").onclick = () => toggle(allKeys(), true);
$("none").onclick = () => toggle(allKeys(), false);
$("count").oninput = refresh;
$("one-each").onchange = refresh;
$("make").onclick = () => makeExam();

// Personal exam: the same planning as the practice page (smart.js) on the child's answers in the database.
async function examFor(id, name) {
    if (running) { openModal($("progress")); return; }
    let s = Secrets.saved();
    if (!s?.db) s = await askPassword();
    if (!s) return;
    token = s.github;
    let attempts;
    try {
        attempts = await fetchAttempts(s.db, id);
    } catch (x) {
        $("progress-title").textContent = "Something went wrong";
        $("progress-busy").hidden = true;
        $("progress-done").hidden = true;
        $("run-link").hidden = true;
        $("progress-error").textContent = `Could not read ${name}'s answers: ${x.message}`;
        $("progress-error").hidden = false;
        openModal($("progress"));
        return;
    }
    const states = skillStates(attempts);
    const known = new Map((await fetch("bank/index.json").then((r) => r.json())).generators.map((g) => [g.key, g]));
    const gens = allKeys().map((key) => known.get(key) || { key });   // with g.added for the new-in-pool boost
    const items = planSkills(gens, states, count() ?? 20)
        .map((g) => `${g.key}@${states.get(g.key)?.level ?? 0}`).join(",");
    makeExam({ name, items });
}
document.querySelectorAll("[data-profile]").forEach((b) => {
    b.onclick = () => examFor(b.dataset.profile, b.dataset.name);
});
$("forget").onclick = (e) => {
    e.preventDefault();
    Secrets.forget();
    token = null;
    e.target.textContent = "Forgotten. The password will be asked next time.";
};

fetch("questions.json", { cache: "no-store" })
    .then((r) => r.json())
    .then((j) => { cfg = j; render(); })
    .catch(() => { $("contests").innerHTML = '<div class="kt-alert kt-alert--danger kt-mt-4">Could not load the questions.</div>'; });
