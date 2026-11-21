"""2026 Q14 (Canada, Grade 3-4) - towers of cubes: which ones can you see from the front?

Original: Selina built towers from cubes on a square grid. From above, each number shows the
tower's height (4 x 4 grid, rows from back to front: 4 8 8 6 / 2 6 6 8 / 6 4 2 4 / 2 2 4 6).
From the front (in the arrows' direction) she cannot see towers hiding behind taller ones.
How many towers can she see from the front?  (A) 8  (B) 9  (C) 10  (D) 11  (E) 12.
Column by column from the front: 2,6,2,4 -> 2 towers; 2,4,6,8 -> 4; 4,2,6,8 -> 3; 6,4,8,6 -> 2.
2 + 4 + 3 + 2 = 11.  Answer: D.  (Answer key for 2026 is our own: solved by us.)

Core skill: look along one line of towers at a time, from the near end: a tower can be seen only
if it is taller than every tower in front of it in that line (so remember the tallest so far).
Children count all towers, one per column, or compare each tower only with its next neighbour.

Our grids never have a tower as tall as the tallest one in front of it, so "hidden" is clear.
"""
import math

from reportlab.lib import colors

from kangaroo import Fig, Question, numeric_choices, value_check, variant

META = {
    "source": "set-03/by_level/Grade_03-04/2026 Q14",
    "skill": "Look along one line of towers at a time, starting at your end: remember the tallest tower so far; "
             "a tower is seen only if it is taller than that",
    "topics": ["spatial", "counting", "logic"],
    "keywords": ["hidden towers", "view from the front", "taller ones"],
    "sticker": ("🔭", "Tower spotter"),   # earned when this skill is solid (website)
    "version": 1,
}

PEOPLE = ["Selina", "Mia", "Lena", "Tom", "Ben", "Omar", "Nora", "Leo"]
# direction the viewer looks in (= the way the arrows point) -> the lines of cells, nearest cell first
DIRS = ("up", "down", "right", "left")
OPPOSITE = {"up": "down", "down": "up", "right": "left", "left": "right"}
WHERE = {"up": "the bottom of the picture", "down": "the top of the picture",
         "right": "the left of the picture", "left": "the right of the picture"}


# ------------------------------------------------------------------ the model
def lines(n, d):
    """Lines of sight as lists of (row, col), nearest to the viewer first. Row 0 is the top of the picture."""
    if d == "up":
        return [[(r, c) for r in range(n - 1, -1, -1)] for c in range(n)]
    if d == "down":
        return [[(r, c) for r in range(n)] for c in range(n)]
    if d == "right":
        return [[(r, c) for c in range(n)] for r in range(n)]
    return [[(r, c) for c in range(n - 1, -1, -1)] for r in range(n)]


def heights(g, line):
    return [g[r][c] for r, c in line]


def seen_levels(g, d):
    """Check: set of towers (r, c) seen from direction d, and the number of cube faces seen.

    Worked out level by level (like looking at the cubes): on level L, the first tower in each line
    that is at least L cubes high shows its cube there. A tower is seen if it shows at least one cube.
    """
    n = len(g)
    towers, faces = set(), 0
    for line in lines(n, d):
        for level in range(1, max(heights(g, line)) + 1):
            first = next(cell for cell in line if g[cell[0]][cell[1]] >= level)
            towers.add(first)
            faces += 1
    return towers, faces


def seen_cells(g, d):
    """Set of towers (r, c) seen from direction d (taller than all in front), and the cube faces seen."""
    towers, faces = set(), 0
    for line in lines(len(g), d):
        best = 0
        for r, c in line:
            if g[r][c] > best:
                towers.add((r, c))
                best = g[r][c]
        faces += best
    return towers, faces


def clear(g, d):
    """No tower is exactly as tall as the tallest one in front of it (so 'hidden' is never in doubt)."""
    for line in lines(len(g), d):
        hs = heights(g, line)
        if any(hs[k] == max(hs[:k]) for k in range(1, len(hs))):
            return False
    return True


def adjacent_count(g, d):
    """The mistake: a tower counts as seen if it is taller than the one right in front of it."""
    total = 0
    for line in lines(len(g), d):
        hs = heights(g, line)
        total += 1 + sum(hs[k] > hs[k - 1] for k in range(1, len(hs)))
    return total


def make_grid(rng, n, dirs, hmax, want=None):
    for _ in range(20000):
        g = [[rng.randint(1, hmax) for _ in range(n)] for _ in range(n)]
        if not all(clear(g, d) for d in dirs):
            continue
        counts = [len(seen_cells(g, d)[0]) for d in dirs]
        if any(not (n + 2 <= k <= n * n - 3) for k in counts):
            continue
        if len(dirs) == 1 and (adjacent_count(g, dirs[0]) == counts[0]):
            continue                                       # the neighbour mistake must be a different number
        if want and not want(g):
            continue
        return g
    raise RuntimeError("no grid found")


