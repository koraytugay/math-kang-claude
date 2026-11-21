"""2026 Q16 (Canada, Grade 3-4) - a coloured paper strip that is folded, cut and folded again.

Original: Maya has a paper strip of 8 squares, which she colors. When she folds it in half, the
matching squares line up in the same color. After she cuts off two squares from one end and folds
the rest in half, the matching squares still line up in the same color. What is the greatest number
of different colors the strip could have?  (A) 2  (B) 1  (C) 4  (D) 3  (E) 5.
Squares 1..8. First fold matches 1-8, 2-7, 3-6, 4-5. Cut off 1 and 2; the rest (3..8) folds:
3-8, 4-7, 5-6. Chain: 1=8=3=6=5=4=7=2, so every square has the same colour: 1 colour.  Answer: B.
(The 2026 key in the repo is our own, solved by us - not official.)

Core skill: matching squares must have the same colour, so link them. Every link joins two squares into
one group; the colours you can use at most are the number of groups after ALL the folds. Children count
the pairs of the first fold only (4 colours) or forget that the second fold links the groups together.

How it works: a fold of the part a..b matches i with a+b-i. The answer is built with union-find on those
pairs. The check folds the strip as a real object (squares that land on the same place), then tries every
colouring (backtracking) and takes the one with the most colours.
"""
from kangaroo import Fig, Question, numeric_choices, value_check, variant

META = {
    "source": "set-03/by_level/Grade_03-04/2026 Q16",
    "skill": "Matching squares must have the same colour: write down the pairs of every fold, link the pairs "
             "that share a square, and count the groups that are left",
    "topics": ["logic", "patterns", "spatial"],
    "keywords": ["folded strip", "matching squares", "colour groups"],
    "sticker": ("🎀", "Ribbon folder"),   # earned when this skill is solid (website)
    "version": 1,
}

PEOPLE = ["Maya", "Mia", "Lena", "Nora", "Sara", "Ella", "Zoe", "Ivy"]  # all "she" in the texts


