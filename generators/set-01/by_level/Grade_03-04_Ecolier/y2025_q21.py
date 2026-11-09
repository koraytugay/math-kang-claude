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

from kangaroo import Fig, Question, numeric_choices, value_check, variant, warmup
from kangaroo.figures import row

META = {
    "source": "set-01/by_level/Grade_03-04_Ecolier/2025 Q21",
    "skill": "Closed loops: groups of neighbours can wrap around the start; recognise the same bracelet turned",
    "topics": ["patterns", "spatial", "logic"],
    "keywords": ["bracelet", "loops and neighbours"],
    "version": 4,
}

SHAPES = "CST"
NAME = {"C": "circle", "S": "square", "T": "triangle"}
PLURAL = {"C": "circles", "S": "squares", "T": "triangles"}
# Black-and-white printing: the shape tells the stones apart; fills are black / white / grey.
FILL = {"C": colors.Color(0.15, 0.15, 0.15), "S": colors.white, "T": colors.Color(0.65, 0.65, 0.65)}
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
    return "circles, squares and triangles"


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



# ------------------------------------------------------------------ teaching page
ORIGINAL = list("TSSCTCSTTCC")      # the contest bracelet, clockwise from the top


def _teach_strip(seq, extra=2):
    """The bracelet written in a row, the first stones copied again at the end, with the
    one-of-each groups bracketed underneath."""
    n = len(seq)
    row_ = seq + seq[:extra]
    good = [j for j in range(n) if set(window(seq, j, 3)) == set(SHAPES)]
    f = Fig(len(row_) * 1.2 + 0.6, 3.0, scale=26, margin=4)
    top = 2.3
    for i, k in enumerate(row_):
        x = 0.6 + 1.2 * i
        _stone(f, k, x, top, 0.4)
        f.text(x, top - 0.75, str(i % n + 1), size=9, italic=i >= n)
    xd = 0.6 + 1.2 * n - 0.6
    f.line((xd, 1.2), (xd, 2.9), dash=True, width=0.8)
    f.text(xd + 1.2, 2.95 - 0.1, "copied again", size=8, italic=True)
    levels = []
    for j in good:
        lvl = 0
        while any(abs(j - o) < 3 and l == lvl for o, l in levels):
            lvl += 1
        levels.append((j, lvl))
        y = 1.15 - 0.35 * lvl
        x0, x1 = 0.6 + 1.2 * j - 0.45, 0.6 + 1.2 * (j + 2) + 0.45
        f.polyline([(x0, y + 0.15), (x0, y), (x1, y), (x1, y + 0.15)], width=1.4)
    return f.drawing()


def teach():
    return [
        ("h", "How to think about it: bracelets (stones in a loop)"),
        "A bracelet is a <b>loop</b>: it has no first and no last stone. When you go around and come back to "
        "where you started, the last stone you read and the first one are <b>neighbours</b>.",
        bracelet(ORIGINAL, 95),
        ("h", "Trick 1: write it in a row, then copy the first stones again at the end"),
        "Start at any stone (here: the top one) and go clockwise, drawing each stone in a row. When you are back "
        "at the start, draw the first two stones <b>once more</b>. Now every group of 3 neighbours, also the one "
        "that goes across the start, is just 3 stones side by side in your row.",
        _teach_strip(ORIGINAL),
        "The brackets show the groups with one circle, one square and one triangle. There are 4 of them, and "
        "the last one goes <b>across the start</b> (stones 10, 11 and 1). That one is easy to miss!",
        ("h", "Trick 2: check each answer picture"),
        ("-", "<b>Count first.</b> Before: 4 circles, 3 squares, 4 triangles. Lisa takes away one of each, so the "
              "answer must have 3 circles, 2 squares and 3 triangles. Pictures with other numbers are out."),
        ("-", "<b>Counting is not enough!</b> Some pictures have the right numbers, but the stones taken away "
              "were not next to each other. You still have to compare the order."),
        ("-", "<b>Find a landmark</b>, a spot that is easy to see, such as two triangles side by side. Find it "
              "in both pictures and read clockwise from there. If every stone matches, it is the same "
              "bracelet, only turned."),
        ("h", "Watch out"),
        ("-", "Don't stop at the top: groups can go across the start."),
        ("-", "A turned bracelet is still the same bracelet. Always read clockwise in both pictures."),
        ("tip", "<b>Try it yourself:</b> lay coins, buttons or Lego bricks in a circle on the table. Take away "
                "three neighbours, close the gap and turn the circle a bit. Can you still find where the gap was?"),
    ]


# ------------------------------------------------------------------ warm-ups (small steps)
@warmup
def w_count(rng, harder):
    """Look closely: count one shape."""
    seq = random_bracelet(rng, rng.choice([8, 9, 10]))
    shape = rng.choice(SHAPES)
    ans = seq.count(shape)
    value = sum(1 for k in seq if k == shape)
    text = f"Look at this bracelet with {legend_text()}. How many {PLURAL[shape]} are on it?"
    sol = f"Put your finger on the top stone and go around once, counting the {PLURAL[shape]}: {ans}."
    choices, ai = numeric_choices(ans, [ans - 1, ans + 1, len(seq) - ans, len(seq)], rng, lo=1, order="asc")
    return Question(text=text, figure=bracelet(seq, 100), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, value))


