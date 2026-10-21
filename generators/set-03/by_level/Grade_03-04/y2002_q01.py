"""2002 Q1 - which square was removed from the picture?

Original: a picture of a kangaroo is drawn on a 4 x 3 grid and one square is
missing. Which of the five squares A-E was removed?  Answer: B.

Core skill: matching a piece to a gap by its edges - where the lines of the
neighbouring squares reach the gap, the missing square must have a line at the
same place on the same side. Children pick a square that "looks like" the
picture but is turned, mirrored, or has a line missing.

Pictures are smooth random curves (paths, strings, rivers) on squared paper, so
every square shows only bits of lines; each square is cut out by clipping the
curves. The answer check reads the crossings straight off the curves (where they
cut the grid lines) and compares them with the line ends at the border of each
option as it is drawn.
"""
import math

from reportlab.lib import colors

from kangaroo import Fig, Question, variant
from kangaroo.figures import LIGHT, row

META = {
    "source": "set-03/by_level/Grade_03-04/2002 Q1",
    "skill": "Find the missing square by its edges: lines must continue at the same places, not turned",
    "topics": ["spatial", "visual"],
    "version": 2,
}

CELL = 32          # points per square, in the picture and in the options
LINE = 1.4
STORIES = [
    "Some paths go across a park. The map was drawn on squared paper, and one square was cut out.",
    "Mia drew some lines on squared paper. Then she cut out one square of her picture.",
    "Leo painted a river and some roads on a map made of squares. One square of the map is missing.",
    "A cat played with balls of wool on squared paper. Now one square of the picture is missing.",
]


# ---------------------------------------------------------------- the picture
def _spline(points, per=24):
    """Smooth curve through the points (Catmull-Rom), as a list of many points."""
    pts = [points[0]] + list(points) + [points[-1]]
    out = []
    for k in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[k - 1], pts[k], pts[k + 1], pts[k + 2]
        for s in range(per):
            t = s / per
            out.append(tuple(0.5 * ((2 * p1[d]) + (-p0[d] + p2[d]) * t
                                    + (2 * p0[d] - 5 * p1[d] + 4 * p2[d] - p3[d]) * t * t
                                    + (-p0[d] + 3 * p1[d] - 3 * p2[d] + p3[d]) * t ** 3) for d in (0, 1)))
    out.append(points[-1])
    return out


def _loop(rng, cx, cy, r, per=24):
    """A closed wobbly loop (like a ball of wool or a pond)."""
    n = 6
    ctrl = [(cx + r * (0.75 + 0.35 * rng.random()) * math.cos(2 * math.pi * k / n),
             cy + r * (0.75 + 0.35 * rng.random()) * math.sin(2 * math.pi * k / n)) for k in range(n)]
    out = []
    for k in range(n):
        p0, p1, p2, p3 = (ctrl[(k + d) % n] for d in (-1, 0, 1, 2))
        for s in range(per):
            t = s / per
            out.append(tuple(0.5 * ((2 * p1[d]) + (-p0[d] + p2[d]) * t
                                    + (2 * p0[d] - 5 * p1[d] + 4 * p2[d] - p3[d]) * t * t
                                    + (-p0[d] + 3 * p1[d] - 3 * p2[d] + p3[d]) * t ** 3) for d in (0, 1)))
    return out + out[:1]


def make_picture(rng, C, R, n_curves):
    curves = []
    for _ in range(n_curves):
        if rng.random() < 0.25:
            r = rng.uniform(0.7, 1.1)
            curves.append(_loop(rng, rng.uniform(r + 0.1, C - r - 0.1), rng.uniform(r + 0.1, R - r - 0.1), r))
        else:
            curves.append(_spline(_walk(rng, C, R)))
    return None if hugs_grid(curves, C, R) else curves


def _walk(rng, C, R):
    """Control points of a calm path across the picture: it starts outside one edge, then takes
    steps of 1.2-1.8 squares, turning at most 50 degrees, until it leaves the picture."""
    while True:
        side = rng.randrange(4)
        t = rng.uniform(0.3, 0.7)
        x, y, a = [(t * C, -0.3, math.pi / 2), (C + 0.3, t * R, math.pi), (t * C, R + 0.3, -math.pi / 2),
                   (-0.3, t * R, 0)][side]
        a += rng.uniform(-0.6, 0.6)
        pts = [(x, y)]
        for _ in range(12):
            a += rng.uniform(-0.87, 0.87)
            step = rng.uniform(1.2, 1.8)
            x, y = x + step * math.cos(a), y + step * math.sin(a)
            pts.append((x, y))
            if not (-0.2 < x < C + 0.2 and -0.2 < y < R + 0.2):
                break
        inside = sum(0 < px < C and 0 < py < R for px, py in pts)
        if inside >= 2 and not (-0.2 < x < C + 0.2 and -0.2 < y < R + 0.2):
            return pts


