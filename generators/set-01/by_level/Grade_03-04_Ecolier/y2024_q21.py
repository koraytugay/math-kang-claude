"""2024 Q21 (Ecolier, Grade 3-4) - frogs on a grid: two jump, the rows and columns still have 2 each.

Original: a 3 x 3 grid with 6 frogs, exactly 2 in each row and in each column (top row: left
and right; middle row: left and middle; bottom row: middle and right). Two of the frogs jump at
the same time, each to a neighbouring field (left, right, up or down) that is empty. After that
there are again two frogs in each row and in each column. How many possibilities are there for
two frogs to jump like this?  A 1  B 2  C 3  D 4  E 5.   Answer: D (4).

Core skill: a frog that jumps sideways takes one away from its column and adds one to the
neighbouring column - so the other frog must jump sideways between the same two columns, the
other way (or both jump up/down between the same two rows). Seeing this "the second jump must
undo the first" idea, instead of trying everything at random, is what makes it hard.
Printed in black and white: frogs are simple outline drawings.
"""
from itertools import combinations

from reportlab.lib import colors

from kangaroo import Fig, Question, numeric_choices, value_check, variant

META = {
    "source": "set-01/by_level/Grade_03-04_Ecolier/2024 Q21",
    "skill": "Two jumps that keep every row and column count: the second jump must undo the first",
    "topics": ["logic", "counting", "spatial"],
    "keywords": ["frogs jumping", "rows and columns"],
    "version": 1,
}

ORIGINAL = frozenset({(0, 0), (0, 2), (1, 0), (1, 1), (2, 1), (2, 2)})   # (row, column), row 0 = top
LETTERS = "ABCDEFGHIJKL"


# ------------------------------------------------------------------ the rules
def single_jumps(F, n):
    """Every jump of one frog to an empty neighbouring field: (from, to)."""
    out = []
    for (r, c) in sorted(F):
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            t = (r + dr, c + dc)
            if 0 <= t[0] < n and 0 <= t[1] < n and t not in F:
                out.append(((r, c), t))
    return out


def balanced(G, n, k):
    return (all(sum(1 for f in G if f[0] == r) == k for r in range(n))
            and all(sum(1 for f in G if f[1] == c) == k for c in range(n)))


def good_pairs(F, n, k):
    """Answer check: try every pair of jumps (two different frogs, two different empty fields)."""
    out = []
    for a, b in combinations(single_jumps(F, n), 2):
        if a[0] == b[0] or a[1] == b[1]:
            continue
        if balanced((F - {a[0], b[0]}) | {a[1], b[1]}, n, k):
            out.append((a, b))
    return out


def clever_count(F, n):
    """The way to think: sideways jumps between columns c and c+1 in two rows, one each way
    (and the same for up/down jumps between two rows)."""
    total = 0
    for c in range(n - 1):
        right = [r for r in range(n) if (r, c) in F and (r, c + 1) not in F]
        left = [r for r in range(n) if (r, c + 1) in F and (r, c) not in F]
        total += sum(1 for a in right for b in left if a != b)
    for r in range(n - 1):
        down = [c for c in range(n) if (r, c) in F and (r + 1, c) not in F]
        up = [c for c in range(n) if (r + 1, c) in F and (r, c) not in F]
        total += sum(1 for a in down for b in up if a != b)
    return total


def random_grid(rng, n, k):
    """Frogs with exactly k in every row and column."""
    while True:
        cols = [0] * n
        F = set()
        okay = True
        for r in range(n):
            free = [c for c in range(n) if cols[c] < k]
            if len(free) < k:
                okay = False
                break
            for c in rng.sample(free, k):
                F.add((r, c))
                cols[c] += 1
        if okay and balanced(F, n, k):
            return frozenset(F)


# ------------------------------------------------------------------ picture
def frog(f, cx, cy, s):
    """A simple frog face, black and white."""
    f.circle(cx, cy - 0.05 * s, 0.33 * s, fill=colors.white, width=0.9)          # head
    for dx in (-0.17, 0.17):
        f.circle(cx + dx * s, cy + 0.27 * s, 0.11 * s, fill=colors.white, width=0.8)   # eyes
        f.circle(cx + dx * s, cy + 0.28 * s, 0.05 * s, fill=colors.black, width=0.3)
    f.arc(cx, cy, 0.2 * s, 210, 330, width=0.9)                                   # smile


