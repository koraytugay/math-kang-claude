"""2026 Q7 (Canada, Grade 3-4) - cutting a stack of overlapping paper squares.

Original: Ann places a white square on the table, then a grey one, then a black one on
top, as shown. Then she cuts the stack along the two lines. How many squares does she get?
(A) 3  (B) 4  (C) 5  (D) 7  (E) 9.
Measured from the figure (white = 10 x 10): grey 8 x 8 in the bottom-left corner, black 5 x 5
in the top-right corner, a vertical cut at 8 from the left and a horizontal cut 2 from the top.
White: 4 pieces, two of them squares (2 x 2 and 8 x 8). Grey: both lines run along its edges,
so it stays whole: 1 square. Black: 4 pieces, two of them squares (2 x 2 and 3 x 3).
5 squares.  Answer: C.  (There is no answer key for 2026 in the repo: solved by us.)

Core skill: each sheet of paper is cut on its own, also the parts hidden under other sheets,
and a cut piece is a square only when its two sides are equal. Children count the regions they
can see in the picture, count every piece (9) or forget that a line running along an edge
does not cut that sheet.

Our figures are drawn on a light grid so the pieces can be measured by counting cells.
"""
from reportlab.lib import colors

from kangaroo import Fig, Question, numeric_choices, value_check, variant

META = {
    "source": "set-03/by_level/Grade_03-04/2026 Q7",
    "skill": "Cut each sheet on its own, also the hidden part under the sheets on top; "
             "then check which pieces have equal sides",
    "topics": ["geometry", "spatial", "counting"],
    "keywords": ["cutting a paper stack", "squares and rectangles", "hidden parts"],
    "sticker": ("🥞", "Stack slicer"),   # earned when this skill is solid (website)
    "version": 1,
}

PEOPLE = [("Ann", "she"), ("Mia", "she"), ("Lena", "she"), ("Tom", "he"), ("Ben", "he"), ("Omar", "he")]
SHADES = {"white": colors.white, "light grey": colors.Color(0.86, 0.86, 0.86),
          "grey": colors.Color(0.68, 0.68, 0.68), "dark grey": colors.Color(0.5, 0.5, 0.5),
          "black": colors.Color(0.3, 0.3, 0.3)}
COLOURS3 = ["white", "grey", "black"]
COLOURS4 = ["white", "light grey", "grey", "black"]
PIECES = ("piece", "pieces")
SQUARES = ("square", "squares")


# ------------------------------------------------------------------ the model
# A sheet is (x, y, s): lower-left corner and side, in grid cells. Sheets are listed bottom first.
# Cuts: xs = x-positions of vertical lines, ys = y-positions of horizontal lines (whole stack).

def _parts(lo, hi, cuts):
    """Lengths of the pieces of [lo, hi] after cutting at the cuts strictly inside it."""
    pts = [lo] + sorted(c for c in cuts if lo < c < hi) + [hi]
    return [b - a for a, b in zip(pts, pts[1:])]


def sheet_pieces(sheet, xs, ys):
    """[(w, h)] of the pieces one sheet is cut into."""
    x, y, s = sheet
    return [(w, h) for w in _parts(x, x + s, xs) for h in _parts(y, y + s, ys)]


def count(sheets, xs, ys):
    pieces = [p for sh in sheets for p in sheet_pieces(sh, xs, ys)]
    return len(pieces), sum(w == h for w, h in pieces)


# ------------------------------------------------------------------ brute force (the check)
def _components(cells, xs, ys):
    """Connected groups of unit cells; two neighbours are joined unless a cut line runs between them."""
    cells, out = set(cells), []
    while cells:
        stack, comp = [cells.pop()], []
        while stack:
            cx, cy = stack.pop()
            comp.append((cx, cy))
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (cx + dx, cy + dy)
                if n not in cells:
                    continue
                if dx and max(cx, n[0]) in xs:          # vertical line between the two cells
                    continue
                if dy and max(cy, n[1]) in ys:
                    continue
                cells.remove(n)
                stack.append(n)
        out.append(comp)
    return out


def _is_square(comp):
    xs_ = [c[0] for c in comp]
    ys_ = [c[1] for c in comp]
    w, h = max(xs_) - min(xs_) + 1, max(ys_) - min(ys_) + 1
    return w == h and len(comp) == w * h


