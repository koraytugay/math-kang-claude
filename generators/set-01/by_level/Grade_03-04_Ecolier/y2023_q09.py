"""2023 Q9 (Ecolier, Grade 3-4) - fill a shape with five pieces: which piece lies on the dot?

Original: Using the pieces A, B, C, D and E one can fill this shape completely. Which of the
pieces lies on the dot?
Shape: an L of unit squares - a row of 5 squares with a column of 3 more squares on top of the
right end; the dot is in the 4th square of the row. Pieces: A a tall thin triangle (3 high, 1 wide),
B a thin triangle (2 high, 1 wide), C a big right triangle (2 by 2, a square and two half squares),
D a square with a half square, E a parallelogram (a square with a half square at each end).
Answer: E (answer key: E). C fills the corner (the bottom right square plus a half square on each
side), A and B together fill the column, D and E fill the rest of the row - E lies on the dot.

Core skill: fitting pieces into a shape - start where there is the least room (a corner, a narrow
arm), match slanted edges with slanted edges, and check with the area (count half squares).
The variants use pieces made of squares and half squares (the original's A and B have steeper
cuts; the reasoning is the same).
"""
from kangaroo import Question, numeric_choices, variant, warmup, value_check
from kangaroo.choices import Choices
from kangaroo import halfsquares as hs

META = {
    "source": "set-01/by_level/Grade_03-04_Ecolier/2023 Q9",
    "skill": "Filling a shape with pieces: start where there is least room (corner, narrow arm), "
             "match slanted edges, check with the number of squares",
    "topics": ["geometry", "spatial", "area"],
    "keywords": ["fill the shape", "jigsaw pieces", "which piece fits"],
    "version": 1,
}

LETTERS = "ABCDE"

# regions of whole cells (x, y), y up
REGIONS_SMALL = [
    [(x, 0) for x in range(4)] + [(3, 1), (3, 2)],                    # L 4 + 2
    [(x, 0) for x in range(4)] + [(x, 1) for x in range(2)],          # 4 + 2 step
    [(x, y) for x in range(3) for y in range(2)],                     # 3 x 2
    [(x, 0) for x in range(3)] + [(1, 1), (1, 2)],                    # T upside down
    [(x, 0) for x in range(5)] + [(4, 1), (4, 2)],                    # L 5 + 2
]
REGIONS_BIG = [
    [(x, 0) for x in range(5)] + [(4, 1), (4, 2), (4, 3)],            # the contest L
    [(x, y) for x in range(4) for y in range(2)],                     # 4 x 2
    [(x, y) for x in range(3) for y in range(3) if (x, y) != (2, 2)],  # 3 x 3 without a corner
    [(x, 0) for x in range(4)] + [(x, 1) for x in range(1, 4)] + [(3, 2)],  # staircase
    [(x, 0) for x in range(5)] + [(0, 1), (4, 1), (4, 2)],            # U-ish
]


def _sizes(rng, total, k, top=5):
    """k piece sizes in half squares (2..top), adding up to total."""
    for _ in range(500):
        s = [rng.randint(2, top) for _ in range(k - 1)]
        last = total - sum(s)
        if 2 <= last <= top:
            return s + [last]
    return None


def _cut(rng, cells, k, top=5):
    """Cut a region into k different-looking pieces, most of them with a slanted edge."""
    for _ in range(400):
        sizes = _sizes(rng, 2 * len(cells), k, top)
        if not sizes:
            continue
        pieces = hs.random_cut(cells, sizes, rng, tries=20)
        if not pieces:
            continue
        if any(hs.same_shape(a, b) for i, a in enumerate(pieces) for b in pieces[i + 1:]):
            continue
        slanted = sum(1 for p in pieces if any(len({q for x, y, q in p if (x, y) == c[:2]}) == 2 for c in p))
        if slanted >= k - 2:
            return pieces
    return None


def _piece_fig(p, rng, turn, scale=13):
    shown = hs.turned(rng, p) if turn else hs.normalize(p)
    return hs.draw(shown, scale=scale), shown


