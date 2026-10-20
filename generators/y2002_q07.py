"""2002 Q7 - which piece cannot belong to the skyline?

Original: a castle skyline (steps, pointed roofs, domes, small bumps) is shown.
Five short pieces of line are shown; four are cut from the skyline, one is
not. Answer: the odd one out.

Core skill: careful visual matching - comparing direction (up vs down), shape
(pointed vs round), size and order, and noticing mirror images.

How it works: the skyline is a sequence of tokens with flat parts ('H')
between features. A piece is a run of features with short flat stubs at both
ends. A fake is a real piece with one detail changed, and it is verified by
exact token matching that the fake appears nowhere in the skyline.
"""
import math

from kangaroo import Fig, Question, variant

META = {
    "source": "2002 Q7",
    "skill": "Visual matching: find which piece of a line drawing fits / does not fit",
    "topics": ["spatial", "visual"],
    "version": 2,
}

YMAX = 3          # highest level of the skyline (in units)
STUB = 0.5        # flat stub at the ends of each piece
MAX_PIECE_W = 6   # piece width (units) that still fits in an option cell

# ---------------------------------------------------------------- geometry
WIDTH = {"V": 0, "D": 1, "P": 2, "A": 2, "B": 2}


def tok_width(t):
    return t[1] if t[0] == "H" else WIDTH[t[0]]


def trace(tokens, x=0.0, y=0.0):
    """Turn tokens into one continuous list of points."""
    pts = [(x, y)]
    for t in tokens:
        k = t[0]
        if k == "H":
            x += t[1]; pts.append((x, y))
        elif k == "V":
            y += t[1]; pts.append((x, y))
        elif k == "D":
            x += 1; y += t[1]; pts.append((x, y))
        elif k == "P":                      # pointed roof
            pts += [(x + 1, y + 1), (x + 2, y)]; x += 2
        elif k == "A":                      # round dome
            pts += [(x + 1 - math.cos(math.pi * i / 16), y + math.sin(math.pi * i / 16))
                    for i in range(1, 17)]; x += 2
        elif k == "B":                      # two small bumps
            for c in (x + 0.5, x + 1.5):
                pts += [(c - 0.5 * math.cos(math.pi * i / 10), y + 0.45 * math.sin(math.pi * i / 10))
                        for i in range(1, 11)]
            x += 2
    return pts


def draw(tokens, scale, margin=4.0):
    pts = trace(tokens)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    f = Fig(max(w, 0.1), max(h, 0.1), scale=scale, margin=margin)
    f.polyline([(px - min(xs), py - min(ys)) for px, py in pts])
    return f.drawing()


# ---------------------------------------------------------------- skyline
def make_skyline(rng, n_features):
    toks, y = [("H", 1)], 0
    for _ in range(n_features):
        while True:
            k = rng.choice("VVVDPABA")
            if k == "V":
                dy = rng.choice([-2, -1, 1, 2])
                if 0 <= y + dy <= YMAX:
                    toks.append(("V", dy)); y += dy; break
            elif k == "D":
                dy = rng.choice([-1, 1])
                if 0 <= y + dy <= YMAX:
                    toks.append(("D", dy)); y += dy; break
            elif toks[-2:-1] != [(k,)]:
                toks.append((k,)); break
        toks.append(("H", rng.choice([1, 1, 2])))
    return toks


def piece_mids(sky, n_feat):
    """All runs of n_feat features (with the flat parts between them)."""
    out = []
    for i in range(1, len(sky) - 1, 2):
        mid = sky[i:i + 2 * n_feat - 1]
        if len(mid) == 2 * n_feat - 1 and i + len(mid) < len(sky):
            out.append(tuple(mid))
    return out


def fits(mid, sky):
    n = len(mid)
    return any(tuple(sky[i:i + n]) == mid for i in range(1, len(sky) - n, 2))


def with_stubs(mid):
    return [("H", STUB)] + list(mid) + [("H", STUB)]


def width(mid):
    return sum(tok_width(t) for t in with_stubs(mid))


# ---------------------------------------------------------------- fakes
SHAPE_NAME = {"P": "a pointed roof", "A": "a round dome", "B": "two small bumps"}


def _feature_idx(mid, kinds):
    return [i for i, t in enumerate(mid) if t[0] in kinds]


