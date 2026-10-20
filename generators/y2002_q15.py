"""2002 Q15 - silhouettes of a flag in the wind: which one is impossible?

Original: From her window Karla looks at the wall of a house where she sees the
silhouette of a rectangular flag flying in the wind. At five moments she draws
the silhouette. Which of the 5 pictures cannot be right unless the flag is torn?
In picture B the flag does not cover the whole pole edge: part of the edge that
is sewn to the pole is missing.  Answer: B.

Core skill: knowing what stays the same while a shape moves. The side of the
flag fixed to the pole always shows at full length; the flag can look narrower
(it turns away) but never wider than it really is. Children look at the "messy"
outlines instead of checking these two facts.
"""
import math

from reportlab.lib import colors

from kangaroo import Fig, Question, variant
from kangaroo.figures import GREY, LIGHT, column, row

META = {
    "source": "2002 Q15",
    "skill": "What cannot change when a flag or door moves: the fixed edge stays whole, nothing gets wider",
    "topics": ["spatial", "logic", "geometry"],
    "version": 2,
}

NAMES = ["Karla", "Mia", "Leo", "Sara", "Tom", "Nina"]
GRIDC = colors.Color(0.78, 0.78, 0.78)

# ------------------------------------------------------------------ geometry
# A flag is w wide and h tall, sewn to the pole (x = 0) from y = 0 to y = h.
# A silhouette is a polygon; possible ones keep that pole edge and stay within reach.


def _area(pts):
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]))) / 2


def _reach(x, y, h):
    """Distance from (x, y) to the pole edge."""
    dy = 0 if 0 <= y <= h else (y if y < 0 else y - h)
    return math.hypot(x, dy)


def possible_shape(rng, w, h):
    """A random silhouette the flag can really make (half-unit corners)."""
    for _ in range(200):
        kind = rng.choice(["turned", "slant", "flap", "flap", "wave"])
        if kind == "turned":                       # flag turned away: a narrower rectangle
            c = rng.choice([x / 2 for x in range(2, 2 * w)])
            pts = [(0, 0), (0, h), (c, h), (c, 0)]
        elif kind == "slant":                      # free edge slanted (like E)
            c1, c2 = rng.sample([x / 2 for x in range(2, 2 * w + 1)], 2)
            pts = [(0, 0), (0, h), (c1, h), (c2, 0)]
        elif kind == "flap":                       # a corner lifted or drooping (like A, D)
            up = rng.choice([0.5, 1.0])
            ct = rng.choice([x / 2 for x in range(1, 2 * w - 1)])
            cf = rng.choice([x / 2 for x in range(3, 2 * w + 1)])
            ym = rng.choice([y / 2 for y in range(1, 2 * h)])
            cb = rng.choice([x / 2 for x in range(1, 2 * w - 1)])
            pts = [(0, 0), (0, h), (ct, h + up), (cf, ym), (cb, rng.choice([0, -0.5]))]
        else:                                      # wavy free edge
            xs = [rng.choice([x / 2 for x in range(3, 2 * w + 1)]) for _ in range(3)]
            pts = [(0, 0), (0, h), (xs[0], h), (xs[1], h / 2), (xs[2], 0)]
        if _ok(pts, w, h):
            return pts
    return [(0, 0), (0, h), (w - 1, h), (w - 1, 0)]


def _ok(pts, w, h):
    return (all(0 <= x <= w and _reach(x, y, h) <= w for x, y in pts)
            and _area(pts) <= w * h * 0.95 and _simple(pts))


def _simple(pts):
    """No two non-neighbouring edges cross."""
    def cross(p, q, r, s):
        def o(a, b, c):
            return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        return o(p, q, r) * o(p, q, s) < 0 and o(r, s, p) * o(r, s, q) < 0
    n = len(pts)
    edges = [(pts[i], pts[(i + 1) % n]) for i in range(n)]
    return not any(cross(*edges[i], *edges[j]) for i in range(n) for j in range(i + 2, n)
                   if not (i == 0 and j == n - 1))


def torn_shape(rng, w, h, where=None):
    """Part of the pole edge is bare - only possible if the flag is torn (like B)."""
    where = where or rng.choice(["bottom", "bottom", "top"])
    g = rng.choice([h / 3, h / 2]) if h >= 3 else h / 2
    g = round(g * 2) / 2
    c = rng.choice([x / 2 for x in range(2, 2 * w - 1)])
    far = rng.choice([x / 2 for x in range(2 * w - 2, 2 * w + 1)])
    if where == "bottom":     # bare at the bottom of the pole
        return [(0, g), (0, h), (far, h), (c, 0), (1, 0), (1, g)]
    return [(0, 0), (0, h - g), (1, h - g), (1, h), (far, h), (c, 0)]


