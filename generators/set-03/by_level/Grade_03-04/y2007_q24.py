"""2007 Q24 - fold a square twice, cut off a corner, unfold: which design is impossible?

Original: A square of paper is folded twice so that the result is a square again.
One corner of the new square is cut out and the paper is unfolded. Which design
cannot be obtained this way? A: all four corners cut (octagon), B and C: notches
in the middle of two opposite sides, D: a diamond hole in the middle,
E: all of these designs can be obtained.  Answer: E.

Core skill: folding/cutting symmetry - after two folds the small square has
four corners: the centre of the paper, a real paper corner, and two middles of
paper edges. One cut is copied four times (mirrored over both folds), so the
design is always symmetric left-right and top-bottom.
"""
from reportlab.graphics.shapes import Polygon
from reportlab.lib import colors

from kangaroo import Fig, Question, value_check, variant
from kangaroo.figures import GREY, column, row

META = {
    "source": "2007 Q24",
    "skill": "Fold twice, cut, unfold: one cut is mirrored over both folds (4 copies, symmetric)",
    "topics": ["spatial", "geometry"],
    "version": 3,
}

Q = 4.0                     # the folded square is [0, Q] x [0, Q]; the paper is [-Q, Q] x [-Q, Q]
# corners of the folded square: centre of the paper, paper corner, middle of right edge, middle of top edge
CORNERS = {"centre": (0, 0), "corner": (Q, Q), "side_lr": (Q, 0), "side_tb": (0, Q)}
WHAT = {"centre": "a hole in the middle", "corner": "all four corners cut off",
        "side_lr": "notches in the middle of the left and right sides",
        "side_tb": "notches in the middle of the top and bottom sides"}


def cut_shape(corner, kind, s):
    """The piece cut from the folded square at `corner` (a triangle or a square of size s)."""
    cx, cy = CORNERS[corner]
    dx = 1 if cx == 0 else -1
    dy = 1 if cy == 0 else -1
    if kind == "triangle":
        return [(cx, cy), (cx + dx * s, cy), (cx, cy + dy * s)]
    return [(cx, cy), (cx + dx * s, cy), (cx + dx * s, cy + dy * s), (cx, cy + dy * s)]


def unfold(poly):
    """All four mirror copies of a cut (the cut goes through all four layers)."""
    out = []
    for mx in (1, -1):
        for my in (1, -1):
            out.append([(mx * x, my * y) for x, y in poly])
    return _dedupe(out)


# ---------------------------------------------------------------- answer checks
# The paper is split into N x N little cells (i, j); folding twice puts cell i on top of cell
# N - 1 - i (left-right) and likewise for j, so the folded square is i, j >= N / 2.
N = 30                      # no cell centre lies on a cut line (cuts are at 1.5 from a corner)
H = N // 2


def _centre(i):
    return -Q + (i + 0.5) * 2 * Q / N


def _inside(pt, poly):
    """Ray casting: is the point inside the polygon?"""
    x, y = pt
    hit = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            hit = not hit
    return hit


def holes(polys):
    """The cells of the paper that a drawn design has cut away."""
    return frozenset((i, j) for i in range(N) for j in range(N)
                     if any(_inside((_centre(i), _centre(j)), p) for p in polys))


def _on_top(i):
    """The cell of the folded square that cell i ends up under."""
    return i if i >= H else N - 1 - i


def cut_through_layers(cut):
    """Fold, cut, unfold: every cell that lies under the cut when the paper is folded."""
    return frozenset((i, j) for i in range(N) for j in range(N)
                     if _inside((_centre(_on_top(i)), _centre(_on_top(j))), cut))


def pieces_cut_off(cells):
    """How many separate bits of paper fall out (cells joined side to side)."""
    left, n = set(cells), 0
    while left:
        n += 1
        todo = [left.pop()]
        while todo:
            i, j = todo.pop()
            for nb in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                if nb in left:
                    left.discard(nb)
                    todo.append(nb)
    return n


def can_make(polys):
    """A design comes from cutting one corner of the folded square if it looks the same flipped
    left-right and top-bottom, and folded up it is one piece at exactly one corner."""
    cells = holes(polys)
    if not cells or any((N - 1 - i, j) not in cells or (i, N - 1 - j) not in cells for i, j in cells):
        return False
    folded = {(i, j) for i, j in cells if i >= H and j >= H}
    corners = {(H, H), (N - 1, N - 1), (N - 1, H), (H, N - 1)}
    return pieces_cut_off(folded) == 1 and len(folded & corners) == 1