def mutate(mid, rng, subtle):
    """Return (fake_mid, explanation) or None if this mutation does not apply."""
    kinds = ["flip_v", "flip_d", "shape", "mirror"]
    if subtle:
        kinds = ["resize_v", "flat_len", "swap", "mirror", "flip_v", "shape"]
    kind = rng.choice(kinds)
    m = list(mid)
    if kind in ("flip_v", "resize_v"):
        idx = _feature_idx(m, "V")
        if not idx:
            return None
        i = rng.choice(idx)
        dy = m[i][1]
        if kind == "flip_v":
            m[i] = ("V", -dy)
            why = f"it steps {'down' if dy > 0 else 'up'} where the line steps {'up' if dy > 0 else 'down'}"
        else:
            new = dy // abs(dy) * (3 - abs(dy))      # 1 <-> 2
            m[i] = ("V", new)
            why = f"its step is {'taller' if abs(new) > abs(dy) else 'shorter'} than in the line"
    elif kind == "flip_d":
        idx = _feature_idx(m, "D")
        if not idx:
            return None
        i = rng.choice(idx)
        m[i] = ("D", -m[i][1])
        why = "its slope goes the wrong way"
    elif kind == "shape":
        idx = _feature_idx(m, "PAB")
        if not idx:
            return None
        i = rng.choice(idx)
        old = m[i][0]
        new = rng.choice([k for k in "PAB" if k != old])
        m[i] = (new,)
        why = f"it has {SHAPE_NAME[new]} where the line has {SHAPE_NAME[old]}"
    elif kind == "flat_len":
        idx = [i for i, t in enumerate(m) if t[0] == "H"]
        if not idx:
            return None
        i = rng.choice(idx)
        m[i] = ("H", 3 - m[i][1])
        why = "its flat part between the two features has the wrong length"
    elif kind == "swap":
        idx = _feature_idx(m, "VDPAB")
        if len(idx) < 2 or m[idx[0]] == m[idx[-1]]:
            return None
        m[idx[0]], m[idx[-1]] = m[idx[-1]], m[idx[0]]
        why = "it has the right shapes but in the wrong order"
    else:  # mirror
        m = [(t[0], -t[1]) if t[0] in "VD" else t for t in reversed(m)]
        why = "it is a mirror image of a part of the line"
    if tuple(m) == tuple(mid):
        return None
    return tuple(m), why


def make_fake(sky, real_mids, rng, subtle, n_feat):
    for _ in range(400):
        base = rng.choice(piece_mids(sky, n_feat))
        r = mutate(base, rng, subtle)
        if (r and not fits(r[0], sky) and r[0] not in real_mids and width(r[0]) <= MAX_PIECE_W
                and not drawn_fits(r[0], sky)):   # token matching misses e.g. a short step inside a tall one
            return r
    return None


def build(rng, n_feat, n_real, n_fake, subtle, n_features):
    """Skyline + n_real distinct real pieces + n_fake distinct fakes (retries until possible)."""
    while True:
        sky = make_skyline(rng, n_features)
        mids = [m for m in dict.fromkeys(piece_mids(sky, n_feat)) if width(m) <= MAX_PIECE_W
                and any(t[0] != "H" for t in m)]
        if len(mids) < n_real:
            continue
        real = rng.sample(mids, n_real)
        fakes, ok = [], True
        for _ in range(n_fake):
            r = make_fake(sky, real + [f for f, _ in fakes], rng, subtle, n_feat)
            if not r:
                ok = False
                break
            fakes.append(r)
        if ok:
            return sky, real, fakes


def _on_line(q, segs, eps=1e-6):
    """Is point q on one of the segments? segs: [((x1, y1), (x2, y2)), ...]."""
    qx, qy = q
    for (x1, y1), (x2, y2) in segs:
        if qx < min(x1, x2) - 1e-3 or qx > max(x1, x2) + 1e-3:
            continue
        dx, dy = x2 - x1, y2 - y1
        L = dx * dx + dy * dy
        t = 0 if L == 0 else max(0.0, min(1.0, ((qx - x1) * dx + (qy - y1) * dy) / L))
        if (x1 + t * dx - qx) ** 2 + (y1 + t * dy - qy) ** 2 < eps:
            return True
    return False


def drawn_fits(mid, sky):
    """Answer check by geometry, not tokens: can the drawn piece be slid onto the drawn line?"""
    piece = trace(with_stubs(mid))
    dense = piece + [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in zip(piece, piece[1:])]
    line = trace(sky)
    segs = list(zip(line, line[1:]))
    x_end = max(p[0] for p in line)
    for k in range(int(2 * x_end) + 1):
        x0 = k / 2
        starts = {round(y1, 6) for (xa, y1), (xb, y2) in segs if abs(y1 - y2) < 1e-9 and xa <= x0 <= xb}
        for y0 in starts:
            if all(_on_line((x0 + px, y0 + py), segs) for px, py in dense):
                return True
    return False


def scale_for(sky):
    return min(11.0, 380.0 / sum(tok_width(t) for t in sky))


