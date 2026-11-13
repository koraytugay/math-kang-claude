"""2023 Q12 (Ecolier, Grade 3-4) - two crossing streets split the same houses in two ways.

Original: North of Straße A (street A) there are 7 houses. East of Straße B (street B)
there are 8 houses. South of Straße A (street A) there are 5 houses.
How many houses are there West of Straße B (street B)?
(A) 4  (B) 5  (C) 6  (D) 7  (E) 8.
(The map shows a village with street A going west-east and street B going north-south,
crossing in the middle, and a compass; no houses are drawn.)
Every house is north or south of street A: 7 + 5 = 12 houses in the village. Every house is
also east or west of street B: 12 - 8 = 4 houses west.  Answer: A (answer key: A).

Core skill: "the same houses, counted in two different ways". Children look for the houses
in the four corners of the map (which they cannot know), or combine the numbers at random
(8 - 5, 7 + 8 - 5, ...). The step is to see that north + south = all the houses = east + west.
"""
from reportlab.lib import colors

from kangaroo import Fig, Question, numeric_choices, value_check, variant, warmup
from kangaroo.figures import row

META = {
    "source": "set-01/by_level/Grade_03-04_Ecolier/2023 Q12",
    "skill": "One street splits all the houses into two groups: north + south = all houses = east + west",
    "topics": ["logic", "counting", "spatial"],
    "keywords": ["houses and streets", "north south east west", "two ways to split"],
    "version": 2,
}

STREET = colors.Color(0.55, 0.55, 0.55)
HOUSES = ("house", "houses")
OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}
STREET_OF = {"north": "A", "south": "A", "east": "B", "west": "B"}


# ------------------------------------------------------------------ the village as data
class Village:
    """Houses as (x, y) points; street A is the line y = 0, street B is x = 0 (and street C is x = xc)."""

    def __init__(self, nw, ne, sw, se, rng, mid=None):
        # mid = (north, south) houses between street B and street C (three-street map)
        self.xc = 2.0 if mid else None
        self.houses = []
        top, bottom = [0.68, 1.0, 1.32], [-0.4, -0.85, -1.3]
        def put(n, xs, ys):
            cells = rng.sample([(x, y) for x in xs for y in ys], n)    # distinct spots, no overlaps
            self.houses += [(x + rng.uniform(-0.05, 0.05), y + rng.uniform(-0.04, 0.04)) for x, y in cells]
        west = [-2.2, -1.75, -1.3, -0.85, -0.4]
        east = [2.4, 2.85, 3.3, 3.75] if mid else [0.4, 0.85, 1.3, 1.75, 2.2]
        put(nw, west, top)
        put(sw, west, bottom)
        put(ne, east, top)
        put(se, east, bottom)
        if mid:
            put(mid[0], [0.45, 0.95, 1.5], top)
            put(mid[1], [0.45, 0.95, 1.5], bottom)

    def count(self, side):
        """Count the houses on one side of a street, point by point."""
        test = {"north": lambda x, y: y > 0, "south": lambda x, y: y < 0,
                "east": lambda x, y: x > 0, "west": lambda x, y: x < 0,
                "eastC": lambda x, y: x > self.xc, "between": lambda x, y: 0 < x < self.xc}[side]
        return sum(1 for x, y in self.houses if test(x, y))

    def corner(self, ns, ew):
        return sum(1 for x, y in self.houses
                   if (y > 0) == (ns == "north") and (x > 0) == (ew == "east"))


# ------------------------------------------------------------------ picture
def compass(size=0.9):
    f = Fig(2.0, 2.0, max_px=44, margin=4, font_size=10)
    c = 1.0
    for dx, dy, lab in [(0, 1, "N"), (0, -1, "S"), (1, 0, "E"), (-1, 0, "W")]:
        tip = (c + dx * 0.55, c + dy * 0.55)
        f.line((c, c), tip, width=1.0)
        px, py = -dy, dx
        f.poly([tip, (tip[0] - dx * 0.2 + px * 0.1, tip[1] - dy * 0.2 + py * 0.1),
                (tip[0] - dx * 0.2 - px * 0.1, tip[1] - dy * 0.2 - py * 0.1)], fill=colors.black, width=0.5)
        f.text(c + dx * 0.85, c + dy * 0.85, lab, size=10)
    return f.drawing()