# ------------------------------------------------------------------ the model (the answer)
def fold_pairs(a, b):
    """Squares a..b (1-based) folded in half: i is matched with a+b-i."""
    return [(i, a + b - i) for i in range(a, (a + b + 1) // 2)]


def intervals(n, cuts):
    """The parts that are folded: the whole strip, then what is left after each cut from the left end."""
    out, start = [(1, n)], 1
    for k in cuts:
        start += k
        out.append((start, n))
    return out


def groups(n, cuts):
    """Union-find on all the matching pairs: the groups of squares that must share a colour."""
    parent = list(range(n + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in intervals(n, cuts):
        for i, j in fold_pairs(a, b):
            parent[find(i)] = find(j)
    out = {}
    for i in range(1, n + 1):
        out.setdefault(find(i), []).append(i)
    return sorted(out.values())


# ------------------------------------------------------------------ the check (independent)
def _landing_pairs(n, cuts):
    """Fold the strip for real: squares that land on the same spot match. (0-based positions.)"""
    pairs, lo = [], 0
    for step in [0] + list(cuts):
        lo += step
        spots = {}
        for x in range(lo, n):
            spots.setdefault(min(x - lo, n - 1 - x), []).append(x)
        pairs += [tuple(v) for v in spots.values() if len(v) == 2]
    return pairs


def best_colouring(n, cuts):
    """Try colourings left to right (new colours numbered in order); the most colours that obey every pair."""
    pairs = _landing_pairs(n, cuts)
    partner = {x: [] for x in range(n)}
    for p, q in pairs:
        partner[max(p, q)].append(min(p, q))
    best = [0, None]
    col = [0] * n

    def go(x, used):
        if used + (n - x) <= best[0]:
            return
        if x == n:
            best[0], best[1] = used, col[:]
            return
        forced = {col[p] for p in partner[x]}
        if len(forced) > 1:
            return
        options = forced or set(range(used + 1))
        for c in sorted(options, reverse=True):
            col[x] = c
            go(x + 1, max(used, c + 1))

    go(0, 0)
    return best


def check_colours(n, cuts):
    return best_colouring(n, cuts)[0]


def check_with_first(n, cuts):
    _, col = best_colouring(n, cuts)
    return sum(c == col[0] for c in col)


# ------------------------------------------------------------------ picture and text
def strip_pic(n, max_px=250):
    f = Fig(n, 1, max_px=max_px, margin=8)
    for i in range(n):
        f.rect(i, 0, 1, 1, fill=None, width=1.2)
        f.text(i + 0.5, 0.5, str(i + 1), size=10)
    return f.drawing()


def _intro(name, n):
    return (f"{name} has a paper strip of {n} squares, numbered 1 to {n}, which she colours. "
            "When she folds it in half, the matching squares line up in the same colour.")


def _cut_text(name, k, which="one end", more=False):
    words = {2: "two", 4: "four", 6: "six", 8: "eight", 10: "ten", 12: "twelve", 14: "fourteen"}
    w = words.get(k, str(k))
    extra = " more" if more else ""
    return f"cuts off {w}{extra} squares from {which}"


def _pairs_text(a, b):
    return ", ".join(f"{i} with {j}" for i, j in fold_pairs(a, b))


def _explain(n, cuts):
    parts = []
    for step, (a, b) in enumerate(intervals(n, cuts)):
        what = "Folding the whole strip" if step == 0 else f"Folding squares {a} to {b}"
        parts.append(f"{what} matches {_pairs_text(a, b)}.")
    gs = groups(n, cuts)
    shown = ", ".join("{" + ", ".join(map(str, g)) + "}" for g in gs)
    if len(gs) == 1:
        tail = "Matching squares share a colour and the pairs link up into one group, so every square has the same colour."
    else:
        tail = (f"Matching squares share a colour, and the pairs link up into {len(gs)} groups: {shown}. "
                f"Each group can have its own colour.")
    return " ".join(parts) + " " + tail


def _colour_mistakes(n, cuts):
    first = len(fold_pairs(1, n))
    last = len(fold_pairs(*intervals(n, cuts)[-1]))
    return [(first, "count only the pairs of the first fold"),
            (last, "count only the pairs of the last fold"),
            (first + last, "add the pairs of the folds, but forget that they link up"),
            (n, "give every square its own colour")]


# ------------------------------------------------------------------ variants
@variant(difficulty=1)
def original(rng, harder):
    """The original: fold, cut off two squares, fold again: the most colours?"""
    n = rng.choice([10, 12] if harder else [8, 10])
    name = rng.choice(PEOPLE)
    cuts = [2]
    ans = len(groups(n, cuts))
    text = (_intro(name, n) + f" After she {_cut_text(name, 2)} and folds the rest in half, the matching squares "
            "still line up in the same colour.\n\nWhat is the greatest number of different colours the strip could have?")
    sol = _explain(n, cuts) + (f" Here {name} cut off squares 1 and 2 (the other end works the same way): "
                               f"at most {ans} colour{'s' if ans != 1 else ''}.")
    choices, ai = numeric_choices(ans, _colour_mistakes(n, cuts), rng, lo=1, order="asc")
    return Question(text=text, figure=strip_pic(n), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, check_colours(n, cuts)))


@variant(difficulty=2)
def bigger_cut(rng, harder):
    """She cuts off more squares: fewer links, more colours possible."""
    n, k = rng.choice([(12, 4), (12, 6), (12, 8), (16, 8)] if harder else [(8, 4), (8, 6), (12, 6)])
    name = rng.choice(PEOPLE)
    ans = len(groups(n, [k]))
    text = (_intro(name, n) + f" After she {_cut_text(name, k)} and folds the rest in half, the matching squares "
            "still line up in the same colour.\n\nWhat is the greatest number of different colours the strip could have?")
    sol = _explain(n, [k]) + f" (Here {name} cut off squares 1 to {k}.) At most {ans} colours."
    choices, ai = numeric_choices(ans, _colour_mistakes(n, [k]), rng, lo=1, order="asc")
    return Question(text=text, figure=strip_pic(n), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, check_colours(n, [k])))


@variant(difficulty=2)
def same_as_first(rng, harder):
    """How many squares must have the colour of square 1 (itself included)?"""
    n, k = rng.choice([(12, 4), (12, 8), (16, 8), (16, 12)] if harder else [(8, 4), (8, 6), (12, 6), (12, 4)])
    name = rng.choice(PEOPLE)
    g = next(x for x in groups(n, [k]) if 1 in x)
    ans = len(g)
    text = (_intro(name, n) + f" After she {_cut_text(name, k, 'the left end')} and folds the rest in half, "
            "the matching squares still line up in the same colour.\n\n"
            f"How many of the {n} squares must have the same colour as square 1? (Count square 1 too.)")
    sol = (_explain(n, [k]) + f" Square 1 is in the group {{{', '.join(map(str, g))}}}, "
           f"so {ans} squares must have its colour.")
    mistakes = [(2, "count only square 1 and the square it matches in the first fold"),
                (len(groups(n, [k])), "give the number of colours instead"),
                (n // 2, "think it is half of the strip")]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1, order="asc")
    return Question(text=text, figure=strip_pic(n), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, check_with_first(n, [k])))


@variant(difficulty=3)
def two_cuts(rng, harder):
    """Cut, fold, cut again, fold again: every fold adds links."""
    while True:
        n = rng.choice([12, 16] if harder else [10, 12])
        k1, k2 = rng.choice([(2, 2), (2, 4), (4, 2), (4, 4), (2, 6)])
        if n - k1 - k2 >= 2 and len(groups(n, [k1, k2])) != len(groups(n, [k1])):
            break
    name = rng.choice(PEOPLE)
    cuts = [k1, k2]
    ans = len(groups(n, cuts))
    text = (_intro(name, n) + f" After she {_cut_text(name, k1)} and folds the rest in half, the matching squares "
            f"still line up in the same colour. Then she {_cut_text(name, k2, 'the same end', more=True)} and folds "
            "the rest in half, and again the matching squares line up in the same colour.\n\n"
            "What is the greatest number of different colours the strip could have?")
    sol = _explain(n, cuts) + f" (Here {name} cut from the left: squares 1 to {k1}, then {k1 + 1} to {k1 + k2}.)"
    choices, ai = numeric_choices(ans, _colour_mistakes(n, cuts)
                                  + [(len(groups(n, [k1])), "forget the last fold")], rng, lo=1, order="asc")
    return Question(text=text, figure=strip_pic(n), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, check_colours(n, cuts)))


@variant(difficulty=3)
def how_many_cut(rng, harder):
    """Reverse: the most colours is given; how many squares were cut off?"""
    n = rng.choice([12, 14, 16] if harder else [10, 12])
    table = {k: len(groups(n, [k])) for k in range(2, n - 1, 2)}
    unique = [k for k, c in table.items() if list(table.values()).count(c) == 1 and c >= 2]
    k = rng.choice(unique)
    name = rng.choice(PEOPLE)
    c = table[k]
    text = (_intro(name, n) + f" Then she cuts off some squares from the left end, so that the rest still folds in "
            f"half with the matching squares in the same colour. The greatest number of different colours the strip "
            f"could have is now {c}.\n\nHow many squares did {name} cut off?")
    sol = (f"Try the cuts that leave a strip that folds in half. Cutting off {k} squares gives {c} groups of squares "
           f"that must share a colour: " + _explain(n, [k])
           + " Every other cut gives a different number of colours.")
    mistakes = [(c, "give the number of colours instead"), (n // 2, "cut half of the strip")]
    choices, ai = numeric_choices(k, mistakes, rng, lo=2, order="asc", step=2)
    return Question(text=text, figure=strip_pic(n), choices=choices, answer=ai, solution=sol,
                    check=lambda i: int(choices[i]) % 2 == 0 and 2 <= int(choices[i]) <= n - 2
                    and check_colours(n, [int(choices[i])]) == c
                    and sum(check_colours(n, [kk]) == c for kk in range(2, n - 1, 2)) == 1)
