"""2007 Q1 - which numbers could Zita have written along the forking road?

Original: Zita walked from left to right along a road that splits three times
(branches 1|2, then 3|4, then 5|6) and wrote down the numbers she saw. Which group
could she have written?  A 1,2,4  B 2,3,4  C 2,3,5  D 1,5,6  E 1,2,5.  Answer: C.

Core skill: a route through forks takes exactly one branch at every fork, in
order - so a valid list has one number from each fork, never two from the same
fork, and none missing. Counting routes multiplies the choices.
"""
import math

from kangaroo import Fig, Question, numeric_choices, text_choices, variant

META = {
    "source": "2007 Q1",
    "skill": "Routes through forks: one branch from every fork; number of routes = product of choices",
    "topics": ["logic", "counting"],
    "version": 2,
}

NAMES = ["Zita", "Mia", "Leo", "Sara", "Tom", "Nina"]
FORK_W, LINK = 4.0, 1.4


def road_pic(forks, name):
    """forks: list of lists of labels, one list per fork (top branch first)."""
    k = len(forks)
    W = 2.4 + k * FORK_W + (k - 1) * LINK + 0.8
    f = Fig(W, 4.2, scale=14, margin=4)
    y0 = 2.1
    f.text(0.6, y0 + 0.75, name, size=9)
    f.line((0, y0), (1.6, y0), width=1.3)
    f.poly([(1.6, y0 + 0.25), (2.1, y0), (1.6, y0 - 0.25)], fill=None, width=1.0)
    x = 2.4
    f.line((2.1, y0), (x, y0), width=1.3)
    for i, labels in enumerate(forks):
        n = len(labels)
        bulges = [1.5, -1.5] if n == 2 else [1.6, 0.0, -1.6]
        for lab, b in zip(labels, bulges):
            pts = [(x + FORK_W * t / 20, y0 + b * math.sin(math.pi * t / 20)) for t in range(21)]
            f.polyline(pts, width=1.3)
            ly = y0 + b + (0.45 if b > 0 else -0.45 if b < 0 else 0.62)
            f.text(x + FORK_W / 2, ly, str(lab), size=10)
        x += FORK_W
        if i < k - 1:
            f.line((x, y0), (x + LINK, y0), width=1.3)
            x += LINK
    f.line((x, y0), (x + 0.8, y0), width=1.3)
    return f.drawing()


def _forks(rng, k, three=False, numbers=False):
    if numbers:
        pool = rng.sample(range(1, 20), 3 * k)
    else:
        pool = list(range(1, 3 * k + 1))
    out, j = [], 0
    for i in range(k):
        n = 3 if three and rng.random() < 0.5 else 2
        out.append(pool[j:j + n])
        j += n
    return out


def _fmt(group):
    return ", ".join(map(str, group[:-1])) + " and " + str(group[-1])


@variant(difficulty=1)
def which_group(rng, harder):
    """The original."""
    k = 4 if harder else 3
    forks = _forks(rng, k)
    good = [rng.choice(f) for f in forks]
    wrong = set()
    while len(wrong) < 4:
        g = list(good)                             # both branches of one fork, another fork skipped
        i, j = rng.sample(range(k), 2)
        g[j] = [b for b in forks[i] if b != g[i]][0]
        wrong.add(tuple(sorted(g)))
    good_t = tuple(sorted(good))
    opts = [_fmt(list(w)) for w in wrong]
    name = rng.choice(NAMES)
    text = f"{name} walks along the road from left to right and writes down every number on the way."
    after = f"Which group of numbers could {name} have written?"
    sol = (f"At every fork {name} takes exactly one branch, so there must be one number from each fork: "
           f"{_fmt(list(good_t))} works. Each of the others has two numbers from the same fork.")
    choices, ai = text_choices(_fmt(list(good_t)), opts, rng)
    return Question(text=text, figure=road_pic(forks, name), after_figure=after, choices=choices,
                    answer=ai, solution=sol)