def brute(sheets, xs, ys, which=None):
    """Cut every sheet cell by cell: (pieces, square pieces) for all sheets or sheet `which`."""
    pieces = squares = 0
    for i, (x, y, s) in enumerate(sheets):
        if which is not None and i != which:
            continue
        comps = _components([(a, b) for a in range(x, x + s) for b in range(y, y + s)], set(xs), set(ys))
        pieces += len(comps)
        squares += sum(_is_square(c) for c in comps)
    return pieces, squares


def top_view(sheets, xs, ys):
    """Regions seen from above (top colour + cuts): (regions, regions that look like squares)."""
    top = {}
    for i, (x, y, s) in enumerate(sheets):
        for a in range(x, x + s):
            for b in range(y, y + s):
                top[(a, b)] = i
    regions = []
    for i in range(len(sheets)):
        regions += _components([c for c, t in top.items() if t == i], set(xs), set(ys))
    return len(regions), sum(_is_square(c) for c in regions)


# ------------------------------------------------------------------ making a stack
def _covered(pt, sh):
    x, y, s = sh
    return x <= pt[0] <= x + s and y <= pt[1] <= y + s


def _readable(sheets):
    """Every lower sheet shows two opposite corners (so its square is clear) and enough paper."""
    for i, (x, y, s) in enumerate(sheets[:-1]):
        above = sheets[i + 1:]
        free = [not any(_covered(c, a) for a in above)
                for c in ((x, y), (x + s, y + s), (x + s, y), (x, y + s))]
        if not ((free[0] and free[1]) or (free[2] and free[3])):
            return False
    return True


def make_stack(rng, n_sheets, n_v, n_h, N, want=None):
    """Random readable stack and cuts; `want(sheets, xs, ys)` adds conditions."""
    for _ in range(20000):
        S = rng.randint(N - 3, N)
        sheets = [(0, 0, S)]
        for _ in range(n_sheets - 1):
            s = rng.randint(3, S - 2)
            sheets.append((rng.randint(0, S - s), rng.randint(0, S - s), s))
        if len(set(sheets)) < n_sheets or not _readable(sheets):
            continue
        xs = sorted(rng.sample(range(1, S), n_v))
        ys = sorted(rng.sample(range(1, S), n_h))
        if any(b - a < 2 for a, b in zip(xs, xs[1:])) or any(b - a < 2 for a, b in zip(ys, ys[1:])):
            continue
        # every line cuts at least two sheets, and every sheet is cut or touched by a line
        if any(sum(x < c < x + s for x, _, s in sheets) < 2 for c in xs):
            continue
        if any(sum(y < c < y + s for _, y, s in sheets) < 2 for c in ys):
            continue
        if any(min(w, h) < 2 for sh in sheets for w, h in sheet_pieces(sh, xs, ys)):
            continue                                     # no thin strips: every piece is easy to see
        pieces, squares = count(sheets, xs, ys)
        seen, seen_sq = top_view(sheets, xs, ys)
        if not (2 <= squares < pieces <= 16) or seen == pieces or seen_sq == squares:
            continue
        if want and not want(sheets, xs, ys):
            continue
        return S, sheets, xs, ys
    raise RuntimeError("no stack found")


# ------------------------------------------------------------------ picture
def _scissors(f, x, y, horizontal):
    """A small pair of scissors at the end of a cut line."""
    if horizontal:
        f.line((x - 0.5, y + 0.25), (x + 0.15, y - 0.12), width=0.8)
        f.line((x - 0.5, y - 0.25), (x + 0.15, y + 0.12), width=0.8)
        f.circle(x + 0.3, y + 0.18, 0.15, width=0.7)
        f.circle(x + 0.3, y - 0.18, 0.15, width=0.7)
    else:
        f.line((x + 0.25, y - 0.5), (x - 0.12, y + 0.15), width=0.8)
        f.line((x - 0.25, y - 0.5), (x + 0.12, y + 0.15), width=0.8)
        f.circle(x + 0.18, y + 0.3, 0.15, width=0.7)
        f.circle(x - 0.18, y + 0.3, 0.15, width=0.7)


