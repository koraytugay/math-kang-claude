"""2022 Q24 (Ecolier, Grade 3-4) - coloured cards hide numbers; the row sums are given.

Original: Under cards with the same colour, the same number is always found. If the three
hidden numbers in one row are added, one obtains the number to the right of the row.
    grey  white white -> 34
    grey  white black -> 32
    white grey  grey  -> 26
Which number is hidden under the black card?  (A) 6 (B) 8 (C) 10 (D) 12 (E) 14
Rows 1 and 3 together have 3 grey and 3 white cards: 34 + 26 = 60, so one grey + one white
= 20. Row 2 is grey + white + black = 32, so black = 32 - 20 = 12.  Answer: D (12).

Core skill: no row can be solved on its own (every row has two or three unknown colours).
Children try to guess or divide a row by 3. The method: look for rows to put together or to
compare - two rows that together have the same number of each colour, two rows that differ in
one card, or a row that has only one unknown colour left. Twist (Part C): the row sums and the
column sums both add up to all the cards, so a missing column sum needs no colours at all.
"""
from reportlab.lib import colors

from kangaroo import Fig, Question, numeric_choices, value_check, variant
from kangaroo.solve import linear_value

META = {
    "source": "set-01/by_level/Grade_03-04_Ecolier/2022 Q24",
    "skill": "Cards hiding numbers: put two rows together or compare two rows, until a row has only one unknown colour",
    "topics": ["arithmetic", "logic"],
    "keywords": ["colour cards", "row sums", "same colour same number"],
    "sticker": ("🟫", "Colour code breaker"),   # earned when this skill is solid (website)
    "version": 1,
}

FILL = {"white": colors.white, "grey": colors.Color(0.72, 0.72, 0.72),
        "black": colors.Color(0.22, 0.22, 0.22), "dotted": colors.white}
COLOURS = ["white", "grey", "black", "dotted"]

RULES = ("Cards of the same colour always hide the same number. "
         "The number at the end of a row is the sum of the hidden numbers in that row.")


# ------------------------------------------------------------------ picture
def draw(grid, row_sums, col_sums=None):
    """Card grid. row_sums / col_sums: list of numbers or "?" (None = not shown)."""
    n_r, n_c = len(grid), len(grid[0])
    extra_x = 1.6
    extra_y = 0.9 if col_sums else 0
    f = Fig(n_c + extra_x, n_r + extra_y, max_px=27 * (n_c + extra_x), margin=6, font_size=12)
    for r, line in enumerate(grid):
        y = n_r - 1 - r + extra_y
        for c, col in enumerate(line):
            f.rect(c, y, 1, 1, fill=FILL[col], width=1.0)
            if col == "dotted":
                for dx, dy in [(0.25, 0.25), (0.75, 0.25), (0.5, 0.5), (0.25, 0.75), (0.75, 0.75)]:
                    f.circle(c + dx, y + dy, 0.07, fill=colors.black, width=0.5)
        if row_sums and row_sums[r] is not None:
            f.line((n_c + 0.15, y + 0.5), (n_c + 0.65, y + 0.5), width=0.8)
            f.line((n_c + 0.52, y + 0.6), (n_c + 0.65, y + 0.5), width=0.8)
            f.line((n_c + 0.52, y + 0.4), (n_c + 0.65, y + 0.5), width=0.8)
            f.text(n_c + 0.75, y + 0.5, str(row_sums[r]), anchor="start")
    if col_sums:
        for c, s in enumerate(col_sums):
            f.line((c + 0.5, extra_y - 0.05), (c + 0.5, extra_y - 0.4), width=0.8)
            f.line((c + 0.4, extra_y - 0.28), (c + 0.5, extra_y - 0.4), width=0.8)
            f.line((c + 0.6, extra_y - 0.28), (c + 0.5, extra_y - 0.4), width=0.8)
            f.text(c + 0.5, extra_y - 0.68, str(s))
    return f.drawing()


# ------------------------------------------------------------------ helpers
def count(line):
    out = {}
    for c in line:
        out[c] = out.get(c, 0) + 1
    return out


def shuffled_row(rng, line):
    line = list(line)
    rng.shuffle(line)
    return line


def row_check(grid, sums, target, choices):
    """Answer check: re-solve from the drawn cards and the shown sums (exact elimination)."""
    eqs = [(count(line), s) for line, s in zip(grid, sums) if isinstance(s, int)]
    return value_check(choices, int(linear_value(eqs, target)))


def phrase(cnt):
    """{'grey': 2, 'white': 1} -> '2 grey and 1 white'."""
    parts = [f"{n} {c}" for c, n in cnt.items()]
    return " and ".join(parts) if len(parts) < 3 else ", ".join(parts[:-1]) + " and " + parts[-1]