# ------------------------------------------------------------------ variants
@variant(difficulty=2)
def dot_piece(rng, harder):
    """The original: five pieces fill the shape; which piece lies on the dot?"""
    for _ in range(300):
        cells = rng.choice(REGIONS_BIG)
        region = hs.from_cells(cells)
        pieces = _cut(rng, cells, 5)
        if not pieces:
            continue
        sols = hs.tilings(region, pieces, flip=True, limit=40)
        # the dot: a quarter that the same piece covers in every way of filling the shape
        sure = [q for q in sorted(region) if len({s[q] for s in sols}) == 1]
        owner = {q: i for i, p in enumerate(pieces) for q in p}
        sure = [q for q in sure if owner[q] == sols[0][q]]
        if not sure:
            continue
        dq = rng.choice(sure)
        ans = owner[dq]
        dot = hs.half_centre(pieces[ans], dq)
        figs = [_piece_fig(p, rng, harder) for p in pieces]
        text = ("Using the pieces A, B, C, D and E you can fill this shape completely. The pieces may be "
                "turned. Which of the pieces lies on the dot?")
        sol = ("Start where there is the least room: the corners and the narrow parts of the shape. Slanted "
               f"edges must meet slanted edges. When all pieces are in, piece {LETTERS[ans]} lies on the dot.")
        check_sols = hs.tilings(region, [s for _, s in figs], flip=True, limit=40)
        def check(i, _sols=check_sols, _dq=dq):
            return bool(_sols) and all(s[_dq] == i for s in _sols)
        choices = Choices([f"piece {c}" for c in LETTERS],
                          {i: "guess from the look of the piece instead of fitting all of them"
                           for i in range(5) if i != ans})
        return Question(text=text, figure=hs.outline(cells, scale=19, dot=dot), choices=choices,
                        choice_figures=[f for f, _ in figs], answer=ans, solution=sol, check=check)
    raise RuntimeError("no puzzle found")


def _other_piece(rng, size, avoid):
    """A random connected piece of `size` half squares that looks different from all in `avoid`."""
    for _ in range(500):
        cells = [(x, y) for x in range(3) for y in range(3)]
        cut = hs.random_cut(cells, [size] + [18 - size], rng, tries=5)
        if not cut:
            continue
        p = hs.normalize(cut[0])
        if not any(hs.same_shape(p, a) for a in avoid):
            return p
    raise RuntimeError("no other piece")


@variant(difficulty=1)
def missing_piece(rng, harder):
    """Four pieces are in place; which piece fills the hole?"""
    pieces = None
    while not pieces:
        cells = rng.choice(REGIONS_BIG if harder else REGIONS_SMALL)
        pieces = _cut(rng, cells, 4 if not harder else 5)
    big = [i for i, p in enumerate(pieces) if len(p) >= 6 and
           any(len({r for a, b, r in p if (a, b) == (x, y)}) == 2 for x, y, _ in p)]
    hole = rng.choice(big) if big else max(range(len(pieces)), key=lambda i: len(pieces[i]))
    placed = [p for i, p in enumerate(pieces) if i != hole]
    region = hs.from_cells(cells)
    size = len(pieces[hole]) // 2
    wrong = []
    for s in [size, size, size + 1, size - 1 if size > 2 else size + 2]:
        wrong.append(_other_piece(rng, s, [pieces[hole]] + wrong))
    opts = [hs.normalize(pieces[hole])] + wrong
    rng.shuffle(opts)
    ans = next(i for i, o in enumerate(opts) if hs.same_shape(o, pieces[hole]))
    shown = [hs.turned(rng, o) if harder else o for o in opts]
    fig = hs.draw(region, scale=19, fill=None, extra=[(p, hs.GREYFILL) for p in placed])
    text = ("Some pieces are already in the shape (grey). Which piece fills the white gap exactly? "
            "The piece may be turned.")
    sol = (f"Count the half squares of the gap ({size}) and look at where its slanted edges are. "
           f"Only piece {LETTERS[ans]} has the same shape.")
    gap = region - frozenset().union(*placed)
    mist = {}
    for i, o in enumerate(opts):
        if i != ans:
            mist[i] = ("pick a piece with the right size but the wrong shape" if len(o) == len(gap)
                       else "pick a piece that is too big or too small")
    return Question(text=text, figure=fig, choices=Choices([f"piece {c}" for c in LETTERS], mist),
                    choice_figures=[hs.draw(o, scale=13) for o in shown], answer=ans, solution=sol,
                    check=lambda i: bool(hs.tilings(gap, [shown[i]], flip=True, limit=1)))


