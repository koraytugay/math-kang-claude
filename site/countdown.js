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

const CONTEST = new Date(2027, 2, 21);              // Sunday, March 21, 2027 (local time)
const KIDS = ["deniz", "toprak"];                   // the parent's test profile does not count
const GOALS = [25, 50, 100, 250, 500, 750, 1000, 1500, 2000, 3000, 5000];
const CHEERS = [
    "Every question makes your brain a little stronger.",
    "Mistakes are how you learn. Keep hopping!",
    "Kangaroos can't walk backwards. Only forwards!",
    "A little practice every day adds up to a lot.",
    "You are getting better every single day.",
    "Tricky question? Draw it, try small numbers, check every option.",
];

// ------------------------------------------------------------------ countdown
const midnight = (d) => new Date(d.getFullYear(), d.getMonth(), d.getDate());
function tick() {
    const now = new Date();
    const days = Math.round((CONTEST - midnight(now)) / DAY);
    if (days > 0) {
        $("days").textContent = days;
        $("days-unit").textContent = days === 1 ? "day to go! Tomorrow is the day!" : "days to go!";
        const left = new Date(CONTEST - now);
        const h = Math.floor((CONTEST - now) / 36e5);
        $("clock").textContent = `${h.toLocaleString()} hours · ${String(left.getUTCMinutes()).padStart(2, "0")} min · ${String(left.getUTCSeconds()).padStart(2, "0")} s`;
    } else if (days === 0) {
        $("days").textContent = "🎉"; $("days-unit").textContent = "It's contest day! You've got this!"; $("clock").textContent = "";
    } else {
        $("days").textContent = "🏅"; $("days-unit").textContent = "You did the contest! So proud of you."; $("clock").textContent = "";
    }
    return days;
}

// ------------------------------------------------------------------ numbers (both kids together)
function numbers(byKid, gens) {
    const n = { answered: 0, right: 0, learned: 0, partC: 0, days: 0, streak: 0, solid: 0, skills: gens.length };
    const dates = new Set();
    const solid = new Set();
    for (const attempts of byKid) {
        const real = attempts.filter((a) => !a.variant?.startsWith("warmup:"));
        n.answered += real.filter((a) => a.chosen >= 0).length;
        n.right += real.filter((a) => a.correct).length;
        n.partC += real.filter((a) => a.correct && a.difficulty === 3).length;
        // learned: a question first got wrong (or skipped), and later a question of the same skill right
        // on the first try (not a quick guess) - the same rule as the parent page
        const counted = new Set();
        for (const a of real) {
            if (a.correct || counted.has(a.id)) continue;
            const later = real.some((b) => b.gen === a.gen && b.correct && new Date(b.at) > new Date(a.at)
                && !isGuess(b.difficulty, b.seconds));
            if (later) { counted.add(a.id); n.learned++; }
        }
        for (const a of attempts) dates.add(midnight(new Date(a.at)).getTime());
        for (const [key, s] of skillStates(attempts)) if (s.status === "solid") solid.add(key);
    }
    n.days = dates.size;
    n.solid = solid.size;
    // practice days in a row, up to today (or up to yesterday: today may still come)
    let d = midnight(new Date()).getTime();
    if (!dates.has(d)) d -= DAY;
    while (dates.has(d)) { n.streak++; d = midnight(new Date(d - DAY / 2)).getTime(); }
    return n;
}

// ------------------------------------------------------------------ stickers
const STICKERS = [
    ["🐣", "First hop", "Answer your first question", (n) => n.answered >= 1],
    ["🔟", "Ten!", "Answer 10 questions", (n) => n.answered >= 10],
    ["💯", "Hundred club", "Answer 100 questions", (n) => n.answered >= 100],
    ["🚀", "Rocket", "Answer 250 questions", (n) => n.answered >= 250],
    ["🏔️", "Mountain top", "Answer 500 questions", (n) => n.answered >= 500],
    ["👑", "Kangaroo royalty", "Answer 1000 questions", (n) => n.answered >= 1000],
    ["🌱", "Brain sprout", "Learn from 5 mistakes", (n) => n.learned >= 5],
    ["🌳", "Brain tree", "Learn from 25 mistakes", (n) => n.learned >= 25],
    ["🧠", "Mega brain", "Learn from 100 mistakes", (n) => n.learned >= 100],
    ["🎯", "Bullseye", "50 right on the first try", (n) => n.right >= 50],
    ["🏹", "Sharpshooter", "250 right on the first try", (n) => n.right >= 250],
    ["🧗", "Part C climber", "10 hard Part C questions right", (n) => n.partC >= 10],
    ["🦅", "Part C eagle", "50 hard Part C questions right", (n) => n.partC >= 50],
    ["🔥", "On fire", "Practise 3 days in a row", (n) => n.streak >= 3],
    ["⚡", "Lightning week", "Practise 7 days in a row", (n) => n.streak >= 7],
    ["📅", "Ten days", "Practise on 10 different days", (n) => n.days >= 10],
    ["⭐", "Skill star", "Get 5 skills to solid", (n) => n.solid >= 5],
    ["🏆", "Skill champion", "Get every skill to solid", (n) => n.skills > 0 && n.solid >= n.skills],
    ["🦘", "Contest day", "Be ready on March 21!", () => midnight(new Date()) >= CONTEST],
];

