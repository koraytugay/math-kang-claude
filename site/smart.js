// Personal practice logic, shared by the practice page, the exam page ("For Deniz") and the parent page.
"use strict";

// Every child has their own state per skill (generator), replayed from their answers in time order.
//
// SCORE (0..100): how well the child knows the skill. Points per answer (first try counts):
//   right Part A +15, Part B +20, Part C +25, Part C harder +30;
//   right but too fast (probably a guess) +5; wrong first, right on the second try +5; wrong -20.
// After a week without practice the score fades about 10% per week, so forgotten skills come back.
// STATUS: needs work (< 15 and at least one real mistake) / getting there / solid (>= 60 and 3+ right
// answers, so one lucky easy answer never makes a skill solid). Only the parent page shows these words.
// WEIGHT (how often a skill shows up): 1 + (100 - score) / 10, a little more when it has not been seen for
// a while; untried skills 6. Every right answer lowers it, every wrong one raises it.
// LEVEL (which questions): right -> one level up next time (Part A -> B -> C -> harder numbers);
// wrong -> one level down. A quick guess does not raise the level.
const DAY = 864e5;
const LEVELS = [[1, false], [2, false], [3, false], [3, true]];     // [difficulty, harder]
const RIGHT_POINTS = [15, 20, 25, 30];                               // by level of the question answered
const WRONG_POINTS = -20, SMALL_POINTS = 5, FADE_PER_WEEK = 0.9;
const NEEDS_WORK = 15, SOLID = 60, SOLID_RIGHTS = 3, NEW_WEIGHT = 6;
// A right answer faster than this (seconds, by Part A/B/C) is probably a guess.
const MIN_SECONDS = { 1: 4, 2: 6, 3: 8 };
const isGuess = (difficulty, seconds) => seconds != null && seconds < (MIN_SECONDS[difficulty] ?? 4);
const levelOf = (difficulty, harder) => Math.max(0, LEVELS.findIndex(([d, h]) => d === difficulty && h === !!harder));
const fade = (score, fromMs, toMs) => score * Math.pow(FADE_PER_WEEK, Math.max(0, toMs - fromMs - 7 * DAY) / (7 * DAY));

function skillStates(attempts, now = Date.now()) {
    const states = new Map();
    // Replay in time order. Row order is not enough: answers saved while offline are uploaded later.
    const inTime = [...attempts].sort((a, b) => new Date(a.at) - new Date(b.at));
    for (const a of inTime) {
        if (a.variant?.startsWith("warmup:")) continue;   // warm-ups never change the plan
        const t = new Date(a.at).getTime();
        const s = states.get(a.gen) || { score: 0, level: 0, last: t, tries: 0, rights: 0, wrongs: 0, stuck: 0 };
        s.score = fade(s.score, s.last, t);
        s.tries++;
        s.last = t;
        if (a.correct) {
            const guess = isGuess(a.difficulty, a.seconds);
            s.score += guess ? SMALL_POINTS : RIGHT_POINTS[levelOf(a.difficulty, a.harder)];
            if (!guess) { s.level = Math.min(LEVELS.length - 1, s.level + 1); s.rights++; }
            s.stuck = 0;
        } else {
            s.score += a.second_try ? SMALL_POINTS : WRONG_POINTS;
            s.wrongs++;
            s.level = Math.max(0, s.level - 1);
            s.stuck++;                                       // wrong in a row: 2+ means warm-ups first
        }
        s.score = Math.max(0, Math.min(100, s.score));
        states.set(a.gen, s);
    }
    for (const s of states.values()) {
        s.score = Math.round(fade(s.score, s.last, now));
        // "needs work" only after real mistakes (a lucky or quick answer alone is just "getting there")
        s.status = s.score < NEEDS_WORK && s.wrongs > 0 ? "needs work"
            : s.score >= SOLID && s.rights >= SOLID_RIGHTS ? "solid" : "getting there";
        const weeksAway = (now - s.last) / (7 * DAY);
        s.weight = 1 + (100 - s.score) / 10 + Math.min(2, weeksAway);   // long unseen: a little more often
    }
    return states;
}

