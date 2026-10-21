"""2007 Q17 - a painted 3 x 3 x 3 cube is cut up: how many small cubes have 2 painted faces?

Original: A cube with side 3 cm is painted grey and cut into cubes with side 1 cm.
How many of the small cubes have exactly 2 faces painted?
A 4  B 6  C 8  D 10  E 12.  They sit on the edges, not at the corners: a cube
has 12 edges, with one such cube on each.  Answer: E.

Core skill: sorting the small cubes by where they sit - corners (3 painted
faces), edges without corners (2), middles of faces (1), inside (0) - and
counting each group with the cube's 8 corners, 12 edges and 6 faces.
"""
from kangaroo import Question, numeric_choices, value_check, variant
from kangaroo.cubes import SIX, draw_cubes, painted_counts
from kangaroo.solve import only

META = {
    "source": "set-03/by_level/Grade_03-04/2007 Q17",
    "skill": "Painted cube cut up: corners 3 faces, edges 2, face middles 1, inside 0",
    "topics": ["counting", "spatial", "geometry"],
    "version": 1,
}

WORD = {0: "no", 1: "exactly 1", 2: "exactly 2", 3: "exactly 3"}
WHERE = {3: "at the corners", 2: "on the edges, but not at the corners",
         1: "in the middle part of each face", 0: "inside, where no paint reaches"}


def block(a, b, c):
    return {(x, y, z) for x in range(a) for y in range(b) for z in range(c)}


def with_paint(cells, k, skip=()):
    """Answer checks: small cubes with exactly k faces on the outside (not counting directions in skip)."""
    return sum(sum((x + dx, y + dy, z + dz) not in cells for dx, dy, dz in SIX if (dx, dy, dz) not in skip) == k
               for x, y, z in cells)


def _pic(a, b, c):
    return draw_cubes(block(a, b, c), scale=13 if max(a, b, c) <= 4 else 11)


def _formula(n, k):
    return {3: "8 corners, one cube each: 8",
            2: f"12 edges with {n} − 2 = {n - 2} such cubes each: 12 × {n - 2} = {12 * (n - 2)}",
            1: f"6 faces with {n - 2} × {n - 2} = {(n - 2) ** 2} each: 6 × {(n - 2) ** 2} = {6 * (n - 2) ** 2}",
            0: f"{n - 2} × {n - 2} × {n - 2} = {(n - 2) ** 3}"}[k]


@variant(difficulty=1)
def two_faces(rng, harder):
    """The original."""
    n = rng.choice([4, 5]) if harder else 3
    ans = 12 * (n - 2)
    text = (f"A cube with sides of {n} cm is painted grey all over and then cut into small cubes with "
            f"sides of 1 cm.")
    after = "How many of the small cubes have exactly 2 painted faces?"
    sol = f"They sit {WHERE[2]}. {_formula(n, 2)[0].upper() + _formula(n, 2)[1:]}."
    others = painted_counts(n, n, n)
    mistakes = [others[3], others[1], 4 * (n - 2), 6 * (n - 2), 12 * n, 8 * (n - 2)]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, figure=_pic(n, n, n), after_figure=after, choices=choices, answer=ai,
                    solution=sol,
                    check=value_check(choices, with_paint(block(n, n, n), 2)))


@variant(difficulty=1)
def always_eight(rng, harder):
    """Three painted faces: always the 8 corners, whatever the size."""
    n = rng.choice([5, 6, 8, 10]) if harder else rng.choice([3, 4, 5])
    text = (f"A big cube made of {n} × {n} × {n} = {n ** 3} small cubes is painted on the outside, "
            f"also underneath, and then taken apart.")
    after = "How many small cubes have exactly 3 painted faces?"
    sol = "Only the corner cubes have 3 painted faces, and a cube always has 8 corners, however big it is."
    mistakes = [12, 6, 24, 4 * n, 3 * n]      # edges, faces, or "grows with the cube"
    choices, ai = numeric_choices(8, mistakes, rng, lo=1)
    return Question(text=text, figure=_pic(n, n, n) if n <= 5 else None, after_figure=after,
                    choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, with_paint(block(n, n, n), 3)))


