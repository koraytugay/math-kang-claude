"""2023 Q23 (Ecolier, Grade 3-4) - a ring of circles with the sums of neighbours written between them.

Original: A teacher wants to write the numbers from 1 to 7 into the circles. He writes exactly one
number in each circle. When he adds up the two numbers of circles that are next to each other, he
gets the number that is written between the two circles. Which number does he write in the circle
with the question mark?  (A) 1  (B) 2  (C) 3  (D) 4  (E) 5.
Ring of 7 circles; going clockwise from the top the sums are 8, 9, 6, 9, 8, 9, 7 and the "?" circle
sits between the sums 6 and 9 (bottom right).
Guess ? = x and go around: 6 - x, 3 + x, 5 - x, 2 + x, 7 - x, 1 + x, and back: (1 + x) + x = 9, so x = 4.
Answer: D (answer key: D).

Core skill: "guess a number and go around the ring". From one circle and one sum you get the next
circle; with a ring of an odd number of circles, only one guess closes the ring. Children try to
split a single sum (6 = 3 + 3) or guess without checking all the way round.
"""
import math
from itertools import permutations

from reportlab.lib import colors

from kangaroo import Fig, Question, numeric_choices, value_check, variant, warmup

META = {
    "source": "set-01/by_level/Grade_03-04_Ecolier/2023 Q23",
    "skill": "Sums between neighbours in a ring: guess the number in one circle, go around the ring "
             "and check that it closes",
    "topics": ["arithmetic", "logic", "patterns"],
    "keywords": ["sums in a ring", "guess and check", "neighbour sums"],
    "version": 1,
}

GREY = colors.Color(0.8, 0.8, 0.8)


# ------------------------------------------------------------------ picture
def ring_pic(nums, sums, ask=None, hide_sum=None, max_px=120, row=False):
    """Circles in a ring (or in a row) with the sums written between neighbours.
    nums[i] = number shown in circle i (None = empty), ask = index of the '?' circle,
    hide_sum = index of a sum shown as '?'. Sum i is between circle i and circle i+1."""
    n = len(nums)
    if row:
        pos = [(i * 1.3, 0.0) for i in range(n)]
        f = Fig((n - 1) * 1.3 + 1, 1.0, max_px=max_px, margin=8, font_size=12)
        P = [(x + 0.5, 0.35) for x, y in pos]
        mids = [((P[i][0] + P[i + 1][0]) / 2, 0.95) for i in range(n - 1)]
    else:
        R = 1.25
        f = Fig(2 * R + 1.2, 2 * R + 1.2, max_px=max_px, margin=6, font_size=12)
        c = R + 0.6
        P = [(c + R * math.sin(2 * math.pi * i / n), c + R * math.cos(2 * math.pi * i / n)) for i in range(n)]
        mids = []
        for i in range(n):
            a = 2 * math.pi * (i + 0.5) / n
            mids.append((c + (R + 0.42) * math.sin(a), c + (R + 0.42) * math.cos(a)))
    r = 0.24
    for i in range(len(mids)):
        a, b = P[i], P[(i + 1) % n]
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        ux, uy = (b[0] - a[0]) / d, (b[1] - a[1]) / d
        f.line((a[0] + ux * r, a[1] + uy * r), (b[0] - ux * r, b[1] - uy * r), width=1.1)
        f.text(*mids[i], "?" if i == hide_sum else str(sums[i]), size=12)
    for i, (x, y) in enumerate(P):
        f.circle(x, y, r, fill=GREY if i == ask else colors.white, width=1.1)
        if i == ask:
            f.text(x, y, "?", size=12)
        elif nums[i] is not None:
            f.text(x, y, str(nums[i]), size=12)
    return f.drawing()


def ring_sums(nums):
    n = len(nums)
    return [nums[i] + nums[(i + 1) % n] for i in range(n)]


def solve_ring(n, sums, pool):
    """Check side: every way to put the numbers of `pool` (each once) into the ring that gives these sums."""
    return [p for p in permutations(pool, n) if ring_sums(p) == list(sums)]


def _walk(x, sums, start):
    """Generator side: start with x in circle `start` and go around using the sums."""
    n = len(sums)
    vals = {start: x}
    i = start
    for _ in range(n - 1):
        vals[(i + 1) % n] = sums[i] - vals[i]
        i = (i + 1) % n
    return vals, vals[i] + x == sums[i]


