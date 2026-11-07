"""2025 Q10 (Ecolier, Grade 3-4) - two children running around a circle in opposite directions.

Original: Max draws a large circle in the sand. Lisa adds the letters A, B, C and D
(A at the top, then B, C, D clockwise, evenly spaced). Lisa and Max start at the same
time from point A. Lisa goes clockwise around the circle, Max runs anti-clockwise.
They meet for the first time at point B, then at C, at D and then again at point A.
How many times has Max run around the circle by then?
A 1-times  B 2-times  C 3-times  D 4-times  E 5-times.
Between two meetings the two of them together run exactly once around the circle.
Lisa only gets from one letter to the next (1/4 of the circle), so Max runs the other
3/4. Four meetings: Max runs 4 x 3 quarters = 3 times around.  Answer: C.

Core skill: "between two meetings, together they cover one whole lap". Children see
four meetings and answer 4, or think "Max ran past A only once". They have to turn
the picture into parts of the circle: the slow runner's part and the fast runner's part.
"""
from fractions import Fraction
from math import gcd, lcm

from reportlab.lib import colors

from kangaroo import Fig, Question, numeric_choices, value_check, variant

META = {
    "source": "set-01/by_level/Grade_03-04_Ecolier/2025 Q10",
    "skill": "Running towards each other around a circle: between two meetings they cover one whole lap together",
    "topics": ["logic", "arithmetic", "spatial"],
    "version": 1,
}

PAIRS = [("Lisa", "Max"), ("Mia", "Tom"), ("Anna", "Ben"), ("Sara", "Leo"), ("Emma", "Sam"), ("Zoe", "Jack")]
LET_A = "ABCDEFGH"
LET_P = "PQRSTUVW"
TIMES = ("time", "times")


# ------------------------------------------------------------------ brute-force check
def simulate(P, cw, acw, steps=None):
    """Brute force on a circle of P ticks: each step one child moves `cw` ticks clockwise and the
    other `acw` ticks anticlockwise. Stops when both are back at the start together (or after
    `steps` steps). Returns (meeting places in ticks clockwise from the start, laps cw, laps acw)."""
    assert P % (cw + acw) == 0          # then no meeting can fall between two steps
    a = b = t = 0
    meets = []
    while True:
        t += 1
        a += cw
        b += acw
        pa, pb = a % P, (-b) % P
        if pa == pb:
            meets.append(pa)
        if (steps is None and pa == 0 and pb == 0) or t == steps:
            return meets, Fraction(a, P), Fraction(b, P)


# ------------------------------------------------------------------ picture
def _arrow(f, cx, cy, r, a0, a1):
    """Arc from angle a0 to a1 (degrees) with an arrowhead at a1."""
    import math
    f.arc(cx, cy, r, a0, a1, width=1.0)
    t = math.radians(a1)
    sgn = 1 if a1 > a0 else -1               # anticlockwise if the angle grows
    tip = (cx + r * math.cos(t), cy + r * math.sin(t))
    d = (-math.sin(t) * sgn, math.cos(t) * sgn)
    n = (math.cos(t), math.sin(t))
    L, W = 0.17, 0.08
    base = (tip[0] - d[0] * L, tip[1] - d[1] * L)
    f.poly([tip, (base[0] + n[0] * W, base[1] + n[1] * W), (base[0] - n[0] * W, base[1] - n[1] * W)],
           fill=colors.black, width=0.6)


def circle_pic(labels, cw_name, acw_name, max_px=118):
    """Circle with points labelled clockwise from the top, and two arrows with names at the top."""
    import math
    R, cx, cy = 1.0, 1.75, 1.3
    f = Fig(3.5, 3.0, max_px=max_px, margin=6, font_size=10.5)
    f.arc(cx, cy, R, 0, 360, width=1.3)
    k = len(labels)
    for i, lab in enumerate(labels):
        a = math.radians(90 - 360 * i / k)
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        f.circle(x, y, 0.055, fill=colors.Color(0.95, 0.6, 0.6) if i == 0 else colors.white, width=0.8)
        rr = 0.78 if len(lab) == 1 else 0.62
        f.text(cx + rr * R * math.cos(a), cy + rr * R * math.sin(a), lab, size=10)
    _arrow(f, cx, cy, 1.22, 80, 38)           # clockwise, right
    _arrow(f, cx, cy, 1.22, 100, 142)         # anticlockwise, left
    f.text(cx + 0.45, cy + 1.5, cw_name, anchor="start", size=10, italic=True)
    f.text(cx - 0.45, cy + 1.5, acw_name, anchor="end", size=10, italic=True)
    return f.drawing()


def _story(rng):
    a, b = rng.choice(PAIRS)
    return (a, b) if rng.random() < 0.5 else (b, a)


