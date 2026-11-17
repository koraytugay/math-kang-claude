"""2022 Q19 (Ecolier, Grade 3-4) - an ant crawls up, across and down a pyramid of cubes.

Original: A pyramid is built from cubes (3 x 3 at the bottom, 2 x 2 in the middle, 1 on top).
All cubes have side length 10 cm. An ant crawls along the line drawn across the pyramid
(from the floor on one side, over the top, to the floor on the other side).
How long is the path taken by the ant?  (A) 30 cm (B) 60 cm (C) 70 cm (D) 80 cm (E) 90 cm
Up: 3 x 10 = 30 cm, down: 30 cm. The flat pieces together go across the whole pyramid:
30 cm (the ledges are only 5 cm each, the top 10 cm).  30 + 30 + 30 = 90 cm.  Answer: E.

Core skill: the path has many short pieces and the flat ones are not whole cube sides (the
ledges are half a cube). Counting pieces fails. The method: push all the up pieces together
(= the height), all the down pieces (= the height) and all the flat pieces (= the width
from one end to the other). Twist: going over the pyramid is longer than the floor by just
twice the height.

Figures are drawn from the front (a side view), so the half-cube ledges are easy to see.
"""
from reportlab.lib import colors

from kangaroo import Fig, Question, numeric_choices, value_check, variant

META = {
    "source": "set-01/by_level/Grade_03-04_Ecolier/2022 Q19",
    "skill": "A path over steps: add all the up pieces, all the down pieces and all the flat pieces separately",
    "topics": ["geometry", "spatial"],
    "keywords": ["ant path", "up and across", "pyramid of cubes"],
    "sticker": ("🐜", "Ant trail"),   # earned when this skill is solid (website)
    "version": 1,
}

CUBE = colors.Color(0.88, 0.88, 0.88)
RED = colors.Color(0.85, 0.1, 0.1)
ANTS = ["An ant", "A ladybird", "A beetle", "A snail"]


# ------------------------------------------------------------------ shapes and paths
def pyramid(n):
    """Cubes of a pyramid seen from the front: level k has n - k cubes, shifted by k/2."""
    return [(k * 0.5 + i, k) for k in range(n) for i in range(n - k)]


def towers(heights):
    return [(x, y) for x, h in enumerate(heights) for y in range(h)]


def outline(cubes):
    """The path over the top of the cubes, from the floor at the left to the floor at the
    right, as points (worked out from the drawn cubes: the top of every x-position)."""
    xs = sorted({x for x, _ in cubes} | {x + 1 for x, _ in cubes})
    def top(x):   # height of the column of cubes just right of x
        return max([y + 1 for cx, y in cubes if cx <= x < cx + 1] or [0])
    pts = [(xs[0], 0)]
    for a, b in zip(xs, xs[1:]):
        h = top((a + b) / 2)
        if pts[-1][1] != h:
            pts.append((a, h))
        pts.append((b, h))
    if pts[-1][1] != 0:
        pts.append((xs[-1], 0))
    return pts


def length(pts):
    """Answer check: walk the drawn path piece by piece and add up the pieces."""
    return sum(abs(x2 - x1) + abs(y2 - y1) for (x1, y1), (x2, y2) in zip(pts, pts[1:]))


