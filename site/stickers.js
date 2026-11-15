// Stickers, shared by the countdown page (both kids together) and the practice page (one child: a sticker
// unlocked during practice is celebrated, even if the brother already has it). Needs smart.js (DAY, isGuess,
// skillStates). numbers(byKid, gens): byKid is a list of attempt lists (one per child).
"use strict";

const CONTEST = new Date(2027, 2, 21);              // Sunday, March 21, 2027 (local time)
const midnight = (d) => new Date(d.getFullYear(), d.getMonth(), d.getDate());

// ------------------------------------------------------------------ numbers (one child or both together)
const rightAnswer = (a) => (a.correct && !isGuess(a.difficulty, a.seconds)) || (!a.correct && a.second_try);

function numbers(byKid, gens) {
    const byKey = new Map(gens.map((g) => [g.key, g]));
    const n = { answered: 0, right: 0, learned: 0, partB: 0, partC: 0, harder: 0, second: 0, days: 0, streak: 0,
                solid: 0, skills: gens.length, tried: 0, bestRun: 0, seconds: 0, patient: 0, bestDay: 0, warmups: 0,
                early: 0, holiday: false, newYear: false, last: 0, exams: 0, examsTotal: 0, topics: {} };
    const dates = new Map();                        // day -> answers that day (both kids)
    const solid = new Set(), tried = new Set();
    for (const attempts of byKid) {
        const real = attempts.filter((a) => !a.variant?.startsWith("warmup:"))
            .sort((a, b) => new Date(a.at) - new Date(b.at));
        n.warmups += attempts.length - real.length;
        n.answered += real.filter((a) => a.chosen >= 0).length;
        // right answers: on the first try (not a quick guess) or on the second try - what the goal flags count
        // (all answers filled them too fast; a son: "a right second try is right too")
        n.right += real.filter(rightAnswer).length;
        n.second += real.filter((a) => !a.correct && a.second_try).length;
        n.partB += real.filter((a) => a.correct && a.difficulty === 2).length;
        n.partC += real.filter((a) => a.correct && a.difficulty === 3).length;
        n.harder += real.filter((a) => a.correct && a.difficulty === 3 && a.harder).length;
        n.patient += real.filter((a) => a.correct && a.seconds >= 120).length;   // kept thinking and got it
        // learned: a question first got wrong (or skipped), and later a question of the same skill right
        // on the first try (not a quick guess) - the same rule as the parent page
        const counted = new Set();
        let run = 0;
        for (const a of real) {
            run = a.correct ? run + 1 : 0;                       // right on the first try in a row (one child)
            n.bestRun = Math.max(n.bestRun, run);
            tried.add(a.gen);
            n.seconds += a.seconds || 0;
            if (rightAnswer(a)) for (const t of byKey.get(a.gen)?.topics || []) n.topics[t] = (n.topics[t] || 0) + 1;
            if (a.correct || counted.has(a.id)) continue;
            const later = real.some((b) => b.gen === a.gen && b.correct && new Date(b.at) > new Date(a.at)
                && !isGuess(b.difficulty, b.seconds));
            if (later) { counted.add(a.id); n.learned++; }
        }
        for (const a of attempts) {
            const t = new Date(a.at), day = midnight(t).getTime();
            dates.set(day, (dates.get(day) || 0) + 1);
            if (t.getHours() < 9) n.early++;
            if (day >= new Date(2026, 11, 21).getTime() && day <= new Date(2027, 0, 3).getTime()) n.holiday = true;
            if (day === new Date(2027, 0, 1).getTime()) n.newYear = true;
            n.last = Math.max(n.last, t.getTime());
        }
        for (const [key, s] of skillStates(attempts)) if (s.status === "solid") solid.add(key);
    }
    n.days = dates.size;
    n.bestDay = Math.max(0, ...dates.values());
    n.solid = solid.size;
    n.tried = tried.size;
    // a "gym badge": every question from one past exam is solid
    const exams = new Map();
    for (const g of gens) exams.set(g.contest, [...(exams.get(g.contest) || []), g.key]);
    n.examsTotal = exams.size;
    n.exams = [...exams.values()].filter((keys) => keys.every((k) => solid.has(k))).length;
    // practice days in a row, up to today (or up to yesterday: today may still come)
    let d = midnight(new Date()).getTime();
    if (!dates.has(d)) d -= DAY;
    while (dates.has(d)) { n.streak++; d = midnight(new Date(d - DAY / 2)).getTime(); }
    return n;
}