def _key(poly):
    return frozenset((round(x, 3), round(y, 3)) for x, y in poly)


def _dedupe(polys):
    seen, out = set(), []
    for p in polys:
        k = _key(p)
        if k not in seen:
            seen.add(k)
            out.append(p)
    return out


def design_key(polys):
    return frozenset(_key(p) for p in polys)


def _on_border(a, b):
    return any(a[i] == b[i] and abs(a[i]) == Q for i in (0, 1))


def design_pic(polys, scale=8.5):
    """The unfolded paper (grey) with the cut-out parts removed."""
    f = Fig(2 * Q, 2 * Q, scale=scale, margin=4)
    sh = lambda p: (p[0] + Q, p[1] + Q)
    f.rect(0, 0, 2 * Q, 2 * Q, fill=GREY, width=1.1)
    edges = {}
    for poly in polys:
        n = len(poly)
        for i in range(n):
            a, b = poly[i], poly[(i + 1) % n]
            k = frozenset((a, b))
            edges[k] = edges.get(k, 0) + 1
    for poly in polys:
        # push points on the paper border a little outwards so the white covers the border line
        pts = [(x + (0.15 if x == Q else -0.15 if x == -Q else 0),
                y + (0.15 if y == Q else -0.15 if y == -Q else 0)) for x, y in poly]
        flat = [sh(p) for p in pts]
        # white outline too, so two mirrored copies that touch show no seam between them
        f.d.add(Polygon([c for p in flat for c in f.p(*p)], fillColor=colors.white,
                        strokeColor=colors.white, strokeWidth=1.2))
    for k, cnt in edges.items():
        a, b = tuple(k)
        if cnt == 1 and not _on_border(a, b):
            f.line(sh(a), sh(b), width=1.1)
    return f.drawing()


def folded_pic(cuts, labels=False, scale=13, margin=None):
    """The folded square: folds dashed (left and bottom), paper edges solid, cut parts dark."""
    f = Fig(Q, Q, scale=scale, margin=margin if margin is not None else (14 if labels else 6))
    f.rect(0, 0, Q, Q, fill=colors.white, width=0.1)
    for poly in cuts:
        f.poly(poly, fill=colors.Color(0.35, 0.35, 0.35), width=0.6)
    f.line((Q, 0), (Q, Q), width=1.3)
    f.line((0, Q), (Q, Q), width=1.3)
    f.line((0, 0), (Q, 0), dash=True, width=1.3)
    f.line((0, 0), (0, Q), dash=True, width=1.3)
    if labels:
        for name, (x, y) in zip("ABCD", [CORNERS["side_tb"], CORNERS["corner"], CORNERS["side_lr"],
                                        CORNERS["centre"]]):
            f.text(x + (0.45 if x else -0.45), y + (0.45 if y else -0.45), name, size=10)
    return f.drawing()


def _arrowhead(f, tip, d, size=0.55):
    """Two short strokes at `tip`, for an arrow travelling in direction d = (dx, dy)."""
    dx, dy = d
    n = (dx * dx + dy * dy) ** 0.5
    dx, dy = dx / n, dy / n
    for s in (1, -1):
        f.line(tip, (tip[0] - size * (dx + s * 0.6 * dy), tip[1] - size * (dy - s * 0.6 * dx)), width=1)


def _arrow_pic(scale=8):
    f = Fig(1.6, Q, scale=scale, margin=12)
    f.line((0, 0.8 * Q), (1.6, 0.8 * Q), width=1)
    _arrowhead(f, (1.6, 0.8 * Q), (1, 0))
    return f.drawing()


def fold_strip(scale=8):
    """How the paper is folded: the square, folded left onto right, then bottom onto top."""
    a = Fig(2 * Q, 2 * Q, scale=scale, margin=12)
    a.rect(0, 0, 2 * Q, 2 * Q, fill=colors.white, width=1.1)
    a.line((Q, 0), (Q, 2 * Q), dash=True, width=1)
    a.arc(Q, 2 * Q + 0.3, Q * 0.55, 175, 5, width=1, ry=1.0)          # left half over to the right
    _arrowhead(a, (Q + Q * 0.55, 2 * Q + 0.3), (0.3, -1))
    b = Fig(Q, 2 * Q, scale=scale, margin=12)
    b.rect(0, 0, Q, 2 * Q, fill=colors.white, width=1.1)
    b.line((0, Q), (Q, Q), dash=True, width=1)
    b.arc(Q + 0.3, Q, 1.0, -85, 85, width=1, ry=Q * 0.55)             # bottom half up onto the top
    _arrowhead(b, (Q + 0.3, Q + Q * 0.55), (-1, 0.3))
    return row([a.drawing(), _arrow_pic(scale), b.drawing(), _arrow_pic(scale), folded_pic([], scale=scale, margin=12)],
               gap=2)