def draw(cubes, path, side, a_label="A", b_label="B", max_px=150):
    w = max(x + 1 for x, _ in cubes)
    h = max(y + 1 for _, y in cubes)
    f = Fig(w, h, max_px=max_px, margin=26)
    for x, y in cubes:
        f.rect(x, y, 1, 1, fill=CUBE, width=0.9)
    f.line((-0.4, 0), (w + 0.4, 0), width=1.0)
    for p, q in zip(path, path[1:]):
        f.line(p, q, width=2.6, color=RED)
    if a_label:
        f.point(*path[0], a_label, "sw")
    if b_label:
        f.point(*path[-1], b_label, "se")
    bottom = sorted(x for x, y in cubes if y == 0)
    x0, y0 = bottom[len(bottom) // 2], 0       # label a middle cube, away from A and B
    f.side((x0, y0), (x0 + 1, y0), f"{side} cm", "below")
    return f.drawing()


def parts(pts):
    up = sum(max(0, b[1] - a[1]) for a, b in zip(pts, pts[1:]))
    down = sum(max(0, a[1] - b[1]) for a, b in zip(pts, pts[1:]))
    flat = sum(abs(b[0] - a[0]) for a, b in zip(pts, pts[1:]))
    return up, down, flat


def cm(v):
    return f"{v:g}"


# ------------------------------------------------------------------ variants
@variant(difficulty=1)
def stairs(rng, harder):
    """Whole-cube steps: from the floor, up the stairs, over the top and down the back."""
    n = rng.choice([4, 5]) if harder else 3
    s = rng.choice([6, 8, 12, 20]) if harder else 10
    cubes = towers(list(range(1, n + 1)))
    pts = outline(cubes)
    who = rng.choice(ANTS)
    text = (f"Stairs are built from cubes with side length {s} cm. "
            f"{who} crawls along the red line from A to B.\n\nHow long is the path?")
    up, down, flat = parts(pts)
    total = (up + down + flat) * s
    sol = (f"Up: {n} × {s} = {up * s} cm. Down the back: {down * s} cm. "
           f"Flat pieces together: {n} × {s} = {flat * s} cm. In all {total} cm.")
    mistakes = [((up + flat) * s, "forget the way down the back"),
                (up * s, "count only the way up"),
                (2 * up * s, "count only the up and down pieces")]
    ch, ans = numeric_choices(total, mistakes, rng, unit="cm", lo=1, step=s)
    return Question(text=text, figure=draw(cubes, pts, s), choices=ch, answer=ans, solution=sol,
                    difficulty=1, check=value_check(ch, int(length(pts) * s)))


@variant(difficulty=2)
def over_the_pyramid(rng, harder):
    """The original: the ledges are only half a cube."""
    n = rng.choice([4, 5]) if harder else 3
    s = rng.choice([6, 8, 12, 20]) if harder else 10
    cubes = pyramid(n)
    pts = outline(cubes)
    who = rng.choice(ANTS)
    text = (f"A pyramid is built from cubes with side length {s} cm (you see it from the front). "
            f"{who} crawls along the red line from A, over the top, to B.\n\nHow long is the path?")
    up, down, flat = parts(pts)
    total = int((up + down + flat) * s)
    pieces = len(pts) - 1
    sol = (f"All the up pieces: {n} × {s} = {n * s} cm, all the down pieces: {n * s} cm. "
           f"The flat pieces together reach from A to B: {n * s} cm (each step is only half a cube). "
           f"{n * s} + {n * s} + {n * s} = {total} cm.")
    mistakes = [(pieces * s, "count every piece of the path as a whole cube side"),
                (n * s + n * s // 2, "go only up to the middle of the top"),
                (2 * n * s, "count only the up and down pieces"),
                ((2 * n + 1) * s, "count only one cube side for the flat pieces")]
    ch, ans = numeric_choices(total, mistakes, rng, unit="cm", lo=1, step=s)
    return Question(text=text, figure=draw(cubes, pts, s), choices=ch, answer=ans, solution=sol,
                    difficulty=2, check=value_check(ch, int(length(pts) * s)))


@variant(difficulty=2)
def how_much_longer(rng, harder):
    """Twist: over the pyramid vs. along the floor - only the ups and downs are extra."""
    n = rng.choice([4, 5]) if harder else rng.choice([3, 4])
    s = rng.choice([6, 8, 12, 20]) if harder else 10
    cubes = pyramid(n)
    pts = outline(cubes)
    who = rng.choice(ANTS)
    text = (f"A pyramid is built from cubes with side length {s} cm (you see it from the front). "
            f"{who} crawls along the red line from A, over the top, to B. "
            f"Its friend walks along the floor straight from A to B."
            f"\n\nHow much longer is the way over the pyramid?")
    up, down, flat = parts(pts)
    diff = (up + down) * s
    sol = (f"The flat pieces of the red line together are just as long as the floor from A to B. "
           f"So only the up and down pieces are extra: {n} × {s} + {n} × {s} = {diff} cm.")
    mistakes = [(n * s, "count only the way up"),
                ((up + down + flat) * s, "give the whole red line, not the difference"),
                ((len(pts) - 1) * s - n * s, "count every piece as a whole cube side")]
    ch, ans = numeric_choices(diff, mistakes, rng, unit="cm", lo=1, step=s)
    floor = abs(pts[-1][0] - pts[0][0])
    return Question(text=text, figure=draw(cubes, pts, s), choices=ch, answer=ans, solution=sol,
                    difficulty=2, check=value_check(ch, int((length(pts) - floor) * s)))


@variant(difficulty=3)
def over_the_towers(rng, harder):
    """Towers of different heights in a row: down into every gap counts too."""
    k = 6 if harder else 5
    s = rng.choice([6, 8, 12, 20]) if harder else 10
    while True:
        hs = [rng.randint(1, 4 if harder else 3) for _ in range(k)]
        dips = sum(1 for i in range(1, k - 1) if hs[i] < hs[i - 1] and hs[i] < hs[i + 1])
        if dips >= 1 and len(set(hs)) >= 3:
            break
    cubes = towers(hs)
    pts = outline(cubes)
    who = rng.choice(ANTS)
    text = (f"Towers are built from cubes with side length {s} cm. "
            f"{who} crawls along the red line from A, over all the towers, to B.\n\nHow long is the path?")
    up, down, flat = parts(pts)
    total = (up + down + flat) * s
    sol = (f"Flat pieces together: {k} × {s} = {flat * s} cm. Up pieces together: {up} cube sides = {up * s} cm. "
           f"Down pieces together: {down} cube sides = {down * s} cm. In all {total} cm.")
    mistakes = [((k + 2 * max(hs)) * s, "go up to the highest tower and down once, forgetting the dips"),
                ((up + flat) * s, "forget the down pieces"),
                (sum(hs) * s, "count the cubes instead of the path")]
    ch, ans = numeric_choices(total, mistakes, rng, unit="cm", lo=1, step=s)
    return Question(text=text, figure=draw(cubes, pts, s), choices=ch, answer=ans, solution=sol,
                    difficulty=3, check=value_check(ch, int(length(pts) * s)))


@variant(difficulty=3)
def find_the_cube(rng, harder):
    """Turned around: the path length is known - how big is one cube?"""
    n = rng.choice([4, 5]) if harder else 3
    s = rng.choice([4, 6, 8, 12, 20]) if harder else rng.choice([4, 6, 8, 12])
    cubes = pyramid(n)
    pts = outline(cubes)
    up, down, flat = parts(pts)
    total = int((up + down + flat) * s)
    who = rng.choice(ANTS)
    text = (f"A pyramid is built from equal cubes (you see it from the front). "
            f"{who} crawls along the red line from A, over the top, to B. The path is {total} cm long."
            f"\n\nHow long is the side of one cube?")
    pieces = len(pts) - 1
    sol = (f"Up: {n} cube sides, down: {n} cube sides, flat pieces together: {n} cube sides "
           f"(from A to B). That is {3 * n} cube sides = {total} cm, so one side is {total} ÷ {3 * n} = {s} cm.")
    mistakes = [(total // (2 * n), "forget the flat pieces")]
    if total % pieces == 0:
        mistakes.append((total // pieces, "count every piece of the path as a whole cube side"))
    if total % n == 0:
        mistakes.append((total // n, "divide by the number of levels"))
    ch, ans = numeric_choices(s, mistakes, rng, unit="cm", lo=1)
    drawn = draw(cubes, pts, "?")
    return Question(text=text, figure=drawn, choices=ch, answer=ans, solution=sol, difficulty=3,
                    check=lambda i: abs(length(pts) * int(ch[i].split()[0]) - total) < 1e-9)
