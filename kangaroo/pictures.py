"""Reusable contest pictures built on Fig: balance scales, clock faces, ..."""
from __future__ import annotations

import math

from reportlab.lib import colors

from .figures import Fig

# ------------------------------------------------------------------ items
# Item shapes used on balances (and anywhere else small objects are needed).
# size = width in units
ITEM_SIZE = {"dot": 0.62, "ball": 1.45, "box": 1.05, "tri": 1.1}
DARK = colors.Color(0.45, 0.45, 0.45)
MID = colors.Color(0.75, 0.75, 0.75)


def draw_item(f: Fig, kind: str, x: float, y: float):
    """Draw item `kind` with its bottom-left corner at (x, y)."""
    s = ITEM_SIZE[kind]
    if kind == "dot":
        f.circle(x + s / 2, y + s / 2, s / 2, fill=DARK, width=0.8)
    elif kind == "ball":
        f.circle(x + s / 2, y + s / 2, s / 2, fill=colors.white, width=1.0)
    elif kind == "box":
        f.rect(x, y, s, s, fill=MID, width=0.9)
    elif kind == "tri":
        f.poly([(x, y), (x + s, y), (x + s / 2, y + s * 0.9)], fill=colors.white, width=0.9)


def _layout(items, width):
    """Pack items into rows (bottom row first) that fit in `width`. Big items go at the bottom."""
    items = sorted(items, key=lambda k: -ITEM_SIZE[k])
    rows, cur, cur_w = [], [], 0.0
    for k in items:
        s = ITEM_SIZE[k] + 0.08
        if cur and cur_w + s > width:
            rows.append(cur)
            cur, cur_w = [], 0.0
        cur.append(k)
        cur_w += s
    if cur:
        rows.append(cur)
    return rows


PAN_W = 5.6


def _pile_height(items):
    return sum(max(ITEM_SIZE[k] for k in r) for r in _layout(items, PAN_W - 0.3)) if items else 0


def balance(left, right, tilt: int = 0, scale: float = 13, legend=None,
            left_extra: str = "", right_extra: str = ""):
    """A two-pan balance.

    left/right: lists of item kinds, e.g. ["ball", "ball", "dot"].
    tilt: 0 level, -1 left side down, +1 right side down.
    legend: list of (kind, name) shown under the scale, e.g. [("dot", "orange")].
    left_extra/right_extra: a short label (like "?") drawn on top of a pile.
    """
    W = 2 * PAN_W + 3.0
    pile = max(_pile_height(left), _pile_height(right), 1.0)
    leg_h = 1.6 if legend else 0
    H = leg_h + 3.4 + pile + 0.8
    f = Fig(W, H, scale=scale, margin=4)
    base = leg_h
    cx = W / 2
    # stand
    f.rect(cx - 1.6, base, 3.2, 0.3, fill=MID, width=0.8)
    f.poly([(cx - 0.7, base + 0.3), (cx + 0.7, base + 0.3), (cx, base + 2.4)], fill=MID, width=0.8)
    # beam
    ang = math.radians(-8 * tilt)
    half = W / 2 - 1.3
    by = base + 2.4
    lx, ly = cx - half * math.cos(ang), by - half * math.sin(ang)
    rx, ry = cx + half * math.cos(ang), by + half * math.sin(ang)
    f.line((lx, ly), (rx, ry), width=2)
    for (px, py), items, extra in (((lx, ly), left, left_extra), ((rx, ry), right, right_extra)):
        top = py + 0.8
        f.line((px, py), (px, top), width=1.2)
        f.polyline([(px - PAN_W / 2, top + 0.35), (px - PAN_W / 2 + 0.3, top),
                    (px + PAN_W / 2 - 0.3, top), (px + PAN_W / 2, top + 0.35)], width=1.3)
        y = top + 0.04
        for r in _layout(items, PAN_W - 0.3):
            rw = sum(ITEM_SIZE[k] + 0.08 for k in r) - 0.08
            x = px - rw / 2
            for k in r:
                draw_item(f, k, x, y)
                x += ITEM_SIZE[k] + 0.08
            y += max(ITEM_SIZE[k] for k in r)
        if extra:
            f.text(px, y + 0.55, extra, size=15)
    if legend:
        n = len(legend)
        slot = W / n
        for i, (kind, name) in enumerate(legend):
            x0 = slot * i + slot / 2 - 1.6
            s = ITEM_SIZE[kind]
            draw_item(f, kind, x0, 0.75 - s / 2)
            f.text(x0 + s + 0.3, 0.75, f"= {name}", anchor="start", size=10)
    return f.drawing()


