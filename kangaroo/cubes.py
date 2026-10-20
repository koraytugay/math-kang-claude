"""Buildings made of unit cubes, drawn like the contest: front faces square,
depth going up and to the right, right-hand faces shaded.

A building is a set of cells (x, y, z): x to the right, y away from the viewer
(0 = front row), z up.
"""
from __future__ import annotations

from reportlab.lib import colors

from .figures import Fig

SIDE = colors.Color(0.86, 0.84, 0.80)   # shaded right-hand faces
DX, DY = 0.45, 0.38                     # how far one step of depth moves on paper


def draw_cubes(cells, scale: float = 9, margin: float = 4, width: float = 0.7):
    cells = set(cells)
    if not cells:
        raise ValueError("no cubes to draw")
    xs = [c[0] for c in cells]; ys = [c[1] for c in cells]; zs = [c[2] for c in cells]
    x0, y0, z0 = min(xs), min(ys), min(zs)
    W = max(xs) - x0 + 1 + DX * (max(ys) - y0 + 1)
    H = max(zs) - z0 + 1 + DY * (max(ys) - y0 + 1)
    f = Fig(W, H, scale=scale, margin=margin)

    def P(x, y, z):
        return (x - x0 + DX * (y - y0), z - z0 + DY * (y - y0))

    # painter's order: far rows first, then left to right, then bottom to top
    for (x, y, z) in sorted(cells, key=lambda c: (-c[1], c[0], c[2])):
        if (x + 1, y, z) not in cells:
            f.poly([P(x + 1, y, z), P(x + 1, y + 1, z), P(x + 1, y + 1, z + 1), P(x + 1, y, z + 1)],
                   fill=SIDE, width=width)
        if (x, y, z + 1) not in cells:
            f.poly([P(x, y, z + 1), P(x + 1, y, z + 1), P(x + 1, y + 1, z + 1), P(x, y + 1, z + 1)],
                   fill=colors.white, width=width)
        if (x, y - 1, z) not in cells:
            f.poly([P(x, y, z), P(x + 1, y, z), P(x + 1, y, z + 1), P(x, y, z + 1)],
                   fill=colors.white, width=width)
    return f.drawing()


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