# ------------------------------------------------------------------ picture
ARROW = colors.black


def _arrow(f, x, y, d, ln=0.75):
    """An arrow centred at (x, y) pointing in direction d."""
    dx, dy = {"up": (0, 1), "down": (0, -1), "right": (1, 0), "left": (-1, 0)}[d]
    tail = (x - dx * ln / 2, y - dy * ln / 2)
    tip = (x + dx * ln / 2, y + dy * ln / 2)
    f.line(tail, tip, width=1.1)
    h, w = 0.28, 0.17
    base = (tip[0] - dx * h, tip[1] - dy * h)
    px, py = -dy, dx
    f.poly([tip, (base[0] + px * w, base[1] + py * w), (base[0] - px * w, base[1] - py * w)],
           fill=colors.black, width=0.6)


def towers_pic(g, dirs, max_px=125):
    n = len(g)
    pad = 1.0
    left = pad if "right" in dirs else 0
    right = pad if "left" in dirs else 0
    bottom = pad if "up" in dirs else 0
    top = pad if "down" in dirs else 0
    f = Fig(n + left + right, n + bottom + top, max_px=max_px, margin=6)
    ox, oy = left, bottom
    for r in range(n):
        for c in range(n):
            x, y = ox + c, oy + n - 1 - r
            f.rect(x, y, 1, 1, fill=colors.Color(0.96, 0.96, 0.96), width=0.8)
            f.text(x + 0.5, y + 0.5, str(g[r][c]), size=11)
    for d in dirs:
        for k in range(n):
            if d == "up":
                _arrow(f, ox + k + 0.5, oy - pad / 2, d)
            elif d == "down":
                _arrow(f, ox + k + 0.5, oy + n + pad / 2, d)
            elif d == "right":
                _arrow(f, ox - pad / 2, oy + n - 1 - k + 0.5, d)
            else:
                _arrow(f, ox + n + pad / 2, oy + n - 1 - k + 0.5, d)
    return f.drawing()


# ------------------------------------------------------------------ text helpers
def _word(d):
    return "column" if d in ("up", "down") else "row"


def _plural(k, one, many):
    return f"{k} {one if k == 1 else many}"


def _look(name, d):
    if d == "up":
        return f"{name} looks at the towers from the front (in the arrows' direction)."
    return f"{name} looks at the towers in the direction of the arrows."


def _intro(name, d):
    return (f"{name} built towers from cubes on a square grid. From above, each number shows the tower's height. "
            f"{_look(name, d)} {name} cannot see towers hiding behind taller ones.")


def _line_story(g, d, show_faces=False):
    """'Column 1: 2, 6, 2, 4 -> sees 2 towers' for every line (heights listed nearest first)."""
    n = len(g)
    out = []
    for k, line in enumerate(lines(n, d), 1):
        hs = heights(g, line)
        best, vis = 0, []
        for h in hs:
            if h > best:
                vis.append(h)
                best = h
        listing = ", ".join(map(str, hs))
        if show_faces:
            out.append(f"{_word(d)} {k}: {listing} → tallest {best}, so {best} cubes")
        else:
            out.append(f"{_word(d)} {k}: {listing} → {_plural(len(vis), 'tower', 'towers')}")
    return "; ".join(out)


def _how(d):
    return ("Go along each " + _word(d) + f" starting from {WHERE[d]} and remember the tallest tower so far: "
            "a tower is seen only if it is taller than that.")


def _count_mistakes(g, d, seen):
    n = len(g)
    return [(n, f"count only one tower in each {_word(d)}"),
            (n * n, "count all the towers"),
            (len(seen_cells(g, OPPOSITE[d])[0]), "look from the other side"),
            (adjacent_count(g, d), "compare each tower only with the one right in front of it")]


# ------------------------------------------------------------------ variants
@variant(difficulty=1)
def front_count(rng, harder):
    """The original: how many towers can she see from the front?"""
    n = 5 if harder else 4
    name = rng.choice(PEOPLE)
    g = make_grid(rng, n, ["up"], 9 if harder else 8)
    seen = len(seen_cells(g, "up")[0])
    text = _intro(name, "up") + f"\n\nHow many towers can {name} see from the front?"
    sol = _how("up") + " " + _line_story(g, "up") + f". Together: {seen} towers."
    choices, ai = numeric_choices(seen, _count_mistakes(g, "up", seen), rng, lo=1, order="asc")
    return Question(text=text, figure=towers_pic(g, ["up"]), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, len(seen_levels(g, "up")[0])))


