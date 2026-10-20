"""2002 Q6 - perimeter of a rectangle cut from a square.

Original: ABCD is a square with side 10 cm. AMTD is a rectangle with shorter
side 3 cm (M on AB, T on DC). How many cm is the perimeter of the square larger
than the perimeter of AMTD?  Answer: 40 - 26 = 14 cm.

Core skill: the perimeter of a piece cut from a shape is built from sides you
already know; cutting adds the cut line twice and removes outer edges.
Variants approach this idea from different angles, from a direct rerun
(Part A) to working backwards from the pieces (Part C).
"""
from fractions import Fraction

from kangaroo import Fig, Question, numeric_choices, value_check, variant
from kangaroo.geometry import perimeter, rect_pts
from kangaroo.figures import GREY

META = {
    "source": "2002 Q6",
    "skill": "Perimeter of rectangles cut from a square or rectangle",
    "topics": ["geometry", "perimeter"],
    "version": 1,
}

# square vertex names (top-left, top-right, bottom-right, bottom-left) + cut points (top, bottom)
NAMES = [("ABCD", "MT"), ("PQRS", "EF"), ("KLMN", "XY"), ("WXYZ", "EF")]


def _square_with_cut(s, w, names, shade=None):
    (tl, tr, br, bl), (top, bot) = names
    f = Fig(s, s, max_px=95)
    if shade == "left":
        f.rect(0, 0, w, s, fill=GREY)
    elif shade == "right":
        f.rect(w, 0, s - w, s, fill=GREY)
    f.rect(0, 0, s, s)
    f.line((w, 0), (w, s))
    f.point(0, s, tl, "nw"); f.point(s, s, tr, "ne")
    f.point(s, 0, br, "se"); f.point(0, 0, bl, "sw")
    f.point(w, s, top, "n"); f.point(w, 0, bot, "s")
    return f.drawing()