def wide_shape(rng, w, h):
    """Wider than the flag itself."""
    extra = rng.choice([1, 1.5]) if w <= 3 else rng.choice([1, 1.5, 2])
    kind = rng.choice(["rect", "slant"])
    if kind == "rect":
        return [(0, 0), (0, h), (w + extra, h), (w + extra, 0)]
    return [(0, 0), (0, h), (w + extra, h), (w - 1, 0)]


# ------------------------------------------------------------------ drawing
def _scale(w):
    """Points per unit: as big as fits in one answer column (all five share it, so sizes compare)."""
    return min(12.0, 64 / (w + 2.2))


def _caption(drawing, label, size=10):
    lab = Fig(10, 1, scale=10, margin=0)
    lab.text(5, 0.5, label, size=size)
    return column([drawing, lab.drawing()], gap=2)


def flag_pic(pts, w, h, grid=False):
    """Pole plus grey silhouette, in a frame that is the same for every picture."""
    W, top, bot = w + 2.2, h + 1.6, -1.6
    scale = _scale(w)
    f = Fig(W, top - bot, scale=scale, margin=4)
    sh = lambda x, y: (x + 0.2, y - bot)
    if grid:
        for gx in range(0, int(W) + 1):
            f.line(sh(gx, bot + 0.6), sh(gx, top - 0.4), width=0.4, color=GRIDC)
        for gy in range(int(bot + 1), int(top)):
            f.line(sh(0, gy), sh(W - 0.4, gy), width=0.4, color=GRIDC)
    f.poly([sh(x, y) for x, y in pts], fill=GREY, width=0.9)
    f.line(sh(0, bot + 0.3), sh(0, top - 0.2), width=3.2)
    return f.drawing()


def flat_flag(w, h, label):
    f = Fig(w + 2.2, h + 1.0, scale=_scale(w), margin=4)
    for gx in range(0, w + 2):
        f.line((gx + 0.2, 0.5), (gx + 0.2, h + 0.9), width=0.4, color=GRIDC)
    for gy in range(1, h + 1):
        f.line((0.2, gy), (w + 1.6, gy), width=0.4, color=GRIDC)
    f.rect(0.2, 0.5, w, h, fill=GREY, width=0.9)
    f.line((0.2, 0.2), (0.2, h + 1.0), width=3.2)
    return _caption(f.drawing(), label)


def _size(rng, harder):
    return rng.choice([(4, 3), (5, 3), (4, 2)] if harder else [(3, 2), (4, 2), (4, 3)])


def _intro(name):
    return (f"A rectangular flag flies on a pole in front of a wall, and the sun throws its shadow "
            f"onto the wall. The wind turns and folds the flag, but the side sewn to the pole always "
            f"stays on the pole. {name} draws the shadow at five different moments.")


# ------------------------------------------------------------------ variants
@variant(difficulty=1)
def torn_flag(rng, harder):
    """The original: four real silhouettes and one where the pole edge is not all there."""
    w, h = _size(rng, harder)
    name = rng.choice(NAMES)
    pics = [possible_shape(rng, w, h) for _ in range(4)]
    bad = torn_shape(rng, w, h)
    k = rng.randint(0, 4)
    pics.insert(k, bad)
    figs = [flag_pic(p, w, h) for p in pics]
    text = _intro(name)
    after = "Which picture cannot be right unless the flag is torn?"
    sol = (f"The side sewn to the pole always shows at its full length. In picture {'ABCDE'[k]} part "
           f"of the pole is bare, so a piece of the flag is missing.")
    return Question(text=text, after_figure=after, choices=[f"picture {c}" for c in "ABCDE"],
                    answer=k, choice_figures=figs, solution=sol)


@variant(difficulty=1)
def door(rng, harder):
    """A hinged door seen from the front: same height, never wider."""
    w, h = rng.choice([(3, 4), (2, 4), (3, 5)] if not harder else [(4, 5), (3, 5), (4, 6)])
    name = rng.choice(NAMES)
    widths = rng.sample([x / 2 for x in range(1, 2 * w + 1)], 4)
    pics = [[(0, 0), (0, h), (c, h), (c, 0)] for c in widths]
    kind = rng.choice(["wide", "short", "tall"])
    if kind == "wide":
        bad = [(0, 0), (0, h), (w + 1, h), (w + 1, 0)]
        why = "it is wider than the door itself"
    elif kind == "short":
        bad = [(0, 0), (0, h - 1), (w - 0.5, h - 1), (w - 0.5, 0)]
        why = "it is shorter than the door, but turning never changes the height"
    else:
        bad = [(0, 0), (0, h + 1), (w - 1, h + 1), (w - 1, 0)]
        why = "it is taller than the door, but turning never changes the height"
    k = rng.randint(0, 4)
    pics.insert(k, bad)

    def pic(pts):
        f = Fig(w + 1.6, h + 2.0, scale=min(12.0, 74 / (h + 2.0)), margin=4)
        for gx in range(0, w + 2):
            f.line((gx + 0.3, 0.3), (gx + 0.3, h + 1.8), width=0.4, color=GRIDC)
        for gy in range(1, h + 2):
            f.line((0.3, gy + 0.3), (w + 1.5, gy + 0.3), width=0.4, color=GRIDC)
        f.poly([(x + 0.3, y + 0.3) for x, y in pts], fill=LIGHT, width=1.0)
        f.line((0.3, 0.3), (0.3, max(y for _, y in pts) + 0.3), width=2.6)   # hinge side
        return f.drawing()

    text = (f"A cupboard door is {w} squares wide and {h} squares tall. Its hinges are on the left "
            f"side (thick line). {name} looks at it straight from the front while it slowly opens, "
            f"and draws what the door looks like at five moments.")
    after = "Which picture cannot be right?"
    sol = (f"When a door opens it looks narrower, but it keeps the same height and is never wider "
           f"than {w} squares. Picture {'ABCDE'[k]} is wrong: {why}.")
    return Question(text=text, after_figure=after, choices=[f"picture {c}" for c in "ABCDE"],
                    answer=k, choice_figures=[pic(p) for p in pics], solution=sol)


