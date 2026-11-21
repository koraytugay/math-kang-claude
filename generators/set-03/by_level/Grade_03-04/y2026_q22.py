"""2026 Q22 (Canada, Grade 3-4) - a big cube of black and white cubes: what could she see from another side?

Original: The big cube (3 x 3 x 3) is made out of 16 black cubes and 11 white cubes, all of the same
size. Lily is looking towards the cube in the direction shown (an arrow from the left). What could
she see?  Five 3 x 3 pictures (A)-(E).
Reading the drawing (front, top and right faces are shown), x to the right, y away, z up:
  front (y=0), rows from the top: B W B / B W B / W W W
  top (z=2), every row (y=0,1,2): B W B
  right (x=2), rows z=2/1/0, columns y=0,1,2: B B B / B W W / W B B
The 19 cubes on these three faces hold 10 black, so the 8 cubes hidden behind them (x<2, y>0, z<2)
hold 16 - 10 = 6 black and 2 white. From the left Lily sees the face x=0: the top row (B B B) and the
front column (B, B, W from top to bottom, on her right) are known; four cubes of her picture are hidden
cubes. Picture B (B B B / B W B / W B W) needs 2 white hidden cubes - allowed. A and C need 3, D and E
do not copy the known cubes.  Answer: B.  (The 2026 key in the repo is our own: solved by us.)

Core skill: the cubes you can see on the faces of a drawing are also on the faces you cannot see: copy them
(and turn the picture the right way round for the new side); the other cubes are hidden, and the
colour totals tell how many black and white cubes are left for them.

How it works: the cube is a dict (x, y, z) -> black?. The answer is built from a real random cube. The check
tries every way to fill the 8 hidden cubes with exactly the right number of black ones and sees whether the
picture can come out.
"""
import random
from itertools import combinations, product

from reportlab.graphics.shapes import Polygon
from reportlab.lib import colors

from kangaroo import Fig, Question, numeric_choices, value_check, variant
from kangaroo.choices import Choices

META = {
    "source": "set-03/by_level/Grade_03-04/2026 Q22",
    "skill": "The cubes you see on the faces of the drawing are on the other faces too: copy them first "
             "(turn the picture the right way round), then use the colour totals for the hidden cubes",
    "topics": ["spatial", "logic", "counting"],
    "keywords": ["hidden cubes", "cube views", "black and white cubes"],
    "sticker": ("👀", "Side peeker"),   # earned when this skill is solid (website)
    "version": 1,
}

PEOPLE = ["Lily", "Mia", "Lena", "Nora", "Sara", "Ella", "Zoe", "Maya"]
DX, DY = 0.45, 0.38                       # one step of depth on paper
EDGE = colors.Color(0.2, 0.6, 0.85)
BLACK = colors.Color(0.04, 0.04, 0.04)
N = 3


# ------------------------------------------------------------------ the cube
def visible_cell(c, n=N):
    """On one of the three faces drawn in the picture: front (y=0), top (z=n-1), right (x=n-1)."""
    x, y, z = c
    return y == 0 or z == n - 1 or x == n - 1


HIDDEN = [(x, y, z) for x in range(N) for y in range(N) for z in range(N) if not visible_cell((x, y, z))]
VIEW = {   # what a viewer on that side sees: rows from the top, columns from the left -> the cube
    "left": lambda r, c: (0, N - 1 - c, N - 1 - r),
    "back": lambda r, c: (N - 1 - c, N - 1, N - 1 - r),
}
SIDE_WORDS = {"left": "from the left side", "back": "from behind"}


def view_of(cube, side):
    return tuple(tuple(cube[VIEW[side](r, c)] for c in range(N)) for r in range(N))


def mirror(v):
    return tuple(tuple(reversed(row)) for row in v)


def is_known(side, r, c):
    return visible_cell(VIEW[side](r, c))


def random_cube(rng, p_black=0.5):
    return {(x, y, z): rng.random() < p_black for x in range(N) for y in range(N) for z in range(N)}


def possible_views(cube, side, hidden_black):
    """Every picture the viewer could see if the visible faces stay as they are and the 8 hidden cubes
    hold exactly `hidden_black` black cubes (the check: try all the ways)."""
    base = {c: cube[c] for c in cube if visible_cell(c)}
    out = set()
    for blacks in combinations(range(len(HIDDEN)), hidden_black):
        full = dict(base)
        for k, c in enumerate(HIDDEN):
            full[c] = k in blacks
        out.add(view_of(full, side))
    return out


