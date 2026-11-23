"""2026 Q23 (Canada, Grade 3-4) - sweets in a grid: the numbers show the sweets in the neighbouring squares.

Original: Each square in a 3 x 3 grid has at least one sweet. The numbers show how many sweets are in
the neighbouring squares. (Two squares are neighbours if they share a side.)
Numbers: 2 4 3 / 7 7 3 / 4 6 5. How many sweets are in all nine squares?  (A) 16 (B) 17 (C) 18 (D) 20 (E) 21.
The top-left number 2 = the two neighbours of the corner, each at least 1, so both are 1. Going on square by
square gives the sweets 2 1 1 / 1 1 2 / 4 3 1 (every number checked): 16.  Answer: A.
(The 2026 key in the repo is our own: solved by us. Brute force over all grids finds this is the only one.)

Core skill: a number in the picture is a sum of neighbours, not the sweets of its own square. Start where
there is the least choice (a corner has only two neighbours, an end square of a row has only one), then use
each square you have found in the next number. Children add up the numbers they see (41) or read each number
as the sweets in its own square.

Easy versions: work forwards (add the neighbours of one square), a row of 3 or 4 squares (the end number IS the
sweets of its neighbour), then 2 x 3 and 3 x 3 grids.
"""
from kangaroo import Fig, Question, numeric_choices, value_check, variant

META = {
    "source": "set-03/by_level/Grade_03-04/2026 Q23",
    "skill": "A number is the sum of the neighbours' sweets, not its own square: start where there is the least "
             "choice (an end or a corner has the fewest neighbours), then use every square you find in the next number",
    "topics": ["logic", "arithmetic", "counting"],
    "keywords": ["sums of neighbours", "sweet grid", "working backwards"],
    "sticker": ("🍬", "Sweet solver"),   # earned when this skill is solid (website)
    "rungs": ("easier", "easier", "aligned", "harder"),   # vs the original contest question: steps 1, 2, 3, 3 harder (2026-11-23)
    "version": 1,
}

PEOPLE = ["Mia", "Lena", "Nora", "Sara", "Ella", "Zoe", "Maya", "Ivy"]
NEIGHBOUR_RULE = "(Two squares are neighbours if they share a side.)"


# ------------------------------------------------------------------ the model
def cells(shape):
    rows, cols = shape
    return [(r, c) for r in range(rows) for c in range(cols)]


def neighbours(shape, cell):
    r, c = cell
    rows, cols = shape
    return [(r + dr, c + dc) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))
            if 0 <= r + dr < rows and 0 <= c + dc < cols]


def sums_of(shape, sweets):
    """sweets: dict cell -> number. The number shown in every square: the sweets of its neighbours."""
    return {c: sum(sweets[n] for n in neighbours(shape, c)) for c in cells(shape)}


# ------------------------------------------------------------------ the check: every grid that fits the picture
def solve(shape, shown, limit=200):
    """All ways to put at least one sweet in every square so that every number in the picture is right
    (square by square with backtracking; a number is checked as soon as all its neighbours are filled)."""
    order = cells(shape)
    pos = {c: i for i, c in enumerate(order)}
    ready = {}                                   # index -> cells whose number can be checked now
    for c in order:
        if shown[c] is None:                     # a hidden number: nothing to check there
            continue
        ready.setdefault(max(pos[n] for n in neighbours(shape, c)), []).append(c)
    top = max(v for v in shown.values() if v is not None)
    # a square cannot have more sweets than a neighbouring number allows (the other neighbours have at least 1)
    cap = {c: min([shown[n] - (len(neighbours(shape, n)) - 1) for n in neighbours(shape, c)
                   if shown[n] is not None] or [top]) for c in order}
    found, cur = [], {}

    def go(i):
        if len(found) >= limit:
            return
        if i == len(order):
            found.append(dict(cur))
            return
        for v in range(1, min(top, cap[order[i]]) + 1):
            cur[order[i]] = v
            if all(sum(cur[n] for n in neighbours(shape, c)) == shown[c] for c in ready.get(i, [])):
                go(i + 1)
        del cur[order[i]]

    go(0)
    return found


