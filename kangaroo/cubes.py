"""Buildings made of unit cubes, drawn like the contest: front faces square,
depth going up and to the right, right-hand faces shaded.

A building is a set of cells (x, y, z): x to the right, y away from the viewer
(0 = front row), z up.
"""
from __future__ import annotations

from reportlab.lib import colors

from .figures import Fig

SIDE = colors.Color(0.80, 0.78, 0.74)   # shaded right-hand faces
TOP = colors.Color(0.93, 0.93, 0.93)    # top faces, lighter than the sides, so depth reads at a glance
GLASS = colors.Color(0.45, 0.45, 0.45)  # edges of a glass box: grey, so they don't look like cube edges
DX, DY = 0.45, 0.38                     # how far one step of depth moves on paper


def draw_cubes(cells, scale: float = 9, margin: float = 4, width: float = 0.7, box=None):
    """box=(a, b, c): also draw a glass box a wide, b deep, c tall around the cubes
    (corner at 0, 0, 0): back edges dashed before the cubes, front edges after."""
    cells = set(cells)
    if not cells and not box:
        raise ValueError("no cubes to draw")
    pts = list(cells) + ([(0, 0, 0), (box[0] - 1, box[1] - 1, box[2] - 1)] if box else [])
    xs = [c[0] for c in pts]; ys = [c[1] for c in pts]; zs = [c[2] for c in pts]
    x0, y0, z0 = min(xs), min(ys), min(zs)
    W = max(xs) - x0 + 1 + DX * (max(ys) - y0 + 1)
    H = max(zs) - z0 + 1 + DY * (max(ys) - y0 + 1)
    f = Fig(W, H, scale=scale, margin=margin)

    def P(x, y, z):
        return (x - x0 + DX * (y - y0), z - z0 + DY * (y - y0))

    if box:
        a, b, c = box
        for e in ((P(0, b, 0), P(a, b, 0)), (P(0, b, 0), P(0, b, c)), (P(0, 0, 0), P(0, b, 0))):
            f.line(*e, dash=True, width=0.8, color=GLASS)

    # painter's order: far rows first, then left to right, then bottom to top
    for (x, y, z) in sorted(cells, key=lambda c: (-c[1], c[0], c[2])):
        if (x + 1, y, z) not in cells:
            f.poly([P(x + 1, y, z), P(x + 1, y + 1, z), P(x + 1, y + 1, z + 1), P(x + 1, y, z + 1)],
                   fill=SIDE, width=width)
        if (x, y, z + 1) not in cells:
            f.poly([P(x, y, z + 1), P(x + 1, y, z + 1), P(x + 1, y + 1, z + 1), P(x, y + 1, z + 1)],
                   fill=TOP, width=width)
        if (x, y - 1, z) not in cells:
            f.poly([P(x, y, z), P(x + 1, y, z), P(x + 1, y, z + 1), P(x, y, z + 1)],
                   fill=colors.white, width=width)
    if box:
        a, b, c = box
        front = [((0, 0, 0), (a, 0, 0)), ((a, 0, 0), (a, 0, c)), ((a, 0, c), (0, 0, c)), ((0, 0, c), (0, 0, 0)),
                 ((a, 0, 0), (a, b, 0)), ((a, b, 0), (a, b, c)), ((a, 0, c), (a, b, c)),
                 ((0, 0, c), (0, b, c)), ((0, b, c), (a, b, c))]
        for p, q in front:
            f.line(P(*p), P(*q), width=1.1, color=GLASS)
    return f.drawing()


def painted_counts(a: int, b: int, c: int) -> dict:
    """A block a x b x c (each at least 2), painted all over and cut into unit cubes:
    {number of painted faces: number of small cubes}."""
    if min(a, b, c) < 2:
        raise ValueError("every side must be at least 2 cubes")
    out = {0: 0, 1: 0, 2: 0, 3: 0}
    for x in range(a):
        for y in range(b):
            for z in range(c):
                out[(x in (0, a - 1)) + (y in (0, b - 1)) + (z in (0, c - 1))] += 1
    return out


def tunnel(n: int, depth: int, wall: int = 1, height: int | None = None):
    """A square frame n wide (and `height` tall) with a hole, `depth` cubes long.
    The hole goes through from front to back and sits on the bottom wall."""
    height = height or n
    return {(x, y, z) for x in range(n) for z in range(height) for y in range(depth)
            if not (wall <= x < n - wall and wall <= z < height - wall)}


def step_pyramid(layers):
    """layers: bottom-up list of (side, height); each layer is a solid side x side
    square block centred on the one below (sides should drop by 2)."""
    base = layers[0][0]
    cells, z = set(), 0
    for side, h in layers:
        off = (base - side) // 2
        for dz in range(h):
            for x in range(side):
                for y in range(side):
                    cells.add((off + x, off + y, z + dz))
        z += h
    return cells


# ---------------------------------------------------------------- answer checks (cube by cube)
SIX = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]


def exposed_faces(cell, cells) -> int:
    """How many faces of this cube touch the outside (no neighbour there)."""
    x, y, z = cell
    return sum((x + dx, y + dy, z + dz) not in cells for dx, dy, dz in SIX)


def buried(cells, layers: int = 1) -> int:
    """Cubes with at least `layers` cubes of the building around them in every direction."""
    cells = set(cells)
    rng = range(-layers, layers + 1)
    return sum(all((x + dx, y + dy, z + dz) in cells for dx in rng for dy in rng for dz in rng)
               for x, y, z in cells)