def _wavy(f, pts, width=4.5):
    for a, b in zip(pts, pts[1:]):
        f.line(a, b, width=width, color=STREET)


def village_pic(names=("A", "B"), third=None, houses=None, max_px=150, show_compass=True):
    """Village outline with street A (west-east) and street B (north-south), optionally street C
    east of B. `houses` = Village to draw the houses as small squares."""
    x0, x1 = -2.8, (4.4 if third else 2.8)
    f = Fig(x1 - x0, 3.6, max_px=max_px, margin=6, font_size=9.5)
    T = lambda x, y: (x - x0, y + 1.8)
    # outline: a rounded box
    r = 0.4
    w, h = x1 - x0, 3.6
    import math
    pts = []
    for cx, cy, a0 in [(w - r, h - r, 0), (r, h - r, 90), (r, r, 180), (w - r, r, 270)]:
        pts += [(cx + r * math.cos(math.radians(a0 + 15 * i)), cy + r * math.sin(math.radians(a0 + 15 * i)))
                for i in range(7)]
    f.poly(pts, width=1.0)
    _wavy(f, [T(x0, 0.08), T(-1.4, -0.05), T(0, 0.0), T(1.4, 0.06), T(x1, -0.04)])
    _wavy(f, [T(0.06, 1.8), T(-0.04, 0.9), T(0, 0), T(0.05, -0.9), T(-0.03, -1.8)])
    if third:
        _wavy(f, [T(2.0, 1.8), T(2.06, 0.9), T(2.0, 0), T(1.95, -0.9), T(2.03, -1.8)])
    f.text(*T(-2.62, 0.34), f"Street {names[0]}", anchor="start", size=9)
    f.text(*T(0.16, 1.6), f"Street {names[1]}", anchor="start", size=9)
    if third:
        f.text(*T(2.16, 1.6), f"Street {third}", anchor="start", size=9)
    if houses:
        for x, y in houses.houses:
            px, py = T(x, y)
            f.rect(px - 0.09, py - 0.09, 0.18, 0.18, fill=colors.white, width=0.8)
    d = f.drawing()
    return row([d, compass()], gap=8) if show_compass else d


# ------------------------------------------------------------------ helpers
def _quadrants(rng, harder, lo=1):
    hi = 9 if harder else 5
    if harder:
        lo = max(lo, 2)
    return [rng.randint(lo, hi) for _ in range(4)]       # nw, ne, sw, se


def _says(side, n):
    s = "is" if n == 1 else "are"
    return f"{side.capitalize()} of street {STREET_OF[side]} there {s} {n} {HOUSES[0] if n == 1 else HOUSES[1]}."


def _facts(*facts, lead="Two streets cross in a village (see the map).\n"):
    """The facts as a bulleted list (see kangaroo.layout), then the question in a new paragraph.
    lead: a sentence before the list (it only says what the map shows)."""
    return lead + "\n".join(f"- {f}" for f in facts) + "\n\n"


# ------------------------------------------------------------------ variants
@variant(difficulty=1)
def cross_streets(rng, harder):
    """The original: three sides are given, find the fourth."""
    while True:
        v = Village(*_quadrants(rng, harder), rng)
        counts = {s: v.count(s) for s in OPP}
        ask = rng.choice(list(OPP))
        if len(set(counts.values())) >= 3:
            break
    given = [s for s in ["north", "east", "south", "west"] if s != ask]
    # the original order: one side of A, one side of B, the other side of A
    pair = OPP[ask]                                   # same street as the asked side
    other = [s for s in given if s != pair]
    order = [other[0], pair, other[1]]
    text = (_facts(*(_says(s, counts[s]) for s in order)) +
            f"How many houses are there {ask} of street {STREET_OF[ask]}?")
    a, b = other
    total = counts[a] + counts[b]
    ans = total - counts[pair]
    sol = (f"Every house is either {a} or {b} of street {STREET_OF[a]}: {counts[a]} + {counts[b]} = {total} houses. "
           f"Every house is also either {pair} or {ask} of street {STREET_OF[ask]}: {total} − {counts[pair]} = {ans}.")
    mistakes = [(counts[pair], f"think the {ask} side has as many houses as the {pair} side"),
                (counts[a], f"use the {a} number"), (counts[b], f"use the {b} number"),
                (abs(counts[pair] - counts[a]), "subtract two numbers that do not belong together"),
                (counts[a] + counts[pair] - counts[b], "add and subtract the wrong numbers"),
                (total + counts[pair], "add up all three numbers")]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=0, order="asc")
    return Question(text=text, figure=village_pic(), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, v.count(ask)))