def folding_figure(cuts=None, labels=False):
    """The fold strip, then (bigger) the small square with its cut or its corner names."""
    if cuts is None and not labels:
        return fold_strip()
    return row([fold_strip(), _arrow_pic(), folded_pic(cuts or [], labels=labels)], gap=2)


INTRO = ("A square piece of paper is folded in half, and in half again, so that it is a small square "
         "(see the picture: the dashed sides of the small square are the folds).")


def _possible(rng):
    corner = rng.choice(list(CORNERS))
    kind = rng.choice(["triangle", "square"])
    s = 1.5                     # one size only: smaller cuts are hard to see, and look like near-duplicates
    return (corner, kind, s), unfold(cut_shape(corner, kind, s))


def _impossible(rng):
    """Designs that one cut of the folded square cannot make, and why."""
    (corner, kind, s), full = _possible(rng)
    how = rng.choice(["one", "two_copies", "two_cuts"])
    if how == "one":
        return [rng.choice(full)], "it has only one cut part, but the cut goes through four layers"
    if how == "two_copies" and len(full) == 4:
        i = rng.randrange(4)
        keep = [full[i], full[i ^ 1]] if rng.random() < 0.5 else [full[i], full[3 - i]]
        return _dedupe(keep), "it is not the same on all four sides, so it is not mirrored over both folds"
    (c2, k2, s2), other = _possible(rng)
    while c2 == corner:
        (c2, k2, s2), other = _possible(rng)
    return _dedupe(full + other), "it needs two different cuts"


def _distinct_possibles(rng, n):
    out, keys = [], set()
    while len(out) < n:
        spec, d = _possible(rng)
        k = design_key(d)
        if k not in keys:
            keys.add(k)
            out.append((spec, d))
    return out


@variant(difficulty=1)
def which_cannot(rng, harder):
    """Four designs can be made, one cannot."""
    goods = _distinct_possibles(rng, 4)
    bad, why = _impossible(rng)
    while design_key(bad) in {design_key(d) for _, d in goods}:
        bad, why = _impossible(rng)
    pics = [d for _, d in goods] + [bad]
    rng.shuffle(pics)
    k = pics.index(bad)
    text = INTRO + " One corner of the small square is cut off, and the paper is unfolded."
    after = "Which design <b>cannot</b> be made this way?"
    sol = (f"The cut goes through four layers, so it appears four times, mirrored over both folds. "
           f"Design {'ABCDE'[k]} is impossible: {why}.")
    return Question(text=text, figure=fold_strip(), after_figure=after, choices=[f"design {c}" for c in "ABCDE"], answer=k,
                    choice_figures=[design_pic(p) for p in pics], solution=sol,
                    check=lambda i: not can_make(pics[i]))


@variant(difficulty=1)
def which_result(rng, harder):
    """The folded square with its cut is shown; which design appears when it is unfolded?"""
    corner = rng.choice(list(CORNERS))
    kind = rng.choice(["triangle", "square"])
    s = 1.5
    cut = cut_shape(corner, kind, s)
    good = unfold(cut)
    others = []
    for c2 in CORNERS:
        if c2 != corner:
            others.append(unfold(cut_shape(c2, kind, s)))
    bad, _ = _impossible(rng)
    while design_key(bad) in {design_key(o) for o in others + [good]}:
        bad, _ = _impossible(rng)
    pics = others + [bad, good]
    rng.shuffle(pics)
    k = pics.index(good)
    text = INTRO + " The dark part is cut off, then the paper is unfolded."
    after = "What does the paper look like?"
    sol = (f"The cut corner is {'the centre of the paper' if corner == 'centre' else 'a real corner of the paper' if corner == 'corner' else 'the middle of a side of the paper'} "
           f"(look where the folds are). Mirrored four times it gives {WHAT[corner]}: design {'ABCDE'[k]}.")
    return Question(text=text, figure=folding_figure([cut]), after_figure=after,
                    choices=[f"design {c}" for c in "ABCDE"], answer=k,
                    choice_figures=[design_pic(p) for p in pics], solution=sol,
                    check=lambda i: holes(pics[i]) == cut_through_layers(cut))


