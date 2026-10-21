"""2007 Q8 - which piece completes the rectangle?

Original: Which of the five pieces fits together with the given piece (an L of
squares: a column of 3 on a row of 3) to form a rectangle?  Answer: B.

Core skill: seeing the "missing part" of a rectangle - the gap left by a piece
has a definite shape and size (rectangle area minus the piece), and the right
answer may be turned. Children choose a piece that looks similar but has one
square too many or in the wrong place.
"""
from itertools import combinations

from kangaroo import Question, numeric_choices, text_choices, value_check, variant
from kangaroo.figures import GREY, row
from kangaroo.polyomino import (can_tile, draw_shape, makes_rectangle, neighbours, normalize,
                                orientations, random_shape, same_shape)

META = {
    "source": "2007 Q8",
    "skill": "Completing a rectangle: the missing part has a fixed shape and size; turn pieces in your head",
    "topics": ["spatial", "geometry"],
    "version": 2,
}

NOTE = "Pieces may be turned and flipped over."


def _connected(cells):
    cells = set(cells)
    if not cells:
        return False
    seen, todo = set(), [next(iter(cells))]
    while todo:
        c = todo.pop()
        if c not in seen:
            seen.add(c)
            todo += [n for n in neighbours(c) if n in cells]
    return seen == cells


def rect(w, h):
    return frozenset((x, y) for x in range(w) for y in range(h))


def split_rectangle(rng, w, h, k):
    """Split a w x h rectangle into a k-square piece and the rest, both connected."""
    R = rect(w, h)
    for _ in range(500):
        piece = {rng.choice(sorted(R))}
        while len(piece) < k:
            c = rng.choice(sorted(piece))
            n = rng.choice(neighbours(c))
            if n in R:
                piece.add(n)
        rest = R - piece
        if _connected(rest):
            return frozenset(piece), frozenset(rest)
    return None


def completes(given, other):
    """Can `other` (turned/flipped) be put next to `given` (as drawn) to make a rectangle?"""
    area = len(given) + len(other)
    g = normalize(given)
    gw = max(x for x, _ in g) + 1
    gh = max(y for _, y in g) + 1
    for w in range(1, area + 1):
        if area % w:
            continue
        h = area // w
        if w < gw or h < gh:
            continue
        for dx in range(w - gw + 1):
            for dy in range(h - gh + 1):
                placed = {(x + dx, y + dy) for x, y in g}
                gap = rect(w, h) - placed
                if len(gap) == len(other) and _connected(gap) and same_shape(gap, other):
                    return True
    return False


def _near_misses(rng, good, given, n=4):
    """Pieces like `good` with one square moved (or added/removed) that do not complete the rectangle."""
    out = []
    for _ in range(600):
        cells = set(good)
        how = rng.random()
        if how < 0.6 or len(cells) < 3:                 # move one square
            cells.remove(rng.choice(sorted(cells)))
            cells.add(rng.choice(sorted({m for c in cells for m in neighbours(c)} - cells)))
        elif how < 0.8:                                  # one square too many
            cells.add(rng.choice(sorted({m for c in cells for m in neighbours(c)} - cells)))
        else:                                            # one square too few
            cells.remove(rng.choice(sorted(cells)))
        cand = normalize(cells)
        if not _connected(cand) or completes(given, cand):
            continue
        if any(same_shape(cand, o) for o in out):
            continue
        out.append(cand)
        if len(out) == n:
            return out
    return None


def _show(p, rng):
    return rng.choice(orientations(p, flip=False))


