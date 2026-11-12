"""Shapes made of unit squares and half squares (squares cut along a diagonal).

Every unit cell (x, y) is split into four quarter triangles by both diagonals:
q = 0 bottom, 1 right, 2 top, 3 left. A shape is a frozenset of (x, y, q).
A half square is two quarters next to each other ({0,1}, {1,2}, {2,3} or {3,0}); a whole square is all four.
Gives: turning/flipping, an exact tiling solver, random cutting of a region into pieces, drawings.
"""
from __future__ import annotations

from reportlab.lib import colors

from .figures import Fig

FILL = colors.Color(0.86, 0.91, 0.97)
GREYFILL = colors.Color(0.78, 0.78, 0.78)
HALVES = [(0, 1), (1, 2), (2, 3), (3, 0)]


def square(x, y):
    return {(x, y, q) for q in range(4)}


def from_cells(cells):
    return frozenset(t for x, y in cells for t in square(x, y))


def area2(shape) -> int:
    """Area in half squares."""
    return len(shape) // 2


def normalize(shape):
    mx = min(x for x, _, _ in shape)
    my = min(y for _, y, _ in shape)
    return frozenset((x - mx, y - my, q) for x, y, q in shape)


def _turn(shape):          # 90 degrees clockwise: point (X, Y) -> (Y, -X)
    return [(y, -x - 1, (q + 3) % 4) for x, y, q in shape]


def _flip(shape):          # mirror: X -> -X
    return [(-x - 1, y, {1: 3, 3: 1}.get(q, q)) for x, y, q in shape]


def orientations(shape, flip: bool = True):
    out, base = [], [list(shape)] + ([_flip(shape)] if flip else [])
    for s in base:
        for _ in range(4):
            s = _turn(s)
            n = normalize(s)
            if n not in out:
                out.append(n)
    return out


def same_shape(a, b, flip: bool = True) -> bool:
    return normalize(b) in orientations(a, flip)


def turned(rng, shape, flip: bool = False):
    return rng.choice(orientations(shape, flip))


def tilings(region, pieces, flip: bool = True, limit: int = 50):
    """Ways to fill `region` exactly with every piece once (turning, and if flip also turning over).
    Returns up to `limit` solutions, each a dict {quarter: piece index}."""
    region = frozenset(region)
    if sum(len(p) for p in pieces) != len(region):
        return []
    orients = [orientations(p, flip) for p in pieces]
    found = []

    def solve(left, unused, owner):
        if len(found) >= limit:
            return
        if not left:
            found.append(dict(owner))
            return
        x, y, q = min(left)
        for i in list(unused):
            for o in orients[i]:
                for a, b, q2 in o:
                    if q2 != q:
                        continue
                    dx, dy = x - a, y - b
                    cells = {(u + dx, v + dy, r) for u, v, r in o}
                    if cells <= left:
                        for c in cells:
                            owner[c] = i
                        solve(left - cells, unused - {i}, owner)
                        for c in cells:
                            del owner[c]

    solve(region, frozenset(range(len(pieces))), {})
    return found


def _units(cells, rng):
    """Cut every cell along a random diagonal: a list of half squares (each a frozenset of 2 quarters)."""
    out = []
    for x, y in cells:
        a, b = rng.choice([((0, 1), (2, 3)), ((3, 0), (1, 2))])
        out += [frozenset((x, y, q) for q in a), frozenset((x, y, q) for q in b)]
    return out


def _touch(u, v):
    """Two half squares share an edge (inside one cell, or across a cell side)."""
    for x, y, q in u:
        for x2, y2, q2 in v:
            if (x, y) == (x2, y2) and (q - q2) % 4 in (1, 3):
                return True
            if (q, q2) == (1, 3) and (x2, y2) == (x + 1, y) or (q, q2) == (3, 1) and (x2, y2) == (x - 1, y):
                return True
            if (q, q2) == (2, 0) and (x2, y2) == (x, y + 1) or (q, q2) == (0, 2) and (x2, y2) == (x, y - 1):
                return True
    return False


