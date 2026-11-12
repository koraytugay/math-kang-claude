"""2023 Q15 (Ecolier, Grade 3-4) - fewest colours for circles joined by lines.

Original: Hanni wants to colour in the circles in the diagram. When two circles are connected
by a line they should have different colours. What is the minimum number of colours she needs?
(A) 2  (B) 3  (C) 4  (D) 5  (E) 6.
Diagram: 7 circles - two on top, three in the middle, two at the bottom - forming two diamonds
side by side that share the middle circle; the two bottom circles are also joined by a line.
The middle circle and the two bottom circles form a triangle, so 3 colours are needed; and 3 are
enough (middle red, bottom blue and yellow, the left and right circles red, the top circles blue).
Answer: B (answer key: B).

Core skill: two halves - "a triangle forces 3 colours" (a lower bound) and "show that this many is
really enough by colouring step by step" (an upper bound). Children guess 2 because colours seem
to take turns, or count circles/lines. A ring with an odd number of circles needs 3 even
without a triangle.
"""
import math

from kangaroo import Question, numeric_choices, text_choices, value_check, variant, warmup
from kangaroo.choices import Choices
from kangaroo.pictures import node_graph
from kangaroo.solve import colourings, min_colours

META = {
    "source": "set-01/by_level/Grade_03-04_Ecolier/2023 Q15",
    "skill": "Fewest colours: find circles that are all joined to each other (a triangle needs 3), "
             "then colour step by step to show that many is enough",
    "topics": ["logic", "spatial", "counting"],
    "keywords": ["colouring circles", "fewest colours", "neighbours different"],
    "version": 1,
}

COLOURS = ["red", "blue", "yellow"]
LETTER = {0: "R", 1: "B", 2: "Y"}
NAMES = ["Hanni", "Mia", "Leo", "Anna", "Tom", "Sara"]


# ------------------------------------------------------------------ graphs (positions + lines)
def diamonds(w, base):
    """w diamonds side by side (like the contest picture); base=True joins the bottom circles."""
    top = [(0.5 + i, 2.0) for i in range(w)]
    mid = [(float(i), 1.0) for i in range(w + 1)]
    bot = [(0.5 + i, 0.0) for i in range(w)]
    pos = top + mid + bot
    T, M, B = 0, w, 2 * w + 1
    edges = []
    for i in range(w):
        edges += [(T + i, M + i), (T + i, M + i + 1), (B + i, M + i), (B + i, M + i + 1)]
        if base and i < w - 1:
            edges.append((B + i, B + i + 1))
    return pos, edges


def ring(n):
    R = 0.5 / math.sin(math.pi / n) * 1.1
    pos = [(R + R * math.sin(2 * math.pi * i / n), R + R * math.cos(2 * math.pi * i / n)) for i in range(n)]
    return pos, [(i, (i + 1) % n) for i in range(n)]


def wheel(n):
    pos, edges = ring(n)
    R = pos[0][1] / 2
    return pos + [(R, R)], edges + [(i, n) for i in range(n)]


def triangle_centre():
    return [(0, 0), (2, 0), (1, 1.73), (1, 0.62)], [(0, 1), (1, 2), (2, 0), (0, 3), (1, 3), (2, 3)]


def house():
    return [(0, 0), (1.2, 0), (1.2, 1.1), (0, 1.1), (0.6, 2.0)], [(0, 1), (1, 2), (2, 3), (3, 0), (2, 4), (3, 4)]


def prism():
    pos = [(0, 0), (2.4, 0), (1.2, 2.08), (0.8, 0.5), (1.6, 0.5), (1.2, 1.2)]
    return pos, [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3), (1, 4), (2, 5)]


def ladder(cols, diagonal=False):
    pos = [(float(c), float(r)) for r in range(2) for c in range(cols)]
    edges = [(c, c + 1) for c in range(cols - 1)] + [(cols + c, cols + c + 1) for c in range(cols - 1)]
    edges += [(c, cols + c) for c in range(cols)]
    if diagonal:
        edges.append((0, cols + 1))
    return pos, edges


def grid3():
    pos = [(float(c), float(r)) for r in range(3) for c in range(3)]
    edges = [(r * 3 + c, r * 3 + c + 1) for r in range(3) for c in range(2)]
    edges += [(r * 3 + c, (r + 1) * 3 + c) for r in range(2) for c in range(3)]
    return pos, edges


