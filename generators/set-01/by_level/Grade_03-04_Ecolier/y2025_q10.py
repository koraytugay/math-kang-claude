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

from kangaroo import Fig, Question, numeric_choices, value_check, variant, warmup

META = {
    "source": "set-01/by_level/Grade_03-04_Ecolier/2025 Q10",
    "skill": "Running towards each other around a circle: between two meetings they cover one whole lap together",
    "topics": ["logic", "arithmetic", "spatial"],
    "keywords": ["runners on a circle", "meeting on a circle"],
    "version": 3,
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



# ------------------------------------------------------------------ teaching page
RED = colors.Color(0.85, 0.2, 0.2)
BLUE = colors.Color(0.15, 0.4, 0.85)


def _path(f, cx, cy, r, a0, a1, color, width=3.0):
    """A thick coloured arc from angle a0 to a1 (degrees), with an arrowhead at a1."""
    import math
    n = max(4, int(abs(a1 - a0) / 6))
    pts = [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
            cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    for p, q in zip(pts, pts[1:]):
        f.line(p, q, width=width, color=color)
    t = math.radians(a1)
    sgn = 1 if a1 > a0 else -1
    tip = pts[-1]
    d = (-math.sin(t) * sgn, math.cos(t) * sgn)
    nn = (math.cos(t), math.sin(t))
    base = (tip[0] - d[0] * 0.2, tip[1] - d[1] * 0.2)
    f.poly([tip, (base[0] + nn[0] * 0.1, base[1] + nn[1] * 0.1), (base[0] - nn[0] * 0.1, base[1] - nn[1] * 0.1)],
           fill=color, width=0.5)


def _teach_circle():
    """The original: Lisa's piece A->B (1 part, red, outside), Max's piece A->D->C->B (3 parts, blue, inside)."""
    import math
    cx, cy, R = 2.2, 1.7, 1.0
    f = Fig(4.4, 3.4, max_px=125, margin=4, font_size=11)
    f.arc(cx, cy, R, 0, 360, width=1.0)
    for i, lab in enumerate("ABCD"):
        a = math.radians(90 - 90 * i)
        f.circle(cx + R * math.cos(a), cy + R * math.sin(a), 0.05, fill=colors.white, width=0.8)
        f.text(cx + 0.8 * R * math.cos(a), cy + 0.8 * R * math.sin(a), lab, size=11)
    _path(f, cx, cy, 1.18, 88, 4, RED)                 # Lisa: A -> B clockwise, outside
    _path(f, cx, cy, 0.6, 92, 360 - 4, BLUE)           # Max: A -> D -> C -> B anticlockwise, inside
    f.text(cx + 1.05, cy + 1.25, "Lisa: 1 part", anchor="start", size=11)
    f.text(cx - 1.05, cy + 1.25, "Max: 3 parts", anchor="end", size=11)
    f.text(cx, 0.15, "First meeting at B: 1 part + 3 parts = the whole circle", size=10, italic=True)
    return f.drawing()


def _teach_line():
    """The circle cut open at A and laid flat."""
    f = Fig(8.4, 1.6, scale=30, margin=4, font_size=11)
    y = 0.6
    f.line((0.2, y), (8.2, y), width=1.2)
    for i, lab in enumerate("ABCDA"):
        x = 0.2 + 2 * i
        f.line((x, y - 0.12), (x, y + 0.12), width=1.2)
        f.text(x, y - 0.4, lab, size=11)
    f.line((0.2, y + 0.35), (2.2, y + 0.35), width=3, color=RED)
    f.line((2.2, y + 0.55), (8.2, y + 0.55), width=3, color=BLUE)
    f.text(1.2, y + 0.8, "Lisa →", size=10)
    f.text(5.2, y + 0.95, "← Max", size=10)
    return f.drawing()


def teach():
    rows = [["Meeting", "Where", "Lisa has run", "Max has run"]]
    for i, lab in enumerate("BCDA", 1):
        rows.append([str(i), lab, f"{i} part{'s' if i > 1 else ''}", f"{3 * i} parts"])
    return [
        ("h", "How to think about it: two runners going opposite ways round a circle"),
        "In these questions two children start at the same spot and run around a circle in <b>opposite "
        "directions</b>, so they keep meeting. You are asked where they meet, how often, or how many times one "
        "of them runs around.",
        ("tip", "<b>The big idea:</b> between two meetings, the two runners <b>together</b> run exactly "
                "<b>once around the circle</b>."),
        "Why? Right after a meeting they stand on the same spot. They run apart, and they meet again when the "
        "gap between them is closed — that is when Lisa's piece and Max's piece together make the whole circle.",
        _teach_circle(),
        ("h", "Step by step: the contest question"),
        ("-", "<b>1. Cut the circle into equal parts.</b> The letters A, B, C, D cut it into 4 equal parts."),
        ("-", "<b>2. Who runs how much until the first meeting?</b> They meet at B. Lisa ran A to B: "
              "<b>1 part</b>. Max ran A to D to C to B: <b>3 parts</b>. Together 4 parts = once around."),
        ("-", "<b>3. It is the same every time.</b> From one meeting to the next, Lisa runs 1 more part "
              "and Max 3 more parts."),
        ("-", "<b>4. Keep count in a table.</b>"),
        ("table", rows),
        ("-", "<b>5. Change parts into laps.</b> Max ran 12 parts, and 4 parts make one lap: "
              "12 ÷ 4 = <b>3 times around</b>."),
        ("h", "Another way to see it"),
        "Cut the circle open at A and lay it flat. Lisa starts at the left end, Max at the right end. "
        "They meet where their two pieces touch — the two pieces always fill the whole line.",
        _teach_line(),
        ("h", "Watch out"),
        ("-", "The number of <b>meetings</b> (4) is not the number of <b>laps</b> (3). Read what the question asks."),
        ("-", "Check your answer: Lisa's laps + Max's laps = number of meetings. Here 1 + 3 = 4."),
        ("-", "If they run equally fast, each runs half the circle: they meet exactly opposite the start."),
        ("tip", "<b>Try it yourself:</b> walk around a table with a friend or your brother, in opposite directions, one of "
                "you slowly and one fast. Stop every time you meet and count how many parts each of you walked."),
    ]


# ------------------------------------------------------------------ warm-ups (small steps)
@warmup
def w_equal_speed(rng, harder):
    """Equally fast: they meet opposite the start."""
    a, b = _story(rng)
    k = rng.choice([6, 8])
    letters = LET_P[:k]
    text = (f"{a} and {b} start together at point P and run around the circle in opposite directions. "
            f"They run <b>equally fast</b>. At which point do they meet for the first time?")
    meets, _, _ = simulate(2 * k, 1, 1)             # 2 ticks per gap
    pos = k // 2
    others = [i for i in range(k) if i != pos]
    opts = sorted([pos] + rng.sample(others, 4))
    sol = (f"Equally fast means each runs half of the circle. Half of {k} gaps is {k // 2} gaps: "
           f"point {letters[pos]}, right opposite P.")
    return Question(text=text, figure=circle_pic(letters, a, b), choices=[f"point {letters[i]}" for i in opts],
                    answer=opts.index(pos), solution=sol, check=lambda i: 2 * opts[i] == meets[0])


@warmup
def w_parts_first(rng, harder):
    """Until the first meeting: slow part + fast part = whole circle."""
    a, b = _story(rng)
    k, s = rng.choice([(4, 1), (5, 1), (6, 1), (6, 2), (8, 3)])
    text = (f"A circle is cut into {k} equal parts. {a} and {b} start together and run in opposite "
            f"directions. When they meet for the first time, {a} has run {s} part{'s' if s > 1 else ''}. "
            f"How many parts has {b} run?")
    ans = k - s
    sol = f"Together they ran once around, that is {k} parts. {k} − {s} = {ans}."
    _, lc, la = simulate(k, s, k - s, steps=1)
    choices, ai = numeric_choices(ans, [s, k, k + s, ans - 1, ans + 1], rng, lo=1, order="asc",
                                  unit=("part", "parts"))
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, int(la * k)))