@variant(difficulty=1)
def whole_village(rng, harder):
    """How many houses in the whole village? One number is extra."""
    v = Village(*_quadrants(rng, harder), rng)
    c = {s: v.count(s) for s in OPP}
    if rng.random() < 0.5:
        both, extra = ("north", "south"), rng.choice(["east", "west"])
    else:
        both, extra = ("east", "west"), rng.choice(["north", "south"])
    order = [both[0], extra, both[1]]
    text = (_facts(*(_says(s, c[s]) for s in order), "No house stands on a street.") +
            "How many houses are there in the village altogether?")
    ans = c[both[0]] + c[both[1]]
    sol = (f"Every house is either {both[0]} or {both[1]} of street {STREET_OF[both[0]]}, so the village has "
           f"{c[both[0]]} + {c[both[1]]} = {ans} houses. The {extra} houses are already counted in these.")
    mistakes = [(ans + c[extra], "add up all three numbers"),
                (c[both[0]] + c[extra], f"add the {both[0]} and the {extra} houses"),
                (c[both[1]] + c[extra], f"add the {both[1]} and the {extra} houses"),
                (ans - c[extra], f"take away the {extra} houses")]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1, order="asc", unit=HOUSES)
    return Question(text=text, figure=village_pic(), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, len(v.houses)))


@variant(difficulty=2)
def class_groups(rng, harder):
    """No map: the same children split by two different questions."""
    lo, hi = (12, 30) if harder else (8, 15)
    # (first split sentence with {a} {b}, question group, its opposite, sentence saying the others are the opposite)
    stories = [
        ("In a class there are {a} girls and {b} boys.", "came to school by bus", "walked to school",
         " All the other children walked to school."),
        ("In a class, {a} children have a pet and {b} children have no pet.", "wear glasses",
         "do not wear glasses", ""),
        ("In a class, {a} children have a sister and {b} children have no sister.", "can swim", "cannot swim", ""),
    ]
    intro, p2, q2, others = rng.choice(stories)
    while True:
        cells = [rng.randint(2, hi // 2 + 2) for _ in range(4)]   # (p1,p2) (p1,q2) (q1,p2) (q1,q2)
        kids = [(i < 2, i % 2 == 0) for i, n in enumerate(cells) for _ in range(n)]
        a = sum(1 for g, _ in kids if g)
        b = len(kids) - a
        c = sum(1 for _, h in kids if h)
        if lo <= a and lo <= b and a != b and c not in (a, b):
            break
    text = intro.format(a=a, b=b) + f" {c} children {p2}.{others} How many children {q2}?"
    ans = a + b - c
    sol = (f"There are {a} + {b} = {a + b} children in the class. {c} of them {p2}, so the others "
           f"{q2}: {a + b} − {c} = {ans}.")
    mistakes = [(abs(a - c), f"take {c} away from {a} only"), (abs(b - c), f"take {c} away from {b} only"),
                (a + b + c, "add up all the numbers"), (a + b, "count the whole class")]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=0, order="asc")
    value = sum(1 for _, h in kids if not h)
    return Question(text=text, choices=choices, answer=ai, solution=sol, check=value_check(choices, value))


@variant(difficulty=2)
def same_both_sides(rng, harder):
    """Twist: east and west have equally many houses."""
    while True:
        q = _quadrants(rng, harder)
        nw, ne, sw, se = q
        if nw + sw == ne + se:
            break
    v = Village(nw, ne, sw, se, rng)
    n, s = v.count("north"), v.count("south")
    ew = rng.choice(["east", "west"])
    text = (_facts(_says('north', n), _says('south', s),
                   "West of street B there are just as many houses as east of street B.") +
            f"How many houses are there {ew} of street B?")
    ans = (n + s) // 2
    sol = (f"The village has {n} + {s} = {n + s} houses. Street B cuts them into two equal groups: "
           f"{n + s} ÷ 2 = {ans}.")
    mistakes = [(n + s, "forget to share the houses between the two sides"), (n, "use the north number"),
                (s, "use the south number"), (abs(n - s), "take the south houses away from the north houses")]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1, order="asc", unit=HOUSES)
    return Question(text=text, figure=village_pic(), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, v.count(ew)))


