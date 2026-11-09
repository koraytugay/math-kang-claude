"""2024 Q23 (Ecolier, Grade 3-4) - which figure can (not) be built from three given parts.

Original: Kanga wants to build a figure out of three parts made of cubes: a T of 4 cubes, an
L of 3 cubes and an L of 4 cubes (all flat, one cube deep). He can also rotate or flip the
parts. Which of the five figures (11 cubes each) can he NOT make?
Answer: E (a 3 x 3 block with one cube on top of each top corner).

Core skill: fitting pieces into a shape in your head. Start where there is only one way to fit a
piece (a corner, a cube that sticks out), then see what is left. Every figure has the right
number of cubes, so counting alone does not help.
Printed in black and white: cubes are outlined, the sides are light grey.
"""
from kangaroo import Question, numeric_choices, value_check, variant
from kangaroo.cubes import draw_cubes
from kangaroo.polyomino import covers, normalize, orientations, same_shape, tilings

META = {
    "source": "set-01/by_level/Grade_03-04_Ecolier/2024 Q23",
    "skill": "Fit given pieces into a shape: start where a piece fits only one way, then look at what is left",
    "topics": ["spatial", "geometry", "logic"],
    "keywords": ["building with parts", "fitting pieces"],
    "version": 1,
}

PIECES = {
    "T": frozenset({(0, 1), (1, 1), (2, 1), (1, 0)}),
    "L3": frozenset({(0, 0), (1, 0), (1, 1)}),
    "L4": frozenset({(0, 0), (0, 1), (0, 2), (1, 2)}),
    "I3": frozenset({(0, 0), (1, 0), (2, 0)}),
    "S": frozenset({(0, 0), (1, 0), (1, 1), (2, 1)}),
    "O": frozenset({(0, 0), (1, 0), (0, 1), (1, 1)}),
    "I4": frozenset({(0, 0), (1, 0), (2, 0), (3, 0)}),
    "I2": frozenset({(0, 0), (1, 0)}),
}
ORIGINAL = ["T", "L3", "L4"]


# ------------------------------------------------------------------ shapes
def connected(cells):
    cells = set(cells)
    start = next(iter(cells))
    seen, todo = {start}, [start]
    while todo:
        x, y = todo.pop()
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if n in cells and n not in seen:
                seen.add(n)
                todo.append(n)
    return len(seen) == len(cells)


def size_ok(cells, w=6, h=5):
    c = normalize(cells)
    return max(x for x, _ in c) < w and max(y for _, y in c) < h


def build(rng, names, w=6, h=5):
    """A random figure made of the pieces, each touching the ones before."""
    while True:
        region = set()
        okay = True
        for name in names:
            o = rng.choice(orientations(PIECES[name]))
            if not region:
                region |= o
                continue
            spots = []
            for dx in range(-4, 8):
                for dy in range(-4, 7):
                    cells = {(x + dx, y + dy) for x, y in o}
                    if cells & region:
                        continue
                    touch = any((x + a, y + b) in region for x, y in cells
                                for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                    if touch and size_ok(region | cells, w, h):
                        spots.append(cells)
            if not spots:
                okay = False
                break
            region |= rng.choice(spots)
        if okay:
            return normalize(region)


def spoil(rng, region, pieces, w=6, h=5):
    """Move one cube: same number of cubes, still in one piece, but the parts no longer fit."""
    region = set(region)
    for _ in range(200):
        out = rng.choice(sorted(region))
        rest = region - {out}
        if not connected(rest):
            continue
        spots = sorted({(x + a, y + b) for x, y in rest for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))} - region)
        new = rest | {rng.choice(spots)}
        if size_ok(new, w, h) and not tilings(new, pieces):
            return normalize(new)
    return None


def distinct(shapes, s):
    return all(not same_shape(s, t) for t in shapes)


def pic(cells, scale=10):
    return draw_cubes({(x, 0, y) for x, y in cells}, scale=scale)


