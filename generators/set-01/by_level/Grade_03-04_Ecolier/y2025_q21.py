"""2025 Q21 (Ecolier, Grade 3-4) - a bracelet of stones: take away neighbouring stones.

Original: the picture shows a bracelet with 11 circular, square and triangular gemstones
(clockwise from the top: triangle, square, square, circle, triangle, circle, square,
triangle, triangle, circle, circle). Lisa removes three neighbouring stones, one of
each shape. What bracelet can be created?  (Five bracelets of 8 stones, A-E.)
The groups "square, circle, triangle", "triangle, circle, square", "circle, square,
triangle" and the group across the top "circle, triangle, square" are the only ones
with one stone of each shape; only one of the five pictures is what is left after
taking one of them away (the pictures are turned).

Core skill: reading a closed loop - the stones go round and round, so a group of
neighbours can run across the "start" - and recognising the same bracelet after it is
turned. Pictures with the right number of each shape are traps: the removed stones
must also have been next to each other.
"""
from collections import Counter
from itertools import combinations

from reportlab.lib import colors

from kangaroo import Fig, Question, numeric_choices, value_check, variant
from kangaroo.figures import row

META = {
    "source": "set-01/by_level/Grade_03-04_Ecolier/2025 Q21",
    "skill": "Closed loops: groups of neighbours can wrap around the start; recognise the same bracelet turned",
    "topics": ["patterns", "spatial", "logic"],
    "version": 1,
}

SHAPES = "CST"
NAME = {"C": "circle", "S": "square", "T": "triangle"}
PLURAL = {"C": "circles", "S": "squares", "T": "triangles"}
FILL = {"C": colors.Color(0.87, 0.24, 0.22), "S": colors.Color(0.22, 0.68, 0.36),
        "T": colors.Color(0.15, 0.62, 0.87)}
NAMES = ["Lisa", "Mia", "Tom", "Anna", "Ben", "Sara", "Leo"]


# ------------------------------------------------------------------ loops
def rotations(seq):
    return [tuple(seq[i:] + seq[:i]) for i in range(len(seq))]


def canon(seq):
    """Same key for a bracelet turned or flipped over."""
    seq = list(seq)
    return min(rotations(seq) + rotations(seq[::-1]))


def window(seq, j, m):
    n = len(seq)
    return [seq[(j + t) % n] for t in range(m)]


def remove_run(seq, j, m):
    """Take away the m neighbours starting at position j; the rest, in order."""
    n = len(seq)
    return tuple(seq[(j + m + t) % n] for t in range(n - m))


def remove_at(seq, positions):
    return tuple(s for i, s in enumerate(seq) if i not in positions)


def can_make(seq, target, need: Counter):
    """Answer check: try every group of len(need) neighbours (also across the top)."""
    m = sum(need.values())
    n = len(seq)
    for start in range(n):
        idx = [(start + t) % n for t in range(m)]
        if Counter(seq[i] for i in idx) == need and canon(remove_at(seq, set(idx))) == canon(target):
            return True
    return False


def random_bracelet(rng, n):
    """No three equal stones in a row (also around the top), at least 2 of each shape."""
    while True:
        seq = [rng.choice(SHAPES) for _ in range(n)]
        if (all(seq.count(s) >= 2 for s in SHAPES)
                and not any(len(set(window(seq, j, 3))) == 1 for j in range(n))):
            return seq


def turned(rng, seq):
    seq = list(seq)
    r = rng.randrange(1, len(seq)) if len(seq) > 1 else 0
    return tuple(seq[r:] + seq[:r])


# ------------------------------------------------------------------ pictures
def _stone(f, kind, x, y, h):
    if kind == "C":
        f.circle(x, y, h, fill=FILL["C"], width=0.6)
    elif kind == "S":
        f.rect(x - h * 0.9, y - h * 0.9, 1.8 * h, 1.8 * h, fill=FILL["S"], width=0.6)
    else:
        f.poly([(x - h * 1.05, y - h * 0.8), (x + h * 1.05, y - h * 0.8), (x, y + h)], fill=FILL["T"], width=0.6)


