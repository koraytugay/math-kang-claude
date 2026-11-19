"""2026 Q9 (Canada, Grade 3-4) - finishing a picture puzzle: which piece is left out?

Original: Bella is making a heart puzzle for her mother, as shown (a red heart on a 9 x 9 grid
with 11 white empty squares inside). She needs four of the five pieces to finish it.
Pieces: A = 3 in a row, B = 1 square, C = S-shape of 4, D = 2 squares, E = 2 x 2 square.
Which piece does she leave out?  (A) A  (B) B  (C) C  (D) D  (E) E.
The pieces have 3 + 1 + 4 + 2 + 4 = 14 squares, the hole has 11, so the piece left out has
14 - 11 = 3 squares: A. (B, C, D and E do fill the hole: checked by brute force.)  Answer: A.
(There is no answer key for 2026 in the repo: solved by us.)

Core skill: count first - all pieces together minus the empty squares is the size of the piece
that is left over; when that leaves two candidates (or all pieces are the same size), try which
four pieces really fit, starting where the hole is narrowest.
"""
from itertools import combinations

from reportlab.lib import colors

from kangaroo import Fig, Question, numeric_choices, value_check, variant
from kangaroo.choices import Choices
from kangaroo.figures import column, row
from kangaroo.polyomino import covers, orientations, place_inside, placements, random_shape, same_shape

META = {
    "source": "set-03/by_level/Grade_03-04/2026 Q9",
    "skill": "Count the squares: all the pieces minus the empty squares is the size of the piece left over; "
             "then check that the other pieces really fit",
    "topics": ["spatial", "counting", "geometry"],
    "keywords": ["piece left over", "puzzle pieces", "count the squares"],
    "sticker": ("💝", "Heart puzzler"),   # earned when this skill is solid (website)
    "version": 1,
}

RED = colors.Color(0.9, 0.16, 0.16)
SKY = colors.Color(0.84, 0.93, 0.98)
NOTE = "The pieces may be turned and flipped over."
PEOPLE = [("Bella", "she", "her"), ("Mia", "she", "her"), ("Sara", "she", "her"),
          ("Leo", "he", "his"), ("Sam", "he", "his"), ("Omar", "he", "his")]
FOR = ["mother", "father", "grandma", "grandpa", "teacher", "friend"]

MOTIFS = {
    "heart": """
...........
..RRR.RRR..
.RRRRRRRRR.
RRRRRRRRRRR
RRRRRRRRRRR
.RRRRRRRRR.
..RRRRRRR..
...RRRRR...
....RRR....
.....R.....
...........""",
    "house": """
.....R.....
....RRR....
...RRRRR...
..RRRRRRR..
.RRRRRRRRR.
..RRRRRRR..
..RRRRRRR..
..RRRRRRR..
..RRRRRRR..
..RRRRRRR..
...........""",
    "tree": """
.....R.....
....RRR....
...RRRRR...
..RRRRRRR..
...RRRRR...
..RRRRRRR..
.RRRRRRRRR.
RRRRRRRRRRR
....RRR....
....RRR....
...........""",
    "kite": """
.....R.....
....RRR....
...RRRRR...
..RRRRRRR..
.RRRRRRRRR.
RRRRRRRRRRR
.RRRRRRRRR.
..RRRRRRR..
...RRRRR...
....RRR....
.....R.....""",
}


def _mask(name):
    rows = MOTIFS[name].strip().split("\n")
    n = len(rows)
    return n, frozenset((c, n - 1 - r) for r, line in enumerate(rows) for c, ch in enumerate(line) if ch == "R")


def _inside(mask):
    """Cells whose four neighbours are all part of the picture: holes there look like holes."""
    return frozenset((x, y) for x, y in mask
                     if all(n in mask for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))))


