"""2003 Q18 - which two pieces cover the empty area exactly?

Original: a squared rectangle with an empty area in it, and four pieces made of
squares (1, 2, 3, 4). Which two of these figures can one use to cover exactly
the empty area?  A 1+3  B 2+4  C 2+3  D 1+4  E 3+4.  Answer: C.

Core skill: fitting shapes made of squares - count squares first (the two pieces
must add up to the size of the hole), then turn the pieces in your head to see
if they really fit. Children match by "looks similar" and skip the counting.
"""
from itertools import combinations

from kangaroo import Question, variant
from kangaroo.figures import row
from kangaroo.polyomino import (can_tile, covers, draw_hole, draw_shape, neighbours, normalize,
                                orientations, random_shape, same_shape)

META = {
    "source": "2003 Q18",
    "skill": "Covering a shape with pieces of squares: count the squares, then turn the pieces",
    "topics": ["spatial", "geometry", "counting"],
    "version": 1,
}

NOTE = "The pieces may be turned and flipped over."


def _attach(rng, region, piece, tries=300):
    """Place a turned copy of `piece` next to `region` (no overlap, touching)."""
    region = set(region)
    for _ in range(tries):
        o = rng.choice(orientations(piece))
        ax, ay = rng.choice(sorted(region))
        bx, by = rng.choice(sorted(o))
        nx, ny = rng.choice(neighbours((ax, ay)))
        cells = {(x - bx + nx, y - by + ny) for x, y in o}
        if cells & region:
            continue
        new = normalize(region | cells)
        if max(x for x, _ in new) < 6 and max(y for _, y in new) < 6:
            return new
    return None


def _build(rng, pieces):
    region = normalize(pieces[0])
    for p in pieces[1:]:
        region = _attach(rng, region, p)
        if region is None:
            return None
    return region


def _show(p, rng):
    """A random turned copy for display (never flipped, so it is easy to compare)."""
    return rng.choice(orientations(p, flip=False))


def _distractor(rng, size, avoid):
    for _ in range(200):
        s = random_shape(rng, size)
        if not any(same_shape(s, a) for a in avoid):
            return s
    raise RuntimeError("no distractor")


def _pieces_fig(region, shown):
    figs = [draw_hole(region, scale=9)]
    figs += [draw_shape(p, scale=9, label=str(i + 1)) for i, p in enumerate(shown)]
    return row(figs, gap=14)


def _numbered_check(region, shown, labels):
    """check(i): the numbered pieces named in option i ('1+3') cover the region."""
    return lambda i: covers(region, [shown[int(k) - 1] for k in labels[i].split("+")])


@variant(difficulty=1)
def one_piece(rng, harder):
    """Which single piece fits the hole exactly?"""
    n = rng.randint(6, 7) if harder else rng.randint(5, 6)
    while True:
        region = random_shape(rng, n)
        if len(orientations(region)) == 8:           # no symmetry, so turning matters
            break
    wrong = []
    while len(wrong) < 4:                          # move one square: same size, different shape
        cells = set(region)
        cells.remove(rng.choice(sorted(cells)))
        add = rng.choice(sorted({nb for c in cells for nb in neighbours(c)} - cells))
        cells.add(add)
        cand = normalize(cells)
        if _connected(cand) and not same_shape(cand, region) and not any(same_shape(cand, w) for w in wrong):
            wrong.append(cand)
    opts = wrong + [region]
    rng.shuffle(opts)
    k = opts.index(region)
    shown = [_show(p, rng) for p in opts]
    figs = [draw_shape(p, scale=9) for p in shown]
    text = f"Which piece covers the empty area exactly? {NOTE}"
    sol = (f"The empty area has {n} squares; all pieces do too, so look at the shape. Turn piece "
           f"{'ABCDE'[k]} and it fits exactly; each of the others has one square in a different place.")
    return Question(text=text, figure=draw_hole(region, scale=9), choices=[f"piece {c}" for c in "ABCDE"],
                    answer=k, choice_figures=figs, solution=sol, check=lambda i: covers(region, [shown[i]]))


def _connected(cells):
    cells = set(cells)
    seen, todo = set(), [next(iter(cells))]
    while todo:
        c = todo.pop()
        if c in seen:
            continue
        seen.add(c)
        todo += [nb for nb in neighbours(c) if nb in cells]
    return seen == cells