CONTEXTS = [
    ("Far away we see the skyline of a castle.",
     "Which of the pieces {can} belong to the skyline?"),
    ("This is the outline of a town seen from the river at sunset.",
     "Which piece {can} be part of the outline?"),
    ("Lena cut a strip of paper along this line.",
     "Which piece {can} come from the cut line?"),
]


def _letters_question(rng, harder, want_real):
    subtle = harder or not want_real
    sky, real, fakes = build(rng, n_feat=2, n_real=1 if want_real else 4,
                             n_fake=4 if want_real else 1, subtle=subtle,
                             n_features=10 if harder else 8)
    s = scale_for(sky)
    if want_real:
        items = [(real[0], None)] + fakes
    else:
        items = [(m, None) for m in real] + [fakes[0]]
    rng.shuffle(items)
    answer = next(i for i, (_, why) in enumerate(items) if (why is None) == want_real)
    intro, ask = rng.choice(CONTEXTS)
    ask = ask.format(can="can" if want_real else "cannot")
    if want_real:
        ask = ask.replace("can", "<b>can</b>", 1)
        reasons = "; ".join(f"{'ABCDE'[i]}: {why}" for i, (_, why) in enumerate(items) if why)
        sol = f"Only this piece is found in the line. The others don't fit — {reasons}."
    else:
        ask = ask.replace("cannot", "<b>cannot</b>", 1)
        sol = f"All the other pieces can be found in the line, but this one cannot: {items[answer][1]}."
    return Question(text=intro, figure=draw(sky, s), after_figure=ask,
                    choices=[f"piece {c}" for c in "ABCDE"], answer=answer,
                    choice_figures=[draw(with_stubs(m), s) for m, _ in items], solution=sol,
                    check=lambda i: drawn_fits(items[i][0], sky) == want_real)


@variant(difficulty=1)
def cannot_belong(rng, harder):
    """The original: four real pieces, one fake."""
    return _letters_question(rng, harder, want_real=False)


@variant(difficulty=2)
def can_belong(rng, harder):
    """Reversed: four clever fakes, only one real piece."""
    return _letters_question(rng, harder, want_real=True)


@variant(difficulty=3)
def how_many_fit(rng, harder):
    """Five numbered pieces - how many of them belong? Every piece must be checked."""
    n_real = rng.randint(1, 4)
    sky, real, fakes = build(rng, n_feat=2, n_real=n_real, n_fake=5 - n_real, subtle=True,
                             n_features=10 if harder else 9)
    s = min(scale_for(sky), 11.0)
    items = [(m, None) for m in real] + fakes
    rng.shuffle(items)
    # draw the 5 numbered pieces in one row, bottom-aligned
    traces = [trace(with_stubs(m)) for m, _ in items]
    gap = 1.6
    total_w = sum(max(p[0] for p in t) for t in traces) + gap * 4
    max_h = max(max(p[1] for p in t) - min(p[1] for p in t) for t in traces)
    f = Fig(total_w, max_h + 1.2, scale=s, margin=6)
    x = 0.0
    for n, t in enumerate(traces, 1):
        miny = min(p[1] for p in t)
        f.polyline([(x + px, py - miny + 1.2) for px, py in t])
        w = max(p[0] for p in t)
        f.text(x + w / 2, 0.3, str(n), size=10)
        x += w + gap
    intro, _ = rng.choice(CONTEXTS)
    text = intro
    after = "How many of the pieces 1–5 below belong to the line?"
    # options: five of the counts 0..5 (always containing the answer), in order
    counts = [c for c in range(6) if c != n_real]
    counts.remove(rng.choice(counts))
    counts = sorted(counts + [n_real])
    fitting = [str(i + 1) for i, (_, why) in enumerate(items) if why is None]
    wrong = [f"{i + 1} ({why})" for i, (_, why) in enumerate(items) if why]
    sol = (f"Pieces {', '.join(fitting)} fit. " if len(fitting) > 1 else f"Only piece {fitting[0]} fits. ") + \
          "Not: " + "; ".join(wrong) + "."
    sky_fig = draw(sky, s)
    return Question(text=text, figure=_stack(sky_fig, f.drawing()), after_figure=after,
                    choices=[str(c) for c in counts], answer=counts.index(n_real), solution=sol,
                    check=lambda i: counts[i] == sum(drawn_fits(m, sky) for m, _ in items))


def _stack(top, bottom, gap=10):
    """Put two drawings on top of each other, centred."""
    from reportlab.graphics.shapes import Drawing, Group
    w = max(top.width, bottom.width)
    d = Drawing(w, top.height + bottom.height + gap)
    g1 = Group(*top.contents); g1.translate((w - top.width) / 2, bottom.height + gap)
    g2 = Group(*bottom.contents); g2.translate((w - bottom.width) / 2, 0)
    d.add(g1); d.add(g2)
    return d