# ------------------------------------------------------------------ pictures
def grid_pic(shape, numbers, shade=None, star=None, max_px=120, size=13):
    rows, cols = shape
    f = Fig(cols, rows, max_px=max_px if max(rows, cols) > 2 else 90, margin=6)
    from reportlab.lib import colors
    for (r, c), v in numbers.items():
        x, y = c, rows - 1 - r
        fill = colors.Color(0.98, 0.85, 0.5) if (r, c) == shade else colors.Color(0.96, 0.96, 0.96)
        f.rect(x, y, 1, 1, fill=fill, width=0.9)
        if v is not None:
            f.text(x + 0.5, y + 0.5, str(v), size=size)
    if star is not None:
        r, c = star
        x, y = c, rows - 1 - r
        f.rect(x, y, 1, 1, fill=colors.Color(0.98, 0.85, 0.5), width=1.6)
        f.text(x + 0.5, y + 0.5, "?", size=size + 3)
    return f.drawing()


def _rows_text(shape, sweets):
    rows, cols = shape
    return " / ".join(" ".join(str(sweets[(r, c)]) for c in range(cols)) for r in range(rows))


def _check_story(shape, sweets, shown):
    """A few of the checks, e.g. 'top-left 2 = 1 + 1'."""
    out = []
    for c in cells(shape):
        ns = neighbours(shape, c)
        out.append(f"{shown[c]} = " + " + ".join(str(sweets[n]) for n in ns))
    return "; ".join(out[:3]) + ", ..."


def _random_sweets(rng, shape, top):
    return {c: rng.randint(1, top) for c in cells(shape)}


def _unique(rng, shape, top, tries=4000, want=None):
    """A random sweets grid whose picture has exactly one solution."""
    for _ in range(tries):
        sw = _random_sweets(rng, shape, top)
        shown = sums_of(shape, sw)
        sols = solve(shape, shown, limit=2)
        if len(sols) == 1 and (not want or want(sw, shown)):
            return sw, shown
    raise RuntimeError("no unique grid found")


# ------------------------------------------------------------------ variants
@variant(difficulty=1)
def forward_sum(rng, harder):
    """Easiest: the sweets are shown; add up the sweets of the neighbours of one square."""
    shape = (3, 3)
    sw = _random_sweets(rng, shape, 6 if harder else 4)
    name = rng.choice(PEOPLE)
    target = rng.choice(cells(shape))
    ns = neighbours(shape, target)
    ans = sum(sw[n] for n in ns)
    text = (f"The numbers in the grid show how many sweets are in each square. {NEIGHBOUR_RULE}"
            f"\n\nHow many sweets are in the neighbours of the shaded square?")
    sol = (f"The shaded square has {len(ns)} neighbours, with " + ", ".join(str(sw[n]) for n in ns)
           + f" sweets. Together: {ans}.")
    mistakes = [(sw[target], "count the sweets of the shaded square itself"),
                (ans + sw[target], "count the shaded square too"),
                (sum(sw.values()), "count the sweets of all the squares")]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1, order="asc")
    # check: neighbours are the squares at distance 1 (rows + columns apart)
    check_val = sum(v for c, v in sw.items() if abs(c[0] - target[0]) + abs(c[1] - target[1]) == 1)
    return Question(text=text, figure=grid_pic(shape, sw, shade=target), choices=choices, answer=ai,
                    solution=sol, check=value_check(choices, check_val))


@variant(difficulty=1)
def row_total(rng, harder):
    """A row of 3 or 4 squares: the number at the end is simply the sweets of its one neighbour."""
    n = rng.choice([4, 5] if harder else [3, 4])
    shape = (1, n)
    sw, shown = _unique(rng, shape, 4 if harder else 3)
    name = rng.choice(PEOPLE)
    total = sum(sw.values())
    text = (f"{name} has a row of {n} squares and puts at least one sweet in each square. The numbers show how many "
            f"sweets are in the neighbouring squares. {NEIGHBOUR_RULE}\n\nHow many sweets are in all {n} squares?")
    first = sw[(0, 0)]
    sol = (f"The first number is {shown[(0, 0)]}. That square has only one neighbour, so the second square has "
           f"{shown[(0, 0)]} sweets. Go on along the row, checking every number: the sweets are "
           f"{' '.join(str(sw[(0, c)]) for c in range(n))}. Together: {total}.")
    mistakes = [(sum(shown.values()), "add up the numbers in the picture"),
                (total - first, "forget the first square"),
                (total + 1, "add one too many")]
    choices, ai = numeric_choices(total, mistakes, rng, lo=1, order="asc")
    sols = solve(shape, shown)
    return Question(text=text, figure=grid_pic(shape, shown, max_px=130), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, sum(sols[0].values())))