@variant(difficulty=3)
def one_corner(rng, harder):
    """Reverse/combine: find the houses in one corner (south of A and west of B)."""
    while True:
        nw, ne, sw, se = _quadrants(rng, harder)
        if len({nw, ne, sw, se}) >= 3:
            break
    v = Village(nw, ne, sw, se, rng)
    n, s, e = v.count("north"), v.count("south"), v.count("east")
    k = v.corner("north", "east")
    text = (_facts(_says('north', n), _says('south', s), _says('east', e),
                   f"{k} of the houses are north of street A <b>and</b> east of street B.") +
            f"How many houses are south of street A <b>and</b> west of street B?")
    total = n + s
    w = total - e
    nw_ = n - k
    ans = w - nw_
    sol = (f"The village has {n} + {s} = {total} houses, so {total} − {e} = {w} are west of street B. "
           f"North-west there are {n} − {k} = {nw_} houses. So south-west there are {w} − {nw_} = {ans}.")
    mistakes = [(w, "count all the houses west of street B"), (nw_, "find the north-west corner"),
                (s - (e - k), "find the south-east corner"), (s, "use the south number"),
                (abs(w - k), "take the north-east houses away from the west houses")]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=0, order="asc")
    return Question(text=text, figure=village_pic(), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, v.corner("south", "west")))


@variant(difficulty=3)
def three_streets(rng, harder):
    """Twist: two streets go north-south; how many houses are between them?"""
    hi = 7 if harder else 4
    while True:
        cells = [rng.randint(1, hi) for _ in range(6)]   # nw, ne, sw, se, mid-n, mid-s
        if cells[4] + cells[5] >= 2:
            break
    v = Village(cells[0], cells[1], cells[2], cells[3], rng, mid=(cells[4], cells[5]))
    n, s, w, e = v.count("north"), v.count("south"), v.count("west"), v.count("eastC")
    text = (f"Streets B and C both go from north to south (see map).\n"
            + _facts(_says('north', n), _says('south', s),
                     f"West of street B there {'is' if w == 1 else 'are'} {w} {'house' if w == 1 else 'houses'}.",
                     f"East of street C there {'is' if e == 1 else 'are'} {e} {'house' if e == 1 else 'houses'}.",
                     lead="") +
            f"How many houses are there between street B and street C?")
    total = n + s
    ans = total - w - e
    sol = (f"The village has {n} + {s} = {total} houses. Take away the houses west of B and east of C: "
           f"{total} − {w} − {e} = {ans} houses are left between the two streets.")
    mistakes = [(total - w, "take away only the houses west of street B"),
                (total - e, "take away only the houses east of street C"),
                (abs(n - s), "take the south houses away from the north houses"),
                (abs(w + e - n), "use only the north houses"), (w + e, "add the west and east houses")]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=0, order="asc", unit=HOUSES)
    return Question(text=text, figure=village_pic(names=("A", "B"), third="C", max_px=170), choices=choices,
                    answer=ai, solution=sol, check=value_check(choices, v.count("between")))


