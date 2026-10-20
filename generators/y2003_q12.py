"""2003 Q12 - a paper net is folded into a house: which house is it?

Original: a picture (walls in a strip, a gable wall with a door, a roof) is drawn
on paper and cut out to make a house. Which of the five houses did it become?
Answer: A.

Core skill: folding in your head - walls that are next to each other on the
paper meet at a corner of the house, keep their left/right order (seen from
outside), and a mark on a wall stays on the same side of that wall. Children
pick a house whose walls are mirrored or come from the wrong place on the strip.

Generator model: four walls in a strip, folded with the printed side out. Seen
from outside at a corner, wall i is on the left and wall i+1 on the right.
"""
import math

from reportlab.lib import colors

from kangaroo import Fig, Question, variant
from kangaroo.figures import column, row

META = {
    "source": "2003 Q12",
    "skill": "Folding a net in your head: neighbours stay neighbours, in the same order, marks keep their side",
    "topics": ["spatial", "geometry"],
    "version": 1,
}

KINDS = ["door", "window", "round", "dot"]
DARK = colors.Color(0.3, 0.3, 0.3)
ROOF = colors.Color(0.45, 0.45, 0.45)
POS = {"L": 0.3, "R": 0.7}
H_RATIO = 1.3            # wall height / wall width


def _walls(rng):
    kinds = rng.sample(KINDS, 4)
    return [(k, rng.choice("LR")) for k in kinds]


def valid(walls, left, right):
    return any(walls[i] == left and walls[(i + 1) % 4] == right for i in range(4))


def _flip(face):
    k, p = face
    return (k, "R" if p == "L" else "L")


# ------------------------------------------------------------------ drawing
def _mark(f, face, m, aspect):
    """Draw a wall's mark through m: (u, v) in [0,1]^2 -> problem coords."""
    kind, pos = face
    c = POS[pos]
    if kind == "door":
        f.poly([m(c - 0.16, 0), m(c + 0.16, 0), m(c + 0.16, 0.55), m(c - 0.16, 0.55)], fill=DARK, width=0.6)
    elif kind == "window":
        a, b, y0, y1 = c - 0.17, c + 0.17, 0.55, 0.55 + 0.34 / aspect
        f.poly([m(a, y0), m(b, y0), m(b, y1), m(a, y1)], fill=colors.white, width=0.7)
        f.line(m(c, y0), m(c, y1), width=0.5)
        f.line(m(a, (y0 + y1) / 2), m(b, (y0 + y1) / 2), width=0.5)
    elif kind == "round":
        r = 0.17
        pts = [m(c + r * math.cos(t), 0.68 + r * math.sin(t) / aspect) for t in
               [2 * math.pi * k / 16 for k in range(16)]]
        f.poly(pts, fill=colors.white, width=0.7)
    else:  # dot
        r = 0.08
        pts = [m(c + r * math.cos(t), 0.32 + r * math.sin(t) / aspect) for t in
               [2 * math.pi * k / 12 for k in range(12)]]
        f.poly(pts, fill=colors.black, width=0.4)


def net_pic(walls, scale=30):
    """The four walls in a strip, as drawn on the paper."""
    H = H_RATIO
    f = Fig(4, H, scale=scale, margin=3)
    for i, face in enumerate(walls):
        f.rect(i, 0, 1, H, fill=colors.white, width=0.9)
        _mark(f, face, lambda u, v, i=i: (i + u, v * H), H)
    return f.drawing()


def house_pic(left, right, scale=26):
    """The house seen from outside at a corner: `left` wall and `right` wall."""
    W, s, H = 1.0, 0.45, H_RATIO
    f = Fig(2 * W, H + 2 * s, scale=scale, margin=3)
    # left face: u = 0 at its far (left) edge, u = 1 at the corner
    ml = lambda u, v: (W * u, s * (1 - u) + H * v)
    mr = lambda u, v: (W + W * u, s * u + H * v)
    for m, face in ((ml, left), (mr, right)):
        f.poly([m(0, 0), m(1, 0), m(1, 1), m(0, 1)], fill=colors.white, width=0.9)
        _mark(f, face, m, H)
    f.poly([(W, H), (0, H + s), (W, H + 2 * s), (2 * W, H + s)], fill=ROOF, width=0.9)
    return f.drawing()


def face_pic(face, scale=34):
    f = Fig(1, H_RATIO, scale=scale, margin=3)
    f.rect(0, 0, 1, H_RATIO, fill=colors.white, width=0.9)
    _mark(f, face, lambda u, v: (u, v * H_RATIO), H_RATIO)
    return f.drawing()


NAMES = {"door": "the door", "window": "the square window", "round": "the round window",
         "dot": "the dot (a doorbell)"}


def _bad_views(walls, rng):
    """Wrong views of the house: reversed order, opposite walls, a mirrored mark."""
    out = []
    for i in range(4):
        a, b, c = walls[i], walls[(i + 1) % 4], walls[(i + 2) % 4]
        out += [(b, a), (a, c), (c, a), (_flip(a), b), (a, _flip(b)), (_flip(b), _flip(a))]
    out = [v for v in dict.fromkeys(out) if not valid(walls, *v)]
    rng.shuffle(out)
    return out