@variant(difficulty=2)
def small_grid(rng, harder):
    """A 2 x 3 grid: how many sweets in all six squares?"""
    shape = (2, 3)
    sw, shown = _unique(rng, shape, 4 if harder else 3)
    name = rng.choice(PEOPLE)
    total = sum(sw.values())
    text = (f"Each square in the grid has at least one sweet. The numbers show how many sweets are in the "
            f"neighbouring squares. {NEIGHBOUR_RULE}\n\nHow many sweets are in all six squares?")
    sol = (f"Start at a corner: it has only two neighbours, so its number is their sweets added. "
           f"Work square by square and check every number. The sweets are {_rows_text(shape, sw)} "
           f"(for example {_check_story(shape, sw, shown)}). Together: {total}.")
    mistakes = [(sum(shown.values()), "add up the numbers in the picture"),
                (total + 1, "add one too many"), (total - 1, "add one too few")]
    choices, ai = numeric_choices(total, mistakes, rng, lo=3, order="asc")
    sols = solve(shape, shown)
    return Question(text=text, figure=grid_pic(shape, shown, max_px=120), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, sum(sols[0].values())))


def star_values(shape, shown, star):
    """The sweets the square `star` can have, over every grid that fits all the other (drawn) numbers."""
    sols = solve(shape, {**shown, star: None}, limit=100000)
    return {s_[star] for s_ in sols}


@variant(difficulty=2)
def one_square(rng, harder):
    """3 x 3: how many sweets in the square with the question mark (its own number is hidden)?"""
    shape = (3, 3)
    star = rng.choice([(0, 0), (0, 2), (2, 0), (2, 2), (1, 1), (0, 1), (1, 0)])
    sw, shown = _unique(rng, shape, 4 if harder else 3,
                        want=lambda sw_, sh_: star_values(shape, sh_, star) == {sw_[star]})
    ans = sw[star]
    pic = {c: v for c, v in shown.items() if c != star}
    pic[star] = None
    text = (f"Each square in the grid has at least one sweet. The numbers show how many sweets are in the "
            f"neighbouring squares. {NEIGHBOUR_RULE} The number of the square with the question mark is hidden."
            f"\n\nHow many sweets are in the square with the question mark?")
    sol = (f"The sweets in the whole grid must be {_rows_text(shape, sw)} (start at a corner, which has only "
           f"two neighbours, and check every number: {_check_story(shape, sw, shown)}). "
           f"The square with the question mark has {ans}.")
    choices, ai = numeric_choices(ans, [], rng, lo=1, order="asc")
    values = star_values(shape, shown, star)
    return Question(text=text, figure=grid_pic(shape, pic, star=star), choices=choices, answer=ai, solution=sol,
                    check=lambda i: values == {int(choices[i])})


@variant(difficulty=3)
def grid_total(rng, harder):
    """The original: 3 x 3 grid, how many sweets in all nine squares?"""
    shape = (3, 3)
    sw, shown = _unique(rng, shape, 5 if harder else 4)
    total = sum(sw.values())
    text = (f"Each square in a grid has at least one sweet. The numbers show how many sweets are in the "
            f"neighbouring squares. {NEIGHBOUR_RULE}\n\nHow many sweets are in all nine squares?")
    corner = min(((0, 0), (0, 2), (2, 0), (2, 2)), key=lambda c: shown[c])
    sol = (f"Start with a corner: the corner with the number {shown[corner]} has two neighbours, so those two squares "
           f"add up to {shown[corner]}. Go on square by square and check every number. The sweets are "
           f"{_rows_text(shape, sw)}. Together: {total}.")
    mistakes = [(sum(shown.values()), "add up the numbers in the picture"),
                (sum(shown.values()) // 2, "halve the numbers in the picture"),
                (total + 1, "add one too many"), (total - 1, "add one too few")]
    choices, ai = numeric_choices(total, mistakes, rng, lo=9, order="asc")
    sols = solve(shape, shown)
    return Question(text=text, figure=grid_pic(shape, shown), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, sum(sols[0].values())))