@variant(difficulty=1)
def two_pieces(rng, harder):
    """The original: four pieces, which two cover the hole?"""
    for _ in range(300):
        sa, sb = (rng.randint(4, 6), rng.randint(4, 6)) if harder else (rng.randint(3, 5), rng.randint(3, 5))
        a, b = random_shape(rng, sa), random_shape(rng, sb)
        region = _build(rng, [a, b])
        if region is None:
            continue
        # distractors: one with the size of a, one with the size of b, so counting alone is not enough
        try:
            c = _distractor(rng, sa, [a, b])
            d = _distractor(rng, sb if rng.random() < 0.7 else sb + 1, [a, b, c])
        except RuntimeError:
            continue
        pieces = [a, b, c, d]
        rng.shuffle(pieces)
        pairs = list(combinations(range(4), 2))
        good = [pq for pq in pairs if can_tile(region, [pieces[pq[0]], pieces[pq[1]]])]
        if len(good) == 1:
            break
    else:
        raise RuntimeError("no puzzle found")
    good = good[0]
    others = [pq for pq in pairs if pq != good]
    opts = rng.sample(others, 4) + [good]
    opts.sort()
    labels = [f"{i + 1}+{j + 1}" for i, j in opts]
    k = opts.index(good)
    n = len(region)
    sizes = ", ".join(f"{i + 1}: {len(p)}" for i, p in enumerate(pieces))
    text = f"Which two of these pieces can be used to cover the empty area exactly? {NOTE}"
    sol = (f"The empty area has {n} squares. Pieces have {sizes} squares. Only pieces "
           f"{good[0] + 1} and {good[1] + 1} also fit together in the right shape.")
    shown = [_show(p, rng) for p in pieces]
    return Question(text=text, figure=_pieces_fig(region, shown), choices=labels, answer=k,
                    solution=sol, check=_numbered_check(region, shown, labels))


@variant(difficulty=2)
def two_copies(rng, harder):
    """Two copies of the same piece cover the hole - which piece?"""
    n = rng.randint(5, 6) if harder else rng.randint(4, 5)   # 3 squares: only 2 shapes exist
    for _ in range(300):
        p = random_shape(rng, n)
        region = _build(rng, [p, p])
        if region is None:
            continue
        wrong = []
        for _ in range(200):
            q = random_shape(rng, n)
            if not same_shape(q, p) and not any(same_shape(q, w) for w in wrong) \
                    and not can_tile(region, [q, q]):
                wrong.append(q)
            if len(wrong) == 4:
                break
        if len(wrong) == 4:
            break
    else:
        raise RuntimeError("no puzzle found")
    opts = wrong + [p]
    rng.shuffle(opts)
    k = opts.index(p)
    text = f"Two pieces that are exactly the same cover the empty area. Which piece is it? {NOTE}"
    sol = (f"The empty area has {2 * n} squares, so each piece has {n}; every option has {n}. "
           f"Only two copies of piece {'ABCDE'[k]} fit together into the shape of the hole.")
    shown = [_show(o, rng) for o in opts]
    return Question(text=text, figure=draw_hole(region, scale=9), choices=[f"piece {c}" for c in "ABCDE"],
                    answer=k, choice_figures=[draw_shape(o, scale=9) for o in shown],
                    solution=sol, check=lambda i: covers(region, [shown[i], shown[i]]))


@variant(difficulty=3)
def three_pieces(rng, harder):
    """Five pieces; which three cover the hole?"""
    for _ in range(300):
        sizes = [rng.randint(3, 5) for _ in range(3)]
        trio = [random_shape(rng, s, 3, 3) for s in sizes]
        region = _build(rng, trio)
        if region is None:
            continue
        try:
            extra = [_distractor(rng, rng.choice(sizes), trio), _distractor(rng, rng.choice(sizes), trio)]
        except RuntimeError:
            continue
        pieces = trio + extra
        rng.shuffle(pieces)
        triples = list(combinations(range(5), 3))
        good = [t for t in triples if can_tile(region, [pieces[i] for i in t])]
        if len(good) == 1:
            break
    else:
        raise RuntimeError("no puzzle found")
    good = good[0]
    opts = sorted(rng.sample([t for t in triples if t != good], 4) + [good])
    labels = ["+".join(str(i + 1) for i in t) for t in opts]
    text = f"Which three of these pieces can be used to cover the empty area exactly? {NOTE}"
    sol = (f"The empty area has {len(region)} squares, so the three sizes must add up to {len(region)}. "
           f"Only {' + '.join(str(i + 1) for i in good)} also fit together in the right shape.")
    shown = [_show(p, rng) for p in pieces]
    return Question(text=text, figure=_pieces_fig(region, shown), choices=labels, answer=opts.index(good),
                    solution=sol, check=_numbered_check(region, shown, labels))