def _mistakes(sums, ask, ans):
    n = len(sums)
    left, right = sums[(ask - 1) % n], sums[ask]
    m = []
    if right % 2 == 0:
        m.append((right // 2, "split one sum into two equal numbers"))
    if left % 2 == 0:
        m.append((left // 2, "split one sum into two equal numbers"))
    m.append((abs(left - right), "subtract the two sums next to the circle"))
    m.append((ans + 1, "make a mistake on the way around the ring"))
    m.append((ans - 1, "make a mistake on the way around the ring"))
    return m


# ------------------------------------------------------------------ variants
@variant(difficulty=1)
def odd_ring(rng, harder):
    """The original: numbers 1..n in an odd ring, find the '?'."""
    n = 7 if harder else 5
    nums = list(range(1, n + 1))
    rng.shuffle(nums)
    sums = ring_sums(nums)
    ask = rng.randrange(n)
    # the generator's own way: try every guess and walk around
    ans = next(x for x in range(1, n + 1) if _walk(x, sums, ask)[1])
    text = (f"Lena writes the numbers from 1 to {n} into the circles, each number exactly once. When she adds "
            f"the numbers of two circles next to each other, she gets the number written between them. Which "
            f"number is in the circle with the question mark?")
    vals, _ = _walk(ans, sums, ask)
    path = ", ".join(str(vals[(ask + k) % n]) for k in range(n))
    sol = (f"Guess a number for the question mark and go around the ring, using the sums: only {ans} works "
           f"all the way round ({path}).")
    value = [p[ask] for p in solve_ring(n, sums, range(1, n + 1))]
    choices, ai = numeric_choices(ans, _mistakes(sums, ask, ans), rng, lo=1, order="asc")
    return Question(text=text, figure=ring_pic([None] * n, sums, ask=ask), choices=choices, answer=ai,
                    solution=sol, check=value_check(choices, value[0] if len(set(value)) == 1 else -1))


@variant(difficulty=1)
def in_a_row(rng, harder):
    """Warm into it: numbers in a row, the first one is given."""
    n = 6 if harder else 4
    nums = [rng.randint(1, 9 if harder else 6) for _ in range(n)]
    sums = [nums[i] + nums[i + 1] for i in range(n - 1)]
    shown = [nums[0]] + [None] * (n - 1)
    ask = n - 1
    text = ("The number between two circles is the sum of the numbers in these two circles. "
            "Which number is in the circle with the question mark?")
    steps = ", ".join(f"{sums[i]} − {nums[i]} = {nums[i + 1]}" for i in range(n - 1))
    sol = f"Go step by step from the left: {steps}."
    mistakes = [(sums[-1] - nums[0], "use the first number instead of its neighbour"),
                (sums[-1], "copy the last sum"), (sums[-1] // 2, "split the last sum into two equal numbers")]
    # check: brute force over all numbers 0..20 in each empty circle
    value = _chain(nums[0], sums)[-1]          # re-solve from the shown data
    choices, ai = numeric_choices(nums[-1], mistakes, rng, lo=0, order="asc")
    return Question(text=text, figure=ring_pic(shown, sums, ask=ask, row=True, max_px=48 * n),
                    choices=choices, answer=ai, solution=sol, check=value_check(choices, value))


def _chain(first, sums):
    out = [first]
    for s in sums:
        out.append(s - out[-1])
    return out


@variant(difficulty=2)
def all_together(rng, harder):
    """What do all the circles add up to? Every circle is in two sums."""
    n = rng.choice([6, 7, 8]) if harder else rng.choice([4, 5, 6])
    nums = [rng.randint(1, 9) for _ in range(n)]
    sums = ring_sums(nums)
    text = ("Each number between two circles is the sum of the numbers in these two circles. "
            "What do the numbers in all the circles add up to?")
    total = sum(sums)
    ans = total // 2
    sol = (f"Add all the numbers between the circles: {' + '.join(map(str, sums))} = {total}. Every circle is in "
           f"two of these sums, so all the circles together make {total} ÷ 2 = {ans}.")
    mistakes = [(total, "forget that every circle is counted twice"), ans + sums[0] // 2,
                (total - ans // 2, "take away only part of it")]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1, order="asc")
    return Question(text=text, figure=ring_pic([None] * n, sums, max_px=110), choices=choices, answer=ai,
                    solution=sol, check=value_check(choices, sum(nums)))


@variant(difficulty=2)
def hidden_sum(rng, harder):
    """Numbers 1..n each once; one sum is hidden. Which number is it?"""
    n = 7 if harder else 5
    nums = list(range(1, n + 1))
    rng.shuffle(nums)
    sums = ring_sums(nums)
    h = rng.randrange(n)
    text = (f"The numbers from 1 to {n} are written into the circles, each exactly once. Each number between two "
            f"circles is the sum of the numbers in these two circles. Which number belongs where the question "
            f"mark is?")
    T = n * (n + 1) // 2
    ans = 2 * T - (sum(sums) - sums[h])
    sol = (f"1 + 2 + ... + {n} = {T}. Every circle is in two sums, so all the sums together make 2 × {T} = {2 * T}. "
           f"The shown sums make {sum(sums) - sums[h]}, so the missing one is {2 * T} − {sum(sums) - sums[h]} = {ans}.")
    mistakes = [(T - (sum(sums) - sums[h]) if T > sum(sums) - sums[h] else 2 * T, "forget that every circle is counted twice"),
                (sums[h - 1], "copy the sum next to it"), (ans + 1, "add up wrongly"), (ans - 1, "add up wrongly")]
    value = {ring_sums(p)[h] for p in permutations(range(1, n + 1))
             if all(ring_sums(p)[i] == sums[i] for i in range(n) if i != h)}
    choices, ai = numeric_choices(ans, mistakes, rng, lo=2, order="asc")
    return Question(text=text, figure=ring_pic([None] * n, sums, hide_sum=h), choices=choices, answer=ai,
                    solution=sol, check=value_check(choices, value.pop() if len(value) == 1 else -1))


@variant(difficulty=3)
def even_ring(rng, harder):
    """Twist: an even ring - going around does not decide; the rule 'each number once' does."""
    n = 6 if harder else 4
    while True:
        nums = list(range(1, n + 1))
        rng.shuffle(nums)
        sums = ring_sums(nums)
        ask = rng.randrange(n)
        sols = solve_ring(n, sums, range(1, n + 1))
        if len({p[ask] for p in sols}) == 1:
            break
    ans = nums[ask]
    walks = [x for x in range(1, n + 1) if _walk(x, sums, ask)[1]
             and sorted(_walk(x, sums, ask)[0].values()) == list(range(1, n + 1))]
    assert walks == [ans]
    text = (f"The numbers from 1 to {n} are written into the circles, each exactly once. Each number between two "
            f"circles is the sum of the numbers in these two circles. Which number is in the circle with the "
            f"question mark?")
    sol = (f"With {n} circles every guess closes the ring, so check something else: the numbers must be 1 to {n}, "
           f"each once. Only {ans} gives {', '.join(str(_walk(ans, sums, ask)[0][(ask + k) % n]) for k in range(n))}.")
    others = [x for x in range(1, n + 1) if x != ans]
    mistakes = [(x, "stop when the ring closes, without checking that every number is used once") for x in others]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1, order="asc")
    return Question(text=text, figure=ring_pic([None] * n, sums, ask=ask), choices=choices, answer=ai,
                    solution=sol, check=value_check(choices, sols[0][ask]))


# ------------------------------------------------------------------ teaching page
def teach():
    sums = [8, 9, 6, 9, 8, 9, 7]          # clockwise from the top circle; '?' is circle 3
    rows = [["guess for ?", "going around", "back at ?", "works?"]]
    for x in (3, 4, 5):
        vals, ok = _walk(x, sums, 3)
        path = " → ".join(str(vals[(3 + k) % 7]) for k in range(7))
        rows.append([str(x), path, str(sums[2] - vals[2]), "<b>yes</b>" if ok else "no"])
    return [
        ("h", "How to think about it: sums in a ring"),
        "Each number between two circles is the sum of its two neighbours. If you know <b>one</b> circle, you "
        "know the next one: next = sum − this one. So:",
        ("-", "<b>1. Guess</b> a number for the question mark."),
        ("-", "<b>2. Go around</b> the ring, circle by circle: next = sum − this one."),
        ("-", "<b>3. Check</b> when you come back: do you get your guess again? If not, try another guess."),
        ring_pic([None] * 7, sums, ask=3, max_px=120),
        ("h", "The contest question"),
        "Start at the question mark and go clockwise. The sums on the way are 9, 8, 9, 7, 8, 9, and the last "
        "sum, 6, brings you back to the question mark:",
        ("table", rows),
        ("tip", "Only the guess <b>4</b> comes back to itself. And the numbers are 1 to 7, each once."),
        ("h", "Watch out"),
        ("-", "Do not split one sum in half (6 = 3 + 3): the two neighbours are different numbers."),
        ("-", "Trick for later: add all the sums. Every circle is counted twice, so the sum of all the circles is "
              "half of it."),
    ]


# ------------------------------------------------------------------ warm-ups
@warmup
def w_next(rng, harder):
    """One step: next = sum - this one."""
    a, b = rng.randint(1, 9), rng.randint(1, 9)
    text = "The number between the circles is their sum. Which number is in the circle with the question mark?"
    choices, ai = numeric_choices(b, [(a + b + a, "add instead of subtract"), ((a + b) // 2, "split the sum in two")],
                                  rng, lo=0, order="asc")
    return Question(text=text, figure=ring_pic([a, None], [a + b], ask=1, row=True, max_px=100), choices=choices,
                    answer=ai, solution=f"{a + b} − {a} = {b}.",
                    check=value_check(choices, next(x for x in range(30) if a + x == a + b)))


@warmup
def w_ring_closes(rng, harder):
    """A ring of 3: guess and check."""
    nums = rng.sample(range(1, 10), 3)
    sums = ring_sums(nums)
    text = ("The number between two circles is the sum of these two circles. Which number is in the circle with "
            "the question mark? Guess, go around, and check.")
    ans = nums[0]
    choices, ai = numeric_choices(ans, [(sums[0] // 2, "split one sum in two"), (sums[0] - sums[1] if sums[0] > sums[1]
                                  else ans + 1, "subtract two sums")], rng, lo=1, order="asc")
    value = [p[0] for p in permutations(range(1, 10), 3) if ring_sums(p) == sums]
    return Question(text=text, figure=ring_pic([None] * 3, sums, ask=0, max_px=90), choices=choices, answer=ai,
                    solution=f"Only {ans} works: {nums[0]} → {nums[1]} → {nums[2]} → {nums[0]}.",
                    check=value_check(choices, value[0]))
