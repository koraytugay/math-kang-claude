// Countdown page (countdown.html): days to the contest, and what both kids did together - questions, mistakes
// turned into learning, goals and stickers. Always both kids combined, never one against the other.
"use strict";

const $ = (id) => document.getElementById(id);
const el = (tag, cls, text) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
};

const KIDS = ["deniz", "toprak"];                   // the parent's test profile does not count
// Goals (parent, 2026-11-14), counting right answers (first or second try): ultimate goal 1,000, then a Pokémon
// booster pack at 1,250 (the kids agreed, hyped); a McDonald's treat every 200. Flags count answers right on the
// first try (not a quick guess).
const GOALS = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1250];
const TREATS = [200, 400, 600, 800, 1000];          // a McDonald's treat when this flag is reached
const BOOSTER = 1250;                          // a Pokémon booster pack when this flag is reached
const BIG_GOALS = { 1000: "🌈 Ultimate goal", 1250: "🎴 4 Pokémon packs" };
const CHEERS = [
    "Every question makes your brain a little stronger.",
    "Mistakes are how you learn. Keep hopping!",
    "Kangaroos can't walk backwards. Only forwards!",
    "A little practice every day adds up to a lot.",
    "You are getting better every single day.",
    "Tricky question? Draw it, try small numbers, check every option.",
];

// ------------------------------------------------------------------ countdown
function tick() {
    const now = new Date();
    const days = Math.round((CONTEST - midnight(now)) / DAY);
    if (days > 0) {
        $("days").textContent = days;
        $("days-unit").textContent = days === 1 ? "day to go! Tomorrow is the day!" : "days to go!";
    } else if (days === 0) {
        $("days").textContent = "🎉"; $("days-unit").textContent = "It's contest day! You've got this!";
    } else {
        $("days").textContent = "🏅"; $("days-unit").textContent = "You did the contest! So proud of you.";
    }
    return days;
}

function stickerBook(n) {
    let seen = [];
    try { seen = JSON.parse(localStorage.getItem("mk.stickers")) || []; } catch { /* blocked */ }
    const box = $("stickers");
    box.innerHTML = "";
    const got = [], fresh = [];
    for (const [group, list] of STICKER_GROUPS) {
        const have = list.filter(([, , , test]) => test(n)).length;
        const h = el("div", "mk-sticker-group", group);
        h.append(el("span", "mk-sticker-group__count", `${have} of ${list.length}`));
        box.append(h);
        for (const [emoji, name, how, test] of list) {
            const has = test(n);
            const card = el("div", `mk-sticker ${has ? "mk-sticker--got" : "mk-sticker--locked"}`);
            card.append(el("div", "mk-sticker__emoji", emoji), el("div", "mk-sticker__name", has ? name : "???"),
                el("div", "mk-sticker__how", how));
            card.title = has ? `${name}: ${how}` : `Still to earn: ${how}`;
            if (has) { got.push(name); if (seen.length && !seen.includes(name)) { fresh.push(name); card.classList.add("mk-sticker--new"); } }
            box.append(card);
        }
    }
    $("sticker-count").textContent = `${got.length} of ${STICKERS.length}`;
    try { localStorage.setItem("mk.stickers", JSON.stringify(got)); } catch { /* blocked */ }
    return fresh.length > 0 || (!seen.length && got.length > 0);
}

// ------------------------------------------------------------------ page
function countUp(node, to) {
    const t0 = performance.now(), ms = 1400;
    const step = (t) => {
        const k = Math.min(1, (t - t0) / ms);
        node.textContent = Math.round(to * (1 - Math.pow(1 - k, 3))).toLocaleString();
        if (k < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
}

function render(n, daysLeft) {
    const stats = $("stats");
    stats.innerHTML = "";
    for (const [icon, value, label, cls] of [
        ["✏️", n.answered, "questions answered", "mk-c1"],
        ["🎯", n.right, "right answers", "mk-c2"],
        ["🧠", n.learned, "mistakes turned into learning", "mk-c3"],
        ["📅", n.days, n.days === 1 ? "day of practice" : "days of practice", "mk-c4"],
    ]) {
        const box = el("div", `mk-stat ${cls}`);
        const v = el("div", "mk-stat__value", "0");
        box.append(el("div", "mk-stat__icon", icon), v, el("div", "mk-stat__label", label));
        stats.append(box);
        countUp(v, value);
    }

    // goals: the next flag, a progress bar, and the two big goals
    const next = GOALS.find((g) => g > n.right) ?? GOALS.at(-1);
    const prev = [...GOALS].reverse().find((g) => g <= n.right) ?? 0;
    $("goal-title").textContent = `🏁 ${BIG_GOALS[next] ? BIG_GOALS[next] + ": " : ""}${next.toLocaleString()} right answers`;
    const share = Math.min(1, (n.right - prev) / (next - prev || 1));
    requestAnimationFrame(() => requestAnimationFrame(() => { $("goal-bar").style.width = `${Math.max(2, share * 100)}%`; }));
    const togo = next - n.right;
    $("goal-note").textContent = togo <= 0 ? "Every goal reached, even the ultimate one. WOW!"
        : n.right >= 1000 ? `Ultimate goal reached! Only ${(BOOSTER - n.right).toLocaleString()} more to the 4 Pokémon packs!`
            : `Only ${togo.toLocaleString()} more right answers to the next flag! Ultimate goal: 1,000 · then 4 Pokémon packs at 1,250!`;
    const flags = $("flags");
    flags.innerHTML = "";
    for (const g of GOALS.filter((x) => x !== BOOSTER)) {
        const f = el("span", `mk-flag${n.right >= g ? " mk-flag--done" : ""}`,
            `${n.right >= g ? "✅ " : ""}${g.toLocaleString()}${TREATS.includes(g) ? " 🍔" : ""}`);
        f.title = [BIG_GOALS[g]?.slice(3), TREATS.includes(g) && "McDonald's treat", g === BOOSTER && "Pokémon booster pack"]
            .filter(Boolean).join(" · ");
        flags.append(f);
    }

    // the booster pack: the last pill of the row, filling the rest of it, shiny
    const got = n.right >= BOOSTER;
    flags.append(el("span", `mk-flag mk-flag--booster${got ? " mk-flag--done" : ""}`,
        `${BOOSTER.toLocaleString()} 4 Pokémon Packs!${got ? " You did it!" : ""}`));

    if (stickerBook(n)) setTimeout(confetti, 600);
    if (n.streak >= 2) $("cheer").textContent = `🔥 ${n.streak} days of practice in a row. Keep the streak going!`;
}

async function start(s) {
    $("lock").hidden = true;
    $("view").hidden = false;
    $("cheer").textContent = CHEERS[Math.floor(Math.random() * CHEERS.length)];
    const daysLeft = tick();
    setInterval(tick, 60e3);
    try {
        const [index, ...byKid] = await Promise.all([
            fetch("bank/index.json", { cache: "no-store" }).then((r) => r.json()),
            ...KIDS.map((k) => fetchAttempts(s.db, k)),
        ]);
        render(numbers(byKid, index.generators), daysLeft);
        $("loading").hidden = true;
        $("content").hidden = false;
    } catch (e) {
        $("loading").replaceChildren(el("div", "kt-alert kt-alert--danger", `Could not count the questions: ${e.message}`));
    }
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

const saved = Secrets.saved();
if (saved?.db) start(saved); else { $("lock").hidden = false; $("lock-password").focus(); }