@variant(difficulty=2)
def which_can(rng, harder):
    """Reverse: four designs are impossible, one can be made."""
    (spec, good), = _distinct_possibles(rng, 1)
    bads, whys, keys = [], [], {design_key(good)}
    while len(bads) < 4:
        b, why = _impossible(rng)
        if design_key(b) not in keys:
            keys.add(design_key(b))
            bads.append(b)
    pics = bads + [good]
    rng.shuffle(pics)
    k = pics.index(good)
    text = INTRO + " One corner of the small square is cut off, and the paper is unfolded."
    after = "Which design <b>can</b> be made this way?"
    sol = (f"A single cut appears four times, the same on the left and right and on the top and bottom. "
           f"Only design {'ABCDE'[k]} looks like that ({WHAT[spec[0]]}).")
    return Question(text=text, figure=fold_strip(), after_figure=after, choices=[f"design {c}" for c in "ABCDE"], answer=k,
                    choice_figures=[design_pic(p) for p in pics], solution=sol,
                    check=lambda i: can_make(pics[i]))


@variant(difficulty=2)
def count_pieces(rng, harder):
    """How many separate pieces of paper fall off when unfolded?"""
    corner = rng.choice(list(CORNERS))
    kind = rng.choice(["triangle", "square"])
    cut = cut_shape(corner, kind, 1.5)
    ans = {"centre": 1, "corner": 4, "side_lr": 2, "side_tb": 2}[corner]
    text = INTRO + " The dark part is cut off and falls on the table. It is four layers of paper."
    after = "How many separate pieces of paper are on the table?"
    sol = {1: "The cut is at the centre of the paper, where all four layers are joined: the four copies "
              "make one piece (the hole in the middle).",
           2: "The cut is at the middle of a paper side: the layers are joined in pairs along one fold, "
              "so the cut gives 2 pieces (two notches).",
           4: "The cut is at a real corner of the paper: the four layers are not joined there, so it "
              "gives 4 separate pieces (the four corners)."}[ans]
    choices = ["1", "2", "3", "4", "8"]
    return Question(text=text, figure=folding_figure([cut]), after_figure=after, choices=choices,
                    answer=choices.index(str(ans)), solution=sol,
                    check=value_check(choices, pieces_cut_off(cut_through_layers(cut))))


@variant(difficulty=3)
def which_corner(rng, harder):
    """An unfolded design is shown; at which corner of the folded square was the cut made?"""
    corner = rng.choice(list(CORNERS))
    kind = rng.choice(["triangle", "square"])
    design = unfold(cut_shape(corner, kind, 1.5))
    names = dict(zip(["side_tb", "corner", "side_lr", "centre"], "ABCD"))
    fig = column([folding_figure(labels=True), design_pic(design, scale=9)], gap=8)
    text = (INTRO + " One corner of the small square was cut off, and after unfolding the "
            "paper looks like the bottom picture.")
    after = "Which corner was cut off?"
    choices = ["corner A", "corner B", "corner C", "corner D", "it cannot be made with one cut"]
    sol = (f"The design shows {WHAT[corner]}. That comes from cutting corner {names[corner]} "
           f"({'where both folds meet: the centre of the paper' if corner == 'centre' else 'the real paper corner, away from the folds' if corner == 'corner' else 'where one fold meets a paper edge'}).")
    letter_at = {"A": CORNERS["side_tb"], "B": CORNERS["corner"], "C": CORNERS["side_lr"], "D": CORNERS["centre"]}
    by_letter = {L: next(c for c, xy in CORNERS.items() if xy == pt) for L, pt in letter_at.items()}
    made_by = [L for L in "ABCD" if cut_through_layers(cut_shape(by_letter[L], kind, 1.5)) == holes(design)]

    def check(i):
        return made_by == [choices[i][-1]] if i < 4 else not made_by
    return Question(text=text, figure=fig, after_figure=after, choices=choices,
                    answer=choices.index(f"corner {names[corner]}"), solution=sol, check=check)
