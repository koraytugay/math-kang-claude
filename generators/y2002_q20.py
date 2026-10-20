"""2002 Q20 - cubes left over when a tunnel is rebuilt into a pyramid.

Original: Robert made a tunnel using identical cubes (fig.1: a 5 x 5 frame with a
3 x 3 hole, 4 cubes long). He rearranged it into a complete pyramid (fig.2: a
5 x 5 layer, a 3 x 3 block two cubes high, a tower of 3). How many cubes from the
tunnel did he not use?  Tunnel 16 x 4 = 64, pyramid 25 + 18 + 3 = 46.
Answer: D (18).

Core skill: counting cubes in a 3-D building, including the ones you cannot see -
count one slice (a face or a layer), then multiply by how many slices there are.
Children count only the visible faces, forget the hidden middle of a layer, or
miscount the depth.
"""
from kangaroo import Question, numeric_choices, variant
from kangaroo.cubes import draw_cubes, step_pyramid, tunnel
from kangaroo.figures import Fig, column, row

META = {
    "source": "2002 Q20",
    "skill": "Counting cubes in a 3-D building, hidden ones included (slice x number of slices)",
    "topics": ["counting", "spatial", "geometry"],
    "version": 3,
}

NAMES = ["Robert", "Mia", "Leo", "Sara", "Tom", "Nina"]


def _label(drawing, text):
    f = Fig(4, 1, scale=12, margin=0)
    f.text(2, 0.5, text, size=11)
    return column([drawing, f.drawing()], gap=2)


def _tunnel(rng, harder):
    """(n, depth, cells, front) for a random tunnel."""
    n = rng.choice([5, 6] if harder else [4, 5])
    depth = rng.randint(3, 5) if harder else rng.randint(2, 4)
    cells = tunnel(n, depth)
    return n, depth, cells, len(cells) // depth


def _pyramid(rng, harder, base=None):
    """Bottom-up layers [(side, height)], sides dropping by 2, ending in a 1 x 1 or 2 x 2 top."""
    base = base or rng.choice([5, 6, 7] if harder else [4, 5])
    layers, side = [], base
    while side >= 1:
        h = rng.choice([1, 1, 2]) if side > 2 else rng.randint(1, 3)
        layers.append((side, h))
        side -= 2
    if len(layers) > 1:
        layers[0] = (layers[0][0], 1)       # a one-cube-thick base, like the original
    return layers


def _visible(n, depth, front):
    """Cubes you can count in the picture: the front, plus the top row and right column going back."""
    return front + (2 * n - 1) * (depth - 1)


def _pyr_sum(layers):
    return " + ".join(f"{s} × {s}" + (f" × {h}" if h > 1 else "") for s, h in layers)


def _pyr_mistakes(layers):
    """Pyramid counts from typical errors."""
    total = sum(s * s * h for s, h in layers)
    return [sum(s * h for s, h in layers),                 # counted only the front row of each layer
            sum(s * s for s, h in layers),                 # ignored the heights
            layers[0][0] ** 2 + sum(s * h for s, h in layers[1:]),  # only the front row above the base
            total - layers[0][0] ** 2 + layers[0][0]]


@variant(difficulty=1)
def count_tunnel(rng, harder):
    """How many cubes is the tunnel made of?"""
    n, depth, cells, front = _tunnel(rng, harder)
    name = rng.choice(NAMES)
    fig = draw_cubes(cells, scale=14 if n <= 5 else 12)
    total = front * depth
    text = (f"{name} built this tunnel out of identical cubes. The hole goes straight through "
            f"from the front to the back.")
    after = "How many cubes did " + name + " use?"
    sol = (f"The front has {n} × {n} − {n-2} × {n-2} = {front} cubes. The tunnel is {depth} cubes long, "
           f"so {front} × {depth} = {total}.")
    mistakes = [n * n * depth, front, front * (depth - 1), front * (depth + 1),
                _visible(n, depth, front), n * 4 * depth]
    choices, ai = numeric_choices(total, mistakes, rng, lo=1)
    return Question(text=text, figure=fig, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=1)
def tunnel_to_pyramid(rng, harder):
    """The original: tunnel taken apart, pyramid built, how many cubes are left over?"""
    for _ in range(200):
        n, depth, cells, front = _tunnel(rng, harder)
        layers = _pyramid(rng, harder)
        t = front * depth
        p = sum(s * s * h for s, h in layers)
        if 4 <= t - p <= 40:
            break
    else:
        raise RuntimeError("no tunnel/pyramid pair found")
    name = rng.choice(NAMES)
    fig = row([_label(draw_cubes(cells, scale=11), "fig. 1"),
               _label(draw_cubes(step_pyramid(layers), scale=11), "fig. 2")], gap=26)
    ans = t - p
    text = (f"{name} made a tunnel out of identical cubes (fig. 1). Then {name} took it apart and "
            f"built a complete pyramid (fig. 2) with some of the cubes. Nothing is hollow inside.")
    after = f"How many cubes from the tunnel were <b>not</b> used for the pyramid?"
    sol = (f"Tunnel: {front} cubes in the front, {depth} long: {front} × {depth} = {t}. "
           f"Pyramid: {_pyr_sum(layers)} = {p}. Left over: {t} − {p} = {ans}.")
    mistakes = [t - m for m in _pyr_mistakes(layers)] + [ans + front, ans - front, p - front * (depth - 1)]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, figure=fig, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=2)