def grid_pic(F, n, labels=None, scale=26):
    f = Fig(n, n, scale=scale, margin=3, font_size=10)
    for r in range(n):
        for c in range(n):
            f.rect(c, n - 1 - r, 1, 1, fill=colors.white, width=0.9)
    for (r, c) in F:
        frog(f, c + 0.5, n - 1 - r + 0.47, 1.0)
        if labels:
            f.text(c + 0.85, n - 1 - r + 0.12, labels[(r, c)], size=8)
    return f.drawing()


def _story(n, k):
    return (f"There are exactly {k} frogs in each row and in each column of this {n} × {n} pond. "
            f"A frog can jump to a <b>neighbouring</b> field (left, right, up or down) if it is empty. ")


def _setup(rng, harder, n3=True):
    if not harder and n3:
        return 3, 2, (ORIGINAL if rng.random() < 0.3 else random_grid(rng, 3, 2))
    n = rng.choice([4]) if harder else 3
    return n, 2, random_grid(rng, n, 2)


# ------------------------------------------------------------------ variants
@variant(difficulty=1)
def one_frog(rng, harder):
    """Warming up: how many ways can one frog jump?"""
    n, k, F = _setup(rng, harder)
    ans = len(single_jumps(F, n))
    text = (_story(n, k) + "Only <b>one</b> frog jumps. How many different jumps are possible? "
            "(Count every frog and every empty field it can reach.)")
    per = [sum(1 for j in single_jumps(F, n) if j[0] == fr) for fr in sorted(F)]
    sol = (f"Go frog by frog and count its empty neighbours: {' + '.join(map(str, per))} = {ans}.")
    mistakes = [len(F), n * n - len(F), ans + 2, ans - 2, 2 * len(F), ans + 1]
    choices, ai = numeric_choices(ans, [m for m in mistakes if m > 0], rng, lo=1, order="asc")
    value = sum(1 for (r, c) in F for (rr, cc) in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))
                if 0 <= rr < n and 0 <= cc < n and (rr, cc) not in F)
    return Question(text=text, figure=grid_pic(F, n), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, value))


@variant(difficulty=2)
def count_pairs(rng, harder):
    """The original question."""
    n, k, F = (3, 2, ORIGINAL) if (not harder and rng.random() < 0.4) else _setup(rng, harder)
    pairs = good_pairs(F, n, k)
    if not pairs:
        return count_pairs(rng, harder)
    ans = clever_count(F, n)
    text = (_story(n, k) + "Two of the frogs jump at the same time, each to an empty neighbouring field. "
            f"After that there are again exactly {k} frogs in each row and in each column. "
            "How many possibilities are there for two frogs to jump like this?")
    sol = ("If a frog jumps sideways, one column loses a frog and the next one gets one more - the other "
           "frog must jump sideways between the same two columns, the other way, in another row (the same "
           f"for jumps up and down between two rows). Checking each pair of neighbouring columns and rows gives {ans}.")
    mistakes = [ans + 1, ans - 1, ans + 2, 2 * ans, len(single_jumps(F, n)) // 2, 1]
    choices, ai = numeric_choices(ans, [m for m in mistakes if m > 0], rng, lo=1, order="asc")
    return Question(text=text, figure=grid_pic(F, n), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, len(pairs)))