def hugs_grid(curves, C, R, near=0.08, run=6):
    """A curve that runs along a grid line for a while (hard to see which square it is in):
    several steps in a row close to a grid line and moving almost parallel to it."""
    for c in curves:
        for coord in (0, 1):
            streak = 0
            for p, q in zip(c, c[1:]):
                across = abs(q[coord] - p[coord])
                along = abs(q[1 - coord] - p[1 - coord])
                close = abs(p[coord] - round(p[coord])) < near and 0 <= p[0] <= C and 0 <= p[1] <= R
                streak = streak + 1 if close and across < 0.4 * along else 0
                if streak >= run:
                    return True
    return False


# ---------------------------------------------------------------- cutting out squares
def _clip(a, b, x0, y0):
    """The part of segment a-b inside the square [x0, x0+1] x [y0, y0+1] (Liang-Barsky), or None."""
    (x1, y1), (x2, y2) = a, b
    dx, dy = x2 - x1, y2 - y1
    lo, hi = 0.0, 1.0
    for p, q in ((-dx, x1 - x0), (dx, x0 + 1 - x1), (-dy, y1 - y0), (dy, y0 + 1 - y1)):
        if p == 0:
            if q < 0:
                return None
            continue
        t = q / p
        if p < 0:
            lo = max(lo, t)
        else:
            hi = min(hi, t)
        if lo > hi:
            return None
    if hi - lo < 1e-9:
        return None
    return ((x1 + lo * dx - x0, y1 + lo * dy - y0), (x1 + hi * dx - x0, y1 + hi * dy - y0))


def tile(curves, cell):
    """What square (i, j) shows: little segments in its own 0..1 coordinates."""
    i, j = cell
    out = []
    for c in curves:
        for a, b in zip(c, c[1:]):
            s = _clip(a, b, i, j)
            if s:
                out.append(s)
    return out


def turn(segs, quarter=0, mirror=False):
    """Turn a square a quarter turn (anticlockwise) `quarter` times, mirrored left-right first if asked."""
    def f(p):
        u, v = p
        if mirror:
            u = 1 - u
        for _ in range(quarter):
            u, v = 1 - v, u
        return (u, v)
    return [(f(a), f(b)) for a, b in segs]


# ---------------------------------------------------------------- answer checks: edges
SIDES = ("bottom", "right", "top", "left")


def drawn_edges(segs):
    """Where the lines of a drawn square reach its border: {side: sorted positions}."""
    out = {s: [] for s in SIDES}
    for seg in segs:
        for u, v in seg:
            if abs(v) < 1e-7:
                out["bottom"].append(u)
            elif abs(v - 1) < 1e-7:
                out["top"].append(u)
            elif abs(u) < 1e-7:
                out["left"].append(v)
            elif abs(u - 1) < 1e-7:
                out["right"].append(v)
    return {s: sorted(p) for s, p in out.items()}


def picture_edges(curves, cell):
    """Where the curves cut the four grid lines around square (i, j) - worked out from the curves,
    not from the cut-out squares: {side: sorted positions}."""
    i, j = cell
    out = {s: [] for s in SIDES}
    for c in curves:
        for (x1, y1), (x2, y2) in zip(c, c[1:]):
            for side, horiz, k in (("bottom", True, j), ("top", True, j + 1), ("left", False, i), ("right", False, i + 1)):
                a, b = (y1, y2) if horiz else (x1, x2)
                if (a - k) * (b - k) < 0:
                    t = (k - a) / (b - a)
                    pos = (x1 + t * (x2 - x1)) - i if horiz else (y1 + t * (y2 - y1)) - j
                    if 0 < pos < 1:
                        out[side].append(pos)
    return {s: sorted(p) for s, p in out.items()}


def same_edges(e1, e2, tol=0.2):
    """Do the lines reach the edges at the same places, as far as an eye can tell? Places closer
    than a fifth of a side count as the same, so every wrong option differs clearly."""
    return all(len(e1[s]) == len(e2[s]) and all(abs(a - b) < tol for a, b in zip(e1[s], e2[s])) for s in SIDES)


def clear_edges(e, need_sides=2, need=3):
    """Crossings not too close to a corner or to each other, on enough sides: easy to compare by eye."""
    for s in SIDES:
        p = e[s]
        if any(x < 0.22 or x > 0.78 for x in p) or any(b - a < 0.2 for a, b in zip(p, p[1:])):
            return False
    return sum(1 for s in SIDES if e[s]) >= need_sides and sum(len(e[s]) for s in SIDES) >= need


def describe(e):
    word = {0: "no line", 1: "1 line"}
    return ", ".join(f"{s}: {word.get(len(e[s]), f'{len(e[s])} lines')}" for s in ("top", "right", "bottom", "left"))