def bracelet(seq, size=100):
    """Stones evenly spaced on a ring, the first one at the top, then clockwise."""
    import math
    n = len(seq)
    R = 1.0
    h = min(0.2, 1.15 * math.pi / n * 0.55)
    c = R + h + 0.05
    f = Fig(2 * c, 2 * c, scale=size / (2 * c), margin=2)
    f.arc(c, c, R, 0, 360, width=0.8)
    for i, kind in enumerate(seq):
        a = math.radians(90 - 360 * i / n)
        _stone(f, kind, c + R * math.cos(a), c + R * math.sin(a), h)
    return f.drawing()


def strip(kinds, size=12):
    f = Fig(1.2 * len(kinds), 1.2, scale=size / 1.2 * 1.0, margin=2)
    for i, k in enumerate(kinds):
        _stone(f, k, 0.6 + 1.2 * i, 0.6, 0.45)
    return f.drawing()


def arrow_pic():
    f = Fig(1.6, 1.0, scale=16, margin=2)
    f.line((0, 0.5), (1.3, 0.5), width=1.4)
    f.poly([(1.6, 0.5), (1.2, 0.72), (1.2, 0.28)], fill=colors.black, width=0.6)
    return f.drawing()


def legend_text():
    return "circles (red), squares (green) and triangles (blue)"


# ------------------------------------------------------------------ "which bracelet can she make?"
def _remove_question(rng, n_range, need: Counter, how: str, name: str):
    """Build options: one result of taking away a group of neighbours with `need` stones;
    wrong ones = same stones but not neighbours, a wrong group of neighbours, two stones swapped."""
    m = sum(need.values())
    for _ in range(500):
        seq = random_bracelet(rng, rng.choice(n_range))
        n = len(seq)
        good = [j for j in range(n) if Counter(window(seq, j, m)) == need]
        if not good:
            continue
        valid = {canon(remove_run(seq, j, m)) for j in range(n) if Counter(window(seq, j, m)) == need}
        j = rng.choice(good)
        answer = remove_run(seq, j, m)
        same_count, other = {}, {}
        # same stones, but not all neighbours
        for pos in combinations(range(n), m):
            if Counter(seq[i] for i in pos) != need:
                continue
            r = remove_at(seq, set(pos))
            if canon(r) not in valid:
                same_count.setdefault(canon(r), r)
        # a group of neighbours with the wrong stones
        for jj in range(n):
            if Counter(window(seq, jj, m)) != need:
                r = remove_run(seq, jj, m)
                if canon(r) not in valid:
                    other.setdefault(canon(r), r)
        # the right result with two neighbouring stones swapped
        for i in range(n - m):
            r = list(answer)
            i2 = (i + 1) % (n - m)
            r[i], r[i2] = r[i2], r[i]
            if canon(r) not in valid:
                same_count.setdefault(canon(r), tuple(r))
        sc, ot = list(same_count.values()), list(other.values())
        if len(sc) < 3 or len(sc) + len(ot) < 4:
            continue
        k_same = min(len(sc), rng.choice([3, 4]) if ot else 4)
        wrong = rng.sample(sc, k_same) + rng.sample(ot, 4 - k_same)
        opts = [turned(rng, answer)] + [turned(rng, w) for w in wrong]
        rng.shuffle(opts)
        ai = [canon(o) for o in opts].index(canon(answer))
        group = ", ".join(NAME[s] for s in window(seq, j, m))
        sol = (f"Go around the bracelet and look at every group of {m} neighbours (also the ones across the "
               f"top). Taking away the group {group} leaves the bracelet in {'ABCDE'[ai]}, turned a bit. "
               f"The other pictures need stones that were not next to each other, or other stones.")
        text = (f"The picture shows a bracelet with {legend_text()}. {name} removes {how}. "
                f"Which bracelet can {name} get?")
        return Question(text=text, figure=bracelet(seq, 105), choices=["".join(canon(o)) for o in opts],
                        choice_figures=[bracelet(o, 70) for o in opts], answer=ai, solution=sol,
                        check=lambda i: can_make(seq, opts[i], need))
    raise RuntimeError("no bracelet found")