def all_views():
    return [tuple(tuple(bits[r * 3:(r + 1) * 3]) for r in range(3)) for bits in product([False, True], repeat=9)]


def hamming(a, b):
    return sum(x != y for ra, rb in zip(a, b) for x, y in zip(ra, rb))


# ------------------------------------------------------------------ pictures
def _poly(f, pts, black):
    flat = [c for pt in pts for c in f.p(*pt)]
    f.d.add(Polygon(flat, fillColor=BLACK if black else colors.white, strokeColor=EDGE, strokeWidth=0.8))


def _arrow(f, tail, tip, w=0.14, h=0.3):
    f.line(tail, tip, width=1.6, color=colors.Color(0.93, 0.2, 0.45))
    dx, dy = tip[0] - tail[0], tip[1] - tail[1]
    ln = (dx * dx + dy * dy) ** 0.5
    ux, uy = dx / ln, dy / ln
    base = (tip[0] - ux * h, tip[1] - uy * h)
    px, py = -uy, ux
    f.d.add(Polygon([c for pt in (tip, (base[0] + px * w, base[1] + py * w), (base[0] - px * w, base[1] - py * w))
                     for c in f.p(*pt)], fillColor=colors.Color(0.93, 0.2, 0.45),
                    strokeColor=colors.Color(0.93, 0.2, 0.45), strokeWidth=0.5))


def cube_pic(cube, n=N, side=None, max_px=135):
    """The big cube like the contest: front, top and right faces. `side` adds the arrow of the viewer."""
    left = 1.3 if side == "left" else 0.0
    top = 1.1 if side == "back" else 0.0
    right = 1.2 if side == "back" else 0.0
    w = n + DX * n + left + right
    h = n + DY * n + top
    f = Fig(w, h, max_px=max_px, margin=5)

    def P(x, y, z):
        return (left + x + DX * y, z + DY * y)

    for x in range(n):
        for z in range(n):
            _poly(f, [P(x, 0, z), P(x + 1, 0, z), P(x + 1, 0, z + 1), P(x, 0, z + 1)], cube[(x, 0, z)])
    for x in range(n):
        for y in range(n):
            _poly(f, [P(x, y, n), P(x + 1, y, n), P(x + 1, y + 1, n), P(x, y + 1, n)], cube[(x, y, n - 1)])
    for y in range(n):
        for z in range(n):
            _poly(f, [P(n, y, z), P(n, y + 1, z), P(n, y + 1, z + 1), P(n, y, z + 1)], cube[(n - 1, y, z)])
    if side == "left":
        _arrow(f, (0.0, 1.5), (1.1, 1.5))
    elif side == "back":
        c = P(n, n, n)
        _arrow(f, (c[0] + 1.0, c[1] + 0.85), (c[0] + 0.05, c[1] + 0.04))
    return f.drawing()


def view_pic(v, scale=15):
    f = Fig(3, 3, scale=scale, margin=3)
    for r in range(3):
        for c in range(3):
            _poly(f, [(c, 2 - r), (c + 1, 2 - r), (c + 1, 3 - r), (c, 3 - r)], v[r][c])
    return f.drawing()


# ------------------------------------------------------------------ texts
def _counts(cube):
    black = sum(cube.values())
    seen_black = sum(cube[c] for c in cube if visible_cell(c))
    return black, seen_black


