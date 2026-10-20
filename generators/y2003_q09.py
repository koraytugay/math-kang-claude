"""2003 Q9 - blue cubes hidden inside a red brick.

Original: Chris built the brick in the picture (5 long, 4 tall, 4 deep) from red
and blue cubes of the same size. The outside of the brick is completely red, but
all cubes inside are blue. How many blue cubes did Chris use?
A 12  B 24  C 36  D 40  E 48.
Inside: (5 - 2) x (4 - 2) x (4 - 2) = 3 x 2 x 2 = 12.  Answer: A.

Core skill: the hidden inside of a box is a smaller box - one cube thinner on each
of the two ends, so every side length drops by 2 (not by 1). Children subtract 1,
or count only what they see.
"""
from kangaroo import Question, numeric_choices, variant
from kangaroo.cubes import draw_cubes

META = {
    "source": "2003 Q9",
    "skill": "Inside of a box of cubes: every length drops by 2; outside = total − inside",
    "topics": ["counting", "spatial", "geometry"],
    "version": 1,
}

NAMES = ["Chris", "Mia", "Leo", "Sara", "Tom", "Nina"]


def box(a, b, c):
    """a long, b deep, c tall."""
    return {(x, y, z) for x in range(a) for y in range(b) for z in range(c)}


def _dims(rng, harder):
    lo, hi = (4, 6) if harder else (3, 5)
    while True:
        a, b, c = (rng.randint(lo, hi) for _ in range(3))
        if (a - 2) * (b - 2) * (c - 2) >= 1 and not a == b == c == 3:
            return a, b, c


def _pic(a, b, c):
    return draw_cubes(box(a, b, c), scale={5: 13, 6: 11}.get(max(a, b, c), 13 if max(a, b, c) < 5 else 9))


def _dims_text(a, b, c):
    return f"{a} cubes long, {b} cubes deep and {c} cubes tall"


@variant(difficulty=1)
def blue_inside(rng, harder):
    """The original."""
    a, b, c = _dims(rng, harder)
    name = rng.choice(NAMES)
    ans = (a - 2) * (b - 2) * (c - 2)
    text = (f"{name} built this brick ({_dims_text(a, b, c)}) from red and blue cubes of the same "
            f"size. The outside of the brick is completely red, but all the cubes inside are blue.")
    after = f"How many blue cubes did {name} use?"
    sol = (f"Take away one layer on every side: the inside is {a - 2} × {b - 2} × {c - 2} = {ans}.")
    mistakes = [(a - 1) * (b - 1) * (c - 1), a * b * c - ans, (a - 2) * (b - 2), (a - 2) * (c - 2),
                (b - 2) * (c - 2), a * b * c - a * b * 2, ans * 2]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, figure=_pic(a, b, c), after_figure=after, choices=choices, answer=ai,
                    solution=sol)


@variant(difficulty=1)
def red_outside(rng, harder):
    """How many red cubes are on the outside?"""
    a, b, c = _dims(rng, harder)
    name = rng.choice(NAMES)
    total = a * b * c
    inner = (a - 2) * (b - 2) * (c - 2)
    ans = total - inner
    text = (f"{name} built this brick ({_dims_text(a, b, c)}) from red and blue cubes of the same "
            f"size. Every cube you can see from the outside (also from below and behind) is red. "
            f"All the cubes inside are blue.")
    after = f"How many red cubes did {name} use?"
    sol = (f"All cubes: {a} × {b} × {c} = {total}. Blue inside: {a - 2} × {b - 2} × {c - 2} = {inner}. "
           f"Red: {total} − {inner} = {ans}.")
    mistakes = [2 * (a * b + b * c + a * c), total - (a - 1) * (b - 1) * (c - 1), total, inner,
                a * c + b * c + a * b, ans - 8]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, figure=_pic(a, b, c), after_figure=after, choices=choices, answer=ai,
                    solution=sol)