@variant(difficulty=3)
def left_over(rng, harder):
    """Reverse: four of the five pieces fill the shape. Which piece is left over?"""
    for _ in range(300):
        cells = rng.choice(REGIONS_BIG if harder else REGIONS_SMALL)
        pieces = _cut(rng, cells, 4)
        if not pieces:
            continue
        region = hs.from_cells(cells)
        twin = rng.randrange(4)                     # the extra piece has as many half squares as this one
        extra = _other_piece(rng, len(pieces[twin]) // 2, pieces)
        opts = [hs.normalize(p) for p in pieces] + [extra]
        order = list(range(5))
        rng.shuffle(order)
        opts = [opts[i] for i in order]
        ans = order.index(4)
        shown = [hs.turned(rng, o) if harder else o for o in opts]
        works = [bool(hs.tilings(region, [shown[j] for j in range(5) if j != i], flip=True, limit=1))
                 for i in range(5)]
        if works.count(True) != 1:
            continue
        text = ("Four of the pieces A, B, C, D and E fill this shape completely. The pieces may be turned. "
                "Which piece is left over?")
        sol = (f"Pieces {LETTERS[order.index(twin)]} and {LETTERS[ans]} have the same number of half squares, so "
               f"counting alone does not decide. Fit the pieces in, starting in the corners: piece {LETTERS[ans]} "
               f"is not needed.")
        mist = {order.index(twin): "count the squares but not try to fit the pieces"}
        for i in range(5):
            if i != ans and i not in mist:
                mist[i] = "leave out a piece that is needed"
        return Question(text=text, figure=hs.outline(cells, scale=19), choices=Choices(
                        [f"piece {c}" for c in LETTERS], mist), choice_figures=[hs.draw(o, scale=13) for o in shown],
                        answer=ans, solution=sol, check=lambda i, w=works: w[i])
    raise RuntimeError("no puzzle found")


@variant(difficulty=1)
def how_many_tiles(rng, harder):
    """Fill the shape with copies of one piece: how many are needed?"""
    tiles = {
        "half": hs.normalize({(0, 0, 0), (0, 0, 1)}),
        "big": hs.normalize({(0, 0, 0), (0, 0, 1), (1, 0, 0), (1, 0, 1), (1, 0, 2), (1, 0, 3),
                             (1, 1, 0), (1, 1, 1)}),                                       # 2x2 half
        "trap": hs.normalize(hs.square(0, 0) | {(1, 0, 0), (1, 0, 3)}),                    # square + half
        "para": hs.normalize({(0, 0, 1), (0, 0, 2)} | hs.square(1, 0) | {(2, 0, 0), (2, 0, 3)}),
    }
    while True:
        kind = rng.choice(["trap", "para", "big"] if harder else ["half", "trap", "big"])
        tile = tiles[kind]
        n = rng.randint(4, 6) if harder else rng.randint(3, 5)
        # build a shape by dropping n copies next to each other
        shape = set(hs.turned(rng, tile))
        ok = True
        for _ in range(n - 1):
            placed = False
            for _ in range(100):
                o = hs.turned(rng, tile)
                ax, ay, _q = rng.choice(sorted(shape))
                dx, dy = ax + rng.randint(-2, 1), ay + rng.randint(-2, 1)
                cand = {(x + dx, y + dy, q) for x, y, q in o}
                if cand & shape:
                    continue
                if not any(hs._touch(frozenset([c]), frozenset([d])) for c in cand for d in shape):
                    continue
                shape |= cand
                placed = True
                break
            if not placed:
                ok = False
                break
        if not ok:
            continue
        shape = hs.normalize(shape)
        x0, y0, x1, y1 = hs.bbox(shape)
        if x1 - x0 > 5 or y1 - y0 > 4 or (x1 - x0) * (y1 - y0) * 4 > 1.8 * len(shape):
            continue
        try:
            hs._parts(shape)
        except ValueError:
            continue
        break
    whole = len({(x, y) for x, y, q in shape})
    halves = len(shape) // 2
    text = ("How many pieces like the small one are needed to fill the big shape completely? "
            "The pieces may be turned.")
    sol = (f"Count half squares: the shape has {halves}, one piece has {len(tile) // 2}. "
           f"{halves} ÷ {len(tile) // 2} = {n}.")
    mistakes = [(whole, "count the squares the shape touches"), (halves, "count the half squares of the shape"),
                n + 1, n - 1]
    choices, ai = numeric_choices(n, mistakes, rng, lo=1, order="asc")
    values = [int(c) for c in choices]
    def check(i):
        m = values[i]
        return len(tile) * m == len(shape) and bool(hs.tilings(shape, [tile] * m, flip=True, limit=1))
    from kangaroo.figures import row
    fig = row([hs.draw(shape, scale=19), hs.draw(tile, scale=19)], gap=24)
    return Question(text=text, figure=fig, choices=choices, answer=ai, solution=sol, check=check)


# ------------------------------------------------------------------ warm-ups
@warmup
def w_count_halves(rng, harder):
    """Area in half squares."""
    def slanted(p):
        return any(len({r for a, b, r in p if (a, b) == (x, y)}) == 2 for x, y, _ in p)
    pieces = None
    while not pieces or not any(len(p) >= 6 and slanted(p) for p in pieces):
        pieces = _cut(rng, rng.choice(REGIONS_SMALL), 3, top=6)
    p = hs.normalize(rng.choice([p for p in pieces if len(p) >= 6 and slanted(p)]))
    n = len(p) // 2
    text = "How many half squares (triangles made by cutting a square in two) make up this piece?"
    whole = len({(x, y) for x, y, q in p})
    choices, ai = numeric_choices(n, [(whole, "count the squares the piece touches")], rng, lo=1, order="asc")
    return Question(text=text, figure=hs.draw(p, scale=22), choices=choices, answer=ai,
                    solution=f"A whole square is 2 half squares. Counting gives {n}.",
                    check=value_check(choices, sum(2 if len(poly) == 4 else 1 for poly in hs._parts(p))))


@warmup
def w_corner_first(rng, harder):
    """Which piece fits in the corner? (two pieces fill the shape)"""
    small = [[(0, 0), (1, 0), (1, 1)], [(0, 0), (1, 0), (0, 1), (1, 1)], [(0, 0), (1, 0), (2, 0)],
             [(0, 0), (1, 0), (2, 0), (2, 1)]]
    while True:
        pieces = None
        while not pieces:
            cells = rng.choice(small)
            pieces = _cut(rng, cells, 2, top=6)
        region = hs.from_cells(cells)
        q = hs.half_centre(pieces[0], min(pieces[0]))
        a = hs.normalize(pieces[0])
        wrong = [_other_piece(rng, len(a) // 2 + d, [a]) for d in (0, 1, -1 if len(a) > 4 else 2)]
        opts = [a, hs.normalize(pieces[1])] + wrong
        order = list(range(5))
        rng.shuffle(order)
        opts = [opts[i] for i in order]
        ans = order.index(0)
        mq = min(pieces[0])
        def check(i, opts=opts, region=region, mq=mq):
            # option i is right if it fills the shape together with some other option and covers the dot
            return any(sol[mq] == 0 for j in range(5) if j != i
                       for sol in hs.tilings(region, [opts[i], opts[j]], limit=20))
        if [i for i in range(5) if check(i)] == [ans]:
            break
    text = "Two pieces fill this shape. Which piece lies on the dot? The pieces may be turned."
    return Question(text=text, figure=hs.outline(cells, scale=19, dot=q),
                    choices=Choices([f"piece {c}" for c in LETTERS],
                                    {order.index(1): "pick the piece that fills the other part"}),
                    choice_figures=[hs.draw(o, scale=13) for o in opts], answer=ans,
                    solution="Start in the corner with the dot and try each piece.", check=check)