@variant(difficulty=1)
def remove_three(rng, harder):
    """The original: three neighbouring stones, one of each shape."""
    return _remove_question(rng, [11, 12] if harder else [9, 10], Counter("CST"),
                            "three neighbouring stones, one of each shape", rng.choice(NAMES))


@variant(difficulty=1)
def remove_two(rng, harder):
    """Two neighbouring stones of two given shapes (or three with two the same, when harder)."""
    if harder:
        a, b = rng.sample(SHAPES, 2)
        need = Counter({a: 2, b: 1})
        how = f"three neighbouring stones: two {PLURAL[a]} and one {NAME[b]}"
        n_range = [10, 11]
    else:
        a, b = rng.sample(SHAPES, 2)
        need = Counter({a: 1, b: 1})
        how = f"two neighbouring stones: one {NAME[a]} and one {NAME[b]}"
        n_range = [8, 9]
    return _remove_question(rng, n_range, need, how, rng.choice(NAMES))


# ------------------------------------------------------------------ same bracelet, turned
@variant(difficulty=2)
def same_bracelet(rng, harder):
    """Which picture shows the same bracelet, just turned?"""
    name = rng.choice(NAMES)
    for _ in range(500):
        seq = random_bracelet(rng, rng.choice([10, 11] if harder else [8, 9]))
        n = len(seq)
        key = canon(seq)
        ans = turned(rng, seq)
        wrong = {}
        for i in range(n):
            for d in (1, 2) if harder else (1,):
                r = list(ans)
                r[i], r[(i + d) % n] = r[(i + d) % n], r[i]
                if canon(r) != key:
                    wrong.setdefault(canon(r), tuple(r))
        if len(wrong) < 4:
            continue
        opts = [ans] + rng.sample(list(wrong.values()), 4)
        rng.shuffle(opts)
        ai = opts.index(ans)
        text = (f"{name} has this bracelet with {legend_text()} and turns it around a bit. "
                f"Which picture can show the bracelet now?")
        sol = (f"Pick a special spot (for example a pair of equal stones) and read the stones in order from "
               f"there, going around. Only {'ABCDE'[ai]} has all {n} stones in the same order; in the others "
               f"two stones have swapped places.")
        return Question(text=text, figure=bracelet(seq, 100), choices=["".join(canon(o)) for o in opts],
                        choice_figures=[bracelet(o, 70) for o in opts], answer=ai, solution=sol,
                        check=lambda i: any(tuple(r) == tuple(opts[i]) for r in rotations(seq)))
    raise RuntimeError("no bracelet found")


# ------------------------------------------------------------------ which stones were taken away?
@variant(difficulty=2)
def which_removed(rng, harder):
    """Before and after pictures: which neighbouring stones were removed?"""
    m = 4 if harder else 3
    name = rng.choice(NAMES)
    seq = random_bracelet(rng, rng.choice([11, 12] if harder else [9, 10]))
    n = len(seq)
    j = rng.randrange(n)
    removed = Counter(window(seq, j, m))
    after = turned(rng, remove_run(seq, j, m))
    groups = sorted({tuple(sorted(c)) for c in combinations(SHAPES * m, m)})
    right = tuple(sorted(removed.elements()))
    def dist(g):
        return sum((Counter(g) - Counter(right)).values())
    others = sorted((g for g in groups if g != right), key=lambda g: (dist(g), rng.random()))
    opts = others[:4] + [right]
    rng.shuffle(opts)
    ai = opts.index(right)
    text = (f"{name} takes away {m} neighbouring stones from the bracelet on the left. "
            f"Then the bracelet looks like the one on the right. Which stones did {name} take away?")
    before_n = Counter(seq)
    after_n = Counter(after)
    parts = [f"{before_n[s] - after_n[s]} {NAME[s] if before_n[s] - after_n[s] == 1 else PLURAL[s]}"
             for s in SHAPES if before_n[s] - after_n[s]]
    sol = (f"Count each shape before and after: " +
           ", ".join(f"{PLURAL[s]} {before_n[s]} → {after_n[s]}" for s in SHAPES) +
           f". So {name} took away {', '.join(parts[:-1]) + ' and ' + parts[-1] if len(parts) > 1 else parts[0]}.")
    fig = row([bracelet(seq, 95), arrow_pic(), bracelet(after, 85)], gap=10)
    return Question(text=text, figure=fig, choices=["".join(o) for o in opts],
                    choice_figures=[strip(o) for o in opts], answer=ai, solution=sol,
                    check=lambda i: can_make(seq, after, Counter(opts[i])))