@variant(difficulty=2)
def other_side(rng, harder):
    """The arrows come from another side: lines are rows, or the view is from the back."""
    n = 5 if harder else 4
    name = rng.choice(PEOPLE)
    d = rng.choice(["down", "right", "left"])
    g = make_grid(rng, n, [d], 9 if harder else 8)
    seen = len(seen_cells(g, d)[0])
    text = _intro(name, d) + f"\n\nHow many towers can {name} see?"
    sol = _how(d) + " " + _line_story(g, d) + f". Together: {seen} towers."
    choices, ai = numeric_choices(seen, _count_mistakes(g, d, seen), rng, lo=1, order="asc")
    return Question(text=text, figure=towers_pic(g, [d]), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, len(seen_levels(g, d)[0])))


@variant(difficulty=2)
def hidden_count(rng, harder):
    """Reverse: how many towers are hidden (she cannot see)?"""
    n = 5 if harder else 4
    name = rng.choice(PEOPLE)
    d = rng.choice(["up", "up", "down", "right", "left"])
    g = make_grid(rng, n, [d], 9 if harder else 8)
    seen = len(seen_cells(g, d)[0])
    hidden = n * n - seen
    text = _intro(name, d) + f"\n\nHow many towers can {name} <b>not</b> see?"
    sol = (_how(d) + " " + _line_story(g, d) + f". {name} sees {seen} of the {n * n} towers, "
           f"so {n * n - seen} are hidden.")
    mistakes = [(seen, "count the towers you can see"),
                (n * n - len(seen_cells(g, OPPOSITE[d])[0]), "look from the other side"),
                (n * n - adjacent_count(g, d), "compare each tower only with the one right in front of it"),
                (n * n - n, "think only one tower in each " + _word(d) + " is seen")]
    choices, ai = numeric_choices(hidden, mistakes, rng, lo=1, order="asc")
    all_n = {(r, c) for r in range(n) for c in range(n)}
    return Question(text=text, figure=towers_pic(g, [d]), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, len(all_n - seen_levels(g, d)[0])))


@variant(difficulty=3)
def cube_faces(rng, harder):
    """Twist: not the towers but the cubes (square faces) she can see."""
    n = 5 if harder else 4
    name = rng.choice(PEOPLE)
    d = rng.choice(["up", "up", "down", "right", "left"])
    g = make_grid(rng, n, [d], 9 if harder else 8)
    towers, faces = seen_cells(g, d)
    vis_height = sum(g[r][c] for r, c in towers)
    text = (_intro(name, d) + " Each cube has one square face turned towards " + name + "."
            + f"\n\nHow many square faces of cubes can {name} see?")
    sol = ("A tower you can see shows only the part that sticks up over the towers in front of it, and in a "
           "line you see as many cubes high as the tallest tower: " + _line_story(g, d, show_faces=True)
           + f". Together: {faces} faces.")
    mistakes = [(len(towers), "count the towers you can see instead of their cubes"),
                (vis_height, "count all the cubes of the towers you can see"),
                (sum(sum(row) for row in g), "count all the cubes"),
                (adjacent_count(g, d), "count the towers you can see by comparing neighbours only")]
    choices, ai = numeric_choices(faces, mistakes, rng, lo=1, order="asc")
    return Question(text=text, figure=towers_pic(g, [d]), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, seen_levels(g, d)[1]))


@variant(difficulty=3)
def front_or_back(rng, harder):
    """Twist: one friend looks from the front, another from the back: towers seen by at least one."""
    n = 5 if harder else 4
    name = rng.choice(PEOPLE)
    other = rng.choice([p for p in PEOPLE if p != name])
    g = make_grid(rng, n, ["up", "down"], 9 if harder else 8)
    front, back = seen_cells(g, "up")[0], seen_cells(g, "down")[0]
    union = front | back
    text = (f"{name} and {other} stand on opposite sides of towers built from cubes on a square grid. "
            "From above, each number shows the tower's height. "
            f"{name} looks from the front and {other} from the back (in the arrows' directions). "
            "Nobody can see towers hiding behind taller ones."
            f"\n\nHow many towers can be seen by at least one of them?")
    sol = (f"First the front: {_line_story(g, 'up')}. That is {len(front)} towers. "
           f"Then the back (the other way along each column): {_line_story(g, 'down')}. "
           f"That is {len(back)} towers. Some towers are seen from both sides, count them once: {len(union)} towers.")
    mistakes = [(len(front) + len(back), "add the two numbers, so towers seen by both are counted twice"),
                (max(len(front), len(back)), "take the better view of the two"),
                (len(front & back), "count only the towers both can see"),
                (n * n, "count all the towers")]
    choices, ai = numeric_choices(len(union), mistakes, rng, lo=1, order="asc")
    all_towers = {(r, c) for r in range(n) for c in range(n)}
    return Question(text=text, figure=towers_pic(g, ["up", "down"]), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, len(seen_levels(g, 'up')[0] | seen_levels(g, 'down')[0])))