@variant(difficulty=1)
def square_minus_strip(rng, harder):
    """The original question, sometimes asked about the *other* rectangle."""
    s = rng.randint(12, 30) if harder else rng.randint(6, 14)
    w = rng.randint(2, (s - 1) // 2)
    names = rng.choice(NAMES)
    (tl, tr, br, bl), (top, bot) = names
    sq = tl + tr + br + bl
    other = rng.random() < (0.6 if harder else 0.35)
    if not other:
        rect = tl + top + bot + bl
        text = (f"<i>{sq}</i> is a square. Its side is {s} cm. <i>{rect}</i> is a rectangle. "
                f"Its shorter side is {w} cm.")
        p_rect = 2 * (w + s)
        ans = 4 * s - p_rect
        sol = (f"Square: 4 × {s} = {4*s} cm. Rectangle: {w} + {s} + {w} + {s} = {p_rect} cm. "
               f"Difference {4*s} − {p_rect} = {ans} cm.")
        mistakes = [s - w, 2 * w, 2 * s, p_rect, 4 * (s - w), 4 * s - s - w]
        piece = rect_pts(0, 0, w, s)
    else:
        rect = top + tr + br + bot
        text = (f"<i>{sq}</i> is a square. Its side is {s} cm. The line <i>{top}{bot}</i> cuts it "
                f"into two rectangles, and <i>{tl}{top}</i> = {w} cm.")
        p_rect = 2 * (s - w + s)
        ans = 4 * s - p_rect
        sol = (f"<i>{rect}</i> has sides {s - w} and {s} cm, perimeter {p_rect} cm. "
               f"Square: {4*s} cm. Difference {ans} cm (= 2 × {w}).")
        mistakes = [2 * (s - w), w, s - w, 2 * s, p_rect, 4 * w]
        piece = rect_pts(w, 0, s - w, s)
    after = (f"How many centimetres is the perimeter of the square <i>{sq}</i> larger "
             f"than that of the rectangle <i>{rect}</i>?")
    choices, a = numeric_choices(ans, mistakes, rng, unit="cm", lo=1)
    return Question(text=text, figure=_square_with_cut(s, w, names), after_figure=after,
                    choices=choices, answer=a, solution=sol,
                    check=value_check(choices, perimeter(rect_pts(0, 0, s, s)) - perimeter(piece)))


CONTEXTS = [
    # (intro, piece word, measure question, unit)
    ("A square has perimeter {P} {u}. It is cut along straight lines into {k} rectangles as shown.",
     "What is the sum of the perimeters of all {k} rectangles?", "cm"),
    ("Grandma bakes a square cake. A ribbon {P} {u} long fits exactly around it. She cuts the cake "
     "into {k} rectangular pieces as shown and puts a ribbon around every piece.",
     "How many centimetres of ribbon does she need for all the pieces together?", "cm"),
    ("A square garden is surrounded by a fence {P} {u} long. The gardener divides it into {k} "
     "rectangular beds as shown and puts a separate fence around each bed.",
     "How many metres of fence are around the beds altogether?", "m"),
]


@variant(difficulty=2)
def pieces_total(rng, harder):
    """Cutting adds every cut line twice - whatever the widths are."""
    k = rng.choice([3, 4] if harder else [2, 2, 3])
    s = rng.randint(4, 12) if not harder else rng.randint(6, 20)
    P = 4 * s
    intro, ask, u = rng.choice(CONTEXTS)
    # unequal strip widths for the drawing only (the answer does not depend on them)
    while True:
        cuts = sorted(rng.sample(range(2, 11), k - 1))
        gaps = [b - a for a, b in zip([0] + cuts, cuts + [12])]
        if min(gaps) >= 2 and len(set(gaps)) > 1:
            break
    f = Fig(12, 12, max_px=95)
    f.rect(0, 0, 12, 12)
    for c in cuts:
        f.line((c, 0), (c, 12))
    ans = 2 * s * (k + 1)
    cut_txt = "There is 1 cut" if k == 2 else f"There are {k-1} cuts"
    sol = (f"Side = {P} ÷ 4 = {s} {u}. {cut_txt}; each cut is {s} {u} long and is counted twice "
           f"(once for each piece next to it): {P} + {k-1} × 2 × {s} = {ans} {u}. "
           f"The widths of the pieces don't matter!")
    mistakes = [P, k * P, P + (k - 1) * s, 2 * P, P + 2 * s, P + k * s]
    choices, a = numeric_choices(ans, mistakes, rng, unit=u, lo=1)
    unit = Fraction(s, 12)        # drawing units -> real length
    edges = [0] + cuts + [12]
    total = sum(perimeter(rect_pts(x0 * unit, 0, (x1 - x0) * unit, 12 * unit)) for x0, x1 in zip(edges, edges[1:]))
    return Question(text=intro.format(P=P, u=u, k=k), figure=f.drawing(),
                    after_figure=ask.format(k=k), choices=choices, answer=a, solution=sol,
                    check=value_check(choices, total))


@variant(difficulty=2)
def corner_cut(rng, harder):
    """Cutting a square from a corner does not change the perimeter."""
    a = rng.randint(8, 20) if harder else rng.randint(6, 12)
    b = rng.randint(5, a - 1)
    c = rng.randint(2, min(a, b) // 2)
    f = Fig(a, b, max_px=115)
    pts = [(0, 0), (a, 0), (a, b - c), (a - c, b - c), (a - c, b), (0, b)]
    f.poly(pts, fill=None)
    f.line((a - c, b), (a, b), dash=True); f.line((a, b), (a, b - c), dash=True)
    f.side((0, 0), (a, 0), f"{a} cm", "below")
    f.side((0, 0), (0, b), f"{b} cm", "left")
    f.side((a - c, b - c), (a, b - c), f"{c} cm", "below")
    P = 2 * (a + b)
    text = (f"A rectangle is {a} cm long and {b} cm wide. A square with side {c} cm is cut "
            f"off one corner.")
    after = "What is the perimeter of the remaining shape?"
    sol = (f"The two new edges ({c} cm and {c} cm) replace the two removed pieces of the outer "
           f"edge, which were also {c} cm and {c} cm. So the perimeter is the same as the "
           f"rectangle's: 2 × ({a} + {b}) = {P} cm.")
    mistakes = [P - 4 * c, P - 2 * c, P + 2 * c, P - c, a + b, P + 4 * c]
    choices, ai = numeric_choices(P, mistakes, rng, unit="cm", lo=1)
    return Question(text=text, figure=f.drawing(), after_figure=after,
                    choices=choices, answer=ai, solution=sol, check=value_check(choices, perimeter(pts)))


@variant(difficulty=3)
def notch(rng, harder):
    """A notch in the middle of a side DOES increase the perimeter (by 2 × depth)."""
    a = rng.randint(10, 24) if harder else rng.randint(8, 14)
    b = rng.randint(6, a - 1)
    n = rng.randint(2, a // 3)
    d = rng.randint(2, b // 2)
    x0 = (a - n) // 2
    f = Fig(a, b, max_px=115)
    pts = [(0, 0), (a, 0), (a, b), (x0 + n, b), (x0 + n, b - d), (x0, b - d), (x0, b), (0, b)]
    f.poly(pts)
    f.side((0, 0), (a, 0), f"{a} cm", "below")
    f.side((0, 0), (0, b), f"{b} cm", "left")
    f.side((x0, b - d), (x0 + n, b - d), f"{n} cm", "below")
    f.side((x0 + n, b), (x0 + n, b - d), f"{d} cm", "right")
    P = 2 * (a + b) + 2 * d
    text = (f"A {a} cm by {b} cm rectangle of cardboard has a rectangular notch {n} cm wide and "
            f"{d} cm deep cut out of the middle of its top side.")
    after = "What is the perimeter of the new shape?"
    sol = (f"The bottom of the notch ({n} cm) replaces the {n} cm taken out of the top edge, "
           f"and the two sides of the notch add 2 × {d} cm. "
           f"Perimeter = 2 × ({a} + {b}) + 2 × {d} = {P} cm.")
    base = 2 * (a + b)
    mistakes = [base, base - n, base + d, base + 2 * n, base + 2 * d + 2 * n, base - n + 2 * d]
    choices, ai = numeric_choices(P, mistakes, rng, unit="cm", lo=1)
    return Question(text=text, figure=f.drawing(), after_figure=after,
                    choices=choices, answer=ai, solution=sol, check=value_check(choices, perimeter(pts)))


@variant(difficulty=3)
def strips_to_square(rng, harder):
    """Work backwards: from the perimeter of one strip to the square."""
    k = rng.choice([2, 3, 4] if harder else [2, 3])
    m = rng.randint(3, 10) if harder else rng.randint(2, 6)
    s = k * m
    p = 2 * (s + m)
    thing = rng.choice(["a square sheet of paper", "a square chocolate bar", "a square photo"])
    f = Fig(s, s, max_px=95)
    f.rect(0, 0, s, s)
    for i in range(1, k):
        f.line((i * m, 0), (i * m, s))
    f.rect(0, 0, m, s, fill=GREY)
    ask_side = rng.random() < 0.4
    text = (f"Mia cuts {thing} into {k} equal strips as shown. "
            f"The perimeter of each strip is {p} cm.")
    if ask_side:
        after, ans = "How long is the side of the square?", s
        mistakes = [4 * s, p // 2, m, m * (k + 1), p - s, 2 * m]
    else:
        after, ans = "What is the perimeter of the square?", 4 * s
        mistakes = [k * p, 2 * p, s, 2 * s, p + 2 * m, 4 * m * (k + 1)]
    sol = (f"A strip is the full side long and 1/{k} of it wide, so its perimeter is "
           f"side + side + 2 × (side ÷ {k}) = {2*k + 2} × (side ÷ {k}). "
           f"{p} ÷ {2*k+2} = {m}, so the side is {k} × {m} = {s} cm"
           + ("." if ask_side else f" and the perimeter is {4*s} cm."))
    choices, ai = numeric_choices(ans, mistakes, rng, unit="cm", lo=1)
    sides = [S for S in range(1, 10 * p) if perimeter(rect_pts(0, 0, Fraction(S, k), S)) == p]
    assert len(sides) == 1
    return Question(text=text, figure=f.drawing(), after_figure=after,
                    choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, sides[0] if ask_side else 4 * sides[0]))


@variant(difficulty=3)
def two_perimeters(rng, harder):
    """Square cut into two rectangles: from their perimeters back to the square."""
    s = rng.randint(6, 20) if harder else rng.randint(4, 10)
    w = rng.randint(1, s - 1)
    while 2 * w == s:
        w = rng.randint(1, s - 1)
    names = rng.choice(NAMES)
    (tl, tr, br, bl), (top, bot) = names
    sq = tl + tr + br + bl
    r1, r2 = tl + top + bot + bl, top + tr + br + bot
    p1, p2 = 2 * (w + s), 2 * (s - w + s)
    ask_perim = rng.random() < 0.5
    text = (f"The square <i>{sq}</i> is cut into two rectangles. The perimeter of <i>{r1}</i> "
            f"is {p1} cm and the perimeter of <i>{r2}</i> is {p2} cm.")
    if ask_perim:
        after, ans = f"What is the perimeter of the square <i>{sq}</i>?", 4 * s
    else:
        after, ans = f"How long is the side of the square <i>{sq}</i>?", s
    sol = (f"Together the two perimeters go around the square (4 sides) and along the cut twice "
           f"(2 more sides): {p1} + {p2} = {p1+p2} cm = 6 sides. Side = {p1+p2} ÷ 6 = {s} cm"
           + (f", perimeter 4 × {s} = {4*s} cm." if ask_perim else "."))
    tot = p1 + p2
    mistakes = [tot, tot // 2, tot // 4, abs(p2 - p1), s, 4 * s, 2 * s, tot - s]
    choices, ai = numeric_choices(ans, mistakes, rng, unit="cm", lo=1)
    fits = {S for S in range(1, p1 + p2) for W in range(1, S)
            if perimeter(rect_pts(0, 0, W, S)) == p1 and perimeter(rect_pts(W, 0, S - W, S)) == p2}
    assert len(fits) == 1
    S = fits.pop()
    return Question(text=text, figure=_square_with_cut(s, w, names), after_figure=after,
                    choices=choices, answer=ai, solution=sol, check=value_check(choices, 4 * S if ask_perim else S))