# ------------------------------------------------------------------ pictures
def picture(n, mask, hole, scale=12):
    f = Fig(n, n, scale=scale, margin=3)
    for x in range(n):
        for y in range(n):
            fill = colors.white if (x, y) in hole else (RED if (x, y) in mask else SKY)
            f.rect(x, y, 1, 1, fill=fill, width=0.5)
    return f.drawing()


def _piece(cells, label, h, scale):
    """A piece standing on a line, with its letter below it (like the contest)."""
    w = max(x for x, _ in cells) + 1
    f = Fig(w, h + 1.4, scale=scale, margin=3)
    for x, y in cells:
        f.rect(x, y + 1.4, 1, 1, fill=RED, width=0.9)
    f.text(w / 2, 0.55, label, size=11)
    return f.drawing()


def pieces_row(shown, labels, scale=12):
    h = max(max(y for _, y in p) + 1 for p in shown)
    return row([_piece(p, lab, h, scale) for p, lab in zip(shown, labels)], gap=16)


def figure(n, mask, hole, shown, labels):
    return column([picture(n, mask, hole), pieces_row(shown, labels)], gap=12)


# ------------------------------------------------------------------ making a puzzle
def _shapes(rng, sizes):
    """Distinct random shapes with these sizes (small ones at most 3 x 3, so they draw small)."""
    out = []
    for s in sizes:
        for _ in range(300):
            p = random_shape(rng, s, 3 if s < 4 or rng.random() < 0.7 else 4, 3)
            if not any(same_shape(p, q) for q in out):
                out.append(p)
                break
        else:
            return None
    return out


def _show(p, rng):
    return rng.choice(orientations(p, flip=False))


def _story(rng, motif, n_pieces, n_need):
    name, he, his = rng.choice(PEOPLE)
    words = {4: "four", 5: "five", 6: "six"}
    text = (f"{name} is making a {motif} puzzle for {his} {rng.choice(FOR)}, as shown. "
            f"{he.capitalize()} needs {words[n_need]} of the {words[n_pieces]} pieces to fill the white "
            f"squares. {NOTE}")
    return name, he, text


def build(rng, sizes_fn, n_pieces, good_fn, tries=400):
    """sizes_fn(rng) -> sizes, the first ones are the pieces that go in; good_fn checks the puzzle."""
    for _ in range(tries):
        motif = rng.choice(sorted(MOTIFS))
        n, mask = _mask(motif)
        sizes, n_in = sizes_fn(rng)
        pieces = _shapes(rng, sizes)
        if pieces is None:
            continue
        hole = place_inside(rng, _inside(mask), pieces[:n_in], tries=20, compact=True)
        if hole is None:
            continue
        order = list(range(n_pieces))
        rng.shuffle(order)
        shown = [_show(pieces[i], rng) for i in order]
        res = good_fn(hole, shown)
        if res is not None:
            return motif, n, mask, hole, shown, res
    raise RuntimeError("no puzzle found")


def leave_one(hole, shown):
    """Indices i such that the other pieces fill the hole exactly (brute force)."""
    return [i for i in range(len(shown)) if covers(hole, [p for j, p in enumerate(shown) if j != i])]


def _sizes_text(shown, labels):
    return " + ".join(str(len(p)) for p in shown) + f" = {sum(len(p) for p in shown)}"