# ---------------------------------------------------------------- drawing
def _chains(segs):
    """Join segments that continue each other into longer lines (so they are drawn without seams)."""
    out = []
    for a, b in segs:
        if out and abs(out[-1][-1][0] - a[0]) < 1e-9 and abs(out[-1][-1][1] - a[1]) < 1e-9:
            out[-1].append(b)
        else:
            out.append([a, b])
    return out


def picture_pic(curves, C, R, blanks=(), labels=None, scale=CELL):
    f = Fig(C, R, scale=scale, margin=3)
    for b in blanks:
        f.rect(b[0], b[1], 1, 1, fill=LIGHT, width=0)
        if labels:
            f.text(b[0] + 0.5, b[1] + 0.5, labels[b], size=11)
    for i in range(C):
        for j in range(R):
            if (i, j) in blanks:
                continue
            for ch in _chains(tile(curves, (i, j))):
                f.polyline([(u + i, v + j) for u, v in ch], width=LINE)
    for i in range(C + 1):
        f.line((i, 0), (i, R), width=0.8)
    for j in range(R + 1):
        f.line((0, j), (C, j), width=0.8)
    return f.drawing()


def tile_pic(segs, scale=CELL):
    f = Fig(1, 1, scale=scale, margin=3)
    f.rect(0, 0, 1, 1, fill=colors.white, width=0.9)
    for ch in _chains(segs):
        f.polyline(ch, width=LINE)
    return f.drawing()


# ---------------------------------------------------------------- building a puzzle
def _size(harder):
    return (5, 4, 3) if harder else (4, 3, 2)


def _pick_gap(rng, curves, C, R, inner_only=False):
    cells = [(i, j) for i in range(C) for j in range(R)
             if not inner_only or (0 < i < C - 1 and 0 < j < R - 1)]
    rng.shuffle(cells)
    for c in cells:
        if clear_edges(picture_edges(curves, c)):
            return c
    return None


def _variants_of(segs):
    """The square turned and mirrored: [(how, segments)]."""
    out = []
    for m in (False, True):
        for q in range(4):
            if (q, m) != (0, False):
                out.append((("mirrored and " if m and q else "mirrored" if m else "") +
                            {0: "", 1: "turned", 2: "upside down", 3: "turned"}[q], turn(segs, q, m)))
    return out


def _distinct(cands, avoid, n):
    """Up to n candidates whose edges differ from everything in avoid and from each other."""
    chosen = []
    for why, segs in cands:
        e = drawn_edges(segs)
        if any(same_edges(e, a) for a in avoid) or any(same_edges(e, drawn_edges(s)) for _, s in chosen):
            continue
        chosen.append((why, segs))
        if len(chosen) == n:
            break
    return chosen


def _missing_square(rng, harder, turned_only):
    C, R, n = _size(harder)
    for _ in range(1000):
        curves = make_picture(rng, C, R, n)
        if curves is None:
            continue
        gap = _pick_gap(rng, curves, C, R)
        if gap is None:
            continue
        true = tile(curves, gap)
        e_true = picture_edges(curves, gap)
        turned = _variants_of(true)
        rng.shuffle(turned)
        if turned_only:
            wrong = _distinct(turned, [e_true], 4)
        else:
            others = [("from another place", tile(curves, c)) for c in
                      rng.sample([(i, j) for i in range(C) for j in range(R) if (i, j) != gap], C * R - 1)]
            others = [o for o in others if sum(map(len, drawn_edges(o[1]).values())) >= 2]
            lines = sorted({k for k, c in enumerate(curves) if tile([c], gap)})
            dropped = [("a line is missing", tile([c for k, c in enumerate(curves) if k != drop], gap))
                       for drop in lines] if len(lines) > 1 else []
            pool = (turned[:2] + others[:2] + dropped[:1]) if harder else (others[:3] + turned[:2] + dropped[:1])
            wrong = _distinct(pool + turned + others, [e_true], 4)
        if len(wrong) == 4:
            return C, R, curves, gap, true, e_true, wrong
    raise RuntimeError("no picture found")


def _question(rng, harder, turned_only):
    C, R, curves, gap, true, e_true, wrong = _missing_square(rng, harder, turned_only)
    opts = [s for _, s in wrong] + [true]
    rng.shuffle(opts)
    k = opts.index(true)
    if turned_only:
        text = ("One square was cut out of this picture. Here it is five times, turned in different ways "
                "(and sometimes flipped over).")
        after = "Which one fits back into the gap?"
    else:
        text = rng.choice(STORIES)
        after = "Which square was cut out of the picture?"
    sol = (f"Look where the lines of the picture reach the grey gap: {describe(e_true)}. "
           f"Only square {'ABCDE'[k]} has its lines in exactly those places"
           + (" without being turned." if not turned_only else " in this position.")
           + " The others are " + ", ".join(sorted({w for w, _ in wrong})) + ".")
    return Question(text=text, figure=picture_pic(curves, C, R, blanks=[gap]), after_figure=after,
                    choices=[f"square {c}" for c in "ABCDE"], answer=k,
                    choice_figures=[tile_pic(o) for o in opts], solution=sol,
                    check=lambda i: same_edges(drawn_edges(opts[i]), picture_edges(curves, gap)))