# ------------------------------------------------------------------ teaching page
def teach():
    import random
    rng = random.Random(12)
    demo = Village(2, 5, 2, 3, rng)                 # north 7, east 8, south 5, west 4
    return [
        ("h", "How to think about it: one village, two streets"),
        "Street A goes from west to east. Street B goes from north to south. They cross in the middle of the "
        "village. Here is a village where you can see the houses:",
        village_pic(houses=demo, max_px=160),
        ("-", "<b>Street A</b> cuts the village into a north part and a south part. Count: north 7, south 5. "
              "So the village has 7 + 5 = <b>12 houses</b>."),
        ("-", "<b>Street B</b> cuts the <b>same village</b> into a west part and an east part. Count: west 4, "
              "east 8. And 4 + 8 = <b>12 houses</b> again!"),
        ("tip", "<b>The big idea:</b> every house is either north or south of street A, and every house is "
                "either west or east of street B. So north + south = all the houses = west + east."),
        ("h", "Step by step: the contest question"),
        "In the contest the houses are <b>not</b> drawn. You only know: north 7, east 8, south 5. "
        "How many are west?",
        ("-", "<b>1. Use the two numbers of the same street.</b> North and south both belong to street A: "
              "7 + 5 = 12 houses in the whole village."),
        ("-", "<b>2. Now use the other street.</b> East of B there are 8, so west of B there are 12 − 8 = <b>4</b>."),
        ("table", [["", "street A", "street B"],
                   ["one side", "north: 7", "east: 8"],
                   ["other side", "south: 5", "west: ?"],
                   ["all houses", "12", "12"]]),
        ("h", "Watch out"),
        ("-", "You do not need to know which corner each house is in. You only need the total."),
        ("-", "Do not just add or subtract the numbers in the order you read them. First ask: which numbers "
              "belong to the <b>same</b> street?"),
        ("-", "Check: west + east must give the same total as north + south (4 + 8 = 12 = 7 + 5)."),
    ]


# ------------------------------------------------------------------ warm-ups
@warmup
def w_count_on_map(rng, harder):
    """Count the drawn houses on one side of a street."""
    v = Village(*[rng.randint(1, 4) for _ in range(4)], rng)
    side = rng.choice(list(OPP))
    text = f"Look at the map. How many houses are there {side} of street {STREET_OF[side]}?"
    ans = v.count(side)
    other = v.count(OPP[side])
    sol = f"Count the little squares on the {side} side of street {STREET_OF[side]}: {ans}."
    choices, ai = numeric_choices(ans, [(other, f"count the {OPP[side]} side"),
                                        (len(v.houses), "count all the houses")], rng, lo=0, order="asc")
    value = sum(1 for x, y in v.houses
                if {"north": y > 0, "south": y < 0, "east": x > 0, "west": x < 0}[side])
    return Question(text=text, figure=village_pic(houses=v), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, value))


@warmup
def w_one_street(rng, harder):
    """One street: north + south = all houses."""
    v = Village(*[rng.randint(1, 5) for _ in range(4)], rng)
    n, s = v.count("north"), v.count("south")
    text = (_facts(_says('north', n), _says('south', s), "No house stands on a street.") +
            f"How many houses are there in the village?")
    ans = n + s
    sol = f"Every house is north or south of street A: {n} + {s} = {ans}."
    choices, ai = numeric_choices(ans, [(abs(n - s), "subtract instead of add"), n, s], rng, lo=1, order="asc")
    return Question(text=text, figure=village_pic(), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, len(v.houses)))


@warmup
def w_other_side(rng, harder):
    """All houses known: the other side of street B."""
    v = Village(*[rng.randint(1, 5) for _ in range(4)], rng)
    total = len(v.houses)
    side = rng.choice(["east", "west"])
    k = v.count(side)
    text = (f"There are {total} houses in the village. {_says(side, k)} "
            f"How many houses are there {OPP[side]} of street B?")
    ans = total - k
    sol = f"Every house is east or west of street B: {total} − {k} = {ans}."
    choices, ai = numeric_choices(ans, [(total + k, "add instead of subtract"), (k, f"use the {side} number"),
                                        total], rng, lo=0, order="asc")
    return Question(text=text, figure=village_pic(), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, v.count(OPP[side])))
