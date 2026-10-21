"""2007 Q14 - how many more cubes fit into the aquarium?

Original: Daniella has a cube-shaped aquarium with edges 3 dm. She has put some
cubes with edges 1 dm inside (10 of them, some hidden behind others, see the
picture). At most how many more such cubes can she put in?
A 9  B 13  C 17  D 21  E 27.  The aquarium holds 3 x 3 x 3 = 27; 27 - 10 = 17.
Answer: C.

Core skill: the space in a box is length x width x height cubes; the cubes
already inside must be counted including the hidden ones (every cube stands on
the floor or on another cube), then subtract.
"""
from kangaroo import Question, numeric_choices, value_check, variant
from kangaroo.cubes import draw_cubes

META = {
    "source": "set-03/by_level/Grade_03-04/2007 Q14",
    "skill": "Space in a box = length × width × height; count hidden cubes; subtract",
    "topics": ["counting", "spatial", "geometry"],
    "version": 2,
}

NAMES = ["Daniella", "Mia", "Leo", "Sara", "Tom", "Nina"]


def heights(rng, a, b, c, fill):
    """Column heights on an a x b floor (x right, y back), stacked in the back-left corner:
    never taller towards the front or to the right, so every column top can be seen."""
    for _ in range(500):
        h = [[0] * b for _ in range(a)]
        for x in range(a):
            for y in range(b - 1, -1, -1):
                cap = c
                if x > 0:
                    cap = min(cap, h[x - 1][y])
                if y < b - 1:
                    cap = min(cap, h[x][y + 1])
                h[x][y] = rng.randint(0, cap) if (x, y) != (0, b - 1) else rng.randint(1, c)
        total = sum(map(sum, h))
        if fill[0] <= total <= fill[1]:
            return h
    raise RuntimeError("no stack found")


def cells_of(h):
    return {(x, y, z) for x, col in enumerate(h) for y, n in enumerate(col) for z in range(n)}


def empty_places(h, a, b, c, levels=None):
    """Answer checks: go through every place in the box (only the lowest `levels` layers if given)
    and count the ones without a cube."""
    cells = cells_of(h)
    return sum((x, y, z) not in cells for x in range(a) for y in range(b) for z in range(levels or c))


def _pic(h, box):
    s = 22 if max(box) <= 3 else 19
    return draw_cubes(cells_of(h), scale=s, box=box)


def _hidden(h):
    """Cubes not visible at all: below another cube and with cubes in front and to the right."""
    cells = cells_of(h)
    return sum(1 for (x, y, z) in cells
               if (x, y, z + 1) in cells and (x, y - 1, z) in cells and (x + 1, y, z) in cells)


