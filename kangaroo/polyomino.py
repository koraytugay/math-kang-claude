"""Shapes made of unit squares (polyominoes): random shapes, turning/flipping,
an exact tiling solver, and drawings on squared paper.

A shape is a frozenset of (x, y) cells, y going up.
"""
from __future__ import annotations

from reportlab.lib import colors

from .figures import GREY, Fig


def normalize(cells):
    mx = min(x for x, _ in cells); my = min(y for _, y in cells)
    return frozenset((x - mx, y - my) for x, y in cells)


def orientations(cells, flip: bool = True):
    """All distinct turned (and, if flip, mirrored) copies, normalized."""
    out, cur = set(), list(cells)
    for f in ([False, True] if flip else [False]):
        pts = [(-x, y) for x, y in cur] if f else cur
        for _ in range(4):
            pts = [(y, -x) for x, y in pts]
            out.add(normalize(pts))
    return list(out)


def same_shape(a, b, flip: bool = True) -> bool:
    return normalize(b) in orientations(a, flip)


def neighbours(c):
    x, y = c
    return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]


def random_shape(rng, n: int, max_w: int = 4, max_h: int = 4):
    """A random connected shape of n cells that fits in max_w x max_h."""
    while True:
        cells = {(0, 0)}
        while len(cells) < n:
            c = rng.choice(sorted(cells))
            nb = rng.choice(neighbours(c))
            cells.add(nb)
        s = normalize(cells)
        if max(x for x, _ in s) < max_w and max(y for _, y in s) < max_h:
            return s


def tilings(region, pieces, flip: bool = True, limit: int = 1):
    """Ways to cover `region` exactly using every piece once (turning allowed).
    Returns a list of placements [(piece_index, cells), ...]; at most `limit` of them."""
    region = frozenset(region)
    if sum(len(p) for p in pieces) != len(region):
        return []
    orients = [orientations(p, flip) for p in pieces]
    found = []

    def solve(left, unused, placed):
        if len(found) >= limit:
            return
        if not left:
            found.append(list(placed))
            return
        target = min(left, key=lambda c: (c[1], c[0]))
        for i in list(unused):
            for o in orients[i]:
                anchor = min(o, key=lambda c: (c[1], c[0]))
                dx, dy = target[0] - anchor[0], target[1] - anchor[1]
                cells = frozenset((x + dx, y + dy) for x, y in o)
                if cells <= left:
                    placed.append((i, cells))
                    solve(left - cells, unused - {i}, placed)
                    placed.pop()

    solve(region, frozenset(range(len(pieces))), [])
    return found


def can_tile(region, pieces, flip: bool = True) -> bool:
    return bool(tilings(region, pieces, flip, limit=1))


def draw_shape(cells, scale: float = 9, fill=colors.white, margin: float = 3, label: str = ""):
    """A shape drawn as squares on paper (optionally with a label above it)."""
    w = max(x for x, _ in cells) + 1
    h = max(y for _, y in cells) + 1
    top = 1.4 if label else 0
    f = Fig(w, h + top, scale=scale, margin=margin)
    for x, y in cells:
        f.rect(x, y, 1, 1, fill=fill, width=0.9)
    if label:
        f.text(w / 2, h + 0.75, label, size=11)
    return f.drawing()


def draw_hole(region, scale: float = 9, pad: int = 1):
    """A rectangle of grey squares with the region left empty (white, thin grid)."""
    xs = [x for x, _ in region]; ys = [y for _, y in region]
    x0, x1, y0, y1 = min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad
    W, H = x1 - x0 + 1, y1 - y0 + 1
    f = Fig(W, H, scale=scale, margin=3)
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            if (x, y) in region:
                f.rect(x - x0, y - y0, 1, 1, fill=colors.white, width=0.3)
            else:
                f.rect(x - x0, y - y0, 1, 1, fill=GREY, width=0.9)
    # outline of the hole drawn strong so its shape is clear
    for x, y in region:
        for (nx, ny), seg in (((x + 1, y), ((x + 1, y), (x + 1, y + 1))), ((x - 1, y), ((x, y), (x, y + 1))),
                              ((x, y + 1), ((x, y + 1), (x + 1, y + 1))), ((x, y - 1), ((x, y), (x + 1, y)))):
            if (nx, ny) not in region:
                (a, b), (c, d) = seg
                f.line((a - x0, b - y0), (c - x0, d - y0), width=1.4)
    return f.drawing()


# ---------------------------------------------------------------- answer checks
_TURNS = [lambda x, y: (x, y), lambda x, y: (-y, x), lambda x, y: (-x, -y), lambda x, y: (y, -x),
          lambda x, y: (-x, y), lambda x, y: (y, x), lambda x, y: (x, -y), lambda x, y: (-y, -x)]


def placements(region, piece):
    """Every way to lay the piece (turned or flipped) on squares of the region (written separately
    from tilings(), so it can check it)."""
    region = set(region)
    out = set()
    for t in _TURNS:
        cells = [t(x, y) for x, y in piece]
        ax, ay = cells[0]
        for rx, ry in region:                      # put the piece's first square on every region square
            moved = frozenset((x - ax + rx, y - ay + ry) for x, y in cells)
            if moved <= region:
                out.add(moved)
    return out


def covers(region, pieces) -> bool:
    """Do these pieces (each used once) cover the region exactly, with no overlap?"""
    region = frozenset(region)
    if sum(len(p) for p in pieces) != len(region):
        return False
    options = [placements(region, p) for p in pieces]

    def go(i, used):
        if i == len(pieces):
            return used == region
        return any(go(i + 1, used | pl) for pl in options[i] if not used & pl)
    return go(0, frozenset())


def makes_rectangle(a, b) -> bool:
    """Can piece b (turned or flipped) be put next to piece a (as it is) so they fill a rectangle?"""
    a = normalize(a)
    area = len(a) + len(b)
    aw, ah = max(x for x, _ in a) + 1, max(y for _, y in a) + 1
    for w in range(aw, area + 1):
        if area % w or area // w < ah:
            continue
        h = area // w
        box = frozenset((x, y) for x in range(w) for y in range(h))
        for dx in range(w - aw + 1):
            for dy in range(h - ah + 1):
                if covers(box - {(x + dx, y + dy) for x, y in a}, [b]):
                    return True
    return False