function stickerBook(n) {
    let seen = [];
    try { seen = JSON.parse(localStorage.getItem("mk.stickers")) || []; } catch { /* blocked */ }
    const box = $("stickers");
    box.innerHTML = "";
    const got = [], fresh = [];
    for (const [emoji, name, how, test] of STICKERS) {
        const has = test(n);
        const card = el("div", `mk-sticker ${has ? "mk-sticker--got" : "mk-sticker--locked"}`);
        card.append(el("div", "mk-sticker__emoji", emoji), el("div", "mk-sticker__name", has ? name : "???"),
            el("div", "mk-sticker__how", how));
        card.title = has ? `${name}: ${how}` : `Still to earn: ${how}`;
        if (has) { got.push(name); if (seen.length && !seen.includes(name)) { fresh.push(name); card.classList.add("mk-sticker--new"); } }
        box.append(card);
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

function confetti() {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const colors = ["--kt-gold", "--kt-pink", "--kt-green", "--kt-blue", "--kt-orange", "--kt-purple", "--kt-teal"];
    for (let i = 0; i < 120; i++) {
        const c = el("div", "mk-confetti");
        c.style.left = `${Math.random() * 100}vw`;
        c.style.background = `var(${colors[i % colors.length]})`;
        c.style.animationDuration = `${2.5 + Math.random() * 2.5}s`;
        c.style.animationDelay = `${Math.random() * 0.8}s`;
        c.style.borderRadius = i % 3 ? "2px" : "50%";
        document.body.append(c);
        setTimeout(() => c.remove(), 6000);
    }
}

function render(n, daysLeft) {
    const stats = $("stats");
    stats.innerHTML = "";
    for (const [icon, value, label, cls] of [
        ["✏️", n.answered, "questions answered", "mk-c1"],
        ["🎯", n.right, "right on the first try", "mk-c2"],
        ["🧠", n.learned, "mistakes turned into learning", "mk-c3"],
        ["📅", n.days, n.days === 1 ? "day of practice" : "days of practice", "mk-c4"],
    ]) {
        const box = el("div", `mk-stat ${cls}`);
        const v = el("div", "mk-stat__value", "0");
        box.append(el("div", "mk-stat__icon", icon), v, el("div", "mk-stat__label", label));
        stats.append(box);
        countUp(v, value);
    }

    // goals: the next one, a progress bar, and how many a day would get there by contest day
    const next = GOALS.find((g) => g > n.answered) ?? GOALS.at(-1);
    const prev = [...GOALS].reverse().find((g) => g <= n.answered) ?? 0;
    $("goal-title").textContent = `🏁 ${next.toLocaleString()} questions`;
    $("goal-count").textContent = `${n.answered.toLocaleString()} / ${next.toLocaleString()}`;
    const share = Math.min(1, (n.answered - prev) / (next - prev || 1));
    requestAnimationFrame(() => requestAnimationFrame(() => { $("goal-bar").style.width = `${Math.max(2, share * 100)}%`; }));
    const togo = next - n.answered;
    $("goal-note").textContent = togo <= 0 ? "Every goal reached. Wow!"
        : daysLeft > 0
            ? `Only ${togo.toLocaleString()} more to go! That's about ${Math.max(1, Math.ceil(togo / daysLeft))} a day until the contest.`
            : `Only ${togo.toLocaleString()} more to go!`;
    const flags = $("flags");
    flags.innerHTML = "";
    for (const g of GOALS) flags.append(el("span", `mk-flag ${n.answered >= g ? "mk-flag--done" : ""}`,
        `${n.answered >= g ? "✅ " : ""}${g.toLocaleString()}`));

    if (stickerBook(n)) setTimeout(confetti, 600);
    if (n.streak >= 2) $("cheer").textContent = `🔥 ${n.streak} days of practice in a row. Keep the streak going!`;
}

async function start(s) {
    $("lock").hidden = true;
    $("view").hidden = false;
    $("cheer").textContent = CHEERS[Math.floor(Math.random() * CHEERS.length)];
    const daysLeft = tick();
    setInterval(tick, 1000);
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