def values(rng, colours, harder, lo=2):
    hi = 30 if harder else 15
    return dict(zip(colours, rng.sample(range(lo, hi + 1), len(colours))))


def colour_mistakes(v, asked):
    return [(v[c], f"give the number under the {c} card") for c in v if c != asked]


# ------------------------------------------------------------------ variants
@variant(difficulty=1)
def chain(rng, harder):
    """One row has a single colour: solve it, then the next row has only one unknown colour."""
    a, b, c = rng.sample(COLOURS, 3)
    v = values(rng, [a, b, c], harder)
    rows = [[a, a, a], [a, b, b], [b, a, c]] if not harder else [[a, a, a, a], [a, b, b, b], [b, a, c, c]]
    order = [0, 1, 2]
    rng.shuffle(order)
    grid = [shuffled_row(rng, rows[i]) for i in order]
    sums = [sum(v[x] for x in line) for line in grid]
    n = len(rows[0])
    s = {i: sum(v[x] for x in rows[i]) for i in range(3)}
    nb = rows[1].count(b)
    nc = rows[2].count(c)
    text = RULES + f"\n\nWhich number is hidden under the {c} card?"
    rest = s[2] - v[a] - v[b]
    sol = (f"The row with {n} {a} cards: {a} = {s[0]} ÷ {n} = {v[a]}. "
           f"The row with {phrase(count(rows[1]))}: {nb} {b} = {s[1]} − {(n - nb) * v[a]} = {nb * v[b]}, so {b} = {v[b]}. "
           f"The last row: {nc} {c} = {s[2]} − {v[a]} − {v[b]} = {rest}, so {c} = {v[c]}.")
    mistakes = colour_mistakes(v, c) + [(rest, f"forget that there are {nc} {c} cards in the row")] if nc > 1 else colour_mistakes(v, c)
    if s[2] % n == 0:
        mistakes.append((s[2] // n, f"divide the row sum by {n} as if all the cards were the same"))
    ch, ans = numeric_choices(v[c], mistakes, rng, lo=1)
    return Question(text=text, figure=draw(grid, sums), choices=ch, answer=ans, solution=sol,
                    difficulty=1, check=row_check(grid, sums, {c: 1}, ch))


def add_rows_puzzle(rng, harder):
    """The original: rows a+2b, a+b+c, 2a+b (in any order and positions)."""
    a, b, c = rng.sample(COLOURS, 3)
    v = values(rng, [a, b, c], harder)
    rows = [[a, b, b], [a, b, c], [b, a, a]]
    order = [0, 1, 2]
    rng.shuffle(order)
    grid = [shuffled_row(rng, rows[i]) for i in order]
    sums = [sum(v[x] for x in line) for line in grid]
    return a, b, c, v, rows, grid, sums


@variant(difficulty=2)
def put_rows_together(rng, harder):
    """The original question: two rows together have 3 of each of two colours."""
    a, b, c, v, rows, grid, sums = add_rows_puzzle(rng, harder)
    s1, s2, s3 = (v[a] + 2 * v[b]), (v[a] + v[b] + v[c]), (2 * v[a] + v[b])
    pair = v[a] + v[b]
    asked = a if harder else c
    text = RULES + f"\n\nWhich number is hidden under the {asked} card?"
    sol = (f"Put the two rows without {c} together: {s1} + {s3} = {s1 + s3} for 3 {a} and 3 {b}, "
           f"so one {a} + one {b} = {s1 + s3} ÷ 3 = {pair}. ")
    if asked == c:
        sol += f"The row with {a}, {b} and {c}: {c} = {s2} − {pair} = {v[c]}."
        mistakes = colour_mistakes(v, c) + [(pair, f"stop after finding {a} + {b}")]
        if s2 % 3 == 0:
            mistakes.append((s2 // 3, "divide the row sum by 3 as if all the cards were the same"))
    else:
        sol += (f"The row with 2 {a} and 1 {b} is one {a} + one {b} + one more {a}: "
                f"{a} = {s3} − {pair} = {v[a]}.")
        mistakes = colour_mistakes(v, a) + [(pair, f"stop after finding {a} + {b}"),
                                            (s3 - s1, "take the difference of two row sums")]
    ch, ans = numeric_choices(v[asked], mistakes, rng, lo=1)
    return Question(text=text, figure=draw(grid, sums), choices=ch, answer=ans, solution=sol,
                    difficulty=2, check=row_check(grid, sums, {asked: 1}, ch))


@variant(difficulty=2)
def compare_rows(rng, harder):
    """Two rows differ in one card only: the difference of the sums is the difference of those cards."""
    a, b, c = rng.sample(COLOURS, 3)
    v = values(rng, [a, b, c], harder)
    if v[c] <= v[b]:
        v[b], v[c] = v[c], v[b]
    rows = [[a, b, b], [a, b, c], [c, c, c]]
    order = [0, 1, 2]
    rng.shuffle(order)
    grid = [shuffled_row(rng, rows[i]) for i in order]
    sums = [sum(v[x] for x in line) for line in grid]
    s1, s2, s3 = (sum(v[x] for x in r) for r in rows)
    d = s2 - s1
    text = RULES + f"\n\nWhich number is hidden under the {a} card?"
    sol = (f"The row of 3 {c} cards: {c} = {s3} ÷ 3 = {v[c]}. "
           f"The rows {s1} and {s2} are the same except one card: {b} in one, {c} in the other. "
           f"So {c} is {d} more than {b}: {b} = {v[c]} − {d} = {v[b]}. "
           f"Then {a} = {s1} − {v[b]} − {v[b]} = {v[a]}.")
    mistakes = colour_mistakes(v, a) + [(d, "take the difference of the two rows that look alike"),
                                        (s1 - v[b] - v[c], f"use {c} instead of {b} in the last step")]
    ch, ans = numeric_choices(v[a], mistakes, rng, lo=1)
    return Question(text=text, figure=draw(grid, sums), choices=ch, answer=ans, solution=sol,
                    difficulty=2, check=row_check(grid, sums, {a: 1}, ch))


@variant(difficulty=3)
def missing_column(rng, harder):
    """Twist: row sums and column sums both add up to all the cards - no colour needed."""
    k = 4 if harder else 3
    cols = rng.sample(COLOURS, k)
    v = values(rng, cols, harder)
    while True:
        grid = [[rng.choice(cols) for _ in range(3)] for _ in range(3)]
        if len({x for line in grid for x in line}) == k and all(len(set(line)) > 1 for line in grid):
            break
    rs = [sum(v[x] for x in line) for line in grid]
    cs = [sum(v[grid[r][c]] for r in range(3)) for c in range(3)]
    hide = rng.randrange(3)
    shown_cs = [s if i != hide else "?" for i, s in enumerate(cs)]
    total = sum(rs)
    text = (RULES + " The number below a column is the sum of the hidden numbers in that column."
            "\n\nWhich number belongs in place of the question mark?")
    others = [s for i, s in enumerate(cs) if i != hide]
    sol = (f"All the rows together are all nine cards: {' + '.join(map(str, rs))} = {total}. "
           f"The columns are the same nine cards, so they add up to {total} too: "
           f"? = {total} − {others[0]} − {others[1]} = {cs[hide]}. No colour needs to be found!")
    mistakes = [(total - others[0], "subtract only one of the column sums"),
                (total, "add up the row sums and stop there")]
    mistakes += [(others[0], "copy another column sum")]
    ch, ans = numeric_choices(cs[hide], mistakes, rng, lo=1)
    eqs = [(count(line), s) for line, s in zip(grid, rs)]
    eqs += [(count([grid[r][c] for r in range(3)]), cs[c]) for c in range(3) if c != hide]
    col_target = count([grid[r][hide] for r in range(3)])
    return Question(text=text, figure=draw(grid, rs, shown_cs), choices=ch, answer=ans, solution=sol,
                    difficulty=3, check=value_check(ch, int(linear_value(eqs, col_target))))


@variant(difficulty=3)
def find_the_row_sum(rng, harder):
    """Turned around: one row sum is missing - find the colours from the other rows first."""
    a, b, c, v, rows, grid, sums = add_rows_puzzle(rng, harder)
    # a fourth row with a new mix of the three colours, its sum hidden
    new = shuffled_row(rng, [c, c, a] if not harder else [c, c, b])
    target = sum(v[x] for x in new)
    pair = v[a] + v[b]
    s1, s2, s3 = (v[a] + 2 * v[b]), (v[a] + v[b] + v[c]), (2 * v[a] + v[b])
    other = a if new.count(a) else b
    sol = (f"Put the rows {s1} and {s3} together: 3 {a} and 3 {b} = {s1 + s3}, so {a} + {b} = {pair}. "
           f"Row {s2}: {c} = {s2} − {pair} = {v[c]}. "
           f"Row {s3} is {a} + {b} + {a}: {a} = {s3} − {pair} = {v[a]}, and {b} = {pair} − {v[a]} = {v[b]}. "
           f"The last row: {v[c]} + {v[c]} + {v[other]} = {target}.")
    grid4 = grid + [new]
    sums4 = sums + ["?"]
    text = RULES + "\n\nWhich number belongs in place of the question mark?"
    mistakes = [(v[c] + v[other], f"count only one {c} card"),
                (2 * v[c] + v[b if other == a else a], f"mix up {a} and {b}"),
                (s2, "copy the sum of another row")]
    ch, ans = numeric_choices(target, mistakes, rng, lo=1)
    return Question(text=text, figure=draw(grid4, sums4), choices=ch, answer=ans, solution=sol,
                    difficulty=3, check=row_check(grid, sums, count(new), ch))