@variant(difficulty=2)
def painted(rng, harder):
    """A big cube is dipped in paint and cut up: how many small cubes have k painted faces?"""
    n = rng.choice([4, 5] if harder else [3, 4])
    k = rng.choice([0, 1, 2, 3])
    name = rng.choice(NAMES)
    counts = {3: 8, 2: 12 * (n - 2), 1: 6 * (n - 2) ** 2, 0: (n - 2) ** 3}
    ans = counts[k]
    what = {0: "no paint at all", 1: "paint on exactly one face", 2: "paint on exactly two faces",
            3: "paint on exactly three faces"}[k]
    where = {0: "they are the cubes inside",
             1: f"they are in the middle of each face: 6 × {n - 2} × {n - 2}",
             2: f"they are on the edges but not at the corners: 12 × {n - 2}",
             3: "they are the corners, and a cube always has 8 corners"}[k]
    text = (f"{name} glued {n * n * n} small cubes into a big {n} × {n} × {n} cube (like the picture) "
            f"and painted the whole outside of it, also the bottom. Then the big cube falls apart.")
    after = f"How many small cubes have {what}?"
    tail = {0: f": {n - 2} × {n - 2} × {n - 2} = {ans}.", 1: f" = {ans}.", 2: f" = {ans}.", 3: "."}[k]
    sol = where[0].upper() + where[1:] + tail
    mistakes = [v for kk, v in counts.items() if kk != k] + [ans + 4, 4 * (n - 2), 6 * (n - 2)]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=0)
    return Question(text=text, figure=_pic(n, n, n), after_figure=after, choices=choices, answer=ai,
                    solution=sol)


@variant(difficulty=2)
def how_deep(rng, harder):
    """Reverse: the number of blue cubes is known - how deep is the brick?"""
    a = rng.randint(4, 7 if harder else 6)
    c = rng.randint(3, 5)
    b = rng.randint(3, 6 if harder else 5)
    inner = (a - 2) * (b - 2) * (c - 2)
    name = rng.choice(NAMES)
    text = (f"{name} builds a brick {a} cubes long and {c} cubes tall from red and blue cubes. The "
            f"outside is completely red and the inside is completely blue. {name} used exactly "
            f"{inner} blue cubes.")
    after = "How many cubes deep is the brick?"
    sol = (f"The blue inside is {a - 2} long and {c - 2} tall, so one layer of it has "
           f"{a - 2} × {c - 2} = {(a - 2) * (c - 2)} cubes. {inner} ÷ {(a - 2) * (c - 2)} = {b - 2} "
           f"layers of blue, plus the red front and back: {b}.")
    mistakes = [b - 2, b - 1, b + 1, inner // (a * c) if inner % (a * c) == 0 else -1, b + 2]
    choices, ai = numeric_choices(b, mistakes, rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=3)
def thick_wall(rng, harder):
    """Twist: the red outside is two cubes thick."""
    lo, hi = (6, 8) if harder else (6, 7)
    a, b, c = (rng.randint(lo, hi) for _ in range(3))
    name = rng.choice(NAMES)
    ans = (a - 4) * (b - 4) * (c - 4)
    text = (f"{name} builds a brick {_dims_text(a, b, c)}. To make it strong, the red outside is "
            f"<b>two</b> cubes thick everywhere (also at the bottom, top, front and back). "
            f"Everything inside that is blue.")
    after = "How many blue cubes are there?"
    sol = (f"Two layers come off at each end of every length, so each length drops by 4: "
           f"{a - 4} × {b - 4} × {c - 4} = {ans}.")
    mistakes = [(a - 2) * (b - 2) * (c - 2), (a - 3) * (b - 3) * (c - 3), (a - 4) * (b - 4),
                ans * 2, a * b * c - ans]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, figure=_pic(a, b, c), after_figure=after,
                    choices=choices, answer=ai, solution=sol)