// ------------------------------------------------------------------ stickers
const daysBefore = (k) => CONTEST.getTime() - k * DAY;          // practised when only k days were left
const HOUR = 3600;
const STICKER_GROUPS = [
    ["Questions", [
        ["🐣", "First hop", "Answer your first question", (n) => n.answered >= 1],
        ["🔟", "Ten!", "Answer 10 questions", (n) => n.answered >= 10],
        ["🍀", "Lucky 25", "Answer 25 questions", (n) => n.answered >= 25],
        ["🎈", "Fifty", "Answer 50 questions", (n) => n.answered >= 50],
        ["💯", "Hundred club", "Answer 100 questions", (n) => n.answered >= 100],
        ["🚀", "Rocket", "Answer 250 questions", (n) => n.answered >= 250],
        ["🏔️", "Mountain top", "Answer 500 questions", (n) => n.answered >= 500],
        ["🌌", "Galaxy", "Answer 1000 questions", (n) => n.answered >= 1000],
    ]],
    ["Right answers", [
        ["🎯", "Bullseye", "50 right answers", (n) => n.right >= 50],
        ["🎪", "Showtime", "100 right answers", (n) => n.right >= 100],
        ["🏹", "Sharpshooter", "250 right answers", (n) => n.right >= 250],
        ["🌟", "Superstar", "500 right answers", (n) => n.right >= 500],
        ["💎", "Diamond", "750 right answers", (n) => n.right >= 750],
        ["👑", "Kangaroo royalty", "1000 right answers: the ultimate goal", (n) => n.right >= 1000],
        ["🎴", "4 Pokémon packs!", "1250 right answers", (n) => n.right >= 1250],
    ]],
    ["Learning from mistakes", [
        ["🔄", "Comeback kid", "Right on the second try 5 times", (n) => n.second >= 5],
        ["🪃", "Boomerang", "Right on the second try 25 times", (n) => n.second >= 25],
        ["🌱", "Brain sprout", "Learn from 5 mistakes", (n) => n.learned >= 5],
        ["🌳", "Brain tree", "Learn from 25 mistakes", (n) => n.learned >= 25],
        ["🌲", "Brain forest", "Learn from 50 mistakes", (n) => n.learned >= 50],
        ["🧠", "Mega brain", "Learn from 100 mistakes", (n) => n.learned >= 100],
        ["🦉", "Wise owl", "Learn from 250 mistakes", (n) => n.learned >= 250],
        ["🏃", "Warmed up", "Do 5 warm-up questions", (n) => n.warmups >= 5],
    ]],
    ["Tough ones", [
        ["🧩", "Part B builder", "25 Part B questions right", (n) => n.partB >= 25],
        ["🧗", "Part C climber", "10 hard Part C questions right", (n) => n.partC >= 10],
        ["🦅", "Part C eagle", "50 hard Part C questions right", (n) => n.partC >= 50],
        ["🐉", "Dragon tamer", "100 hard Part C questions right", (n) => n.partC >= 100],
        ["🌋", "Volcano", "10 right with the hardest numbers", (n) => n.harder >= 10],
        ["☄️", "Comet", "50 right with the hardest numbers", (n) => n.harder >= 50],
        ["🐢", "Slow and sure", "Get one right after thinking 2+ minutes", (n) => n.patient >= 1],
        ["🧘", "Deep thinker", "Get 10 right after thinking 2+ minutes", (n) => n.patient >= 10],
    ]],
    ["In a row", [
        ["🖐️", "High five", "5 right on the first try in a row", (n) => n.bestRun >= 5],
        ["🎳", "Strike!", "10 right on the first try in a row", (n) => n.bestRun >= 10],
        ["🌪️", "Unstoppable", "20 right on the first try in a row", (n) => n.bestRun >= 20],
        ["🔥", "On fire", "Practise 3 days in a row", (n) => n.streak >= 3],
        ["⚡", "Lightning week", "Practise 7 days in a row", (n) => n.streak >= 7],
        ["🌠", "Shooting star", "Practise 14 days in a row", (n) => n.streak >= 14],
        ["🌕", "Full moon", "Practise 30 days in a row", (n) => n.streak >= 30],
    ]],
    ["Practice time", [
        ["🗓️", "Five days", "Practise on 5 different days", (n) => n.days >= 5],
        ["📅", "Ten days", "Practise on 10 different days", (n) => n.days >= 10],
        ["📆", "Twenty-five days", "Practise on 25 different days", (n) => n.days >= 25],
        ["🏅", "Fifty days", "Practise on 50 different days", (n) => n.days >= 50],
        ["🎡", "Big day", "Answer 20 questions in one day", (n) => n.bestDay >= 20],
        ["🎆", "Mega day", "Answer 50 questions in one day", (n) => n.bestDay >= 50],
        ["⏱️", "One hour", "Think for 1 hour in total", (n) => n.seconds >= HOUR],
        ["⌛", "Five hours", "Think for 5 hours in total", (n) => n.seconds >= 5 * HOUR],
        ["🕰️", "Ten hours", "Think for 10 hours in total", (n) => n.seconds >= 10 * HOUR],
        ["🌅", "Early bird", "Practise before 9 in the morning", (n) => n.early >= 1],
    ]],
    ["Skills", [
        ["🔍", "Explorer", "Try 10 different skills", (n) => n.tried >= 10],
        ["🗺️", "Adventurer", "Try 25 different skills", (n) => n.tried >= 25],
        ["🧭", "Every path", "Try every skill", (n) => n.skills > 0 && n.tried >= n.skills],
        ["⭐", "Skill star", "Get 5 skills to solid", (n) => n.solid >= 5],
        ["✨", "Sparkle ten", "Get 10 skills to solid", (n) => n.solid >= 10],
        ["💫", "Skill galaxy", "Get 25 skills to solid", (n) => n.solid >= 25],
        ["🏆", "Skill champion", "Get every skill to solid", (n) => n.skills > 0 && n.solid >= n.skills],
        ["🏟️", "Gym badge", "Every question from one past exam solid", (n) => n.exams >= 1],
        ["🎖️", "Three badges", "Every question from 3 past exams solid", (n) => n.exams >= 3],
        ["🏰", "All the gyms", "Every question from every past exam solid", (n) => n.examsTotal > 0 && n.exams >= n.examsTotal],
    ]],
    ["Topics", [
        ["🕵️", "Detective", "25 logic questions right", (n) => (n.topics.logic || 0) >= 25],
        ["🧊", "Cube master", "25 spatial questions right", (n) => (n.topics.spatial || 0) >= 25],
        ["🧮", "Counting champ", "25 counting questions right", (n) => (n.topics.counting || 0) >= 25],
        ["➕", "Number ninja", "25 arithmetic questions right", (n) => (n.topics.arithmetic || 0) >= 25],
        ["📐", "Shape shifter", "25 geometry questions right", (n) => (n.topics.geometry || 0) >= 25],
        ["🔁", "Pattern finder", "25 pattern questions right", (n) => (n.topics.patterns || 0) >= 25],
    ]],
    ["On the way to March 21", [
        ["🎒", "100 days to go", "Practise when 100 days are left", (n) => n.last >= daysBefore(100)],
        ["🎄", "Holiday hopper", "Practise in the winter holidays", (n) => n.holiday],
        ["🥳", "New Year brain", "Practise on January 1", (n) => n.newYear],
        ["🏁", "50 days to go", "Practise when 50 days are left", (n) => n.last >= daysBefore(50)],
        ["🚦", "Final ten", "Practise in the last 10 days", (n) => n.last >= daysBefore(10)],
        ["🌙", "Night before", "Practise on March 20", (n) => n.last >= daysBefore(1)],
        ["🦘", "Contest day", "Be ready on March 21!", () => midnight(new Date()) >= CONTEST],
    ]],
];
const STICKERS = STICKER_GROUPS.flatMap(([, list]) => list);

