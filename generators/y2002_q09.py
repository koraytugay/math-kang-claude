"""2002 Q9 - balance: how many oranges does a melon weigh?

Original: one plate has 6 oranges, the other 2 melons. When one more melon
(like the others) is put on the orange plate, the balance is level.
6 oranges + 1 melon = 2 melons, so 1 melon = 6 oranges.  Answer: E.

Core skill: reasoning with a balance - taking the same thing off both sides,
substituting one kind of object for another, and turning a balance into a
"1 X = n Y" fact.
"""
from kangaroo import Question, numeric_choices, variant
from kangaroo.figures import column, row
from kangaroo.pictures import balance, legend

META = {
    "source": "2002 Q9",
    "skill": "Balance scales: remove equal things from both sides, substitute, scale up",
    "topics": ["logic", "arithmetic", "balance"],
    "version": 1,
}

# (small, big) object names: singular, plural
PAIRS = [
    (("orange", "oranges"), ("melon", "melons")),
    (("apple", "apples"), ("pumpkin", "pumpkins")),
    (("plum", "plums"), ("pineapple", "pineapples")),
    (("marble", "marbles"), ("ball", "balls")),
    (("nut", "nuts"), ("coconut", "coconuts")),
]
# (big, medium, small) for chains
TRIPLES = [
    (("pumpkin", "pumpkins"), ("melon", "melons"), ("orange", "oranges")),
    (("watermelon", "watermelons"), ("pineapple", "pineapples"), ("apple", "apples")),
    (("bowling ball", "bowling balls"), ("football", "footballs"), ("tennis ball", "tennis balls")),
]


def n_of(k, names):
    return f"{k} {names[0] if k == 1 else names[1]}"


@variant(difficulty=1)
def one_more_balances(rng, harder):
    """The original: adding r big items to the small side makes it level."""
    (sm, bg) = rng.choice(PAIRS)
    q = rng.choice([2, 3, 3, 4] if harder else [2, 2, 3])
    r = rng.randint(1, q - 1)
    d = q - r
    m = rng.randint(2, 9 if harder else 6)
    a = m * d
    fig = balance(["dot"] * a, ["ball"] * q, tilt=1,
                  legend=[("dot", sm[0]), ("ball", bg[0])], scale=12)
    more = "one more" if r == 1 else f"{r} more"
    text = (f"On one plate of a balance there are {a} {sm[1]} and on the other there are "
            f"{q} {bg[1]}. When we put {more} {bg[0] if r == 1 else bg[1]}, exactly like the others, "
            f"on the plate with the {sm[1]}, the balance is level.")
    after = f"One {bg[0]} weighs the same as how many {sm[1]}?"
    sol = (f"Take {r} {bg[0] if r == 1 else bg[1]} off both plates: {a} {sm[1]} balance "
           f"{q} − {r} = {d} {bg[0] if d == 1 else bg[1]}"
           + (f". So one {bg[0]} = {a} {sm[1]}." if d == 1 else
              f". So one {bg[0]} = {a} ÷ {d} = {m} {sm[1]}."))
    mistakes = [a, a // q if a % q == 0 else -1, a // (q + r) if a % (q + r) == 0 else -1,
                a + r, m + 1, m - 1, q, a - r, 2 * m]
    choices, ai = numeric_choices(m, mistakes, rng, unit=sm, lo=1)
    return Question(text=text, figure=fig, after_figure=after, choices=choices, answer=ai,
                    solution=sol)