@variant(difficulty=2)
def which_picture(rng, harder):
    """Which picture can show the pond after two frogs jumped?"""
    n, k, F = _setup(rng, harder)
    pairs = good_pairs(F, n, k)
    if not pairs:
        return which_picture(rng, harder)
    a, b = rng.choice(pairs)
    right = (F - {a[0], b[0]}) | {a[1], b[1]}
    # wrong pictures: one frog jumped, two jumps in the same direction, a frog jumped 2 fields, ...
    wrong = set()
    jumps = single_jumps(F, n)
    for x in jumps:
        wrong.add((F - {x[0]}) | {x[1]})
    for x, y in combinations(jumps, 2):
        if x[0] != y[0] and x[1] != y[1]:
            G = (F - {x[0], y[0]}) | {x[1], y[1]}
            if not balanced(G, n, k):
                wrong.add(G)
    wrong = [frozenset(w) for w in wrong if not balanced(w, n, k) and w != F]
    rng.shuffle(wrong)
    # tricky ones: still 2 in every row and column, but a frog jumped too far or diagonally
    reach = {frozenset((F - {p[0], q[0]}) | {p[1], q[1]}) for p, q in pairs}
    empty = [(r, c) for r in range(n) for c in range(n) if (r, c) not in F]
    tricky = set()
    for x, y in combinations(sorted(F), 2):
        for u, v in combinations(empty, 2):
            G = frozenset((F - {x, y}) | {u, v})
            if balanced(G, n, k) and G not in reach:
                tricky.add(G)
    tricky = sorted(tricky, key=sorted)
    rng.shuffle(tricky)
    opts = tricky[:rng.randint(1, 2)]
    opts = opts + wrong[:4 - len(opts)] + [frozenset(right)]
    rng.shuffle(opts)
    text = (_story(n, k) + "Two frogs jump at the same time, each to an empty neighbouring field. After that "
            f"there are again {k} frogs in each row and in each column. Which picture can show the pond "
            "<b>after</b> the jump?")
    sol = (f"First count the frogs in every row and column of each picture. Then look at which frogs moved: in "
           "the right picture each of the two frogs moved just one field (not diagonally), and the second jump "
           "undoes the first.")

    def check(i):
        G = opts[i]
        if not balanced(G, n, k):
            return False
        return any((F - {p[0], q[0]}) | {p[1], q[1]} == G for p, q in good_pairs(F, n, k))
    return Question(text=text, figure=grid_pic(F, n), choices=list("ABCDE"),
                    choice_figures=[grid_pic(o, n, scale=19 if n == 3 else 14) for o in opts], answer=opts.index(right),
                    solution=sol, check=check)


@variant(difficulty=3)
def one_frog_trick(rng, harder):
    """Only one frog jumps and the rows/columns must still have k each: impossible."""
    n, k, F = _setup(rng, harder)
    text = (_story(n, k) + "This time only <b>one</b> frog jumps, to an empty neighbouring field. After the jump "
            f"there must still be exactly {k} frogs in each row and in each column. How many different jumps "
            "are possible?")
    sol = ("None! A sideways jump takes a frog out of one column and puts it into another, so one column has "
           f"{k - 1} and one has {k + 1}. A jump up or down does the same to two rows. The answer is 0.")
    mistakes = [len(single_jumps(F, n)), 1, 2, clever_count(F, n), n]
    choices, ai = numeric_choices(0, mistakes, rng, lo=0, order="asc")
    value = sum(1 for x in single_jumps(F, n) if balanced((F - {x[0]}) | {x[1]}, n, k))
    return Question(text=text, figure=grid_pic(F, n), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, value))


@variant(difficulty=3)
def never_jumps(rng, harder):
    """How many frogs can never be one of the two jumping frogs?"""
    n, k, F = _setup(rng, harder)
    pairs = good_pairs(F, n, k)
    movers = {p[0] for a, b in pairs for p in (a, b)}
    ans = len(F) - len(movers)
    text = (_story(n, k) + "Two frogs jump at the same time, each to an empty neighbouring field, and after that "
            f"there are again {k} frogs in each row and in each column. How many of the frogs can "
            "<b>never</b> be one of the two jumping frogs?")
    sol = (f"Find all the ways ({len(pairs)}): the second jump must undo the first one (sideways between the same "
           f"two columns, or up/down between the same two rows). {len(movers)} frogs take part in some way, so "
           f"{len(F)} - {len(movers)} = {ans} never jump.")
    mistakes = [len(movers), ans + 1, ans + 2, max(ans - 1, 0), len(F), 0]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=0, order="asc")

    def value():
        never = 0
        for fr in F:
            if not any(fr in (a[0], b[0]) for a, b in good_pairs(F, n, k)):
                never += 1
        return never
    return Question(text=text, figure=grid_pic(F, n), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, value()))
