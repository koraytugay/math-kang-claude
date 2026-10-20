"""Plane-geometry helpers used by answer checks."""
from __future__ import annotations

from fractions import Fraction


def perimeter(pts) -> Fraction | float:
    """Length around a polygon with axis-parallel sides (exact for int/Fraction points)."""
    total = 0
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        if x1 != x2 and y1 != y2:
            total += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        else:
            total += abs(x2 - x1) + abs(y2 - y1)
    return total


def rect_pts(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