const shuffle = (xs) => { for (let i = xs.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [xs[i], xs[j]] = [xs[j], xs[i]]; } return xs; };
// Questions added to the pool recently are the ones the kids struggled with lately: up to twice as often,
// fading to normal over NEW_IN_POOL_DAYS days (g.added = when the generator was added, from bank/index.json).
const NEW_IN_POOL_DAYS = 60;
const poolBoost = (g, now = Date.now()) => g.added ? 1 + Math.max(0, 1 - (now - g.added) / (NEW_IN_POOL_DAYS * DAY)) : 1;
// A skill answered in the last RECENT_MINUTES (the session just before) is left out, so a second session
// started right after the first one practises other skills; such skills come back only to fill up.
const RECENT_MINUTES = 30, RECENT_FACTOR = 0.05;
const justPractised = (states, g, now = Date.now()) => (states.get(g.key)?.last ?? 0) > now - RECENT_MINUTES * 60e3;
const weightOf = (states, g) => (states.get(g.key)?.weight ?? NEW_WEIGHT) * poolBoost(g)
    * (justPractised(states, g) ? RECENT_FACTOR : 1);
const isWeak = (states, g) => states.get(g.key)?.status === "needs work";
const isStrong = (states, g) => (states.get(g.key)?.score ?? 0) >= 30;

/** Pick n items without putting one back, each with chance proportional to its weight. */
function weightedSample(items, weight, n) {
    const pool = items.map((x) => ({ x, w: Math.max(0.01, weight(x)) })), out = [];
    while (out.length < n && pool.length) {
        let r = Math.random() * pool.reduce((sum, p) => sum + p.w, 0);
        let i = pool.findIndex((p) => (r -= p.w) <= 0);
        if (i < 0) i = pool.length - 1;
        out.push(pool.splice(i, 1)[0].x);
    }
    return out;
}

/**
 * The skills for one session, in the order to ask them. Weak skills come up most often, but the session
 * stays encouraging: at most 3 "needs work" skills, never two of them in a row, it starts and ends with a
 * skill the child is good at (when there is one), and a weak skill may come back once in the same session.
 */
const MAX_WEAK = 3;
function planSkills(gens, states, n) {
    // weak skills just practised wait for a later session (they stay in `rest` with a tiny weight)
    const weak = gens.filter((g) => isWeak(states, g) && !justPractised(states, g));
    const rest = gens.filter((g) => !weak.includes(g));
    const pickedWeak = weightedSample(weak, (g) => weightOf(states, g), Math.min(MAX_WEAK, n));
    // skills from the session just before only when there are not enough others
    const restFresh = rest.filter((g) => !justPractised(states, g)), restRecent = rest.filter((g) => justPractised(states, g));
    const pickedRest = weightedSample(restFresh, (g) => weightOf(states, g), n - pickedWeak.length);
    pickedRest.push(...weightedSample(restRecent, (g) => weightOf(states, g), n - pickedWeak.length - pickedRest.length));
    // A weak skill may come twice (a second, different question), if there is room.
    const plan = [...pickedWeak, ...pickedRest];
    for (const g of pickedWeak) if (plan.length < n && !justPractised(states, g)) plan.push(g);
    while (plan.length < n && gens.length) plan.push(gens[Math.floor(Math.random() * gens.length)]);

    // Order (by position in the plan): a confident start and finish, weak ones spread out in the middle.
    const idx = plan.map((_, i) => i);
    const strongIdx = shuffle(idx.filter((i) => !isWeak(states, plan[i]) && isStrong(states, plan[i])));
    const firstI = strongIdx[0];
    const lastI = strongIdx.find((i) => i !== firstI && plan[i] !== plan[firstI]);
    const rest2 = shuffle(idx.filter((i) => i !== firstI && i !== lastI));
    const weakI = rest2.filter((i) => isWeak(states, plan[i])), calmI = rest2.filter((i) => !isWeak(states, plan[i]));
    const middle = [];
    while (weakI.length || calmI.length) {             // calm, weak, calm, weak, ...
        if (calmI.length) middle.push(calmI.shift());
        if (weakI.length) middle.push(weakI.shift());
    }
    const order = [firstI, ...middle, lastI].filter((i) => i !== undefined).map((i) => plan[i]);
    for (let k = 1; k < order.length; k++) {           // the same skill twice: keep them apart
        if (order[k] === order[k - 1]) {
            const m = order.findIndex((g, j) => j > k + 1 && g !== order[k] && order[j - 1] !== order[k]);
            if (m > 0) [order[k], order[m]] = [order[m], order[k]];
        }
    }
    return order.slice(0, n);
}

/** A child's answers from the database, oldest first (exam and parent pages; practice has DbStore). */
async function fetchAttempts(dbUrl, profileId) {
    const m = await import("https://cdn.jsdelivr.net/npm/@neondatabase/serverless@1.2.0/+esm");
    const sql = m.neon(dbUrl, { disableWarningInBrowsers: true });
    return sql`select question_id as id, gen, variant, difficulty, harder, chosen, correct, second_try, seconds,
                      created_at as at
               from attempts where profile_id = ${profileId} order by created_at, id`;
}