def _view_options(cube, side, hidden_black, rng):
    """Five pictures: the real view + four impossible ones. Returns (views, answer index, labels)."""
    truth = view_of(cube, side)
    possible = possible_views(cube, side, hidden_black)
    cands = [v for v in all_views() if v not in possible and 1 <= hamming(v, truth) <= 3]
    mir = mirror(truth)

    def kind(v):
        if v == mir:
            return "mirror"
        if any(v[r][c] != truth[r][c] for r in range(3) for c in range(3) if is_known(side, r, c)):
            return "known"
        return "count"

    by = {"mirror": [], "known": [], "count": []}
    for v in cands:
        by[kind(v)].append(v)
    for k in by:
        rng.shuffle(by[k])
    if not by["count"]:
        return None                                        # the totals must rule out at least one picture
    wrong = []
    if mir in cands:
        wrong.append(mir)
    wrong += by["count"][:2]
    pool = by["known"] + by["count"][2:]
    wrong += [v for v in pool if v not in wrong][:4 - len(wrong)]
    if len(wrong) < 4:
        return None
    wrong = wrong[:4]
    opts = wrong + [truth]
    rng.shuffle(opts)
    labels = {}
    for i, v in enumerate(opts):
        if v == truth:
            continue
        labels[i] = {"mirror": "turn the picture the wrong way round (left and right swapped)",
                     "known": "forget to copy the cubes you can already see in the drawing",
                     "count": "forget how many black and white cubes there are in all"}[kind(v)]
    return opts, opts.index(truth), labels, kind


def _reason(v, truth, side, hidden_black, kind):
    k = kind(v)
    if k in ("mirror", "known"):
        return "it does not copy the cubes already visible in the drawing"
    unk = [v[r][c] for r in range(3) for c in range(3) if not is_known(side, r, c)]
    b = sum(unk)
    if b > hidden_black:
        return f"it needs {b} black hidden cubes but only {hidden_black} are hidden"
    return f"it needs {4 - b} white hidden cubes but only {8 - hidden_black} are hidden"


def _view_question(rng, side, mode):
    name = rng.choice(PEOPLE)
    for _ in range(3000):
        if mode == "easy":
            col = rng.random() < 0.5                       # hidden cubes all black / all white
            cube = random_cube(rng)
            for c in HIDDEN:
                cube[c] = col
            hb = 8 if col else 0
        else:
            cube = random_cube(rng, rng.choice([0.5, 0.6]))
            _, seen_black = _counts(cube)
            hb = sum(cube[c] for c in HIDDEN)
            if hb not in (1, 2, 3, 5, 6, 7):                 # 4 would rule nothing out
                continue
        truth = view_of(cube, side)
        known_ok = sum(is_known(side, r, c) for r in range(3) for c in range(3)) == 5
        if not known_ok or sum(sum(r) for r in truth) in (0, 9):
            continue
        built = _view_options(cube, side, hb, rng)
        if built is None:
            continue
        opts, ai, labels, kind = built
        break
    else:
        raise RuntimeError("no cube found")
    total, seen_black = _counts(cube)
    intro = (f"{name} looks at the big cube {SIDE_WORDS[side]}, in the direction of the arrow." if side == "left"
             else f"{name} looks at the big cube {SIDE_WORDS[side]}, in the direction of the arrow.")
    if mode == "easy":
        colour = "black" if hb == 8 else "white"
        text = (f"The big cube is made out of small cubes of the same size. In the picture you can see three of its "
                f"faces. All the cubes you <b>cannot</b> see in the picture are {colour}.\n\n{intro} What does she see?")
        sol = ("The five cubes of her picture that are on the faces you can see are copied from the drawing "
               f"(her picture is turned the other way round: {SIDE_WORDS[side]} left and right swap). "
               f"The other four cubes of her picture are hidden in the drawing, so they are {colour}. "
               f"That is picture {'ABCDE'[ai]}.")
    else:
        text = (f"The big cube is made out of {total} black cubes and {27 - total} white cubes, all of the same size. "
                f"{intro} What could she see?")
        reasons = "; ".join(f"{'ABCDE'[i]}: {_reason(v, opts[ai], side, hb, kind)}"
                            for i, v in enumerate(opts) if i != ai)
        sol = (f"First copy the cubes she sees that are also on the faces drawn for you (her picture is turned "
               f"the other way round). The drawing shows {seen_black} black cubes, so {total} - {seen_black} = {hb} "
               f"black and {8 - hb} white cubes are hidden. Check the pictures: {reasons}. "
               f"Only {'ABCDE'[ai]} is possible.")
    possible = possible_views(cube, side, hb)
    return Question(text=text, figure=cube_pic(cube, side=side),
                    choices=Choices([f"picture {L}" for L in "ABCDE"], labels),
                    choice_figures=[view_pic(v) for v in opts], answer=ai, solution=sol,
                    check=lambda i: opts[i] in possible)