# ------------------------------------------------------------------ variants
@variant(difficulty=1)
def leave_out(rng, harder):
    """The original: the size of the left-over piece is unique, so counting finds it."""
    def sizes(rng):
        lo, hi = (2, 5) if harder else (1, 4)
        s = rng.randint(lo, hi)
        rest = [rng.choice([v for v in range(lo, hi + 1) if v != s]) for _ in range(4)]
        return rest + [s], 4
    def good(hole, shown):
        ok = leave_one(hole, shown)
        return ok[0] if len(ok) == 1 else None
    motif, n, mask, hole, shown, k = build(rng, sizes, 5, good)
    labels = list("ABCDE")
    name, he, text = _story(rng, motif, 5, 4)
    text += f"\n\nWhich piece does {he} leave out?"
    total = sum(len(p) for p in shown)
    sol = (f"There are {len(hole)} white squares. The pieces have {_sizes_text(shown, labels)} squares. "
           f"{total} − {len(hole)} = {len(shown[k])}, so the piece left out has {len(shown[k])} "
           f"{'square' if len(shown[k]) == 1 else 'squares'}: only piece {labels[k]}. The other four fit.")
    big = max(range(5), key=lambda i: len(shown[i]))
    mistakes = {big: "leave out the biggest piece"} if big != k and \
        sum(len(p) == len(shown[big]) for p in shown) == 1 else {}
    return Question(text=text, figure=figure(n, mask, hole, shown, labels), choices=Choices(labels, mistakes),
                    answer=k, solution=sol, check=lambda i: covers(hole, [p for j, p in enumerate(shown) if j != i]))


@variant(difficulty=2)
def same_size(rng, harder):
    """Two pieces have the size of the left-over piece: counting gives two, the shape decides."""
    def sizes(rng):
        s = rng.randint(3, 4) if harder else rng.randint(2, 4)
        rest = [rng.choice([v for v in range(1, 5) if v != s]) for _ in range(3)]
        return [s] + rest + [s], 4
    def good(hole, shown):
        ok = leave_one(hole, shown)
        return ok[0] if len(ok) == 1 else None
    motif, n, mask, hole, shown, k = build(rng, sizes, 5, good)
    labels = list("ABCDE")
    twin = [i for i in range(5) if i != k and len(shown[i]) == len(shown[k])]
    name, he, text = _story(rng, motif, 5, 4)
    text += f"\n\nWhich piece does {he} leave out?"
    total = sum(len(p) for p in shown)
    s = len(shown[k])
    sol = (f"There are {len(hole)} white squares and the pieces have {total} squares together, so the piece "
           f"left out has {total} − {len(hole)} = {s} squares. Pieces {labels[min(k, twin[0])]} and "
           f"{labels[max(k, twin[0])]} both have {s}. Without {labels[twin[0]]} the pieces do not fit "
           f"into the white shape; without {labels[k]} they do. So {he} leaves out {labels[k]}.")
    mistakes = {twin[0]: "count the squares but not check that the other pieces fit"}
    return Question(text=text, figure=figure(n, mask, hole, shown, labels), choices=Choices(labels, mistakes),
                    answer=k, solution=sol, check=lambda i: covers(hole, [p for j, p in enumerate(shown) if j != i]))


def _left_after(hole, pieces):
    """Brute force: lay the pieces in the hole every possible way; sizes of what is left if it is one
    connected group of squares."""
    out = set()
    opts = [placements(hole, p) for p in pieces]

    def go(i, used):
        if i == len(pieces):
            rest = set(hole) - used
            if rest:
                todo, seen = [next(iter(rest))], set()
                while todo:
                    c = todo.pop()
                    if c in seen or c not in rest:
                        continue
                    seen.add(c)
                    x, y = c
                    todo += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
                if seen == rest:
                    out.add(len(rest))
            return
        for pl in opts[i]:
            if not used & pl:
                go(i + 1, used | pl)
    go(0, frozenset())
    return out