@variant(difficulty=1)
def how_many_routes(rng, harder):
    """How many different groups of numbers can be written?"""
    k = rng.choice([3, 4] if harder else [2, 3])
    forks = _forks(rng, k, three=harder)
    sizes = [len(f) for f in forks]
    ans = math.prod(sizes)
    name = rng.choice(NAMES)
    text = f"{name} walks along the road from left to right and writes down every number on the way."
    after = f"How many different groups of numbers can {name} write?"
    sol = (f"The forks have {', '.join(map(str, sizes))} branches; every choice can go with "
           f"every other: {' × '.join(map(str, sizes))} = {ans}.")
    mistakes = [sum(sizes), k, 2 * k, ans + 2, ans // 2]     # added the choices, or counted forks
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, figure=road_pic(forks, name), after_figure=after, choices=choices,
                    answer=ai, solution=sol)


@variant(difficulty=2)
def largest_sum(rng, harder):
    """Largest possible total of the numbers written."""
    k = 4 if harder else 3
    forks = _forks(rng, k, three=harder, numbers=True)
    name = rng.choice(NAMES)
    best = [max(f) for f in forks]
    ans = sum(best)
    text = f"{name} walks along the road from left to right and adds up the numbers along the way."
    after = f"What is the biggest total {name} can get?"
    sol = f"Take the bigger number at every fork: {' + '.join(map(str, best))} = {ans}."
    two_big = sorted(sum(forks, []), reverse=True)[:k]
    mistakes = [sum(two_big),                       # biggest numbers, ignoring the forks
                sum(sum(f) for f in forks),         # all the numbers
                sum(min(f) for f in forks), ans - 1]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, figure=road_pic(forks, name), after_figure=after, choices=choices,
                    answer=ai, solution=sol)


def _all_routes(forks):
    routes = [[]]
    for f in forks:
        routes = [r + [b] for r in routes for b in f]
    return routes


@variant(difficulty=2)
def impossible_total(rng, harder):
    """Which total can she not get?"""
    for _ in range(300):
        k = 3
        forks = _forks(rng, k, three=harder, numbers=True)
        sums = {sum(r) for r in _all_routes(forks)}
        lo, hi = min(sums), max(sums)
        holes = [s for s in range(lo + 1, hi) if s not in sums]
        if holes and len(sums) >= 4:
            break
    else:
        raise RuntimeError("no road found")
    bad = rng.choice(holes)
    good = rng.sample(sorted(sums), 4)
    vals = sorted(good + [bad])
    name = rng.choice(NAMES)
    text = f"{name} walks along the road from left to right and adds up the numbers along the way."
    after = f"Which total can {name} <b>not</b> get?"
    ways = "; ".join(f"{s} = " + " + ".join(map(str, next(r for r in _all_routes(forks) if sum(r) == s)))
                     for s in sorted(good))
    sol = f"{ways}. No route gives {bad}."
    return Question(text=text, figure=road_pic(forks, name), after_figure=after,
                    choices=[str(v) for v in vals], answer=vals.index(bad), solution=sol)


@variant(difficulty=3)
def which_branch(rng, harder):
    """Reverse: the total is known - which number did she see at the middle fork?"""
    for _ in range(500):
        k = 4 if harder else 3
        forks = _forks(rng, k, numbers=True)
        routes = _all_routes(forks)
        totals = {}
        for r in routes:
            totals.setdefault(sum(r), []).append(r)
        unique = [t for t, rs in totals.items() if len(rs) == 1]
        if unique:
            break
    else:
        raise RuntimeError("no road found")
    t = rng.choice(unique)
    route = totals[t][0]
    j = 1
    ans = route[j]
    others = [b for f in forks for b in f if b != ans]
    vals = sorted(rng.sample(others, 4) + [ans])
    name = rng.choice(NAMES)
    text = (f"{name} walks along the road from left to right and adds up the numbers along the way. "
            f"The total is {t}.")
    after = f"Which number did {name} see at the second fork?"
    sol = f"Only one route gives {t}: {' + '.join(map(str, route))} = {t}. At the second fork: {ans}."
    return Question(text=text, figure=road_pic(forks, name), after_figure=after,
                    choices=[str(v) for v in vals], answer=vals.index(ans), solution=sol)