def stack_pic(S, sheets, colours, xs, ys, max_px=140):
    over = 1.3
    f = Fig(S + 2 * over, S + 2 * over, max_px=max_px, margin=4)
    o = over
    for (x, y, s), c in zip(sheets, colours):
        f.rect(o + x, o + y, s, s, fill=SHADES[c], width=1.0)
    grid = colors.Color(0.62, 0.62, 0.62)
    for k in range(1, S):
        f.line((o + k, o), (o + k, o + S), width=0.3, color=grid)
        f.line((o, o + k), (o + S, o + k), width=0.3, color=grid)
    for (x, y, s), c in zip(sheets, colours):          # outlines again, on top of the grid
        f.rect(o + x, o + y, s, s, fill=None, width=1.0)
    for c in xs:
        f.line((o + c, 0.2), (o + c, S + 2 * o - 0.75), dash=True, width=0.9)
        _scissors(f, o + c, S + 2 * o - 0.6, horizontal=False)
    for c in ys:
        f.line((0.2, o + c), (S + 2 * o - 0.75, o + c), dash=True, width=0.9)
        _scissors(f, S + 2 * o - 0.6, o + c, horizontal=True)
    return f.drawing()


# ------------------------------------------------------------------ text helpers
def _placing(name, colours):
    a = "an" if colours[0][0] in "aeiou" else "a"
    rest = colours[1:]
    if len(rest) == 2:
        mid = f"then a {rest[0]} one, then a {rest[1]} one on top"
    else:
        mid = ", ".join(f"then a {c} one" for c in rest[:-1]) + f" and then a {rest[-1]} one on top"
    return f"{name} places {a} {colours[0]} square on the table, {mid}, as shown."


def _lines_word(xs, ys):
    n = len(xs) + len(ys)
    return {2: "the two dashed lines", 3: "the three dashed lines"}[n]


def _explain(sheets, colours, xs, ys):
    parts = []
    for sh, c in zip(sheets, colours):
        ps = sheet_pieces(sh, xs, ys)
        if len(ps) == 1:
            parts.append(f"the {c} square is not cut (no line goes through it): 1 piece, a square")
            continue
        sq = [f"{w}×{h}" for w, h in ps if w == h]
        sq_txt = f"{len(sq)} of them squares ({', '.join(sq)})" if sq else "none of them squares"
        if len(sq) == 1:
            sq_txt = f"1 of them a square ({sq[0]})"
        parts.append(f"the {c} square is cut into {len(ps)} pieces, {sq_txt}")
    return "; ".join(parts) + "."


def _setup(rng, harder, n_v, n_h, want=None):
    name, _ = rng.choice(PEOPLE)
    colours = COLOURS4 if harder else COLOURS3
    n = len(colours)
    S, sheets, xs, ys = make_stack(rng, n, n_v, n_h, 11 if harder else 10, want)
    if rng.random() < 0.5:                               # mirror left-right
        sheets = [(S - x - s, y, s) for x, y, s in sheets]
        xs = sorted(S - c for c in xs)
    intro = (_placing(name, colours) + " The grid helps you measure the paper. "
             f"Then {name} cuts the whole stack along {_lines_word(xs, ys)}.")
    return name, colours, S, sheets, xs, ys, intro


def _pic(S, sheets, colours, xs, ys):
    return stack_pic(S, sheets, colours, xs, ys)


# ------------------------------------------------------------------ variants
def _squares_question(rng, harder, n_v, n_h):
    name, colours, S, sheets, xs, ys, intro = _setup(rng, harder, n_v, n_h)
    pieces, squares = count(sheets, xs, ys)
    seen, seen_sq = top_view(sheets, xs, ys)
    text = intro + "\n\nHow many squares does " + name + " get?"
    sol = ("Cut each square on its own, also the parts you cannot see: "
           + _explain(sheets, colours, xs, ys) + f" Together: {squares} squares.")
    mistakes = [(pieces, "count every piece, also the rectangles"),
                (seen_sq, "count only the squares you can see in the picture"),
                (len(sheets), "count the squares before cutting"),
                (pieces - squares, "count the pieces that are not squares")]
    choices, ai = numeric_choices(squares, mistakes, rng, lo=1, order="asc")
    return Question(text=text, figure=_pic(S, sheets, colours, xs, ys), choices=choices, answer=ai,
                    solution=sol, check=value_check(choices, brute(sheets, xs, ys)[1]))


@variant(difficulty=1)
def stack_cut(rng, harder):
    """The original: three squares, one vertical and one horizontal cut; how many squares?"""
    return _squares_question(rng, harder, 1, 1)