def count_pyramid(rng, harder):
    """Count a step pyramid - most of its cubes are hidden."""
    layers = _pyramid(rng, harder)
    name = rng.choice(NAMES)
    fig = draw_cubes(step_pyramid(layers), scale=11)
    total = sum(s * s * h for s, h in layers)
    text = (f"{name} built this pyramid out of identical cubes. Every layer is a full square, "
            f"with no holes hidden inside.")
    after = "How many cubes are in the pyramid?"
    sol = (f"Count layer by layer, from the bottom: {_pyr_sum(layers)} = {total}.")
    choices, ai = numeric_choices(total, _pyr_mistakes(layers) + [total - 1, total + layers[0][0]], rng, lo=1)
    return Question(text=text, figure=fig, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=2)
def fill_the_hole(rng, harder):
    """How many cubes are needed to fill the tunnel and make a solid block?"""
    n, depth, cells, front = _tunnel(rng, harder)
    name = rng.choice(NAMES)
    fig = draw_cubes(cells, scale=14 if n <= 5 else 12)
    hole = (n - 2) * (n - 2)
    ans = hole * depth
    text = (f"{name} built this tunnel out of identical cubes. The hole goes straight through "
            f"from the front to the back. {name} wants to fill the hole completely, "
            f"so that the tunnel becomes one solid block.")
    after = "How many more cubes are needed?"
    sol = (f"The hole is {n-2} × {n-2} = {hole} cubes in the front and goes {depth} cubes back: "
           f"{hole} × {depth} = {ans}.")
    mistakes = [hole, hole * (depth - 1), hole * (depth + 1), n * n * depth, front * depth,
                (n - 2) * depth, n * n * depth - ans + hole]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, figure=fig, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=3)
def not_enough(rng, harder):
    """Reverse: the pyramid needs more cubes than the tunnel has."""
    for _ in range(200):
        n, depth, cells, front = _tunnel(rng, harder)
        layers = _pyramid(rng, harder, base=rng.choice([5, 6, 7]))
        t = front * depth
        p = sum(s * s * h for s, h in layers)
        if 3 <= p - t <= 40:
            break
    else:
        raise RuntimeError("no tunnel/pyramid pair found")
    name = rng.choice(NAMES)
    fig = row([_label(draw_cubes(cells, scale=10), "tunnel"),
               _label(draw_cubes(step_pyramid(layers), scale=10), "pyramid")], gap=26)
    ans = p - t
    text = (f"{name} has the tunnel on the left. {name} takes it apart to build the pyramid on the "
            f"right, but there are not enough cubes. Nothing is hollow inside the pyramid.")
    after = "How many more cubes does " + name + " need?"
    sol = (f"Tunnel: {front} × {depth} = {t} cubes. Pyramid: {_pyr_sum(layers)} = {p}. "
           f"Missing: {p} − {t} = {ans}.")
    mistakes = [m - t for m in _pyr_mistakes(layers)] + [ans + front, ans - front, p - front]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, figure=fig, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=3)
def longer_tunnel(rng, harder):
    """The tunnel is made longer with the same front - how many cubes in total now?"""
    n, depth, cells, front = _tunnel(rng, harder)
    extra = rng.randint(2, 4)
    name = rng.choice(NAMES)
    fig = draw_cubes(cells, scale=14 if n <= 5 else 12)
    new = depth + extra
    ask_more = rng.random() < 0.5
    ans = front * extra if ask_more else front * new
    text = (f"{name}'s tunnel is {depth} cubes long. The hole goes straight through. "
            f"{name} makes it longer by adding more cubes at the back in the same pattern, until "
            f"it is {new} cubes long.")
    after = ("How many cubes does " + name + " have to add?" if ask_more else
             "How many cubes are in the long tunnel?")
    sol = (f"Each slice of the tunnel has {n} × {n} − {n-2} × {n-2} = {front} cubes. "
           + (f"{extra} new slices: {front} × {extra} = {ans}." if ask_more else
              f"{new} slices: {front} × {new} = {ans}."))
    mistakes = ([n * n * extra, front * new, front * (extra + 1), front * (extra - 1), extra * n]
                if ask_more else
                [n * n * new, front * depth, front * extra, front * depth + extra, front * (new + 1)])
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, figure=fig, after_figure=after, choices=choices, answer=ai, solution=sol)
