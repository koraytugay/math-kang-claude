"""2002 Q22 - in how many ways can the friends sit?

Original: Four friends go to a restaurant and sit down at a table. John always
sits at the same spot. In how many ways can the friends sit around the table?
A 3  B 4  C 6  D 24  E 25.  John is fixed; the other three fill 3 seats in
3 x 2 x 1 = 6 ways.  Answer: C.

Core skill: counting arrangements systematically - fill the places one at a time
and multiply the number of choices (3, then 2, then 1), and notice when someone
is fixed so they do not count. Children list a few by hand and miss some, or
add instead of multiply.
"""
import math

from kangaroo import Fig, Question, numeric_choices, variant

META = {
    "source": "2002 Q22",
    "skill": "Counting arrangements: fill places one by one and multiply the choices",
    "topics": ["counting", "logic"],
    "version": 2,
}

NAMES = ["John", "Anna", "Ben", "Clara", "David", "Emma", "Felix", "Grace", "Hugo", "Iris"]
WORDS = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}


def _fact(n):
    return math.factorial(n)


def _chain(n):
    """'3 × 2 × 1' for n = 3."""
    return " × ".join(str(k) for k in range(n, 0, -1))


def table_pic(n, fixed_letter, round_table=True):
    """A table with n chairs; the first chair (at the top) is marked with a letter."""
    f = Fig(10, 10, scale=8.5, margin=4)
    if round_table:
        f.circle(5, 5, 3.0, fill=None, width=1.2)
    else:
        f.rect(2, 2, 6, 6)
    for i in range(n):
        a = math.radians(90 - 360 * i / n)
        x, y = 5 + 4.3 * math.cos(a), 5 + 4.3 * math.sin(a)
        f.circle(x, y, 0.75, width=1.0)
        if i == 0:
            f.text(x, y, fixed_letter, size=9)
    return f.drawing()


@variant(difficulty=1)
def fixed_seat(rng, harder):
    """The original: one friend always takes the same chair."""
    n = rng.choice([4, 5] if harder else [3, 4, 4])
    names = rng.sample(NAMES, n)
    fixed = names[0]
    ans = _fact(n - 1)
    text = (f"{WORDS[n].capitalize()} friends, {', '.join(names[:-1])} and {names[-1]}, go to a "
            f"restaurant and sit at a table with {n} chairs. {fixed} always sits on the same "
            f"chair (marked {fixed[0]}).")
    after = "In how many different ways can the friends sit around the table?"
    sol = (f"{fixed}'s chair is fixed. The other {n - 1} friends fill the other chairs: "
           f"{_chain(n - 1)} = {ans} ways.")
    mistakes = [_fact(n), n - 1, n, _fact(n) + 1, (n - 1) * (n - 1), 2 * (n - 1)]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, figure=table_pic(n, fixed[0]), after_figure=after,
                    choices=choices, answer=ai, solution=sol)


@variant(difficulty=1)
def photo_line(rng, harder):
    """Children stand in a row for a photo - all orders."""
    n = rng.choice([4] if harder else [3, 3, 4])
    names = rng.sample(NAMES[1:], n)
    ans = _fact(n)
    text = (f"{', '.join(names[:-1])} and {names[-1]} stand in a row for a photo. "
            f"Each time they stand in a different order.")
    after = "How many different photos can they take?"
    sol = (f"{n} children can stand first, then {n - 1} are left for the second place, and so on: "
           f"{_chain(n)} = {ans}.")
    mistakes = [n, n * n, n + (n - 1) + (n - 2), _fact(n - 1), 2 * n, ans + 1]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=2)
def ends_fixed(rng, harder):
    """Two people have fixed places, the rest can swap."""
    n = rng.choice([5, 6] if harder else [4, 5])
    names = rng.sample(NAMES[1:], n)
    a, b = names[0], names[1]
    ans = _fact(n - 2)
    text = (f"{WORDS[n].capitalize()} children, {', '.join(names[:-1])} and {names[-1]}, sit on a "
            f"bench. {a} always sits at the left end and {b} always sits at the right end.")
    after = "In how many different ways can the children sit on the bench?"
    sol = (f"Only the {n - 2} children in the middle can change places: {_chain(n - 2)} = {ans} ways.")
    mistakes = [_fact(n), _fact(n - 1), n - 2, 2 * _fact(n - 2), n, (n - 2) * (n - 2)]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=2)
def outfits(rng, harder):
    """Multiply the choices: tops x bottoms (x shoes)."""
    name = rng.choice(NAMES)
    t = rng.randint(2, 5)
    b = rng.randint(2, 4)
    s = rng.randint(2, 3) if harder else 1
    ans = t * b * s
    clothes = [f"{t} different T-shirts", f"{b} different pairs of trousers"]
    if s > 1:
        clothes.append(f"{s} different pairs of shoes")
    text = (f"{name} has {', '.join(clothes[:-1])} and {clothes[-1]}. An outfit is one "
            f"T-shirt and one pair of trousers" + (" and one pair of shoes." if s > 1 else "."))
    after = "How many different outfits can " + name + " make?"
    sol = (f"Each T-shirt goes with each pair of trousers" + (" and each pair of shoes" if s > 1 else "")
           + f": {t} × {b}" + (f" × {s}" if s > 1 else "") + f" = {ans}.")
    mistakes = [t + b + s if s > 1 else t + b, t * b, t * b + s, t + b * s, ans + 1, ans * 2]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=3)
def side_by_side(rng, harder):
    """Two friends want to sit next to each other in a row."""
    n = 5 if harder else 4
    names = rng.sample(NAMES[1:], n)
    a, b = names[0], names[1]
    ans = 2 * _fact(n - 1)
    text = (f"{WORDS[n].capitalize()} children, {', '.join(names[:-1])} and {names[-1]}, sit in a "
            f"row of {n} chairs at the cinema. {a} and {b} are best friends and want to sit next to "
            f"each other.")
    after = "In how many different ways can the children sit?"
    sol = (f"Think of {a} and {b} as one block: the block and the other {n - 2} make {n - 1} things to "
           f"order, {_chain(n - 1)} = {_fact(n - 1)} ways. Inside the block {a} and {b} can swap, so "
           f"2 × {_fact(n - 1)} = {ans}.")
    mistakes = [_fact(n - 1), _fact(n), _fact(n) - ans, n - 1, 2 * (n - 1), ans + 2]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=3)
def stripes(rng, harder):
    """Colour three stripes of a flag, all different colours, from k colours."""
    k = rng.choice([5, 6] if harder else [3, 4, 4])
    name = rng.choice(NAMES)
    cols = rng.sample(["red", "blue", "green", "yellow", "white", "black", "orange"], k)
    ans = k * (k - 1) * (k - 2)
    text = (f"{name} paints a flag with three stripes: top, middle and bottom. {name} has {k} colours "
            f"({', '.join(cols[:-1])} and {cols[-1]}). All three stripes must be different colours.")
    after = "How many different flags can " + name + " paint?"
    sol = (f"Top stripe: {k} choices, middle: {k - 1}, bottom: {k - 2}. "
           f"{k} × {k - 1} × {k - 2} = {ans}.")
    mistakes = [k * k * k, 3 * k, k + (k - 1) + (k - 2), k * (k - 1), _fact(k), ans // 6 if ans % 6 == 0 else -1]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol)