@variant(difficulty=2)
def all_pieces(rng, harder):
    """How many pieces altogether (hidden pieces count too)?"""
    name, colours, S, sheets, xs, ys, intro = _setup(rng, harder, 1, 1)
    pieces, squares = count(sheets, xs, ys)
    seen, _ = top_view(sheets, xs, ys)
    text = intro + f"\n\nHow many pieces of paper does {name} get?"
    sol = ("Cut each square on its own, also the parts under the other squares: "
           + _explain(sheets, colours, xs, ys) + f" Together: {pieces} pieces.")
    mistakes = [(seen, "count only the pieces you can see in the picture"),
                (4 * len(sheets), "think every square is cut into 4 pieces"),
                (squares, "count only the square pieces"), pieces + 1, pieces - 1]
    choices, ai = numeric_choices(pieces, mistakes, rng, lo=1, unit=PIECES, order="asc")
    return Question(text=text, figure=_pic(S, sheets, colours, xs, ys), choices=choices, answer=ai,
                    solution=sol, check=value_check(choices, brute(sheets, xs, ys)[0]))


@variant(difficulty=2)
def not_squares(rng, harder):
    """Reverse: how many pieces are NOT squares?"""
    name, colours, S, sheets, xs, ys, intro = _setup(rng, harder, 1, 1)
    pieces, squares = count(sheets, xs, ys)
    seen, seen_sq = top_view(sheets, xs, ys)
    ans = pieces - squares
    text = intro + f"\n\nHow many of the pieces are <b>not</b> squares?"
    sol = ("Cut each square on its own, also the parts you cannot see: "
           + _explain(sheets, colours, xs, ys)
           + f" That is {pieces} pieces, {squares} of them squares, so {ans} are not squares.")
    mistakes = [(squares, "count the squares instead"),
                (pieces, "count every piece"),
                (seen - seen_sq, "count only the pieces you can see in the picture")]
    brute_p, brute_s = brute(sheets, xs, ys)
    choices, ai = numeric_choices(ans, mistakes, rng, lo=0, order="asc")
    return Question(text=text, figure=_pic(S, sheets, colours, xs, ys), choices=choices, answer=ai,
                    solution=sol, check=value_check(choices, brute_p - brute_s))


def _seen_squares(sheets, xs, ys, i):
    """Regions of sheet i you can see from above that look like squares."""
    top = {}
    for k, (x, y, s) in enumerate(sheets):
        for a in range(x, x + s):
            for b in range(y, y + s):
                top[(a, b)] = k
    return sum(_is_square(cp) for cp in _components([p for p, t in top.items() if t == i], set(xs), set(ys)))


def _hidden_choices(sheets, xs, ys):
    """Lower sheets with 2+ square pieces where the picture shows a different number of squares."""
    return [i for i in range(len(sheets) - 1)
            if count([sheets[i]], xs, ys)[1] >= 2
            and _seen_squares(sheets, xs, ys, i) != count([sheets[i]], xs, ys)[1]]


@variant(difficulty=2)
def one_colour(rng, harder):
    """Squares of one colour that lies under another sheet (so part of it is hidden)."""
    n_v, n_h = rng.choice([(1, 1), (2, 1), (1, 2)])
    name, colours, S, sheets, xs, ys, intro = _setup(rng, harder, n_v, n_h,
                                                     want=lambda sh, a, b: _hidden_choices(sh, a, b))
    i = rng.choice(_hidden_choices(sheets, xs, ys))
    c = colours[i]
    pieces, squares = count([sheets[i]], xs, ys)
    seen_sq = _seen_squares(sheets, xs, ys, i)
    text = intro + f"\n\nHow many <b>{c}</b> squares does {name} get?"
    sol = (f"Look only at the {c} square, also the part under the other paper: it is cut into "
           f"{pieces} pieces: " + ", ".join(f"{w}×{h}" for w, h in sheet_pieces(sheets[i], xs, ys))
           + f". {squares} of them have equal sides.")
    mistakes = [(seen_sq, f"count only the {c} squares you can see in the picture"),
                (pieces, f"count every {c} piece, also the rectangles"),
                (count(sheets, xs, ys)[1], "count the squares of every colour")]
    choices, ai = numeric_choices(squares, mistakes, rng, lo=0, order="asc")
    return Question(text=text, figure=_pic(S, sheets, colours, xs, ys), choices=choices, answer=ai,
                    solution=sol, check=value_check(choices, brute(sheets, xs, ys, which=i)[1]))


@variant(difficulty=3)
def three_cuts(rng, harder):
    """Three cut lines (two in one direction): more pieces to keep track of."""
    two_v = rng.random() < 0.5
    return _squares_question(rng, harder, 2 if two_v else 1, 1 if two_v else 2)