@variant(difficulty=1)
def complete_rectangle(rng, harder):
    """The original."""
    for _ in range(200):
        w, h = (rng.randint(3, 5), rng.randint(3, 5)) if harder else (rng.randint(3, 4), rng.randint(3, 4))
        k = rng.randint(max(4, w * h // 3), max(4, w * h // 2))
        sp = split_rectangle(rng, w, h, k)
        if not sp:
            continue
        given, good = sp
        g = normalize(given)
        if (max(x for x, _ in g) + 1) * (max(y for _, y in g) + 1) == len(g):
            continue                                     # a rectangle as the grey piece is too easy
        if len(orientations(good)) < 2:
            continue
        wrong = _near_misses(rng, good, given)
        if wrong:
            break
    else:
        raise RuntimeError("no puzzle found")
    opts = wrong + [normalize(good)]
    rng.shuffle(opts)
    k_ans = opts.index(normalize(good))
    text = f"Which of the five pieces fits together with the grey piece to make a rectangle? {NOTE}"
    sol = (f"The grey piece and the right piece together fill a {w} × {h} rectangle: "
           f"{w * h} − {len(given)} = {len(good)} squares, in exactly the shape of the gap. "
           f"Piece {'ABCDE'[k_ans]} (turned) fills it; the others have a square too many, too few, "
           f"or in the wrong place.")
    shown = [_show(o, rng) for o in opts]
    return Question(text=text, figure=draw_shape(normalize(given), scale=13, fill=GREY),
                    choices=[f"piece {c}" for c in "ABCDE"], answer=k_ans,
                    choice_figures=[draw_shape(o, scale=12) for o in shown], solution=sol,
                    check=lambda i: makes_rectangle(given, shown[i]))


@variant(difficulty=1)
def squares_missing(rng, harder):
    """How many squares does the missing piece have? (Smallest rectangle around the piece.)"""
    while True:
        w, h = (rng.randint(4, 6), rng.randint(3, 5)) if harder else (rng.randint(3, 4), rng.randint(3, 4))
        sp = split_rectangle(rng, w, h, rng.randint(w * h // 3, w * h * 2 // 3))
        if sp:
            given, gap = sp
            g = normalize(given)
            if max(x for x, _ in g) + 1 == w and max(y for _, y in g) + 1 == h:
                break
    ans = len(gap)
    text = (f"Tom wants to add one more piece to the grey piece to make the smallest possible rectangle.")
    after = "How many little squares must that piece have?"
    sol = f"The smallest rectangle around the grey piece is {w} × {h} = {w * h} squares. {w * h} − {len(given)} = {ans}."
    mistakes = [len(given), w * h, (w + 1) * h - len(given), ans + 1, ans - 1, 2 * (w + h)]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    g = normalize(given)
    smallest = min(W * H for W in range(1, 3 * w) for H in range(1, 3 * h)
                   if all(x < W and y < H for x, y in g))          # every rectangle the piece fits in
    return Question(text=text, figure=draw_shape(normalize(given), scale=14, fill=GREY), after_figure=after,
                    choices=choices, answer=ai, solution=sol, check=value_check(choices, smallest - len(g)))


@variant(difficulty=2)
def two_make_rectangle(rng, harder):
    """Four pieces, no grey piece: which two together make a rectangle?"""
    for _ in range(300):
        w, h = (rng.randint(3, 5), rng.randint(3, 4)) if harder else (rng.randint(3, 4), rng.randint(2, 3))
        sp = split_rectangle(rng, w, h, rng.randint(w * h // 3, w * h // 2))
        if not sp:
            continue
        a, b = (normalize(x) for x in sp)
        extra = _near_misses(rng, b, a, n=2)
        if not extra:
            continue
        pieces = [a, b] + extra
        rng.shuffle(pieces)
        pairs = list(combinations(range(4), 2))
        good = [pq for pq in pairs if completes(pieces[pq[0]], pieces[pq[1]])]
        if len(good) == 1:
            break
    else:
        raise RuntimeError("no puzzle found")
    good = good[0]
    labels = [f"{i + 1} and {j + 1}" for i, j in pairs if (i, j) != good]
    choices, ai = text_choices(f"{good[0] + 1} and {good[1] + 1}", labels, rng)
    shown = [_show(p, rng) for p in pieces]
    figs = [draw_shape(p, scale=12, fill=GREY, label=str(i + 1)) for i, p in enumerate(shown)]
    text = f"Which two of these pieces fit together to make a rectangle? {NOTE}"
    sol = (f"Pieces {good[0] + 1} and {good[1] + 1} have {len(pieces[good[0]]) + len(pieces[good[1]])} squares "
           f"together and fit into a {w} × {h} rectangle. No other pair does.")
    pair = lambda lab: [shown[int(x) - 1] for x in lab.split(" and ")]
    return Question(text=text, figure=row(figs, gap=18), choices=choices, answer=ai, solution=sol,
                    check=lambda i: makes_rectangle(*pair(choices[i])))


def _two_copies_ok(p):
    n = 2 * len(p)
    return any(can_tile(rect(w, n // w), [p, p]) for w in range(1, n + 1) if n % w == 0)


@variant(difficulty=3)
def two_copies(rng, harder):
    """Two copies of which piece make a rectangle?"""
    n = 6 if harder else 5     # with 4 squares only two shapes fail, too few for 4 wrong options
    for _ in range(400):
        good = random_shape(rng, n)
        if not _two_copies_ok(good) or len(orientations(good)) < 4:
            continue
        wrong = []
        for _ in range(300):
            q = random_shape(rng, n)
            if not _two_copies_ok(q) and not any(same_shape(q, x) for x in wrong):
                wrong.append(q)
            if len(wrong) == 4:
                break
        if len(wrong) == 4:
            break
    else:
        raise RuntimeError("no puzzle found")
    opts = wrong + [good]
    rng.shuffle(opts)
    k = opts.index(good)
    sizes = [(w, 2 * n // w) for w in range(1, 2 * n + 1) if (2 * n) % w == 0 and w <= 2 * n // w]
    text = f"Mia has two copies of the same piece. With which piece can she make a rectangle? {NOTE}"
    sol = (f"Two copies have {2 * n} squares, so the rectangle is " + " or ".join(f"{a} × {b}" for a, b in sizes)
           + f". Only two copies of piece {'ABCDE'[k]} fit together like that.")
    shown = [_show(o, rng) for o in opts]
    return Question(text=text, choices=[f"piece {c}" for c in "ABCDE"], answer=k,
                    choice_figures=[draw_shape(o, scale=12) for o in shown], solution=sol,
                    check=lambda i: makes_rectangle(shown[i], shown[i]))