/** The names of the stickers these numbers earn. */
const earnedStickers = (n) => new Set(STICKERS.filter(([, , , test]) => test(n)).map(([, name]) => name));

function confetti() {
    if (!document.getElementById("mk-confetti-style")) {
        const st = document.createElement("style");
        st.id = "mk-confetti-style";
        st.textContent = `.mk-confetti { position: fixed; top: -20px; width: 10px; height: 16px; z-index: 2000;
            pointer-events: none; animation: mk-fall linear forwards; }
            @keyframes mk-fall { to { transform: translateY(110vh) rotate(720deg); } }`;
        document.head.append(st);
    }
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const colors = ["--kt-gold", "--kt-pink", "--kt-green", "--kt-blue", "--kt-orange", "--kt-purple", "--kt-teal"];
    for (let i = 0; i < 120; i++) {
        const c = document.createElement("div");
        c.className = "mk-confetti";
        c.style.left = `${Math.random() * 100}vw`;
        c.style.background = `var(${colors[i % colors.length]})`;
        c.style.animationDuration = `${2.5 + Math.random() * 2.5}s`;
        c.style.animationDelay = `${Math.random() * 0.8}s`;
        c.style.borderRadius = i % 3 ? "2px" : "50%";
        document.body.append(c);
        setTimeout(() => c.remove(), 6000);
    }
}