def _label(d, items, scale, margin=4):
    """Write labels above a draw_cubes drawing: items = [(x in cube units, text)]."""
    from reportlab.graphics.shapes import String
    h = d.height
    d.height = h + 14
    for x, t in items:
        d.add(String(margin + x * scale, h + 2, t, textAnchor="middle", fontName="Times-Bold", fontSize=10))
    return d


def parts_pic(names):
    """The parts in a row (as one drawing, with gaps)."""
    cubes, x0 = set(), 0
    for n in names:
        c = PIECES[n]
        cubes |= {(x + x0, 0, y) for x, y in c}
        x0 += max(x for x, _ in c) + 3
    return draw_cubes(cubes, scale=11)


def _names(rng, harder, k=3):
    if not harder and rng.random() < 0.5 and k == 3:
        return list(ORIGINAL)
    pool = ["T", "L3", "L4", "I3", "S", "O", "I4"]
    return rng.sample(pool, k)


def _text(k):
    return (f"Kanga wants to build a flat figure out of these {k} parts made of cubes (the picture). "
            "He must use every part once, and he can turn the parts or flip them over. ")


# ------------------------------------------------------------------ variants
def _options(rng, names, good_count):
    """good_count figures that can be built, the rest cannot; all different."""
    pieces = [PIECES[n] for n in names]
    while True:
        goods, bads = [], []
        tries = 0
        while len(goods) < good_count and tries < 200:
            tries += 1
            g = build(rng, names)
            if distinct(goods, g):
                goods.append(g)
        while len(bads) < 5 - good_count and tries < 400:
            tries += 1
            b = spoil(rng, rng.choice(goods) if goods else build(rng, names), pieces)
            if b and distinct(goods + bads, b):
                bads.append(b)
        if len(goods) == good_count and len(bads) == 5 - good_count:
            return goods, bads


@variant(difficulty=1)
def can_make(rng, harder):
    """Which figure CAN he make? (one can, four cannot)"""
    names = _names(rng, harder)
    pieces = [PIECES[n] for n in names]
    goods, bads = _options(rng, names, 1)
    opts = goods + bads
    rng.shuffle(opts)
    ai = opts.index(goods[0])
    text = _text(len(names)) + "Which of these figures <b>can</b> he make?"
    sol = (f"Every figure has {sum(len(p) for p in pieces)} cubes, so count is not enough. Start with a cube that "
           "sticks out: only one part can fill it. Only one figure can be filled completely.")
    return Question(text=text, figure=parts_pic(names), choices=list("ABCDE"),
                    choice_figures=[pic(o) for o in opts], answer=ai, solution=sol,
                    check=lambda i: covers(opts[i], pieces))


@variant(difficulty=2)
def cannot_make(rng, harder):
    """The original: which figure can he NOT make?"""
    names = _names(rng, harder)
    pieces = [PIECES[n] for n in names]
    goods, bads = _options(rng, names, 4)
    opts = goods + bads
    rng.shuffle(opts)
    ai = opts.index(bads[0])
    text = _text(len(names)) + "Which of these figures can he <b>not</b> make?"
    sol = ("Try to fill each figure with the parts, starting at a corner or a cube that sticks out. Four figures "
           f"can be filled; in figure {'ABCDE'[ai]} there is always a gap that no part fits.")
    return Question(text=text, figure=parts_pic(names), choices=list("ABCDE"),
                    choice_figures=[pic(o) for o in opts], answer=ai, solution=sol,
                    check=lambda i: not covers(opts[i], pieces))


@variant(difficulty=1)
def two_parts(rng, harder):
    """Only two parts: which figure can he make?"""
    names = rng.sample(["T", "L3", "L4", "I3", "S", "O"], 2)
    pieces = [PIECES[n] for n in names]
    goods, bads = _options(rng, names, 1)
    opts = goods + bads
    rng.shuffle(opts)
    ai = opts.index(goods[0])
    text = _text(2) + "Which of these figures <b>can</b> he make?"
    sol = (f"Look for one part inside the figure; what is left must be the other part. That works only "
           f"for figure {'ABCDE'[ai]}.")
    return Question(text=text, figure=parts_pic(names), choices=list("ABCDE"),
                    choice_figures=[pic(o) for o in opts], answer=ai, solution=sol,
                    check=lambda i: covers(opts[i], pieces))


