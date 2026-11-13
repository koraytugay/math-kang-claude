"""2023 Q24 (Ecolier, Grade 3-4) - one guess is right, every other guess has all but one cell right.

Original: Maria colours exactly 5 cells of this grid (4 x 4) in grey. Then she has her 5 friends guess
which cells she has coloured in and their answers are the five patterns A, B, C, D and E. Maria looks
at the patterns and says: "One of you is right. The others have each guessed exactly four cells
correctly." Which pattern did Maria paint?
Patterns (rows from the top, columns 1-4):
A: r1c3, r2c1, r2c4, r3c3, r4c3     B: r1c3, r2c1, r2c4, r4c1, r4c3
C: r1c3, r2c4, r3c1, r4c2, r4c3     D: r1c2, r1c3, r2c1, r2c4, r4c3
E: r1c3, r2c1, r2c4, r3c1, r4c3
E shares exactly 4 cells with each of A, B, C and D.  Answer: E (answer key: E).

Core skill: test each candidate against ALL the others (count the cells in common), or notice that
the right pattern is the one that has the most popular cells. Children pick the pattern that "looks
the most typical" or check against only one other pattern.
"""
from reportlab.lib import colors

from kangaroo import Fig, Question, numeric_choices, text_choices, value_check, variant, warmup
from kangaroo.choices import Choices
from kangaroo.figures import row

META = {
    "source": "set-01/by_level/Grade_03-04_Ecolier/2023 Q24",
    "skill": "One guess is right and each other guess has all but one right: test every option against "
             "all the others and count what they have in common",
    "topics": ["logic", "counting", "spatial"],
    "keywords": ["one guess is right", "compare patterns", "cells in common"],
    "version": 2,
}

GREY = colors.Color(0.55, 0.55, 0.55)
NAMES = ["Maria", "Lena", "Tom", "Sara", "Ben", "Mia"]
LETTERS = "ABCDE"


def grid_pic(cells, n, size=56, empty=False):
    f = Fig(n, n, max_px=size, margin=2)
    for r in range(n):
        for c in range(n):
            f.rect(c, n - 1 - r, 1, 1, fill=GREY if (r, c) in cells and not empty else colors.white, width=0.7)
    return f.drawing()


def common(a, b):
    return len(set(a) & set(b))


def fits(cands, i, k):
    """Check side: option i is right iff every other option has exactly k - 1 cells in common with it."""
    return all(common(cands[i], cands[j]) == k - 1 for j in range(len(cands)) if j != i)


def _near(rng, base, allcells, avoid):
    """Move one cell of `base` to a new place."""
    out = set(base)
    out.remove(rng.choice(sorted(base)))
    out.add(rng.choice(sorted(allcells - set(base))))
    out = frozenset(out)
    return out if out not in avoid else None


def _make(rng, n, k, tries=2000):
    """A right pattern and 4 guesses with exactly k - 1 right each, so that only the right one fits."""
    allcells = {(r, c) for r in range(n) for c in range(n)}
    for _ in range(tries):
        right = frozenset(rng.sample(sorted(allcells), k))
        others = []
        while len(others) < 4:
            o = _near(rng, right, allcells, [right] + others)
            if o:
                others.append(o)
        opts = others + [right]
        rng.shuffle(opts)
        if [i for i in range(5) if fits(opts, i, k)] == [opts.index(right)]:
            return right, opts
    raise RuntimeError("no puzzle")


# ------------------------------------------------------------------ variants
@variant(difficulty=1)
def which_pattern(rng, harder):
    """The original: which pattern did she paint?"""
    n, k = (4, 5) if harder else (3, 3)
    right, opts = _make(rng, n, k)
    ai = opts.index(right)
    name = rng.choice(NAMES)
    text = (f"{name} colours exactly {k} cells of a {n} × {n} grid grey. Five friends guess which cells "
            f"{name} coloured: the patterns A to E.\n\n{name} says: \"One of you is right. Each of the others guessed "
            f"exactly {k - 1} cells correctly.\" Which pattern did {name} colour?")
    sol = (f"Compare each pattern with all the others. Pattern {LETTERS[ai]} has exactly {k - 1} grey cells in "
           f"common with every other pattern, so it is the right one.")
    mist = {i: "compare it with only one other pattern" for i in range(5) if i != ai}
    return Question(text=text, figure=grid_pic(set(), n, size=50, empty=True),
                    choices=Choices([f"pattern {c}" for c in LETTERS], mist),
                    choice_figures=[grid_pic(o, n) for o in opts], answer=ai, solution=sol,
                    check=lambda i: fits(opts, i, k))