def legend(entries, scale: float = 10):
    """A row like '[shape] = orange   [shape] = melon' for a list of (kind, name)."""
    widths = [ITEM_SIZE[k] + 0.6 + 0.5 * (len(nm) + 2) + 1.5 for k, nm in entries]
    f = Fig(sum(widths), 1.6, scale=scale, margin=2)
    x = 0.0
    for (kind, nm), w in zip(entries, widths):
        draw_item(f, kind, x, 0.8 - ITEM_SIZE[kind] / 2)
        f.text(x + ITEM_SIZE[kind] + 0.3, 0.8, f"= {nm}", anchor="start", size=10)
        x += w
    return f.drawing()


# ------------------------------------------------------------------ clock / number wheel
def number_wheel(numbers, cuts=(), scale: float = 9, radius: float = 5.0, jagged_seed: int = 0,
                 font_size: float = 10):
    """Numbers placed around a circle (like a clock face, first number at the top).

    cuts: indices i meaning "a crack between numbers[i-1] and numbers[i]"; cracks are
    drawn as jagged lines from the centre to the rim.
    """
    import random
    n = len(numbers)
    R = radius
    f = Fig(2 * R, 2 * R, scale=scale, margin=4)
    f.arc(R, R, R, 0, 360, width=1.3)
    for i, num in enumerate(numbers):
        a = math.radians(90 - 360 * i / n)
        f.text(R + 0.78 * R * math.cos(a), R + 0.78 * R * math.sin(a), str(num), size=font_size)
    rng = random.Random(jagged_seed)

    def jag(p0, p1, steps=9, amp=0.18):
        (x0, y0), (x1, y1) = p0, p1
        L = math.hypot(x1 - x0, y1 - y0)
        nx, ny = -(y1 - y0) / L, (x1 - x0) / L
        pts = []
        for k in range(steps + 1):
            t = k / steps
            j = 0 if k in (0, steps) else rng.uniform(-amp, amp)
            pts.append((x0 + t * (x1 - x0) + j * nx, y0 + t * (y1 - y0) + j * ny))
        return pts

    if len(cuts) == 2:   # two pieces: one crack across the face
        ends = []
        for i in cuts:
            a = math.radians(90 - 360 * (i - 0.5) / n)
            ends.append((R + R * math.cos(a), R + R * math.sin(a)))
        # curve toward the centre (quadratic Bezier) so the crack never runs through a number
        (x0, y0), (x1, y1) = ends
        pts = []
        for k in range(17):
            t = k / 16
            px = (1 - t) ** 2 * x0 + 2 * t * (1 - t) * R + t ** 2 * x1
            py = (1 - t) ** 2 * y0 + 2 * t * (1 - t) * R + t ** 2 * y1
            j = 0 if k in (0, 16) else rng.uniform(-0.12, 0.12)
            pts.append((px + j, py - j))
        f.polyline(pts, width=1.2)
        cuts = ()
    for i in cuts:
        a = math.radians(90 - 360 * (i - 0.5) / n)
        pts = []
        steps = 7
        for k in range(steps + 1):
            t = k / steps
            r = R * t
            jit = 0 if k in (0, steps) else rng.uniform(-0.18, 0.18)
            px = R + r * math.cos(a) - jit * math.sin(a)
            py = R + r * math.sin(a) + jit * math.cos(a)
            pts.append((px, py))
        f.polyline(pts, width=1.2)
    return f.drawing()
