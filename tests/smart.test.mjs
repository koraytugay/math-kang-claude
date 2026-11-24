// Tests for site/smart.js (scoring, rungs, session planning).   Run:  node --test tests/
// smart.js is a plain browser script (no exports), so it is loaded into a vm context here.
import test from "node:test";
import assert from "node:assert/strict";
import vm from "node:vm";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const src = readFileSync(fileURLToPath(new URL("../site/smart.js", import.meta.url)), "utf8");
const { skillStates, planSkills, setRungs, rungOf, DAY } = vm.runInNewContext(
    src + "\n({ skillStates, planSkills, setRungs, rungOf, DAY })", { console });

const T0 = Date.parse("2026-11-01T10:00:00Z");
// one answer; defaults: a right Part A answer in 20 seconds
const ans = (o = {}) => ({ gen: "g1", variant: "v", difficulty: 1, harder: false, correct: true, second_try: null,
    seconds: 20, at: new Date(T0).toISOString(), ...o });
const at = (days, minutes = 0) => new Date(T0 + days * DAY + minutes * 60e3).toISOString();
const state = (attempts, now) => skillStates(attempts, now).get("g1");

test("right Part A answer: +15 points, one rung up from the aligned start", () => {
    const s = state([ans()], T0);
    assert.equal(s.score, 15);
    assert.equal(s.level, 2);
    assert.equal(s.rights, 1);
});

test("points grow with the part: B +20, C +25, C harder +30", () => {
    assert.equal(state([ans({ difficulty: 2 })], T0).score, 20);
    assert.equal(state([ans({ difficulty: 3 })], T0).score, 25);
    assert.equal(state([ans({ difficulty: 3, harder: true })], T0).score, 30);
});

test("a too-fast right answer is a guess: +5 and the rung does not move", () => {
    const s = state([ans({ seconds: 2 })], T0);
    assert.equal(s.score, 5);
    assert.equal(s.level, 1);
    assert.equal(s.rights, 0);
});

test("wrong answer: -20 (never below 0) and one rung down, never below 0", () => {
    const s = state([ans({ correct: false }), ans({ correct: false, at: at(0, 1) })], T0 + 60e3);
    assert.equal(s.score, 0);
    assert.equal(s.level, 0);
    assert.equal(s.wrongs, 2);
    assert.equal(s.status, "needs work");
});

test("wrong first, right on the second try counts +5 (not -20)", () => {
    const s = state([ans({ difficulty: 2 }), ans({ correct: false, second_try: true, at: at(0, 1) })], T0 + 60e3);
    assert.equal(s.score, 25);                 // 20 + 5
    assert.equal(s.level, 1);                  // up one (right), down one (wrong)
});

test("the rung stops at the top (2)", () => {
    const rights = [0, 1, 2, 3, 4].map((i) => ans({ at: at(0, i) }));
    assert.equal(state(rights, T0 + 5 * 60e3).level, 2);
});

test("warm-up answers never change the state", () => {
    const states = skillStates([ans({ variant: "warmup:x", correct: false })], T0);
    assert.equal(states.size, 0);
});

test("answers are replayed in time order, whatever the row order", () => {
    const early = ans({ correct: false, at: at(0) }), late = ans({ difficulty: 2, at: at(0, 5) });
    const a = state([early, late], T0 + 10 * 60e3), b = state([late, early], T0 + 10 * 60e3);
    assert.equal(a.score, b.score);
    assert.equal(a.level, b.level);
});

test("the score does not fade in the first week, then loses ~10% per week", () => {
    const one = [ans({ difficulty: 3, harder: true })];      // 30 points
    assert.equal(state(one, T0 + 7 * DAY).score, 30);
    assert.equal(state(one, T0 + 14 * DAY).score, 27);       // 30 * 0.9
    assert.equal(state(one, T0 + 21 * DAY).score, 24);       // 30 * 0.81 = 24.3
});