INTRO = ("The strip below is cut out and folded into the four walls of a house, with the pictures "
         "on the outside. A flat roof is put on top.")


# ------------------------------------------------------------------ variants
@variant(difficulty=1)
def which_house(rng, harder):
    """The original: which house can the strip make?"""
    walls = _walls(rng)
    i = rng.randrange(4)
    good = (walls[i], walls[(i + 1) % 4])
    bad = _bad_views(walls, rng)
    if not harder:      # easier: prefer the obvious mistakes (opposite walls, swapped order)
        bad.sort(key=lambda v: (v[0] in walls) + (v[1] in walls), reverse=True)
    views = bad[:4] + [good]
    rng.shuffle(views)
    k = views.index(good)
    sol = (f"Walls next to each other on the strip meet at a corner, in the same order: the left one "
           f"stays on the left. Only house {'ABCDE'[k]} shows two neighbouring walls in the right "
           f"order with every mark on the correct side.")
    return Question(text=INTRO, figure=net_pic(walls), after_figure="Which house is it?",
                    choices=[f"house {c}" for c in "ABCDE"], answer=k,
                    choice_figures=[house_pic(*v, scale=26) for v in views], solution=sol)


@variant(difficulty=2)
def which_strip(rng, harder):
    """Reverse: a house is shown; which strip could it be folded from?"""
    walls = _walls(rng)
    i = rng.randrange(4)
    left, right = walls[i], walls[(i + 1) % 4]
    wrong = []
    for _ in range(400):
        w = list(walls)
        how = rng.choice(["swap", "flip", "shuffle"])
        if how == "swap":                   # left and right walls change places
            a, b = walls.index(left), walls.index(right)
            w[a], w[b] = w[b], w[a]
        elif how == "flip":                 # a mark on the wrong side
            j = rng.choice([walls.index(left), walls.index(right)])
            w[j] = _flip(w[j])
        else:
            rng.shuffle(w)
        if not valid(w, left, right) and w not in wrong and w != walls:
            wrong.append(w)
        if len(wrong) == 4:
            break
    strips = wrong + [walls]
    rng.shuffle(strips)
    k = strips.index(walls)
    text = ("A strip of four walls is cut out and folded into this house, with the pictures on the "
            "outside. A flat roof is put on top.")
    sol = (f"The left wall of the house must come right before the right wall on the strip (or the "
           f"right wall is first and the left wall last), with each mark on the same side. Only strip "
           f"{'ABCDE'[k]} works.")
    return Question(text=text, figure=house_pic(left, right, scale=32), after_figure="Which strip was it?",
                    choices=[f"strip {c}" for c in "ABCDE"], answer=k,
                    choice_figures=[net_pic(s, scale=18) for s in strips], solution=sol)


@variant(difficulty=2)
def how_many_houses(rng, harder):
    """How many of the five houses can be made from the strip?"""
    walls = _walls(rng)
    n_good = rng.randint(1, 3)
    goods = rng.sample([(walls[i], walls[(i + 1) % 4]) for i in range(4)], n_good)
    bad = _bad_views(walls, rng)[:5 - n_good]
    views = goods + bad
    rng.shuffle(views)
    lab = []
    for j, v in enumerate(views):
        cap = Fig(4, 1, scale=10, margin=0)
        cap.text(2, 0.5, "ABCDE"[j], size=11)
        lab.append(column([house_pic(*v, scale=24), cap.drawing()], gap=2))
    fig = column([net_pic(walls), row(lab, gap=14)], gap=8)
    good_letters = [("ABCDE"[j]) for j, v in enumerate(views) if v in goods]
    start = rng.choice([s for s in (0, 1) if s <= n_good <= s + 4])
    choices = [str(v) for v in range(start, start + 5)]
    sol = (f"A house is right if its two walls are neighbours on the strip, in the same order, with the "
           f"marks on the correct side. Right: {', '.join(good_letters)}, so {n_good}.")
    return Question(text=INTRO, figure=fig, after_figure="How many of the houses A–E can be made from the strip?",
                    choices=choices, answer=n_good - start, solution=sol)


@variant(difficulty=3)
def right_neighbour(rng, harder):
    """Standing outside, the wall with X is on your left - which wall is on the right?"""
    walls = _walls(rng)
    i = rng.randrange(4)
    a = walls[i]
    good = walls[(i + 1) % 4]
    opts = [good, walls[(i - 1) % 4], walls[(i + 2) % 4], _flip(good), _flip(walls[(i - 1) % 4])]
    rng.shuffle(opts)
    k = opts.index(good)
    text = (INTRO + f" You stand outside the house at a corner. The wall with {NAMES[a[0]]} is on your left.")
    nxt = ("the next wall on the strip" if i < 3 else
           "the first wall on the strip (the strip closes into a ring, so after the last wall comes the first)")
    sol = (f"Folded with the pictures outside, the strip keeps its order: on your right is {nxt}. "
           f"Its mark stays on the same side, so it is picture {'ABCDE'[k]}.")
    return Question(text=text, figure=net_pic(walls), after_figure="Which wall do you see on your right?",
                    choices=[f"wall {c}" for c in "ABCDE"], answer=k,
                    choice_figures=[face_pic(o) for o in opts], solution=sol)