def random_cut(cells, sizes, rng, tries: int = 200):
    """Cut the region of `cells` into connected pieces of the given sizes (in half squares)."""
    for _ in range(tries):
        units = _units(cells, rng)
        nb = {i: [j for j in range(len(units)) if j != i and _touch(units[i], units[j])] for i in range(len(units))}
        free = set(range(len(units)))
        groups = []
        seeds = rng.sample(sorted(free), len(sizes))
        for s in seeds:
            groups.append([s])
            free.discard(s)
        ok = True
        while free and ok:
            grow = [g for g, size in zip(range(len(groups)), sizes) if len(groups[g]) < size and
                    any(j in free for i in groups[g] for j in nb[i])]
            if not grow:
                ok = False
                break
            g = rng.choice(grow)
            j = rng.choice(sorted({j for i in groups[g] for j in nb[i] if j in free}))
            groups[g].append(j)
            free.discard(j)
        if ok and not free and all(len(g) == s for g, s in zip(groups, sizes)):
            return [frozenset(q for i in g for q in units[i]) for g in groups]
    return None


# ------------------------------------------------------------------ drawing
def _parts(shape):
    """Split a shape into polygons: whole squares and half squares (in unit coordinates)."""
    by = {}
    for x, y, q in shape:
        by.setdefault((x, y), set()).add(q)
    polys = []
    for (x, y), qs in sorted(by.items()):
        if len(qs) == 4:
            polys.append([(x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1)])
            continue
        for h in HALVES:
            if set(h) <= qs:
                qs -= set(h)
                corner = {(0, 1): [(x, y), (x + 1, y), (x + 1, y + 1)], (1, 2): [(x + 1, y), (x + 1, y + 1), (x, y + 1)],
                          (2, 3): [(x + 1, y + 1), (x, y + 1), (x, y)], (3, 0): [(x, y + 1), (x, y), (x + 1, y)]}[h]
                polys.append(corner)
        if qs:
            raise ValueError("shape has a lone quarter")
    return polys


def bbox(shape):
    xs = [x for x, _, _ in shape]
    ys = [y for _, y, _ in shape]
    return min(xs), min(ys), max(xs) + 1, max(ys) + 1


def draw(shape, scale: float = 14, fill=FILL, extra=(), dot=None, margin: float = 4, box=None):
    """Draw a shape with its squares and half squares. `extra` = [(shape, fill)] drawn on top
    (e.g. pieces already placed); `dot` = (x, y) for a black dot. `box` = (w, h) in units for a fixed size."""
    x0, y0, x1, y1 = bbox(shape)
    w, h = box or (x1 - x0, y1 - y0)
    f = Fig(w, h, scale=scale, margin=margin)
    for s, fl in [(shape, fill)] + list(extra):
        for poly in _parts(s):
            f.poly([(x - x0, y - y0) for x, y in poly], fill=fl, width=1.0)
    if dot:
        f.circle(dot[0] - x0, dot[1] - y0, 0.07, fill=colors.black, width=0.5)
    return f.drawing()


def outline(cells, scale: float = 14, dot=None, extra=(), margin: float = 4):
    """A region of whole cells drawn on squared paper (light blue squares), like the contest picture."""
    return draw(from_cells(cells), scale=scale, dot=dot, extra=extra, margin=margin)


def half_centre(shape, quarter):
    """A good spot for a dot: the middle of the half square (or square) of `shape` holding `quarter`."""
    x, y, q = quarter
    qs = {r for a, b, r in shape if (a, b) == (x, y)}
    if len(qs) == 4:
        return x + 0.5, y + 0.5
    for h in HALVES:
        if q in h and set(h) <= qs:
            pts = {(0, 1): [(x, y), (x + 1, y), (x + 1, y + 1)], (1, 2): [(x + 1, y), (x + 1, y + 1), (x, y + 1)],
                   (2, 3): [(x + 1, y + 1), (x, y + 1), (x, y)], (3, 0): [(x, y + 1), (x, y), (x + 1, y)]}[h]
            return sum(p[0] for p in pts) / 3, sum(p[1] for p in pts) / 3
    raise ValueError("quarter not in a half square")