test("status: solid needs 60+ AND 3 real rights; 'needs work' needs a real mistake", () => {
    const hard = (m) => ans({ difficulty: 3, harder: true, at: at(0, m) });
    assert.equal(state([hard(0), hard(1)], T0 + 120e3).status, "getting there");        // 60 points, only 2 rights
    assert.equal(state([hard(0), hard(1), hard(2)], T0 + 180e3).status, "solid");        // 90 points, 3 rights
    assert.equal(state([ans({ seconds: 1 })], T0).status, "getting there");              // no mistake, low score
    assert.equal(state([ans({ correct: false })], T0).status, "needs work");
});

test("weight: weak skills come more often than mastered ones, but never zero", () => {
    const weak = state([ans({ correct: false })], T0), solid = skillStates(
        [0, 1, 2, 3].map((m) => ans({ difficulty: 3, harder: true, at: at(0, m) })), T0 + 240e3).get("g1");
    assert.ok(weak.weight > solid.weight * 5, `${weak.weight} vs ${solid.weight}`);
    assert.ok(solid.weight > 0);
});

test("rungOf: per-variant rating wins over the per-step rating over the default", () => {
    setRungs([{ key: "a", rungs: [0, 1, 2, 2], vr: { odd: [2, 2] } }, { key: "b" }]);
    assert.equal(rungOf("a", 1, false, "plain"), 0);
    assert.equal(rungOf("a", 3, true, "plain"), 2);
    assert.equal(rungOf("a", 1, false, "odd"), 2);
    assert.equal(rungOf("b", 2, false, "x"), 1);             // default rungs [1, 1, 2, 2]
});

// ---------------------------------------------------------------- planSkills
const gens = Array.from({ length: 30 }, (_, i) => ({ key: `s${i}` }));
const weakAnswers = (key, m) => ({ ...ans({ gen: key, correct: false }), at: at(0, m) });
const rightAnswers = (key) => [0, 1, 2].map((m) => ({ ...ans({ gen: key, difficulty: 3, harder: true }), at: at(0, m) }));

test("planSkills: always n skills, no skill twice in a row, few weak skills, never two weak ones together", () => {
    // 10 weak skills and 10 solid ones, practised 2 days ago
    const attempts = [
        ...gens.slice(0, 10).flatMap((g, i) => weakAnswers(g.key, i)),
        ...gens.slice(10, 20).flatMap((g) => rightAnswers(g.key)),
    ];
    const now = T0 + 2 * DAY;
    const states = skillStates(attempts, now);
    for (let run = 0; run < 200; run++) {
        const plan = planSkills(gens, states, 10);
        assert.equal(plan.length, 10);
        for (let k = 1; k < plan.length; k++) assert.notEqual(plan[k], plan[k - 1], "same skill twice in a row");
        const weakPlaces = plan.filter((g) => states.get(g.key)?.status === "needs work");
        assert.ok(weakPlaces.length <= 4, `too many weak skills: ${weakPlaces.length}`);     // 3 + one that may come back
        for (let k = 1; k < plan.length; k++)
            assert.ok(!(states.get(plan[k].key)?.status === "needs work" && states.get(plan[k - 1].key)?.status === "needs work"),
                "two weak skills in a row");
    }
});

test("planSkills: owed (studied) skills come in the first 3 places, at most 3 of them", () => {
    const states = new Map();
    for (let run = 0; run < 200; run++) {
        for (const owedCount of [1, 2, 3, 5]) {
            const owed = gens.slice(20, 20 + owedCount);
            const plan = planSkills(gens, states, 10, owed);
            assert.equal(plan.length, 10);
            const firstThree = plan.slice(0, 3);
            for (const g of owed.slice(0, 3)) assert.ok(firstThree.includes(g), `${g.key} not in the first 3`);
            if (owedCount > 3) for (const g of owed.slice(3)) assert.ok(!firstThree.includes(g), "a 4th owed skill jumped the queue");
        }
    }
});

test("planSkills: with one owed skill, place 1 stays a different skill (the child's good one)", () => {
    const states = new Map();
    for (let run = 0; run < 100; run++) {
        const owed = [gens[7]];
        assert.notEqual(planSkills(gens, states, 10, owed)[0], gens[7]);
    }
});