@variant(difficulty=2)
def both_sides(rng, harder):
    """Both kinds of object on both plates - remove what is common."""
    (sm, bg) = rng.choice(PAIRS)
    d = rng.choice([1, 2] if harder else [1, 1, 2])
    m = rng.randint(2, 6 if harder else 4)
    a2 = rng.randint(1, 2)
    a1 = a2 + d
    b1 = rng.randint(1, 3)
    b2 = b1 + m * d
    if harder and rng.random() < 0.5:     # swap sides for variety
        L, R = (["ball"] * a2 + ["dot"] * b2), (["ball"] * a1 + ["dot"] * b1)
        lt = f"{n_of(a2, bg)} and {n_of(b2, sm)}"
        rt = f"{n_of(a1, bg)} and {n_of(b1, sm)}"
    else:
        L, R = (["ball"] * a1 + ["dot"] * b1), (["ball"] * a2 + ["dot"] * b2)
        lt = f"{n_of(a1, bg)} and {n_of(b1, sm)}"
        rt = f"{n_of(a2, bg)} and {n_of(b2, sm)}"
    fig = balance(L, R, tilt=0, legend=[("dot", sm[0]), ("ball", bg[0])], scale=12)
    text = f"The balance is level: {lt} on one plate, {rt} on the other."
    after = f"One {bg[0]} weighs the same as how many {sm[1]}?"
    sol = (f"Take {n_of(a2, bg)} and {n_of(b1, sm)} off both plates. Left: "
           f"{n_of(d, bg)} = {n_of(b2 - b1, sm)}"
           + (f"." if d == 1 else f", so one {bg[0]} = {b2 - b1} ÷ {d} = {m}."))
    mistakes = [b2, b2 - b1, b1 + b2, m + 1, (b2 - b1) // a1 if (b2 - b1) % a1 == 0 else -1,
                b2 // a1 if b2 % a1 == 0 else -1, m * 2, m - 1]
    choices, ai = numeric_choices(m, mistakes, rng, unit=sm, lo=1)
    return Question(text=text, figure=fig, after_figure=after, choices=choices, answer=ai,
                    solution=sol)


@variant(difficulty=2)
def chain(rng, harder):
    """Two balances: big = n medium, medium = k small. Swap twice."""
    big, med, sml = rng.choice(TRIPLES)
    n = rng.randint(2, 3)
    k = rng.randint(2, 4 if harder else 3)
    c = rng.choice([2, 3]) if harder else 1
    b1 = balance(["ball"], ["box"] * n, scale=10)
    b2 = balance(["box"], ["dot"] * k, scale=10)
    fig = column([row([b1, b2], gap=24), legend([("ball", big[0]), ("box", med[0]), ("dot", sml[0])])], gap=4)
    text = (f"The two balances are level. One {big[0]} weighs as much as {n} {med[1]}, "
            f"and one {med[0]} weighs as much as {k} {sml[1]}.")
    after = f"How many {sml[1]} weigh as much as {n_of(c, big)}?"
    ans = c * n * k
    sol = (f"One {big[0]} = {n} {med[1]} = {n} × {k} = {n*k} {sml[1]}"
           + (f"; {c} {big[1]} = {c} × {n*k} = {ans} {sml[1]}." if c > 1 else "."))
    mistakes = [n + k, c * (n + k), c * n, c * k, n * k, ans + c, n * k + 1]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, figure=fig, after_figure=after, choices=choices, answer=ai,
                    solution=sol)


@variant(difficulty=3)
def grams(rng, harder):
    """From a balance fact to real weights."""
    (sm, bg) = rng.choice(PAIRS[:3])
    k = rng.randint(2, 5)
    a = rng.randint(1, 3)
    b = rng.randint(1, 4)
    w = rng.choice([50, 100, 150, 200] if not harder else [75, 120, 125, 150, 250])
    units = a * k + b
    W = units * w
    fig = balance(["ball"], ["dot"] * k, legend=[("dot", sm[0]), ("ball", bg[0])], scale=12)
    ask_big = rng.random() < 0.4
    text = (f"The balance shows that one {bg[0]} weighs as much as {k} {sm[1]}. "
            f"{n_of(a, bg).capitalize()} and {n_of(b, sm)} weigh {W} g altogether.")
    after = f"How much does one {bg[0] if ask_big else sm[0]} weigh?"
    ans = k * w if ask_big else w
    sol = (f"Swap each {bg[0]} for {k} {sm[1]}: {a} × {k} + {b} = {units} {sm[1]} weigh {W} g. "
           f"One {sm[0]}: {W} ÷ {units} = {w} g"
           + (f"; one {bg[0]}: {k} × {w} = {k*w} g." if ask_big else "."))
    wrong = [W // (a + b) if W % (a + b) == 0 else -1, (k * w) if not ask_big else w,
             w * (k - 1) if ask_big else w * 2, w * (k + 1) if ask_big else w // 2 if w % 2 == 0 else -1,
             W - k * w, W // 2 if ask_big else -1]
    choices, ai = numeric_choices(ans, wrong, rng, unit="g", lo=10, step=25 if w % 25 == 0 else 5)
    return Question(text=text, figure=fig, after_figure=after, choices=choices, answer=ai,
                    solution=sol)


@variant(difficulty=3)
def what_to_add(rng, harder):
    """Second balance is missing some small items - how many to add?"""
    (sm, bg) = rng.choice(PAIRS)
    k = rng.randint(2, 4)
    a = rng.randint(1, 2 if not harder else 3)
    b = rng.randint(0, 3)
    c = rng.randint(1, a * k + b - 1)
    ans = a * k + b - c
    b1 = balance(["ball"], ["dot"] * k, scale=9)
    b2 = balance(["ball"] * a + ["dot"] * b, ["dot"] * c, tilt=-1, scale=9, right_extra="?")
    fig = column([row([b1, b2], gap=24), legend([("dot", sm[0]), ("ball", bg[0])])], gap=4)
    text = (f"The first balance is level. On the second balance there "
            f"{'is' if a == 1 else 'are'} {n_of(a, bg)}"
            + (f" and {n_of(b, sm)}" if b else "") + f" on the left and {n_of(c, sm)} on the right.")
    after = f"How many {sm[1]} must be added to the right plate to make it level?"
    sol = (f"One {bg[0]} = {k} {sm[1]}, so the left plate is worth {a} × {k}"
           + (f" + {b}" if b else "") + f" = {a*k + b} {sm[1]}. "
           f"The right plate has {c}, so add {a*k + b} − {c} = {ans}.")
    mistakes = [a * k + b, a * k - c, a + b - c, a * k + b + c, ans + k, k - c]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, figure=fig, after_figure=after, choices=choices, answer=ai,
                    solution=sol)