@warmup
def w_next_meeting(rng, harder):
    """They meet at the next point; where is the second meeting?"""
    a, b = _story(rng)
    k = 5
    letters = LET_P[:k]
    text = (f"{a} runs clockwise and {b} anticlockwise (see picture). They start together at P and meet "
            f"for the first time at Q. They keep running just as fast. Where do they meet the second time?")
    meets, _, _ = simulate(k * k, 1, k - 1)
    sol = (f"Each time, {a} runs 1 part (one point further) and {b} the other {k - 1} parts. "
           f"So the second meeting is one point after Q: at R.")
    opts = list(range(k))
    return Question(text=text, figure=circle_pic(letters, a, b), choices=[f"point {c}" for c in letters],
                    answer=2, solution=sol, check=lambda i: opts[i] * k == meets[1])


@warmup
def w_total_parts(rng, harder):
    """The same piece every time: multiply."""
    a, b = _story(rng)
    k = rng.choice([4, 5, 6])
    text = (f"A circle is cut into {k} equal parts. Every time {a} and {b} meet, {b} has run "
            f"{k - 1} more parts. How many parts has {b} run after {k} meetings?")
    ans = k * (k - 1)
    sol = f"{k} meetings × {k - 1} parts = {ans} parts."
    _, _, la = simulate(k * k, 1, k - 1)              # k meetings = until both are back at the start
    choices, ai = numeric_choices(ans, [k + k - 1, k * k, ans - k, k - 1, ans + 1], rng, lo=1, order="asc",
                                  unit=("part", "parts"))
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, int(la * k)))


@warmup
def w_parts_to_laps(rng, harder):
    """From parts to laps: divide."""
    a, _ = _story(rng)
    k = rng.choice([4, 5, 6])
    laps = rng.choice([2, 3, 4])
    n = k * laps
    text = (f"A circle is cut into {k} equal parts. {a} runs {n} parts around the circle. "
            f"How many times has {a} run around the circle?")
    sol = f"One time around is {k} parts. {n} ÷ {k} = {laps}."
    value = sum(1 for t in range(1, n + 1) if t % k == 0)   # count the times a passes the start
    choices, ai = numeric_choices(laps, [n, k, laps + 1, laps - 1, n - k], rng, lo=1, order="asc", unit=TIMES)
    return Question(text=text, choices=choices, answer=ai, solution=sol, check=value_check(choices, value))
