"""2007 Q21 - growing grids of black and white cells: how many white cells next?

Original: three diagrams - 3 x 3 with 1 black cell (8 white), 5 x 5 with 4 black
(21 white), 7 x 7 with 9 black (40 white). If the pattern continues, how many
white cells will the next diagram have?  A 50  B 60  C 65  D 70  E 75.
Next: 9 x 9 = 81 cells, 4 x 4 = 16 black, 81 - 16 = 65.  Answer: C.

Core skill: describing a growing pattern by how it is built (side 3, 5, 7, ...;
black cells 1, 2 x 2, 3 x 3, ...) instead of guessing from the differences
of the numbers alone (8, 21, 40 -> +13, +19 -> +25 is right too, but harder).
"""
from reportlab.lib import colors

from kangaroo import Fig, Question, numeric_choices, variant
from kangaroo.figures import column, row

META = {
    "source": "2007 Q21",
    "skill": "Growing patterns: describe how each diagram is built, then count cells = total − black",
    "topics": ["patterns", "counting"],
    "version": 1,
}

ORD = {1: "1st", 2: "2nd", 3: "3rd"}


def ordinal(n):
    return ORD.get(n, f"{n}th")


def dots(k):
    """Family A (the original): (2k+1) x (2k+1) with black cells at odd-odd places (k x k of them)."""
    n = 2 * k + 1
    return n, {(x, y) for x in range(1, n, 2) for y in range(1, n, 2)}


def framed(k):
    """Family B: a k x k black square with a white border around it."""
    n = k + 2
    return n, {(x, y) for x in range(1, n - 1) for y in range(1, n - 1)}


FAMILIES = {"dots": dots, "framed": framed}


def grid_pic(n, black, caption, cell=6.5):
    f = Fig(n, n, scale=cell, margin=2)
    for x in range(n):
        for y in range(n):
            f.rect(x, y, 1, 1, fill=colors.black if (x, y) in black else colors.white, width=0.6)
    cap = Fig(10, 1, scale=9, margin=0)
    cap.text(5, 0.5, caption, size=9)
    return column([f.drawing(), cap.drawing()], gap=2)


def white(fam, k):
    n, b = FAMILIES[fam](k)
    return n * n - len(b)


def _show(fam, ks, captions=True):
    pics = []
    for k in ks:
        n, b = FAMILIES[fam](k)
        pics.append(grid_pic(n, b, f"{n * n - len(b)} white cells" if captions else ordinal(k)))
    return row(pics, gap=14)


@variant(difficulty=1)
def next_white(rng, harder):
    """The original."""
    s = rng.choice([1, 2]) if harder else 1
    ks = [s, s + 1, s + 2]
    k = s + 3
    n, b = dots(k)
    ans = n * n - len(b)
    w = [white("dots", j) for j in ks]
    text = ("These diagrams follow a pattern of black and white cells. If the pattern continues, how many "
            "white cells will the next diagram have?")
    sol = (f"The sides grow by 2 and the black cells are 1 × 1, 2 × 2, 3 × 3, ... The next diagram is "
           f"{n} × {n} = {n * n} cells with {k} × {k} = {k * k} black: {n * n} − {k * k} = {ans}.")
    mistakes = [w[-1] + (w[-1] - w[-2]),        # same step again
                n * n, (n - 1) ** 2, ans + k, ans - k, 2 * w[-1] - w[0]]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1, step=5 if ans % 5 == 0 else 1)
    return Question(text=text, figure=_show("dots", ks), choices=choices, answer=ai, solution=sol)


@variant(difficulty=1)
def border_next(rng, harder):
    """A white border around a black square."""
    s = rng.choice([1, 2, 3]) if harder else 1
    ks = [s, s + 1, s + 2]
    k = s + 3 if not harder else s + 4
    which = "next diagram" if k == s + 3 else "diagram after the next one"
    n, b = framed(k)
    ans = n * n - len(b)
    text = (f"These diagrams follow a pattern: a black square with a white border around it. "
            f"How many white cells will the {which} have?")
    sol = (f"The border of an {n} × {n} square has {n} + {n} + {n - 2} + {n - 2} = {ans} cells "
           f"(or {n} × {n} − {k} × {k} = {ans}).")
    mistakes = [4 * n, n * n, ans + 4, ans - 4, k * k]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, figure=_show("framed", ks), choices=choices, answer=ai, solution=sol)


@variant(difficulty=2)
def far_diagram(rng, harder):
    """Jump further ahead: the 5th or 6th diagram."""
    m = rng.choice([6, 7]) if harder else rng.choice([5, 6])
    n, b = dots(m)
    ans = n * n - len(b)
    text = (f"The diagrams below are the 1st, 2nd and 3rd of a pattern. How many white cells will the "
            f"{ordinal(m)} diagram have?")
    sol = (f"Diagram number k is (2k + 1) × (2k + 1) with k × k black cells. The {ordinal(m)}: "
           f"{n} × {n} − {m} × {m} = {n * n} − {m * m} = {ans}.")
    mistakes = [n * n,                          # forgot to take away the black cells
                white("dots", m - 1), white("dots", m + 1),   # one diagram too early / too late
                (2 * m) ** 2 - m * m]           # side 2k instead of 2k + 1
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, figure=_show("dots", [1, 2, 3]), choices=choices, answer=ai, solution=sol)


@variant(difficulty=2)
def black_and_total(rng, harder):
    """How many black cells / cells in all in a later diagram?"""
    m = rng.choice([5, 6, 8]) if harder else rng.choice([4, 5])
    n, b = dots(m)
    ask_total = rng.random() < 0.5
    ans = n * n if ask_total else m * m
    text = (f"The diagrams below are the 1st, 2nd and 3rd of a pattern. How many "
            f"{'cells in all' if ask_total else 'black cells'} will the {ordinal(m)} diagram have?")
    sol = (f"The {ordinal(m)} diagram is {n} × {n} = {n * n} cells, with {m} × {m} = {m * m} black ones.")
    mistakes = ([m * m, (n - 1) ** 2, (n + 1) ** 2, n * 4, n * n - m * m] if ask_total
                else [2 * m, m * m + 1, (m - 1) ** 2, (m + 1) ** 2, n])
    choices, ai = numeric_choices(ans, [x for x in mistakes if x != ans], rng, lo=1)
    return Question(text=text, figure=_show("dots", [1, 2, 3]), choices=choices, answer=ai, solution=sol)


@variant(difficulty=3)
def which_diagram(rng, harder):
    """Reverse: which diagram has W white cells?"""
    fam = rng.choice(["dots", "framed"]) if harder else "dots"
    m = rng.randint(5, 9) if harder else rng.randint(4, 6)
    W = white(fam, m)
    text = (f"The diagrams below are the 1st, 2nd and 3rd of a pattern. One diagram further on has "
            f"exactly {W} white cells. Which one is it?")
    n, b = FAMILIES[fam](m)
    sol = (f"Try the diagrams one by one: the {ordinal(m)} is {n} × {n} = {n * n} cells with {len(b)} black, "
           f"so {W} white.")
    vals = sorted({m} | set(rng.sample([v for v in range(max(4, m - 3), m + 5) if v != m], 4)))
    labels = [f"the {ordinal(v)}" for v in vals]
    return Question(text=text, figure=_show(fam, [1, 2, 3], captions=False), choices=labels,
                    answer=vals.index(m), solution=sol)