@variant(difficulty=3)
def missing_part(rng, harder):
    """He used two known parts and one more: which part is the third?"""
    while True:
        names = _names(rng, harder)
        region = build(rng, names)
        known, secret = names[:2], names[2]
        candidates = [n for n in PIECES if n not in known and n != secret]
        rng.shuffle(candidates)
        wrong = [n for n in candidates if not tilings(region, [PIECES[k] for k in known] + [PIECES[n]])][:4]
        if len(wrong) == 4:
            break
    opts = wrong + [secret]
    rng.shuffle(opts)
    text = (f"Kanga built this flat figure out of {len(names)} parts made of cubes, turned or flipped. Two of the "
            f"parts are shown next to it. Which part is the third one?")
    sol = (f"The figure has {len(region)} cubes and the two parts have "
           f"{len(PIECES[known[0]]) + len(PIECES[known[1]])}, so the third part has {len(PIECES[secret])} cubes. "
           f"Put the two parts into the figure; what is left has the shape of part {'ABCDE'[opts.index(secret)]}.")
    w0 = max(a for a, _ in PIECES[known[0]]) + 1
    w1 = max(a for a, _ in PIECES[known[1]]) + 1
    wr = max(a for a, _ in region) + 1
    x1, x2 = w0 + 2, w0 + w1 + 7
    cubes = ({(x, 0, y) for x, y in PIECES[known[0]]} | {(x + x1, 0, y) for x, y in PIECES[known[1]]}
             | {(x + x2, 0, y) for x, y in region})
    fig = _label(draw_cubes(cubes, scale=11), [(w0 / 2, "part"), (x1 + w1 / 2, "part"),
                                               (x2 + wr / 2, "the figure")], 11)
    return Question(text=text, figure=fig, choices=list("ABCDE"),
                    choice_figures=[pic(PIECES[n], scale=11) for n in opts], answer=opts.index(secret),
                    solution=sol,
                    check=lambda i: covers(region, [PIECES[k] for k in known] + [PIECES[opts[i]]]))


@variant(difficulty=3)
def left_over(rng, harder):
    """Four parts are shown; he builds the figure with three of them. Which part is left over?"""
    while True:
        names = rng.sample(["T", "L3", "L4", "I3", "S", "O", "I4"], 4)
        used = names[:3]
        region = build(rng, used)
        fits = [n for n in names if covers(region, [PIECES[m] for m in names if m != n])]
        if fits == [names[3]]:
            break
    shown = list(names)
    rng.shuffle(shown)
    spare = names[3]
    text = ("Kanga has these 4 parts made of cubes (numbered 1 to 4). He builds "
            "the flat figure on the right with <b>three</b> of them, turned or flipped. Which part is left over?")
    cubes, x0, labels = set(), 0, []
    for k, n in enumerate(shown):
        cubes |= {(x + x0, 0, y) for x, y in PIECES[n]}
        w = max(x for x, _ in PIECES[n]) + 1
        labels.append((x0 + w / 2, str(k + 1)))
        x0 += w + 2
    cubes |= {(x + x0 + 2, 0, y) for x, y in region}
    fig = _label(draw_cubes(cubes, scale=10), labels, 10)
    choices = [f"part {i + 1}" for i in range(4)] + ["none, he needs all 4"]
    ai = shown.index(spare)
    total = sum(len(PIECES[n]) for n in names)
    sol = (f"The figure has {len(region)} cubes and the parts have {total} together, so the left-over part has "
           f"{total - len(region)} cubes. Then check which three parts really fill the figure: part {ai + 1} is "
           "left over.")

    def check(i):
        if i == 4:
            return covers(region, [PIECES[n] for n in shown])
        return covers(region, [PIECES[n] for j, n in enumerate(shown) if j != i])
    return Question(text=text, figure=fig, choices=choices, answer=ai,
                    solution=sol, check=check)