# ------------------------------------------------------------------ variants
@variant(difficulty=1)
def hidden_cubes(rng, harder):
    """How many cubes can you not see at all?"""
    n = rng.choice([3, 4] if harder else [2, 3])
    name = rng.choice(PEOPLE)
    cube = {(x, y, z): rng.random() < 0.5 for x in range(n) for y in range(n) for z in range(n)}
    hidden = (n - 1) ** 3
    text = (f"{name} built a big cube from {n ** 3} small cubes. In the picture you can see its front, its top "
            f"and its right side.\n\nHow many of the small cubes can you <b>not</b> see at all in the picture?")
    sol = (f"The cubes you can see are on the front, top or right side. The cubes you cannot see are the ones "
           f"behind the front layer, below the top layer and left of the right layer: that is a smaller cube of "
           f"{n - 1} × {n - 1} × {n - 1} = {hidden}.")
    mistakes = [(n ** 3 - n * n, "count all the cubes behind the front layer"),
                (n ** 3 - 3 * n * n, "count each face as if its cubes were not shared with the other faces"),
                (n ** 3 - 3 * n * n + 3 * n, "count the corner cube, shared by three faces, as hidden"),
                (n ** 3, "count all the cubes")]
    choices, ai = numeric_choices(hidden, mistakes, rng, lo=1, order="asc")

    def check(i):                      # count cells that touch none of the three faces
        k = int(choices[i].split()[0])
        return k == sum(1 for x in range(n) for y in range(n) for z in range(n)
                        if y != 0 and z != n - 1 and x != n - 1)
    return Question(text=text, figure=cube_pic(cube, n=n, max_px=110 if n < 4 else 125),
                    choices=choices, answer=ai, solution=sol, check=check)


@variant(difficulty=2)
def hidden_black(rng, harder):
    """Given the totals: how many black (or white) cubes are hidden?"""
    name = rng.choice(PEOPLE)
    while True:
        cube = random_cube(rng, 0.55)
        total, seen_black = _counts(cube)
        hb = total - seen_black
        if 2 <= hb <= 6:
            break
    ask_white = harder and rng.random() < 0.5
    if ask_white:
        ans, word, other = 8 - hb, "white", "black"
        seen_w = 19 - seen_black
        total_w = 27 - total
        text = (f"{name} made a big cube from {total} black cubes and {total_w} white cubes. In the picture you can "
                f"see its front, top and right side.\n\nHow many of the cubes you cannot see in the picture are white?")
        sol = (f"The picture shows 19 cubes: {seen_black} black and {seen_w} white. So {total_w} - {seen_w} = {ans} "
               f"white cubes are hidden.")
        mistakes = [(seen_w, "count the white cubes you can see"), (total_w, "count all the white cubes"),
                    (hb, "count the hidden black cubes"), (seen_black, "count the black cubes you can see")]
        truth = sum(not cube[c] for c in HIDDEN)
    else:
        ans, word = hb, "black"
        text = (f"{name} made a big cube from {total} black cubes and {27 - total} white cubes. In the picture you can "
                f"see its front, top and right side.\n\nHow many of the cubes you cannot see in the picture are black?")
        sol = (f"The picture shows 19 cubes, {seen_black} of them black. So {total} - {seen_black} = {ans} "
               f"black cubes are hidden.")
        mistakes = [(seen_black, "count the black cubes you can see"), (total, "count all the black cubes"),
                    (8 - hb, "count the hidden white cubes"), (19 - seen_black, "count the white cubes you can see")]
        truth = sum(cube[c] for c in HIDDEN)
    choices, ai = numeric_choices(ans, mistakes, rng, lo=0, order="asc")
    return Question(text=text, figure=cube_pic(cube), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, truth))


@variant(difficulty=2)
def easy_view(rng, harder):
    """The hidden cubes all have one colour: what does she see from the left / from behind?"""
    return _view_question(rng, rng.choice(["left", "back"]) if harder else "left", "easy")


@variant(difficulty=3)
def left_view(rng, harder):
    """The original: totals of black and white given; what could she see from the left?"""
    return _view_question(rng, "left", "count")


@variant(difficulty=3)
def back_view(rng, harder):
    """The same from behind."""
    return _view_question(rng, "back", "count")