@variant(difficulty=2)
def lock_code(rng, harder):
    """Same logic with a number lock: one guess is right, the others have all but one digit right."""
    k = 5 if harder else 4
    while True:
        right = "".join(str(rng.randint(0, 9)) for _ in range(k))
        guesses = set()
        while len(guesses) < 4:
            p = rng.randrange(k)
            d = str(rng.choice([x for x in range(10) if str(x) != right[p]]))
            guesses.add(right[:p] + d + right[p + 1:])
        opts = sorted(guesses | {right})
        rng.shuffle(opts)
        same = lambda a, b: sum(x == y for x, y in zip(a, b))
        ok = [i for i in range(5) if all(same(opts[i], opts[j]) == k - 1 for j in range(5) if j != i)]
        if ok == [opts.index(right)]:
            break
    name = rng.choice(NAMES)
    text = (f"{name} sets a secret code with {k} digits on a bike lock. Five friends guess the code: "
            f"{', '.join(opts[:-1])} and {opts[-1]}.\n\n{name} says: \"One of you is right. Each of the others has "
            f"exactly {k - 1} digits right, in the right place.\" What is the code?")
    sol = (f"Compare each guess with all the others, digit by digit. Only {right} has exactly {k - 1} digits in "
           f"the same places as every other guess.")
    labels = [(o, "compare it with only one other guess") for o in opts if o != right]
    choices, ai = text_choices(right, labels, rng)
    def check(i):
        j = opts.index(choices[i])
        return all(sum(x == y for x, y in zip(opts[j], opts[m])) == k - 1 for m in range(5) if m != j)
    return Question(text=text, choices=choices, answer=ai, solution=sol, check=check)


@variant(difficulty=1)
def how_many_right(rng, harder):
    """Warm into it: how many cells did this guess get right?"""
    n, k = (4, 6) if harder else (3, 4)
    allcells = sorted((r, c) for r in range(n) for c in range(n))
    right = set(rng.sample(allcells, k))
    hits = rng.randint(1, k - 1)
    guess = set(rng.sample(sorted(right), hits)) | set(rng.sample([c for c in allcells if c not in right], k - hits))
    name = rng.choice(NAMES)
    text = (f"{name} coloured the left grid. A friend guessed the right grid. How many cells did the friend "
            f"guess correctly?")
    sol = f"Look for cells that are grey in both grids: {hits}."
    mistakes = [(k - hits, "count the cells that are wrong"), (k, "count all the grey cells"),
                (n * n - len(right | guess), "count the white cells")]
    choices, ai = numeric_choices(hits, mistakes, rng, lo=0, order="asc")
    value = sum(1 for r in range(n) for c in range(n) if (r, c) in right and (r, c) in guess)
    return Question(text=text, figure=row([grid_pic(right, n, 60), grid_pic(guess, n, 60)], gap=30),
                    choices=choices, answer=ai, solution=sol, check=value_check(choices, value))


@variant(difficulty=3)
def not_a_guess(rng, harder):
    """Reverse: nobody was right. Each guess has exactly k-1 right - which pattern fits all the clues?"""
    n, k = (4, 4) if harder else (3, 3)
    allcells = {(r, c) for r in range(n) for c in range(n)}
    while True:
        right = frozenset(rng.sample(sorted(allcells), k))
        guesses = []
        while len(guesses) < 3:
            g = _near(rng, right, allcells, [right] + guesses)
            if g:
                guesses.append(g)
        cands = [right]
        while len(cands) < 5:
            c = _near(rng, rng.choice(guesses), allcells, cands + guesses)
            if c:
                cands.append(c)
        good = [c for c in cands if all(common(c, g) == k - 1 for g in guesses)]
        if good == [right]:
            break
    rng.shuffle(cands)
    ai = cands.index(right)
    name = rng.choice(NAMES)
    text = (f"{name} colours exactly {k} cells of a {n} × {n} grid grey. Three friends guess (top row).\n\n{name} "
            f"says: \"Nobody is right, but each of you guessed exactly {k - 1} cells correctly.\" Which of the "
            f"patterns A to E did {name} colour?")
    sol = (f"Check each pattern against all three guesses: pattern {LETTERS[ai]} has exactly {k - 1} cells in "
           f"common with each of them.")
    mist = {i: "check it against only one or two of the guesses" for i in range(5) if i != ai}
    return Question(text=text, figure=row([grid_pic(g, n, 50) for g in guesses], gap=20),
                    choices=Choices([f"pattern {c}" for c in LETTERS], mist),
                    choice_figures=[grid_pic(c, n) for c in cands], answer=ai, solution=sol,
                    check=lambda i: all(common(cands[i], g) == k - 1 for g in guesses))