@variant(difficulty=1)
def how_many_more(rng, harder):
    """The original."""
    n = 4 if harder else 3
    h = heights(rng, n, n, n, (n * n // 2 + 2, n ** 3 // 2))
    placed = sum(map(sum, h))
    ans = n ** 3 - placed
    name = rng.choice(NAMES)
    text = (f"{name} has a glass aquarium shaped like a cube, {n} dm long, {n} dm wide and {n} dm tall. "
            f"{name} has started to put cubes with edges of 1 dm into it, as in the picture. Every cube "
            f"stands on the bottom or on another cube.")
    after = f"At most how many more such cubes can {name} put into the aquarium?"
    sol = (f"The aquarium holds {n} × {n} × {n} = {n ** 3} cubes. There are already {placed} inside "
           f"(count column by column, also the hidden ones). {n ** 3} − {placed} = {ans}.")
    seen = placed - _hidden(h)
    mistakes = [n ** 3 - seen,            # forgot the hidden cubes
                placed, n ** 3, ans + 1, ans - 1]
    choices, ai = numeric_choices(ans, [m for m in mistakes if m > 0], rng, lo=1)
    return Question(text=text, figure=_pic(h, (n, n, n)), after_figure=after, choices=choices,
                    answer=ai, solution=sol,
                    check=value_check(choices, empty_places(h, n, n, n)))


@variant(difficulty=1)
def count_inside(rng, harder):
    """How many cubes are inside already? Some are hidden."""
    n = 4 if harder else 3
    h = heights(rng, n, n, n, (6, n ** 3 // 2))
    placed = sum(map(sum, h))
    name = rng.choice(NAMES)
    text = (f"{name} puts cubes into a glass box, as in the picture. Every cube stands on the bottom "
            f"or on another cube.")
    after = "How many cubes are in the box?"
    cols = [n for col in h for n in col if n]
    sol = f"Count each column from the bottom: {' + '.join(map(str, cols))} = {placed}."
    seen = placed - _hidden(h)
    mistakes = [seen, len(cols), placed + 1, placed - 1, placed + 2]
    choices, ai = numeric_choices(placed, [m for m in mistakes if m != placed], rng, lo=1)
    return Question(text=text, figure=_pic(h, (n, n, n)), after_figure=after, choices=choices,
                    answer=ai, solution=sol,
                    check=value_check(choices, len(cells_of(h))))


@variant(difficulty=2)
def long_box(rng, harder):
    """A box that is not a cube."""
    a, b, c = (rng.randint(3, 5), rng.randint(2, 3), rng.randint(2, 3)) if not harder else \
              (rng.randint(4, 5), rng.randint(3, 4), rng.randint(3, 4))
    vol = a * b * c
    h = heights(rng, a, b, c, (4, vol // 2))
    placed = sum(map(sum, h))
    ans = vol - placed
    name = rng.choice(NAMES)
    text = (f"{name}'s box is {a} cubes long, {b} cubes deep and {c} cubes tall. Some cubes are already "
            f"inside, as in the picture. Every cube stands on the bottom or on another cube.")
    after = "How many more cubes fit into the box?"
    sol = f"The box holds {a} × {b} × {c} = {vol} cubes. {placed} are inside, so {vol} − {placed} = {ans} more."
    mistakes = [vol - (placed - _hidden(h)),      # forgot the hidden cubes
                vol, a * b - placed if a * b > placed else -1, ans + 1, ans - 1]
    choices, ai = numeric_choices(ans, [m for m in mistakes if m > 0 and m != ans], rng, lo=1)
    return Question(text=text, figure=_pic(h, (a, b, c)), after_figure=after, choices=choices,
                    answer=ai, solution=sol,
                    check=value_check(choices, empty_places(h, a, b, c)))


@variant(difficulty=2)
def bottom_layer(rng, harder):
    """How many more cubes to cover the whole bottom?"""
    n = 4 if harder else 3
    h = heights(rng, n, n, n, (5, n ** 3 // 2))
    on_floor = sum(1 for col in h for k in col if k)
    placed = sum(map(sum, h))
    ans = n * n - on_floor
    name = rng.choice(NAMES)
    text = (f"{name} puts cubes into a glass box, as in the picture. Every cube stands on the bottom "
            f"or on another cube. Now {name} wants to cover the whole bottom of the box with one layer of cubes.")
    after = "How many more cubes are needed for that?"
    sol = (f"The bottom has {n} × {n} = {n * n} places. {on_floor} of them already have a column of cubes. "
           f"{n * n} − {on_floor} = {ans}.")
    mistakes = [n * n - placed if n * n > placed else -1, n ** 3 - placed, on_floor, ans + 1, ans - 1]
    choices, ai = numeric_choices(ans, [m for m in mistakes if m >= 0 and m != ans], rng, lo=0)
    return Question(text=text, figure=_pic(h, (n, n, n)), after_figure=after, choices=choices,
                    answer=ai, solution=sol,
                    check=value_check(choices, empty_places(h, n, n, n, levels=1)))


@variant(difficulty=3)
def two_layers(rng, harder):
    """How many more cubes until the bottom two layers are full?"""
    n = 4 if harder else 3
    h = heights(rng, n, n, n, (6, n ** 3 // 2))
    low = sum(min(k, 2) for col in h for k in col)
    ans = 2 * n * n - low
    placed = sum(map(sum, h))
    name = rng.choice(NAMES)
    text = (f"{name} puts cubes into a glass box, as in the picture. Every cube stands on the bottom "
            f"or on another cube. {name} wants the two bottom layers to be completely full.")
    after = "How many more cubes are needed for that?"
    sol = (f"Two layers hold 2 × {n} × {n} = {2 * n * n} cubes. In those two layers there are already "
           f"{low} cubes (columns count at most 2 each). {2 * n * n} − {low} = {ans}.")
    mistakes = [2 * n * n - placed if 2 * n * n > placed else -1, n * n - low if n * n > low else -1,
                ans + 1, ans - 1, n ** 3 - placed]
    choices, ai = numeric_choices(ans, [m for m in mistakes if m > 0 and m != ans], rng, lo=1)
    return Question(text=text, figure=_pic(h, (n, n, n)), after_figure=after, choices=choices,
                    answer=ai, solution=sol,
                    check=value_check(choices, empty_places(h, n, n, n, levels=2)))
