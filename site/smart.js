// Personal practice logic, shared by the practice page and the exam page ("Exam for Deniz").
"use strict";

// Every child has their own state per skill (generator), replayed from their answers in time order:
//  - box: a review schedule. Wrong -> box 1 (back tomorrow); right -> next box. Box n is due GAP[n] days
//    after the last answer, so known skills come back less and less often.
//  - level: which questions to give. Right -> one level up for next time (Part A -> B -> C -> harder
//    numbers); wrong -> one level down, so a child never gets stuck on something too hard.
const DAY = 864e5, GAP = [0, 1, 3, 7, 21];
const LEVELS = [[1, false], [2, false], [3, false], [3, true]];     // [difficulty, harder]
// A right answer faster than this (seconds, by Part A/B/C) is probably a guess: it does not raise the level.
const MIN_SECONDS = { 1: 4, 2: 6, 3: 8 };
const isGuess = (difficulty, seconds) => seconds != null && seconds < (MIN_SECONDS[difficulty] ?? 4);

function skillStates(attempts) {
    const states = new Map();
    for (const a of attempts) {
        if (a.variant?.startsWith("warmup:")) continue;   // warm-ups never change the plan
        const s = states.get(a.gen) || { box: 0, level: 0, last: 0, tries: 0, stuck: 0 };
        s.tries++;
        s.last = new Date(a.at).getTime();
        if (a.correct) {
            s.box = Math.min(GAP.length - 1, s.box + 1);
            if (!isGuess(a.difficulty, a.seconds)) s.level = Math.min(LEVELS.length - 1, s.level + 1);
            s.stuck = 0;
        } else {
            s.box = 1;
            s.level = Math.max(0, s.level - 1);
            s.stuck++;                                       // wrong in a row: 2+ means warm-ups first
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

/** A child's answers from the database, oldest first (exam page; the practice page has DbStore). */
async function fetchAttempts(dbUrl, profileId) {
    const m = await import("https://cdn.jsdelivr.net/npm/@neondatabase/serverless@1.2.0/+esm");
    const sql = m.neon(dbUrl, { disableWarningInBrowsers: true });
    return sql`select question_id as id, gen, variant, difficulty, harder, chosen, correct, second_try, seconds,
                      created_at as at
               from attempts where profile_id = ${profileId} order by id`;
}