# ------------------------------------------------------------------ teaching page
def teach():
    pat = {
        "A": {(0, 2), (1, 0), (1, 3), (2, 2), (3, 2)}, "B": {(0, 2), (1, 0), (1, 3), (3, 0), (3, 2)},
        "C": {(0, 2), (1, 3), (2, 0), (3, 1), (3, 2)}, "D": {(0, 1), (0, 2), (1, 0), (1, 3), (3, 2)},
        "E": {(0, 2), (1, 0), (1, 3), (2, 0), (3, 2)},
    }
    rows = [["", "A", "B", "C", "D", "E"]]
    for a in "ABCDE":
        rows.append([a] + ["-" if a == b else str(common(pat[a], pat[b])) for b in "ABCDE"])
    return [
        ("h", "How to think about it: one guess is right, the others have one mistake"),
        "If one guess is right, then every other guess must have exactly 4 of its 5 cells in common with the "
        "right one. So test each pattern: <b>count the grey cells it shares with every other pattern</b>.",
        row([grid_pic(pat[c], 4, 52) for c in "ABCDE"], gap=16),
        ("h", "The contest question"),
        "Count the cells in common for each pair (row = the pattern you test):",
        ("table", rows),
        ("tip", "Only row <b>E</b> has a 4 everywhere. So Maria coloured pattern E."),
        ("h", "A quicker way"),
        "Count how many patterns colour each cell. The right pattern keeps the popular cells: every wrong guess "
        "moved just one cell away from it.",
        ("h", "Watch out"),
        ("-", "Do not stop after comparing two patterns: A and B also share 4 cells, but A is not the answer."),
    ]


# ------------------------------------------------------------------ warm-ups
@warmup
def w_common(rng, harder):
    """Count the cells two patterns share."""
    n = 3
    allcells = sorted((r, c) for r in range(n) for c in range(n))
    a = set(rng.sample(allcells, 4))
    b = set(rng.sample(allcells, 4))
    ans = len(a & b)
    text = "How many grey cells do these two patterns have in common (grey in both)?"
    choices, ai = numeric_choices(ans, [(4, "count the grey cells of one pattern"), (8 - ans, "count all grey cells")],
                                  rng, lo=0, order="asc")
    value = sum(1 for cell in allcells if cell in a and cell in b)
    return Question(text=text, figure=row([grid_pic(a, n, 50), grid_pic(b, n, 50)], gap=24), choices=choices,
                    answer=ai, solution=f"Grey in both: {ans}.", check=value_check(choices, value))


@warmup
def w_codes(rng, harder):
    """Compare two codes digit by digit."""
    while True:
        a = "".join(str(rng.randint(1, 9)) for _ in range(4))
        b = "".join(c if rng.random() < 0.6 else str(rng.randint(1, 9)) for c in a)
        if a != b:
            break
    ans = sum(x == y for x, y in zip(a, b))
    text = (f"Two friends guess a 4-digit code: {a} and {b}. In how many places do the two guesses have the "
            f"same digit?")
    choices, ai = numeric_choices(ans, [(4 - ans, "count the places that are different"),
                                        (4, "count all the digits")], rng, lo=0, order="asc")
    value = len([i for i in range(4) if a[i] == b[i]])
    return Question(text=text, choices=choices, answer=ai,
                    solution=f"Compare digit by digit: {ans} places are the same.", check=value_check(choices, value))