def _listing(letters):
    """'point B, then at C, at D and then again at point A' for the meeting places."""
    first, mid, last = letters[0], letters[1:-1], letters[-1]
    s = f"point {first}"
    if mid:
        s += ", then at " + ", at ".join(mid)
    return s + f" and then again at point {last}"


# ------------------------------------------------------------------ variants
@variant(difficulty=1)
def fast_laps(rng, harder):
    """The original: they meet at the next point each time; how many laps did the fast child run?"""
    k = rng.choice([5, 6]) if harder else 4
    cw, acw = _story(rng)
    slow_cw = rng.random() < 0.6
    slow, fast = (cw, acw) if slow_cw else (acw, cw)
    letters = LET_A[:k]
    idx = [(i if slow_cw else -i) % k for i in range(1, k + 1)]
    order = [letters[i] for i in idx]
    text = (f"{cw} and {acw} draw a big circle in the sand and write the letters "
            f"{', '.join(letters[:-1])} and {letters[-1]} on it. They start at the same time from point A. "
            f"{cw} runs clockwise and {acw} runs anticlockwise around the circle (see picture). "
            f"They meet for the first time at {_listing(order)}. "
            f"How many times has {fast} run around the circle by then?")
    ans = k - 1
    sol = (f"Between two meetings they run exactly once around the circle together. {slow} only gets "
           f"to the next letter (1 of {k} parts), so {fast} runs the other {k - 1} parts. "
           f"{k} meetings × {k - 1} parts = {k * (k - 1)} parts = {ans} times around.")
    # check: speeds read off the picture (slow 1 part, fast k-1 parts per meeting), then simulate
    meets, lc, la = simulate(k * k, 1 if slow_cw else k - 1, k - 1 if slow_cw else 1)
    assert [m // k for m in meets] == idx
    laps_fast = la if slow_cw else lc
    choices, ai = numeric_choices(ans, [k, 1, k + 1, k - 2, 2 * k], rng, lo=1, unit=TIMES, order="asc")
    return Question(text=text, figure=circle_pic(letters, cw, acw), choices=choices, answer=ai,
                    solution=sol, check=value_check(choices, int(laps_fast)))


@variant(difficulty=2)
def skip_points(rng, harder):
    """The first meeting is 2 or 3 points along, so they skip points and go round more than once."""
    k, s = rng.choice([(5, 2), (7, 2), (7, 3), (8, 3)]) if harder else rng.choice([(6, 2), (8, 2)])
    cw, acw = _story(rng)
    slow_cw = rng.random() < 0.6
    slow, fast = (cw, acw) if slow_cw else (acw, cw)
    letters = LET_A[:k]
    g = gcd(k, s)
    n_meet = k // g
    idx = [(i * s if slow_cw else -i * s) % k for i in range(1, n_meet + 1)]
    order = [letters[i] for i in idx]
    slow_laps, fast_laps_ = s // g, (k - s) // g
    meets, lc, la = simulate(k * k, s if slow_cw else k - s, k - s if slow_cw else s)
    assert [m // k for m in meets] == idx
    intro = (f"{cw} and {acw} start at the same time from point A of the circle. {cw} runs clockwise, "
             f"{acw} runs anticlockwise (see picture). ")
    ask_laps = rng.random() < 0.5
    if ask_laps:
        text = intro + (f"They meet for the first time at {_listing(order)}. "
                        f"How many times has {fast} run around the circle by then?")
        ans = fast_laps_
        sol = (f"Each time, {slow} runs {s} of the {k} parts and {fast} runs the other {k - s}. "
               f"They meet {n_meet} times, so {fast} runs {n_meet} × {k - s} = {n_meet * (k - s)} parts "
               f"= {ans} times around.")
        mistakes = [n_meet, k - s, slow_laps, n_meet - 1, ans + 1]
        value = int(la if slow_cw else lc)
    else:
        text = intro + (f"They meet for the first time at point {order[0]} and keep on running. "
                        f"How many times do they meet until they are together at point A again? "
                        f"(Count the meeting at A, but not the start.)")
        ans = n_meet
        sol = (f"{slow} moves {s} letters on from one meeting to the next: "
               f"{', '.join(order)}. That is {ans} meetings.")
        mistakes = [k, k - 1, n_meet - 1, n_meet + 1, fast_laps_, k // s]
        value = len(meets)
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1, unit=TIMES if ask_laps else "",
                                  order="asc")
    return Question(text=text, figure=circle_pic(letters, cw, acw), choices=choices, answer=ai,
                    solution=sol, check=value_check(choices, value))


def _ratio_points(m):
    """Number of points on the circle so that the first meeting falls on a point."""
    return m + 1 if m + 1 >= 5 else 2 * (m + 1)


@variant(difficulty=2)
def where_first(rng, harder):
    """Reverse: the speeds are given; at which point do they meet first?"""
    m = rng.choice([3, 5, 7]) if harder else rng.choice([2, 3, 4])
    k = _ratio_points(m)
    cw, acw = _story(rng)
    slow_cw = rng.random() < 0.5
    slow, fast = (cw, acw) if slow_cw else (acw, cw)
    letters = LET_P[:k]
    j = k // (m + 1)                       # points the slow child covers
    pos = j if slow_cw else k - j          # clockwise index of the meeting point
    text = (f"{cw} and {acw} start together at point P and run around the circle in opposite directions: "
            f"{cw} clockwise and {acw} anticlockwise (see picture). The points are evenly spaced. "
            f"{fast} runs {m} times as fast as {slow}. At which point do they meet for the first time?")
    sol = (f"Until they meet they run once around the circle together, and {fast} runs {m} times as far: "
           f"{slow} runs 1 part and {fast} {m} parts of {m + 1}. 1 part of {m + 1} is {j} "
           f"of the {k} gaps, so {slow} only gets to point {letters[pos]}.")
    mirror = (k - pos) % k
    others = [i for i in range(k) if i not in (pos, mirror)]
    wrong = [mirror] + rng.sample(others, 3)
    opts = sorted(wrong + [pos])
    meets, _, _ = simulate(k * (m + 1), 1 if slow_cw else m, m if slow_cw else 1)
    first = meets[0]
    return Question(text=text, figure=circle_pic(letters, cw, acw), choices=[f"point {letters[i]}" for i in opts],
                    answer=opts.index(pos), solution=sol,
                    check=lambda i: opts[i] * (m + 1) == first)


@variant(difficulty=3)
def count_meetings(rng, harder):
    """Reverse: the laps are given; how many meetings were there?"""
    a, b = (rng.choice([(2, 3), (2, 5), (3, 4), (3, 5)]) if harder
            else (1, rng.choice([2, 3, 4, 5])))
    cw, acw = _story(rng)
    slow_cw = rng.random() < 0.5
    slow, fast = (cw, acw) if slow_cw else (acw, cw)
    once = "once" if a == 1 else f"{a} times"
    text = (f"{cw} runs clockwise and {acw} runs anticlockwise around a circle. They start together at "
            f"point A. When they are together at point A again for the first time, {slow} has run around "
            f"the circle {once} and {fast} {b} times. How many times did they meet? "
            f"(Count the meeting at A, but not the start.)")
    ans = a + b
    sol = (f"Between two meetings they run exactly once around the circle together. Together they ran "
           f"{a} + {b} = {ans} times around, so they met {ans} times.")
    meets, lc, la = simulate(a + b, a if slow_cw else b, b if slow_cw else a)
    assert (lc, la) == ((a, b) if slow_cw else (b, a))
    mistakes = [b, b - 1, a + b - 1, a * b, a + b + 1, b - a]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1, order="asc")
    return Question(text=text, figure=circle_pic(["A"], cw, acw, max_px=90), choices=choices, answer=ai,
                    solution=sol, check=value_check(choices, len(meets)))


@variant(difficulty=3)
def minutes(rng, harder):
    """Lap times in minutes: how often do they meet?"""
    pairs = ([(6, 3), (12, 4), (12, 6), (20, 5), (15, 10), (10, 10), (30, 6), (8, 8)] if harder
             else [(6, 3), (12, 6), (12, 4), (6, 6), (10, 10)])
    L, M = rng.choice(pairs)
    base = lcm(L, M)
    T = base * rng.choice([n for n in range(1, 6) if base * n <= (60 if harder else 24)])
    cw, acw = _story(rng)
    slow_cw = rng.random() < 0.5
    slow, fast = (cw, acw) if slow_cw else (acw, cw)
    same = L == M
    text = (f"{cw} and {acw} start together at the same spot of a round track. {cw} runs clockwise and "
            f"{acw} runs anticlockwise. {slow} needs {L} minutes to run once around, "
            f"{fast} {'also' if same else 'only'} needs {M} minutes. After {T} minutes they stop "
            f"— both are back at the start together. How many times did they meet? "
            f"(Count the meeting at the end, but not the start.)")
    ls, lf = T // L, T // M
    ans = ls + lf
    sol = (f"Between two meetings they run once around the track together. In {T} minutes {slow} runs "
           f"{ls} and {fast} runs {lf} times around: {ls} + {lf} = {ans} laps together, so {ans} meetings.")
    mistakes = [lf - ls, lf, ls, ans - 1, ans + 1, T // (L + M) if T >= L + M else 0]
    choices, ai = numeric_choices(ans, [x for x in mistakes if x > 0], rng, lo=1, order="asc")
    meets, _, _ = simulate(L * M, M if slow_cw else L, L if slow_cw else M, steps=T)
    return Question(text=text, figure=circle_pic(["start"], cw, acw, max_px=90), choices=choices, answer=ai,
                    solution=sol, check=value_check(choices, len(meets)))