@variant(difficulty=2)
def too_wide(rng, harder):
    """The flat flag is shown on squares; one shadow is wider than the flag."""
    w, h = _size(rng, harder)
    name = rng.choice(NAMES)
    pics = [possible_shape(rng, w, h) for _ in range(4)]
    k = rng.randint(0, 4)
    pics.insert(k, wide_shape(rng, w, h))
    text = (_intro(name) + f" Spread out flat, the flag is {w} squares wide and {h} squares tall "
            f"(see the picture).")
    after = "Which shadow cannot be right?"
    sol = (f"Turning or folding can only make the flag look narrower. Picture {'ABCDE'[k]} reaches more "
           f"than {w} squares away from the pole, which is wider than the flag.")
    return Question(text=text, figure=flat_flag(w, h, "the flag, flat"), after_figure=after,
                    choices=[f"picture {c}" for c in "ABCDE"], answer=k,
                    choice_figures=[flag_pic(p, w, h, grid=True) for p in pics], solution=sol)


def _mixed(rng, w, h, n_bad):
    """5 (shape, is_wrong) pairs: n_bad wrong ones (torn or too wide), the rest possible."""
    bads = [torn_shape(rng, w, h) if rng.random() < 0.5 else wide_shape(rng, w, h)
            for _ in range(n_bad)]
    items = [(p, False) for p in (possible_shape(rng, w, h) for _ in range(5 - n_bad))]
    items += [(b, True) for b in bads]
    rng.shuffle(items)
    return items


@variant(difficulty=2)
def count_possible(rng, harder):
    """How many of the five shadows could be right?"""
    w, h = _size(rng, harder)
    name = rng.choice(NAMES)
    n_bad = rng.randint(1, 4)
    items = _mixed(rng, w, h, n_bad)
    ans = 5 - n_bad
    text = (_intro(name) + f" Flat, the flag is {w} squares wide and {h} squares tall (see the picture). "
            f"Some of the drawings are wrong.")
    after = "How many of the five drawings can be right?"
    wrong = ["ABCDE"[i] for i, (_, bad) in enumerate(items) if bad]
    sol = (f"A drawing is wrong if part of the pole edge is bare or if it reaches more than {w} squares "
           f"from the pole. Wrong: {', '.join(wrong)}. So {ans} can be right.")
    figs = [_caption(flag_pic(p, w, h, grid=True), "ABCDE"[i], size=11) for i, (p, _) in enumerate(items)]
    fig = column([flat_flag(w, h, "the flag, flat"), row(figs, gap=10)], gap=6)
    start = rng.choice([s for s in (0, 1) if s <= ans <= s + 4])   # five of 0..5, never more than 5
    choices, ai = [str(v) for v in range(start, start + 5)], ans - start
    return Question(text=text, figure=fig, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=3)
def only_one_right(rng, harder):
    """Reverse: four drawings are impossible (torn or too wide); which one can be right?"""
    w, h = _size(rng, harder)
    name = rng.choice(NAMES)
    items = _mixed(rng, w, h, 4)
    k = next(i for i, (_, bad) in enumerate(items) if not bad)
    text = (_intro(name) + f" Flat, the flag is {w} squares wide and {h} squares tall (see the picture). "
            f"Four of the drawings are wrong.")
    after = "Which drawing can be right?"
    sol = (f"Check two things: the pole edge must be covered all the way, and nothing may reach more "
           f"than {w} squares from the pole. Only picture {'ABCDE'[k]} passes both checks.")
    return Question(text=text, figure=flat_flag(w, h, "the flag, flat"), after_figure=after,
                    choices=[f"picture {c}" for c in "ABCDE"], answer=k,
                    choice_figures=[flag_pic(p, w, h, grid=True) for p, _ in items], solution=sol)