@variant(difficulty=2)
def missing_size(rng, harder):
    """Reverse: one piece is lost. How many squares does the lost piece have?"""
    def sizes(rng):
        lo, hi = (2, 5) if harder else (1, 4)
        return [rng.randint(lo, hi) for _ in range(5)], 5
    def good(hole, shown):
        return True
    motif, n, mask, hole, shown, _ = build(rng, sizes, 5, good)
    lost = rng.randrange(5)
    have = [p for i, p in enumerate(shown) if i != lost]
    labels = list("ABCD")
    name, he, his = rng.choice(PEOPLE)
    text = (f"{name} is making a {motif} puzzle, as shown. {he.capitalize()} has the four pieces below, "
            f"but one more piece is needed to fill all the white squares, and it is lost. {NOTE}"
            f"\n\nHow many squares does the lost piece have?")
    h = len(hole)
    t = sum(len(p) for p in have)
    ans = h - t
    sol = (f"There are {h} white squares. The four pieces have {_sizes_text(have, labels)} squares. "
           f"{h} − {t} = {ans}, so the lost piece has {ans} {'square' if ans == 1 else 'squares'}.")
    mistakes = [(h, "count the white squares only"), (t, "count the squares of the pieces you have"),
                ans + 1, ans - 1, ans + 2]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1, unit=("square", "squares"), order="asc")
    found = _left_after(hole, have)
    return Question(text=text, figure=figure(n, mask, hole, have, labels), choices=choices, answer=ai,
                    solution=sol, check=lambda i: found == {int(choices[i].split()[0])})


@variant(difficulty=3)
def two_left(rng, harder):
    """Six pieces, four are needed: which two are left out?"""
    def sizes(rng):
        return [rng.randint(2, 5 if harder else 4) for _ in range(6)], 4
    pairs = list(combinations(range(6), 2))
    def good(hole, shown):
        ok = [pq for pq in pairs if covers(hole, [p for j, p in enumerate(shown) if j not in pq])]
        if len(ok) != 1:
            return None
        total = sum(len(p) for p in shown)
        same = [pq for pq in pairs if pq != ok[0] and total - len(shown[pq[0]]) - len(shown[pq[1]]) == len(hole)]
        return (ok[0], same) if same else None
    motif, n, mask, hole, shown, (right, same) = build(rng, sizes, 6, good)
    labels = list("ABCDEF")
    name, he, text = _story(rng, motif, 6, 4)
    text += f"\n\nWhich two pieces does {he} leave out?"
    wrong_same = rng.sample(same, min(len(same), 2 if not harder else 3))
    others = [pq for pq in pairs if pq != right and pq not in wrong_same]
    opts = sorted(wrong_same + rng.sample(others, 4 - len(wrong_same)) + [right])
    words = [f"{labels[a]} and {labels[b]}" for a, b in opts]
    k = opts.index(right)
    mistakes = {i: "count the squares but not check that the other pieces fit"
                for i, pq in enumerate(opts) if pq in wrong_same}
    total = sum(len(p) for p in shown)
    sol = (f"There are {len(hole)} white squares and the six pieces have {total}, so the two pieces left out "
           f"have {total - len(hole)} squares together. Of the pairs with that many squares, only without "
           f"{labels[right[0]]} and {labels[right[1]]} do the other four fit into the white shape.")
    return Question(text=text, figure=figure(n, mask, hole, shown, labels), choices=Choices(words, mistakes),
                    answer=k, solution=sol,
                    check=lambda i: covers(hole, [p for j, p in enumerate(shown) if j not in opts[i]]))


@variant(difficulty=3)
def all_same(rng, harder):
    """Twist: every piece has the same number of squares, so counting cannot help."""
    s = 5 if harder else 4
    def sizes(rng):
        return [s] * 5, 4
    def good(hole, shown):
        ok = leave_one(hole, shown)
        return ok[0] if len(ok) == 1 else None
    motif, n, mask, hole, shown, k = build(rng, sizes, 5, good)
    labels = list("ABCDE")
    name, he, text = _story(rng, motif, 5, 4)
    text += f"\n\nWhich piece does {he} leave out?"
    sol = (f"Every piece has {s} squares, so counting does not help here. Start where the white shape is "
           f"narrowest or has a corner: only a few pieces fit there. Pieces "
           f"{', '.join(labels[i] for i in range(5) if i != k)} fill the white squares exactly, "
           f"so {he} leaves out {labels[k]}.")
    return Question(text=text, figure=figure(n, mask, hole, shown, labels), choices=Choices(labels),
                    answer=k, solution=sol, check=lambda i: covers(hole, [p for j, p in enumerate(shown) if j != i]))
