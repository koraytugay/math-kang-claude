"""Small drawing helper for contest-style line figures (vector, crisp in the PDF).

Work in "problem units" (e.g. centimetres of the shape); the helper scales
everything to fit a box of `max_px` points and leaves margin for labels.
"""
from __future__ import annotations

import math

from reportlab.graphics.shapes import Drawing, Line, Polygon, PolyLine, String, Rect
from reportlab.lib import colors

GREY = colors.Color(0.82, 0.82, 0.82)
LIGHT = colors.Color(0.92, 0.92, 0.92)


class Fig:
    def __init__(self, w: float, h: float, max_px: float = 110, margin: float = 22,
                 font: str = "Times-Roman", font_size: float = 11, scale: float | None = None):
        """`scale` (points per unit) overrides max_px - use it to draw several figures at the same scale."""
        self.scale = scale if scale else max_px / max(w, h)
        self.margin = margin
        self.font, self.fs = font, font_size
        self.d = Drawing(w * self.scale + 2 * margin, h * self.scale + 2 * margin)

    # --- coordinate transform -------------------------------------------
    def p(self, x: float, y: float) -> tuple[float, float]:
        return self.margin + x * self.scale, self.margin + y * self.scale

    # --- primitives ------------------------------------------------------
    def poly(self, pts, fill=None, width: float = 1.2):
        flat = [c for pt in pts for c in self.p(*pt)]
        self.d.add(Polygon(flat, fillColor=fill, strokeColor=colors.black, strokeWidth=width))

    def rect(self, x, y, w, h, fill=None, width: float = 1.2):
        self.poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], fill=fill, width=width)

    def line(self, a, b, dash: bool = False, width: float = 1.2):
        (x1, y1), (x2, y2) = self.p(*a), self.p(*b)
        ln = Line(x1, y1, x2, y2, strokeColor=colors.black, strokeWidth=width)
        if dash:
            ln.strokeDashArray = [3, 2]
        self.d.add(ln)

    def polyline(self, pts, width: float = 1.2):
        flat = [c for pt in pts for c in self.p(*pt)]
        self.d.add(PolyLine(flat, strokeColor=colors.black, strokeWidth=width))

    def arc(self, cx, cy, r, start_deg=0, end_deg=180, width: float = 1.2, ry=None):
        """Circular (or elliptical with ry) arc around (cx, cy), angles counter-clockwise."""
        ry = r if ry is None else ry
        n = 24
        pts = [(cx + r * math.cos(math.radians(start_deg + (end_deg - start_deg) * i / n)),
                cy + ry * math.sin(math.radians(start_deg + (end_deg - start_deg) * i / n)))
               for i in range(n + 1)]
        self.polyline(pts, width)

    def text(self, x, y, s, anchor="middle", size=None, italic=False):
        """Text at problem coordinates (x, y), no offset."""
        px, py = self.p(x, y)
        self.d.add(String(px, py - (size or self.fs) * 0.35, s, textAnchor=anchor,
                          fontName=("Times-Italic" if italic else self.font),
                          fontSize=size or self.fs))

    def point(self, x, y, name, where: str):
        """Label a vertex. where in {'nw','ne','sw','se','n','s','e','w'}."""
        dx = -1 if "w" in where else (1 if "e" in where else 0)
        dy = 1 if "n" in where else (-1 if "s" in where else 0)
        px, py = self.p(x, y)
        off = 9
        anchor = "end" if dx < 0 else ("start" if dx > 0 else "middle")
        self.d.add(String(px + dx * 4, py + dy * off - self.fs * 0.35, name, textAnchor=anchor,
                          fontName="Times-Italic", fontSize=self.fs))

    def side(self, a, b, s, where: str):
        """Label the side a-b at its midpoint, pushed out to 'above'/'below'/'left'/'right'."""
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        px, py = self.p(mx, my)
        off = 10
        if where == "above":
            px, py, anchor = px, py + off, "middle"
        elif where == "below":
            px, py, anchor = px, py - off, "middle"
        elif where == "left":
            px, py, anchor = px - 5, py, "end"
        else:
            px, py, anchor = px + 5, py, "start"
        self.d.add(String(px, py - self.fs * 0.35, s, textAnchor=anchor,
                          fontName=self.font, fontSize=self.fs * 0.95))

    def drawing(self) -> Drawing:
        return self.d