# ---------------------------------------------------------------- variants
@variant(difficulty=1)
def missing_square(rng, harder):
    """The original: the gap's square among squares from elsewhere, turned ones, one with a line missing."""
    return _question(rng, harder, turned_only=False)


@variant(difficulty=1)
def not_a_piece(rng, harder):
    """The whole picture is shown; four squares are pieces of it, one is not."""
    C, R, n = _size(harder)
    for _ in range(1000):
        curves = make_picture(rng, C, R, n)
        if curves is None:
            continue
        cells = [(i, j) for i in range(C) for j in range(R) if clear_edges(picture_edges(curves, (i, j)), 2, 2)]
        if len(cells) < 5:
            continue
        rng.shuffle(cells)
        real = _distinct([("real", tile(curves, c)) for c in cells], [], 4)
        if len(real) < 4:
            continue
        everywhere = [picture_edges(curves, (i, j)) for i in range(C) for j in range(R)]
        fakes = [f for c in cells for f in _variants_of(tile(curves, c))]
        rng.shuffle(fakes)
        fake = _distinct(fakes, everywhere, 1)
        if fake:
            break
    else:
        raise RuntimeError("no picture found")
    opts = [s for _, s in real] + [fake[0][1]]
    rng.shuffle(opts)
    k = opts.index(fake[0][1])
    text = rng.choice(STORIES).split(".")[0] + ". Here is the whole picture."
    after = "Which of these squares is <b>not</b> a piece of the picture?"
    sol = (f"Find each square in the picture by the places where its lines reach the edges. Squares "
           f"{', '.join('ABCDE'[i] for i in range(5) if i != k)} can be found; square {'ABCDE'[k]} is a piece "
           f"{fake[0][0]}, so it is not in the picture like that.")
    return Question(text=text, figure=picture_pic(curves, C, R), after_figure=after,
                    choices=[f"square {c}" for c in "ABCDE"], answer=k,
                    choice_figures=[tile_pic(o) for o in opts], solution=sol,
                    check=lambda i: not any(same_edges(drawn_edges(opts[i]), e) for e in everywhere))


@variant(difficulty=2)
def turned_square(rng, harder):
    """All five options are the right square, turned or flipped: only one way fits."""
    return _question(rng, harder, turned_only=True)


@variant(difficulty=3)
def which_gap(rng, harder):
    """Five squares are missing (A-E); into which gap does this square fit?"""
    C, R, n = (6, 4, 4) if harder else (5, 4, 3)
    for _ in range(1000):
        curves = make_picture(rng, C, R, n)
        if curves is None:
            continue
        ok = [(i, j) for i in range(C) for j in range(R) if clear_edges(picture_edges(curves, (i, j)), 2, 2)]
        rng.shuffle(ok)
        gaps = []
        for c in ok:                      # gaps never side by side, so every gap edge is visible
            if all(abs(c[0] - g[0]) + abs(c[1] - g[1]) > 1 for g in gaps):
                gaps.append(c)
            if len(gaps) == 5:
                break
        if len(gaps) < 5:
            continue
        gaps.sort(key=lambda g: (-g[1], g[0]))       # letters in reading order
        edges = [picture_edges(curves, g) for g in gaps]
        # the cut-out square must clearly fit only one gap (the other gaps may look alike)
        unique = [a for a in range(5) if not any(same_edges(edges[a], edges[b]) for b in range(5) if b != a)]
        if unique:
            break
    else:
        raise RuntimeError("no picture found")
    names = {g: "ABCDE"[i] for i, g in enumerate(gaps)}
    k = rng.choice(unique)
    piece = tile(curves, gaps[k])
    fig = row([picture_pic(curves, C, R, blanks=gaps, labels=names), tile_pic(piece, scale=CELL + 4)], gap=28)
    text = (rng.choice(STORIES).split(".")[0] + ". Five squares are missing, marked A to E. "
            "The square on the right is one of them (it is not turned).")
    after = "Which gap does it fit into?"
    sol = (f"The square has {describe(drawn_edges(piece))}. Only gap {names[gaps[k]]} has lines reaching "
           f"it at exactly those places.")
    return Question(text=text, figure=fig, after_figure=after, choices=[f"gap {c}" for c in "ABCDE"],
                    answer=k, solution=sol,
                    check=lambda i: same_edges(drawn_edges(piece), picture_edges(curves, gaps[i])))