# ------------------------------------------------------------------ counting groups around a loop
@variant(difficulty=3)
def count_places(rng, harder):
    """How many groups of three neighbours have one stone of each shape? (Some go across the top.)"""
    name = rng.choice(NAMES)
    while True:
        seq = random_bracelet(rng, rng.choice([12, 13] if harder else [10, 11]))
        n = len(seq)
        ans = sum(1 for j in range(n) if set(window(seq, j, 3)) == set(SHAPES))
        straight = sum(1 for j in range(n - 2) if len(set(seq[j:j + 3])) == 3)
        if ans >= 2 and ans > straight:      # at least one group goes across the top
            break
    text = (f"{name} has this bracelet with {legend_text()} and wants to take away three "
            f"<b>neighbouring</b> stones, one of each shape. In how many different places of the bracelet "
            f"is this possible?")
    sol = (f"Go once around the bracelet and look at each group of 3 neighbours. Don't forget the "
           f"group{'s' if ans - straight > 1 else ''} across the top: {ans - straight} of them. In all {ans}.")
    choices, ai = numeric_choices(ans, [straight, ans + 1, ans - 1, n // 3, ans + 2], rng, lo=1, order="asc")
    # check: every set of 3 positions that sit next to each other around the loop
    runs = {frozenset(((s + t) % n) for t in range(3)) for s in range(n)}
    value = sum(1 for pos in combinations(range(n), 3)
                if frozenset(pos) in runs and {seq[i] for i in pos} == set(SHAPES))
    return Question(text=text, figure=bracelet(seq, 110), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, value))


# ------------------------------------------------------------------ reversed: which can NOT be made?
@variant(difficulty=3)
def cannot_make(rng, harder):
    """Four of the pictures can be made, one cannot."""
    name = rng.choice(NAMES)
    need = Counter("CST")
    for _ in range(2000):
        seq = random_bracelet(rng, rng.choice([11, 12] if harder else [10, 11]))
        n = len(seq)
        valid = {}
        for j in range(n):
            if Counter(window(seq, j, 3)) == need:
                r = remove_run(seq, j, 3)
                valid.setdefault(canon(r), r)
        if len(valid) < 4:
            continue
        traps = {}
        for pos in combinations(range(n), 3):
            if Counter(seq[i] for i in pos) == need:
                r = remove_at(seq, set(pos))
                if canon(r) not in valid:
                    traps.setdefault(canon(r), r)
        if not traps:
            continue
        bad = rng.choice(list(traps.values()))
        opts = [turned(rng, r) for r in rng.sample(list(valid.values()), 4)] + [turned(rng, bad)]
        rng.shuffle(opts)
        ai = [canon(o) for o in opts].index(canon(bad))
        text = (f"The picture shows a bracelet with {legend_text()}. {name} removes three neighbouring "
                f"stones, one of each shape. Which bracelet can {name} <b>not</b> get?")
        sol = (f"Find all groups of 3 neighbours with one stone of each shape (also across the top) and "
               f"take each one away. {'ABCDE'[ai]} has the right stones, but they were not next to each other.")
        return Question(text=text, figure=bracelet(seq, 105), choices=["".join(canon(o)) for o in opts],
                        choice_figures=[bracelet(o, 70) for o in opts], answer=ai, solution=sol,
                        check=lambda i: not can_make(seq, opts[i], need))
    raise RuntimeError("no bracelet found")