def pool(harder):
    small = [diamonds(2, True), diamonds(2, False), ring(4), ring(5), ring(6), wheel(4), wheel(5),
             triangle_centre(), house(), ladder(3), ladder(3, True)]
    big = [diamonds(3, True), diamonds(3, False), ring(7), wheel(5), wheel(6), prism(), grid3(),
           ladder(4, True), triangle_centre()]
    return big if harder else small


# ------------------------------------------------------------------ the generator's own reasoning
def _fewest(n, edges):
    """Backtracking: the fewest colours, circle by circle (a different method from the brute-force check)."""
    nb = {v: set() for v in range(n)}
    for a, b in edges:
        nb[a].add(b)
        nb[b].add(a)
    order = sorted(range(n), key=lambda v: -len(nb[v]))
    def fits(k, i, col):
        if i == n:
            return True
        v = order[i]
        for c in range(k):
            if all(col.get(u) != c for u in nb[v]):
                col[v] = c
                if fits(k, i + 1, col):
                    return True
                del col[v]
        return False
    k = 1
    while not fits(k, 0, {}):
        k += 1
    return k


def _has_triangle(n, edges):
    E = {frozenset(e) for e in edges}
    return any({frozenset((a, b)), frozenset((b, c)), frozenset((a, c))} <= E
               for a in range(n) for b in range(a + 1, n) for c in range(b + 1, n))


def _mistakes(n, edges, k):
    deg = max(sum(v in e for e in edges) for v in range(n))
    tri = _has_triangle(n, edges)
    m = [(n, "give every circle its own colour"), (deg + 1, "count the lines at the busiest circle and add 1"),
         (len(edges), "count the lines")]
    if k > 2:
        m.append((2, "think two colours can always take turns" if tri
                  else "look for a triangle, and think 2 colours are enough when there is none"))
    if k == 4:
        m.append((3, "find a triangle and stop there"))
    if k == 2:
        m.append((3, "think every picture needs at least 3 colours"))
    m.append(k + 1)
    return m


# ------------------------------------------------------------------ variants
@variant(difficulty=1)
def fewest_colours(rng, harder):
    """The original: what is the smallest number of colours?"""
    pos, edges = rng.choice(pool(harder))
    n = len(pos)
    k = _fewest(n, edges)
    name = rng.choice(NAMES)
    text = (f"{name} wants to colour in the circles in the diagram. When two circles are connected by a "
            f"line they should have different colours. What is the minimum number of colours {name} needs?")
    if k == 2:
        sol = "Two colours are enough: colour the circles in turn, so that every line joins two different colours."
    elif _has_triangle(n, edges):
        sol = (f"Look for circles that are all joined to each other: a triangle needs 3 different colours"
               f"{' and here even 4 circles are all joined to each other' if k == 4 else ''}. "
               f"Then colour step by step: {k} colours are enough.")
    else:
        sol = (f"There is no triangle, but the ring has an odd number of circles: two colours taking turns "
               f"do not fit around it. {k} colours are enough.")
    choices, ai = numeric_choices(k, _mistakes(n, edges, k), rng, lo=1, order="asc")
    return Question(text=text, figure=node_graph(pos, edges, max_px=95 if n < 7 else 110), choices=choices,
                    answer=ai, solution=sol, check=value_check(choices, min_colours(n, edges)))


@variant(difficulty=2)
def zoo_cages(rng, harder):
    """Same idea, new story: animals that must not share a cage."""
    pos, edges = rng.choice(pool(harder))
    n = len(pos)
    k = _fewest(n, edges)
    labels = {i: "ABCDEFGHIJ"[i] for i in range(n)}
    text = (f"A zoo has {n} animals, A to {labels[n - 1]}. A line between two animals means that they do not "
            f"get along, so they must not live in the same cage. Any number of animals can live in one cage. "
            f"What is the smallest number of cages the zoo needs?")
    sol = (f"A cage is like a colour: animals joined by a line need different cages. "
           f"{'Look for animals that are all joined to each other. Then s' if k > 2 else 'S'}"
           f"hare the animals out step by step: {k} cages are enough, and fewer do not work.")
    zoo = {"give every circle its own colour": "give every animal its own cage",
           "count the lines at the busiest circle and add 1": "count the lines at the busiest animal and add 1",
           "count the lines": "count the lines",
           "find a triangle and stop there": "find three animals that all fight and stop there",
           "think every picture needs at least 3 colours": "think you always need at least 3 cages"}
    mistakes = []
    for x in _mistakes(n, edges, k):
        if isinstance(x, tuple):
            v, t = x
            mistakes.append((v, zoo.get(t, "think two cages are always enough")))
        else:
            mistakes.append(x)
    choices, ai = numeric_choices(k, mistakes, rng, lo=1, order="asc", unit=("cage", "cages"))
    return Question(text=text, figure=node_graph(pos, edges, labels=labels, max_px=95 if n < 7 else 110),
                    choices=choices, answer=ai, solution=sol, check=value_check(choices, min_colours(n, edges)))