@variant(difficulty=2)
def painted_brick(rng, harder):
    """A brick (not a cube): edges have different lengths."""
    a, b, c = sorted((rng.randint(2, 4), rng.randint(3, 5), rng.randint(2, 4)) if not harder
                     else (rng.randint(3, 5), rng.randint(3, 6), rng.randint(4, 6)), reverse=True)
    k = rng.choice([1, 2])
    counts = painted_counts(a, b, c)
    ans = counts[k]
    text = (f"A brick {a} cubes long, {b} cubes deep and {c} cubes tall is made of small cubes. It is "
            f"painted on the outside, also underneath, and then taken apart.")
    after = f"How many small cubes have {WORD[k]} painted face{'s' if k > 1 else ''}?"
    if k == 2:
        sol = (f"On each edge, the cubes between the two corners: the brick has 4 edges of each length "
               f"{a}, {b}, {c}, so 4 × ({a - 2} + {b - 2} + {c - 2}) = {ans}.")
    else:
        sol = (f"The middle part of each face: 2 × ({a - 2} × {b - 2} + {a - 2} × {c - 2} + {b - 2} × "
               f"{c - 2}) = {ans}.")
    mistakes = [counts[3 - k] if 3 - k != k else -1, counts[3], counts[0], 12 * (min(a, b, c) - 2),
                ans + 4, ans - 4]
    choices, ai = numeric_choices(ans, [m for m in mistakes if m >= 0 and m != ans], rng, lo=0)
    return Question(text=text, figure=_pic(a, b, c), after_figure=after, choices=choices, answer=ai,
                    solution=sol,
                    check=value_check(choices, with_paint(block(a, b, c), k)))


def _no_bottom_counts(n):
    """Cube standing on a table: every face painted except the bottom."""
    out = {0: 0, 1: 0, 2: 0, 3: 0}
    for x in range(n):
        for y in range(n):
            for z in range(n):
                k = (x in (0, n - 1)) + (y in (0, n - 1)) + (z == n - 1)
                out[k] += 1
    return out


@variant(difficulty=2)
def not_underneath(rng, harder):
    """Painted while standing on the table - the bottom stays unpainted."""
    n = rng.choice([4, 5]) if harder else 3
    k = rng.choice([2, 3])
    counts = _no_bottom_counts(n)
    ans = counts[k]
    full = painted_counts(n, n, n)
    text = (f"A cube made of {n} × {n} × {n} small cubes stands on the table and is painted grey on all "
            f"sides you can reach: the top and the four sides, but <b>not</b> the bottom. Then it is "
            f"taken apart.")
    after = f"How many small cubes have exactly {k} painted faces?"
    if k == 3:
        sol = "Only the 4 top corners: they have the top and two sides painted. The bottom corners lose their bottom face."
    else:
        sol = (f"Top edges without their corners: 4 × {n - 2} = {4 * (n - 2)} (top and one side). Upright "
               f"edges without the top corner: 4 × {n - 1} = {4 * (n - 1)} (two sides; the bottom corners "
               f"count here because their bottom is not painted). Total {counts[2]}.")
    mistakes = [full[k], full[k] - 4, ans + 4, ans - 2, 8]
    choices, ai = numeric_choices(ans, [m for m in mistakes if m > 0 and m != ans], rng, lo=1)
    return Question(text=text, figure=_pic(n, n, n), after_figure=after, choices=choices, answer=ai,
                    solution=sol,
                    check=value_check(choices, with_paint(block(n, n, n), k, skip=[(0, 0, -1)])))


@variant(difficulty=3)
def how_big(rng, harder):
    """Reverse: from the number of 2-face cubes back to the size of the cube."""
    n = rng.randint(4, 7) if harder else rng.randint(3, 5)
    two = 12 * (n - 2)
    ask_total = rng.random() < 0.5
    ans = n ** 3 if ask_total else n
    text = (f"A big cube made of small cubes is painted on the outside and taken apart. Exactly {two} "
            f"small cubes have 2 painted faces.")
    after = ("How many small cubes was the big cube made of?" if ask_total
             else "How many small cubes long is each edge of the big cube?")
    sol = (f"A cube has 12 edges, so each edge has {two} ÷ 12 = {n - 2} cubes between its corners. "
           f"With the 2 corners, an edge is {n} cubes long" + (f", and the cube has {n} × {n} × {n} = {n ** 3}."
                                                             if ask_total else "."))
    mistakes = ([(n - 1) ** 3, (n + 1) ** 3, (n - 2) ** 3, two * 2, n * n * 6] if ask_total
                else [n - 2, n - 1, n + 1, two // 6, two // 4])
    choices, ai = numeric_choices(ans, [m for m in mistakes if m > 0 and m != ans], rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, (lambda m: m ** 3 if ask_total else m)(only(m for m in range(2, 12) if with_paint(block(m, m, m), 2) == two))))