@warmup
def w_row_of_three(rng, harder):
    """Three neighbours in a row - the group across the top."""
    from itertools import product
    seq = random_bracelet(rng, 8)
    n = len(seq)
    j = rng.choice([n - 2, n - 1])                    # a group that goes across the top
    right = tuple(window(seq, j, 3))
    cw = {tuple(window(seq, i, 3)) for i in range(n)}
    acw = {tuple(window(seq[::-1], i, 3)) for i in range(n)}
    pool = [t for t in product(SHAPES, repeat=3) if t not in cw | acw]
    same_stones = [t for t in pool if sorted(t) == sorted(right)]
    rng.shuffle(pool)
    wrong = (same_stones + [t for t in pool if t not in same_stones])[:4]
    opts = wrong + [right]
    rng.shuffle(opts)
    text = (f"Going <b>clockwise</b> around this bracelet, which three stones come one after another? "
            f"(Read each answer from left to right.)")
    sol = ("Go around clockwise and look at every group of 3 neighbours. The right group goes across the "
           "top: the last stone(s) before the top and the first one(s) after it.")
    return Question(text=text, figure=bracelet(seq, 100), choices=["".join(o) for o in opts],
                    choice_figures=[strip(o, size=14) for o in opts], answer=opts.index(right), solution=sol,
                    check=lambda i: tuple(opts[i]) in cw)


@warmup
def w_groups_count(rng, harder):
    """A loop of n stones has n groups of 3 neighbours (not n - 2)."""
    seq = random_bracelet(rng, rng.choice([7, 8, 9]))
    n = len(seq)
    text = (f"This bracelet has {n} stones. How many different groups of 3 <b>neighbouring</b> stones are "
            f"there? (Don't forget the groups that go across the top.)")
    sol = (f"Every stone starts one group: that stone and the next two, going clockwise. "
           f"{n} stones, so {n} groups. In a straight row there would only be {n - 2}.")
    runs = {frozenset((s + t) % n for t in range(3)) for s in range(n)}
    value = sum(1 for c in combinations(range(n), 3) if frozenset(c) in runs)
    choices, ai = numeric_choices(n, [n - 2, n - 1, n // 3, n + 1, 3], rng, lo=1, order="asc")
    return Question(text=text, figure=bracelet(seq, 100), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, value))


@warmup
def w_remove_one(rng, harder):
    """Take away the only square: which bracelet is left (turned)?"""
    while True:
        n = 9
        seq = [rng.choice("CT") for _ in range(n - 1)]
        seq.insert(rng.randrange(n), "S")
        if seq.count("C") >= 3 and seq.count("T") >= 3:
            break
    name = rng.choice(NAMES)
    sq = seq.index("S")
    answer = remove_at(seq, {sq})
    wrong = {}
    for d in (1, 2, 3):                              # the right stones, two of them swapped
        for i in range(n - 1):
            r = list(answer)
            r[i], r[(i + d) % (n - 1)] = r[(i + d) % (n - 1)], r[i]
            if canon(r) != canon(answer):
                wrong.setdefault(canon(r), tuple(r))
    wl = list(wrong.values())
    if len(wl) < 4:
        return w_remove_one(rng, harder)
    opts = [turned(rng, answer)] + [turned(rng, w) for w in rng.sample(wl, 4)]
    rng.shuffle(opts)
    ai = [canon(o) for o in opts].index(canon(answer))
    text = f"{name} takes the square off this bracelet and closes the gap. Which bracelet is left?"
    sol = ("The other stones stay in the same order. Find a landmark (for example two equal stones side by side) "
           f"and read clockwise: only {'ABCDE'[ai]} matches, turned a bit.")

    def ok(i):
        squares = [k for k, s_ in enumerate(seq) if s_ == "S"]
        return len(squares) == 1 and canon(remove_at(seq, set(squares))) == canon(opts[i])
    return Question(text=text, figure=bracelet(seq, 95), choices=["".join(canon(o)) for o in opts],
                    choice_figures=[bracelet(o, 66) for o in opts], answer=ai, solution=sol, check=ok)


@warmup
def w_turned(rng, harder):
    """Same bracelet, only turned - with just 6 stones."""
    while True:
        seq = list(rng.choice(["CCSTTS", "CSSTCT", "CCTSTS", "CTTSCS", "CSTTSC"]))
        rng.shuffle(seq)
        if len({canon(r) for r in rotations(seq)}) == 1 and len(set(rotations(seq))) == 6:
            break
    n = len(seq)
    ans = turned(rng, seq)
    wrong = {}
    for i in range(n):
        r = list(ans)
        r[i], r[(i + 1) % n] = r[(i + 1) % n], r[i]
        if canon(r) != canon(seq):
            wrong.setdefault(canon(r), tuple(r))
    if len(wrong) < 4:
        return w_turned(rng, harder)
    opts = [ans] + rng.sample(list(wrong.values()), 4)
    rng.shuffle(opts)
    ai = opts.index(ans)
    text = "Which picture shows the same bracelet, only turned?"
    sol = (f"Find a landmark in the bracelet (for example two equal stones side by side) and read clockwise "
           f"from there. Only {'ABCDE'[ai]} matches all 6 stones.")
    return Question(text=text, figure=bracelet(seq, 90), choices=["".join(canon(o)) for o in opts],
                    choice_figures=[bracelet(o, 66) for o in opts], answer=ai, solution=sol,
                    check=lambda i: tuple(opts[i]) in {tuple(r) for r in rotations(seq)})