@variant(difficulty=2)
def hand_in_hand(rng, harder):
    """A ring of children: even ring 2 shirts, odd ring 3 - even with no triangle."""
    n = rng.choice([7, 8, 9, 10, 11, 12] if harder else [5, 6, 7, 8])
    if rng.random() < 0.6 and n % 2 == 0:
        n += 1                                         # odd rings are the trap, show them more often
    pos, edges = ring(n)
    k = 2 if n % 2 == 0 else 3
    text = (f"{n} children stand in a ring and hold hands, as in the picture. Two children who hold hands "
            f"must wear T-shirts of different colours. What is the smallest number of colours needed?")
    if k == 2:
        sol = f"Take turns: red, blue, red, blue, ... With {n} children (an even number) the ring closes nicely."
    else:
        sol = (f"Red, blue, red, blue, ... works until the last child: with {n} children (an odd number) "
               f"the last child holds hands with two different colours. So 3 colours are needed.")
    mistakes = [(2, "take turns with two colours and forget that the ring closes") if k == 3
                else (3, "think a ring always needs 3 colours"),
                (n, "give every child a different colour"), (n // 2, "count the pairs of children"), 4]
    choices, ai = numeric_choices(k, mistakes, rng, lo=1, order="asc")
    return Question(text=text, figure=node_graph(pos, edges, max_px=100), choices=choices, answer=ai,
                    solution=sol, check=value_check(choices, min_colours(n, edges)))


def _possible(n, edges, fixed, q):
    """Generator side: colours circle q can get in some correct colouring (backtracking)."""
    nb = {v: set() for v in range(n)}
    for a, b in edges:
        nb[a].add(b)
        nb[b].add(a)
    out = set()
    for cq in range(3):
        col = dict(fixed)
        if q in col and col[q] != cq:
            continue
        col[q] = cq
        free = [v for v in range(n) if v not in col]
        def go(i):
            if i == len(free):
                return True
            v = free[i]
            for c in range(3):
                if all(col.get(u) != c for u in nb[v]):
                    col[v] = c
                    if go(i + 1):
                        return True
                    del col[v]
            return False
        if all(col.get(u) != cq for u in nb[q]) and all(col[a] != col[b] for a, b in edges
                                                          if a in col and b in col) and go(0):
            out.add(cq)
    return out


@variant(difficulty=1)
def which_colour(rng, harder):
    """Some circles are already coloured: which colour must the circle with ? get?"""
    choices3 = [g for g in pool(harder) if _fewest(len(g[0]), g[1]) == 3]
    while True:
        pos, edges = rng.choice(choices3)
        n = len(pos)
        sols = list(colourings(n, edges, 3))
        c = rng.choice(sols)
        q = rng.randrange(n)
        others = [v for v in range(n) if v != q]
        fixed = {v: c[v] for v in rng.sample(others, rng.randint(2, 3 if harder else 4))}
        nbq = {b if a == q else a for a, b in edges if q in (a, b)}
        direct = {fixed[v] for v in nbq if v in fixed}
        if _possible(n, edges, fixed, q) != {c[q]}:
            continue
        if harder == (len(direct) < 2):                # harder: the colour follows only through a chain
            break
    name = rng.choice(NAMES)
    labels = {v: LETTER[col] for v, col in fixed.items()}
    labels[q] = "?"
    text = (f"{name} colours the circles red (R), blue (B) and yellow (Y). Circles joined by a line must get "
            f"different colours. Some circles are already coloured. {name} wants to colour all the other "
            f"circles too. Which colour must the circle with the question mark get?")
    ans = COLOURS[c[q]]
    near = [COLOURS[x] for x in sorted(direct)]
    wrong = [(w, "use a colour of a circle it is joined to" if w in near else "not check all the circles")
             for w in COLOURS if w != ans]
    pa, pb = sorted(rng.sample(range(3), 2))
    wrong.append((f"{COLOURS[pa]} or {COLOURS[pb]}, both work", "think there is a choice"))
    wrong.append(("it cannot be done", "think it cannot be done"))
    choices, ai = text_choices(ans, wrong, rng)
    sol = (f"The circle with the question mark must differ from the circles it is joined to"
           f"{'' if len(direct) == 2 else ', and those are forced by their own neighbours'}. "
           f"Only {ans} fits.")
    allowed = {COLOURS[x] for x in {col[q] for col in colourings(n, edges, 3, fixed)}}
    def check(i):
        o = choices[i]
        if o == "it cannot be done":
            return not allowed
        if " or " in o:
            a, b = o.split(", ")[0].split(" or ")
            return allowed == {a, b}
        return allowed == {o}
    return Question(text=text, figure=node_graph(pos, edges, labels=labels, max_px=100 if n < 7 else 115),
                    choices=choices, answer=ai, solution=sol, check=check)


def _two_rings(a, b):
    """A ring of a circles and a ring of b circles that share one circle (circle 0)."""
    pos, edges = [(0.0, 0.0)], []
    for size, side in ((a, -1), (b, 1)):
        R = 0.55 / math.sin(math.pi / size)
        start = len(pos)
        ids = [0] + list(range(start, start + size - 1))
        for k in range(1, size):
            t = 2 * math.pi * k / size
            pos.append((side * (R - R * math.cos(t)), R * math.sin(t)))
        edges += [(ids[i], ids[(i + 1) % size]) for i in range(size)]
    return pos, edges


def _two_colourable_without(n, edges, v):
    """Generator side: is the graph without circle v colourable with 2 colours? (breadth-first search)"""
    E = [(a, b) for a, b in edges if v not in (a, b)]
    side = {}
    for s in range(n):
        if s == v or s in side:
            continue
        side[s], todo = 0, [s]
        while todo:
            x = todo.pop()
            for a, b in E:
                for p, q in ((a, b), (b, a)):
                    if p == x:
                        if q not in side:
                            side[q] = 1 - side[x]
                            todo.append(q)
                        elif side[q] == side[x]:
                            return False
    return True


@variant(difficulty=3)
def take_one_away(rng, harder):
    """Reverse: only 2 colours - which circle must be taken away?"""
    a, b = rng.choice([(3, 5), (5, 5), (5, 3), (3, 7)] if harder else [(3, 3), (3, 5), (5, 3)])
    pos, edges = _two_rings(a, b)
    n = len(pos)
    good = [v for v in range(n) if _two_colourable_without(n, edges, v)]
    assert good == [0]
    opts = [0] + rng.sample(range(1, n), 4)
    rng.shuffle(opts)
    letters = "ABCDE"
    labels = {v: letters[i] for i, v in enumerate(opts)}
    name = rng.choice(NAMES)
    text = (f"{name} has only <b>two</b> colours. Circles joined by a line must get different colours. "
            f"{name} may take away one circle together with its lines. Which circle must {name} take away, "
            f"so that two colours are enough for the other circles?")
    sol = (f"A ring with an odd number of circles cannot be coloured with two colours taking turns. "
           f"There are two such rings ({a} and {b} circles). Only circle {labels[0]} belongs to both rings, "
           f"so taking it away breaks both of them.")
    choices = Choices([f"circle {letters[i]}" for i in range(5)],
                      {i: "take away a circle that is in only one of the two rings"
                       for i in range(5) if opts[i] != 0})
    def check(i):
        v = opts[i]
        rest = [u for u in range(n) if u != v]
        idx = {u: j for j, u in enumerate(rest)}
        E = [(idx[x], idx[y]) for x, y in edges if v not in (x, y)]
        return next(colourings(n - 1, E, 2), None) is not None
    return Question(text=text, figure=node_graph(pos, edges, labels=labels, max_px=130),
                    choices=choices, answer=opts.index(0), solution=sol, check=check)


# ------------------------------------------------------------------ teaching page
def teach():
    pos, edges = diamonds(2, True)
    # top 0,1 ; middle 2,3,4 ; bottom 5,6
    colour = {3: 0, 5: 1, 6: 2, 2: 0, 4: 0, 0: 1, 1: 1}
    ring_pos, ring_edges = ring(5)
    return [
        ("h", "How to think about it: the fewest colours"),
        "Circles joined by a line must get different colours. To find the <b>fewest</b> colours, you need "
        "two things:",
        ("-", "<b>1. Why you need at least this many.</b> Look for circles that are <b>all</b> joined to each "
              "other. Three circles that form a triangle need 3 different colours."),
        ("-", "<b>2. Why this many is enough.</b> Really colour the picture, one circle after the other. "
              "Start with the circle that has the most lines. For each new circle, look at the circles it is "
              "joined to and pick a colour they do not have."),
        ("h", "The contest question"),
        "The middle circle and the two bottom circles form a triangle: you need at least 3 colours. "
        "And 3 colours are enough — here is one way (R = red, B = blue, Y = yellow):",
        node_graph(pos, edges, labels={v: LETTER[c] for v, c in colour.items()}, max_px=110),
        ("tip", "Answer: <b>3</b> colours. Lines only care about the two circles at their ends — the left and "
                "the right circle may both be red, because no line joins them."),
        ("h", "Watch out"),
        ("-", "No triangle does not always mean 2 colours! In a ring of 5 circles, red, blue, red, blue ... does "
              "not fit: the last circle touches red and blue. Count the circles in a ring: even is fine with 2, "
              "odd needs 3."),
        node_graph(ring_pos, ring_edges, labels={0: "R", 1: "B", 2: "R", 3: "B", 4: "?"}, max_px=80),
        ("-", "Do not count the circles or the lines — many circles can share a colour."),
    ]


# ------------------------------------------------------------------ warm-ups
@warmup
def w_triangle(rng, harder):
    """Three circles all joined: 3 colours."""
    pos, edges = [(0, 0), (1.4, 0), (0.7, 1.2)], [(0, 1), (1, 2), (2, 0)]
    if rng.random() < 0.5:
        pos, edges = pos + [(2.1, 1.2)], edges + [(1, 3), (2, 3)]
    n = len(pos)
    text = ("Circles joined by a line must get different colours. What is the smallest number of colours "
            "you need?")
    sol = "Three circles that are all joined to each other need three different colours" + \
          ("." if n == 3 else "; the fourth circle can use the colour of the circle it is not joined to.")
    choices, ai = numeric_choices(3, [(n, "give every circle its own colour"), (2, "use two colours taking turns"),
                                      (len(edges), "count the lines")], rng, lo=1, order="asc")
    return Question(text=text, figure=node_graph(pos, edges, max_px=70), choices=choices, answer=ai,
                    solution=sol, check=value_check(choices, min_colours(n, edges)))


@warmup
def w_square(rng, harder):
    """A ring of 4 or 6: two colours take turns."""
    n = rng.choice([4, 6])
    pos, edges = ring(n)
    text = ("Circles joined by a line must get different colours. What is the smallest number of colours "
            "you need?")
    sol = "Red, blue, red, blue, ... - opposite circles may share a colour, so 2 colours are enough."
    choices, ai = numeric_choices(2, [(n, "give every circle its own colour"), (3, "think a ring needs 3 colours")],
                                  rng, lo=1, order="asc")
    return Question(text=text, figure=node_graph(pos, edges, max_px=75), choices=choices, answer=ai,
                    solution=sol, check=value_check(choices, min_colours(n, edges)))


@warmup
def w_next_colour(rng, harder):
    """One step of colouring: a circle joined to red and blue."""
    pos, edges = [(0, 0), (1.4, 0), (0.7, 1.2)], [(0, 1), (1, 2), (2, 0)]
    a, b = rng.sample(range(3), 2)
    ans = 3 - a - b
    text = ("Circles joined by a line must get different colours. You only have red (R), blue (B) and "
            "yellow (Y). Which colour must the circle with the question mark get?")
    wrong = [(COLOURS[a], "use the colour of a circle it is joined to"),
             (COLOURS[b], "use the colour of a circle it is joined to"),
             ("it cannot be done", "think it cannot be done"), ("any colour works", "think there is a choice")]
    choices, ai = text_choices(COLOURS[ans], wrong, rng)
    allowed = {COLOURS[col[2]] for col in colourings(3, edges, 3, {0: a, 1: b})}
    return Question(text=text, figure=node_graph(pos, edges, labels={0: LETTER[a], 1: LETTER[b], 2: "?"}, max_px=70),
                    choices=choices, answer=ai,
                    solution=f"It is joined to {COLOURS[a]} and {COLOURS[b]}, so it must be {COLOURS[ans]}.",
                    check=lambda i: {choices[i]} == allowed)
