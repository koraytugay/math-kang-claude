"""2024 Q19 (Ecolier, Grade 3-4) - two repeating patterns at the same time.

Original: 60 children stand in a row. Each child has a high-visibility vest and a backpack.
The vests alternate: yellow, green, yellow, green, ... The backpacks go: red, brown,
purple, red, brown, purple, ... How many children have a yellow vest and a purple
backpack?  A 3  B 4  C 6  D 8  E 10.
Both patterns start again together every 6 children (child 7 looks like child 1). In each
block of 6 only child 3 (then 9, 15, ...) is yellow + purple. 60 = 10 blocks: 10.  Answer: E.

Core skill: two patterns together make one longer pattern ("block"). Write both patterns
under the numbers 1, 2, 3, ... until they start again at the same time, count in one block,
then multiply - and handle the children left over. Traps: the block is not always
length x length (2 and 4 repeat every 4, so some pairs never happen), and N is not always a
whole number of blocks.

Printed in black and white: the patterns are T-shirts (white, striped, dotted, black) and cards
with shapes (circle, star, ...), never colours.
"""
import math
from math import gcd

from reportlab.lib import colors

from kangaroo import Fig, Question, numeric_choices, value_check, variant, warmup

META = {
    "source": "set-01/by_level/Grade_03-04_Ecolier/2024 Q19",
    "skill": "Two repeating patterns together: find the block where both start again, count in it, multiply",
    "topics": ["patterns", "counting", "arithmetic"],
    "keywords": ["two repeating patterns", "shirts and cards"],
    "version": 3,
}

# Black-and-white printing: T-shirt patterns and card shapes instead of colours.
SHIRT = ["white", "striped", "dotted", "black"]
CARD = ["circle", "star", "triangle", "square", "diamond", "cross"]
VEST, BAG = SHIRT, CARD          # the two patterns (names kept short in the code)


def lcm(a, b):
    return a * b // gcd(a, b)


def count(p1, p2, n, x, y):
    """Answer check: walk along the row child by child."""
    return sum(1 for i in range(n) if p1[i % len(p1)] == x and p2[i % len(p2)] == y)


def positions(p1, p2, n, x, y):
    return [i + 1 for i in range(n) if p1[i % len(p1)] == x and p2[i % len(p2)] == y]


def _pats(rng, a, b):
    return rng.sample(SHIRT, a), rng.sample(CARD, b)


def _lst(p):
    """The pattern written out as in the contest: short patterns twice, long ones once and a bit."""
    shown = p * 2 if len(p) <= 3 else p + p[:2]
    return ", ".join(shown) + ", ..."


def _text(n, p1, p2):
    return (f"{n} children stand in a row. Each child wears a T-shirt and holds a card with a shape on it.\n"
            f"- The T-shirts repeat like this: {_lst(p1)}\n"
            f"- The cards repeat like this: {_lst(p2)}\n\n")


def _ask(x, y):
    return f"How many children have a <b>{x}</b> T-shirt <b>and</b> a <b>{y}</b> card?"


# ------------------------------------------------------------------ picture
DARK = colors.Color(0.2, 0.2, 0.2)


def shirt(f, x0, y0, w, h, kind, width=0.8):
    """A T-shirt pattern in a box (black and white only)."""
    f.rect(x0, y0, w, h, fill=DARK if kind == "black" else colors.white, width=width)
    if kind == "striped":
        k = 4
        for j in range(1, k):
            yy = y0 + h * j / k
            f.line((x0, yy), (x0 + w, yy), width=1.3)
    elif kind == "dotted":
        for i in range(3):
            for j in range(3):
                f.circle(x0 + w * (i + 0.5) / 3, y0 + h * (j + 0.5) / 3, min(w, h) * 0.07,
                         fill=colors.black, width=0.3)


def shape(f, cx, cy, r, kind, width=0.8):
    """A card shape, outlined and filled black so it prints clearly."""
    fill = colors.black
    if kind == "circle":
        f.circle(cx, cy, r * 0.85, fill=fill, width=width)
    elif kind == "square":
        s = r * 0.78
        f.rect(cx - s, cy - s, 2 * s, 2 * s, fill=fill, width=width)
    elif kind == "triangle":
        f.poly([(cx - r, cy - r * 0.8), (cx + r, cy - r * 0.8), (cx, cy + r)], fill=fill, width=width)
    elif kind == "diamond":
        f.poly([(cx, cy + r), (cx + r * 0.75, cy), (cx, cy - r), (cx - r * 0.75, cy)], fill=fill, width=width)
    elif kind == "star":
        pts = []
        for i in range(10):
            a = math.pi / 2 + i * math.pi / 5
            rr = r if i % 2 == 0 else r * 0.42
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        f.poly(pts, fill=fill, width=width)
    elif kind == "cross":
        t = r * 0.33
        f.poly([(cx - t, cy + r), (cx + t, cy + r), (cx + t, cy + t), (cx + r, cy + t), (cx + r, cy - t),
                (cx + t, cy - t), (cx + t, cy - r), (cx - t, cy - r), (cx - t, cy - t), (cx - r, cy - t),
                (cx - r, cy + t), (cx - t, cy + t)], fill=fill, width=width)
    else:
        raise ValueError(kind)


def children_pic(p1, p2, n, mark=(), scale=19, numbers=True):
    """The first n children: head, T-shirt (body) and a card held up beside them; marked ones get a box."""
    step = 2.0
    f = Fig(step * n + 0.2, 3.4, scale=scale, margin=3, font_size=9)
    for i in range(n):
        x = 0.2 + step * i + 0.7
        if i + 1 in mark:
            f.rect(x - 0.75, 0.05, 1.9, 3.25, fill=colors.Color(0.92, 0.92, 0.92), width=1.2)
        f.line((x + 0.4, 1.6), (x + 0.75, 1.75), width=1.0)                           # arm
        f.rect(x + 0.55, 1.55, 0.75, 0.9, fill=colors.white, width=0.7)               # card
        shape(f, x + 0.925, 2.0, 0.28, p2[i % len(p2)], width=0.5)
        shirt(f, x - 0.4, 1.0, 0.8, 1.2, p1[i % len(p1)])                             # T-shirt
        f.circle(x, 2.6, 0.33, fill=colors.white, width=0.8)                          # head
        f.line((x - 0.2, 1.0), (x - 0.2, 0.55), width=1.0)
        f.line((x + 0.2, 1.0), (x + 0.2, 0.55), width=1.0)
        if numbers:
            f.text(x, 0.25, str(i + 1), size=9)
    return f.drawing()


def table_pic(p1, p2, n, mark=(), block=None, scale=21):
    """Positions 1..n with a T-shirt square and a card shape under each; block lines; matches boxed."""
    f = Fig(n + 2.4, 3.2, scale=scale, margin=3, font_size=9)
    f.text(1.1, 2.7, "child", size=9, italic=True)
    f.text(1.1, 1.75, "T-shirt", size=9, italic=True)
    f.text(1.1, 0.8, "card", size=9, italic=True)
    for i in range(n):
        x = 2.4 + i + 0.5
        if i + 1 in mark:
            f.rect(x - 0.47, 0.3, 0.94, 2.75, fill=colors.Color(0.9, 0.9, 0.9), width=1.6)
        f.text(x, 2.7, str(i + 1), size=10)
        shirt(f, x - 0.3, 1.45, 0.6, 0.6, p1[i % len(p1)], width=0.7)
        shape(f, x, 0.8, 0.27, p2[i % len(p2)], width=0.5)
        if block and (i + 1) % block == 0 and i + 1 < n:
            f.line((x + 0.5, 0.2), (x + 0.5, 3.15), width=1.6, dash=True)
    return f.drawing()


# ------------------------------------------------------------------ variants
@variant(difficulty=1)
def both_count(rng, harder):
    """The original: how many children have T-shirt x and card y?"""
    a, b = rng.choice([(2, 3), (3, 4), (2, 5), (3, 5)]) if harder else (2, 3)
    L = lcm(a, b)
    n = L * rng.choice([k for k in range(4, 21) if L * k <= (120 if harder else 60)])
    p1, p2 = _pats(rng, a, b)
    x, y = rng.choice(p1), rng.choice(p2)
    per = sum(1 for i in range(L) if p1[i % a] == x and p2[i % b] == y)
    ans = n // L * per
    text = _text(n, p1, p2) + _ask(x, y)
    first = positions(p1, p2, L, x, y)[0]
    sol = (f"Both patterns start again together every {L} children. In each block of {L} only child number "
           f"{first} (then {first + L}, {first + 2 * L}, ...) has a {x} T-shirt and a {y} card. "
           f"{n} ÷ {L} = {n // L} blocks, so {ans}.")
    mistakes = [n // a, n // b, n // (a + b), 2 * ans, ans // 2, n // a + n // b, ans + 1]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1, order="asc")
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, count(p1, p2, n, x, y)))


@variant(difficulty=2)
def leftover(rng, harder):
    """The row does not end at the end of a block: count the leftover children too."""
    a, b = rng.choice([(3, 4), (2, 5), (3, 5)]) if harder else rng.choice([(2, 3), (3, 2)])
    L = lcm(a, b)
    while True:
        p1, p2 = _pats(rng, a, b)
        x, y = rng.choice(p1), rng.choice(p2)
        first = positions(p1, p2, L, x, y)[0]
        n = L * rng.randint(4, 12 if harder else 8) + rng.randint(1, L - 1)
        if n % L >= first:              # the leftover part contains one more match
            break
    full = n // L
    ans = count(p1, p2, n, x, y)
    text = _text(n, p1, p2) + _ask(x, y)
    sol = (f"The patterns start again together every {L} children; in each block child number {first} matches. "
           f"{n} = {full} × {L} + {n % L}: {full} full blocks give {full}, and in the {n % L} children left "
           f"over child {full * L + first} matches too. {full} + 1 = {ans}.")
    mistakes = [full, ans + 1, n // a, n // b, full - 1]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1, order="asc")
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, sum(1 for i in range(1, n + 1)
                                                   if p1[(i - 1) % a] == x and p2[(i - 1) % b] == y)))


@variant(difficulty=2)
def child_number(rng, harder):
    """What does child number k wear?"""
    a, b = rng.choice([(3, 4), (2, 5), (4, 3)]) if harder else (2, 3)
    p1, p2 = _pats(rng, a, b)
    n = 60 if not harder else 100
    k = rng.randint(n // 2, n)
    right = (p1[(k - 1) % a], p2[(k - 1) % b])
    # mistakes: off by one in one of the patterns
    wrong = {(p1[(k - 2) % a], right[1]), (right[0], p2[(k - 2) % b]), (p1[k % a], p2[k % b]),
             (right[0], p2[k % b]), (p1[k % a], right[1])} - {right}
    pool = [(v, g) for v in p1 for g in p2 if (v, g) != right and (v, g) not in wrong]
    wrong = list(wrong)
    rng.shuffle(wrong)
    rng.shuffle(pool)
    opts = (wrong + pool)[:4] + [right]
    rng.shuffle(opts)
    text = _text(n, p1, p2) + f"What does child number <b>{k}</b> wear?"
    sol = (f"The T-shirts repeat every {a}: {k} = {(k - 1) // a} × {a} + {(k - 1) % a + 1}, so the T-shirt is the "
           f"{(k - 1) % a + 1}{'st' if (k - 1) % a == 0 else 'nd' if (k - 1) % a == 1 else 'rd' if (k - 1) % a == 2 else 'th'} "
           f"one: {right[0]}. The cards repeat every {b}: {k} = {(k - 1) // b} × {b} + {(k - 1) % b + 1}, "
           f"so the card is a {right[1]}.")

    def walk(i):
        v = g = None
        for c in range(1, k + 1):
            v, g = p1[(c - 1) % a], p2[(c - 1) % b]
        return opts[i] == (v, g)
    return Question(text=text, choices=[f"{v} T-shirt, {g} card" for v, g in opts], answer=opts.index(right),
                    solution=sol, check=walk)


@variant(difficulty=2)
def kth_match(rng, harder):
    """Which number does the m-th matching child have?"""
    a, b = rng.choice([(3, 4), (2, 5), (3, 5)]) if harder else (2, 3)
    L = lcm(a, b)
    p1, p2 = _pats(rng, a, b)
    x, y = rng.choice(p1), rng.choice(p2)
    first = positions(p1, p2, L, x, y)[0]
    m = rng.randint(4, 9)
    ans = first + (m - 1) * L
    n = 100 if ans <= 100 else 200
    text = (_text(n, p1, p2) + f"Count only the children with a <b>{x}</b> T-shirt and a <b>{y}</b> card. "
            f"Which number in the row does the <b>{m}th</b> of them have?")
    sol = (f"The first one is child {first}. The patterns start again together every {L} children, so the next "
           f"ones are {first + L}, {first + 2 * L}, ... The {m}th: {first} + {m - 1} × {L} = {ans}.")
    mistakes = [first + m * L, m * L, ans - 1, ans + 1, first * m, m * a * b + first]
    choices, ai = numeric_choices(ans, [v for v in mistakes if v > 0], rng, lo=1, order="asc")
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, positions(p1, p2, n, x, y)[m - 1]))


@variant(difficulty=3)
def never_together(rng, harder):
    """Lengths with a common factor (2 and 4, 4 and 6): some pairs never happen."""
    a, b = rng.choice([(2, 4), (4, 6), (4, 2)]) if harder else rng.choice([(2, 4), (4, 2)])
    L = lcm(a, b)
    if a > len(VEST) or b > len(BAG):
        a, b = 2, 4
    p1, p2 = _pats(rng, a, b)
    n = L * rng.randint(5, 12)
    pairs = [(v, g) for v in p1 for g in p2]
    zero = [pr for pr in pairs if count(p1, p2, L, *pr) == 0]
    some = [pr for pr in pairs if pr not in zero]
    x, y = rng.choice(zero) if rng.random() < 0.6 else rng.choice(some)
    ans = n // L * count(p1, p2, L, x, y)
    text = _text(n, p1, p2) + _ask(x, y)
    pos = positions(p1, p2, L, x, y)
    sol = (f"Write the first children down: both patterns start again together already after {L} children "
           f"(not {a} × {b} = {a * b}). " +
           (f"In each block of {L} no child has a {x} T-shirt and a {y} card, so the answer is 0."
            if not pos else
            f"In each block of {L} child number {pos[0]} matches. {n} ÷ {L} = {n // L} blocks: {ans}."))
    mistakes = [n // (a * b), n // a, n // b, ans + n // L, 0, n // (a * b) * 2]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=0, order="asc")
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, count(p1, p2, n, x, y)))


@variant(difficulty=3)
def lamps(rng, harder):
    """A different story: two lamps flashing - when do they flash together?"""
    a, b = rng.choice([(4, 6), (6, 8), (6, 9), (3, 5), (4, 10)]) if harder else rng.choice([(2, 3), (3, 4), (4, 6), (2, 5)])
    L = lcm(a, b)
    n = L * rng.randint(3, 8)
    n = n if n <= 120 else L * 3
    text = (f"A big lamp flashes every {a} seconds and a small lamp flashes every {b} seconds. They flash "
            f"together right at the start. How many times do they flash <b>together</b> in the next {n} seconds? "
            f"(Count a flash exactly at second {n}, but not the one at the start.)")
    ans = n // L
    sol = (f"The big lamp flashes at {a}, {2 * a}, {3 * a}, ... and the small one at {b}, {2 * b}, {3 * b}, ... The first time both "
           f"flash is at second {L}" + (f" (not {a} × {b} = {a * b})" if L != a * b else "") +
           f", then every {L} seconds. {n} ÷ {L} = {ans}.")
    mistakes = [n // (a * b), n // a, n // b, n // a + n // b, ans + 1, ans - 1]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1, order="asc")
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, sum(1 for t in range(1, n + 1) if t % a == 0 and t % b == 0)))


# ------------------------------------------------------------------ teaching page
def teach():
    p1, p2 = ["white", "striped"], ["circle", "star", "triangle"]
    p3, p4 = ["white", "striped"], ["circle", "star", "triangle", "square"]
    return [
        ("h", "How to think about it: two patterns at the same time"),
        "In these questions two things repeat at the same time, for example the pattern on the T-shirt and the shape "
        "on the card. You have to find out how often a certain pair happens, like \"white T-shirt <b>and</b> "
        "triangle card\".",
        ("tip", "<b>The big idea:</b> two patterns together make one <b>longer pattern</b>. Find the block where "
                "<b>both start again at the same time</b>, count inside one block, then multiply."),
        ("h", "Step by step: the contest question"),
        ("-", "<b>1. Write it down.</b> Write the numbers 1, 2, 3, ... and draw both patterns under them. Stop when "
              "both patterns start again <b>at the same time</b>: child 7 looks exactly like child 1."),
        table_pic(p1, p2, 12, mark=(3, 9), block=6),
        ("-", "<b>2. The block is 6 children long.</b> After every 6 children everything repeats (the dashed line)."),
        ("-", "<b>3. Count in one block.</b> In children 1 to 6, only child 3 has a white T-shirt and a triangle "
              "card. So there is <b>1 in every block</b>."),
        ("-", "<b>4. Multiply.</b> 60 children = 60 ÷ 6 = 10 blocks. 10 × 1 = <b>10</b> children."),
        "Another way to see it: white T-shirts are children 1, 3, 5, 7, ... (odd numbers). Triangle cards are "
        "children 3, 6, 9, 12, ... Both: 3, 9, 15, 21, ... always 6 more.",
        ("h", "Watch out"),
        ("-", "<b>The block is not always \"one length × the other\".</b> 2 kinds of T-shirt and 4 kinds of "
              "card start again together after only <b>4</b> children, not 8. Then some pairs <b>never</b> "
              "happen. Here a striped T-shirt never gets a circle card:"),
        table_pic(p3, p4, 8, block=4),
        ("-", "<b>Children left over:</b> 64 children with a block of 6 is 10 blocks (60 children) and 4 more. "
              "Check those 4 one by one."),
        ("tip", "<b>Try it yourself:</b> take a pencil and draw the first 12 children of a pattern. Circle "
                "the ones you are looking for. Can you see the block?"),
    ]


# ------------------------------------------------------------------ warm-ups
@warmup
def w_one_pattern(rng, harder):
    """One pattern only: what shape does number k hold?"""
    p = rng.sample(BAG, 3)
    k = rng.randint(10, 20)
    right = p[(k - 1) % 3]
    others = [c for c in BAG if c not in p]
    opts = p + rng.sample(others, 2)
    text = (f"Children stand in a row. Their cards repeat like this: {_lst(p)} "
            f"What shape is on the card of child number {k}?")
    sol = (f"The shapes repeat every 3 children. {k} = {(k - 1) // 3} × 3 + {(k - 1) % 3 + 1}, so it is the "
           f"same as child {(k - 1) % 3 + 1}: {right}.")
    walk = [p[(c - 1) % 3] for c in range(1, k + 1)][-1]
    return Question(text=text, figure=children_pic(["white"], p, 7, scale=17), choices=opts,
                    answer=opts.index(right), solution=sol, check=lambda i: opts[i] == walk)


@warmup
def w_how_many_one(rng, harder):
    """One pattern only: how many children have card y?"""
    b = rng.choice([3, 4])
    p = rng.sample(BAG, b)
    y = rng.choice(p)
    n = b * rng.randint(6, 10)
    ans = n // b
    text = f"{n} children stand in a row. Their cards repeat like this: {_lst(p)} How many have a {y} card?"
    sol = f"In every {b} children there is one {y} card. {n} ÷ {b} = {ans}."
    choices, ai = numeric_choices(ans, [n // 2, ans + 1, ans - 1, n - ans, b], rng, lo=1, order="asc")
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, sum(1 for i in range(n) if p[i % b] == y)))


@warmup
def w_first_block(rng, harder):
    """Look at the picture of the first block and count the matches."""
    p1, p2 = _pats(rng, 2, 3)
    x, y = rng.choice(p1), rng.choice(p2)
    ans = count(p1, p2, 6, x, y)
    text = (f"Here are the first 6 children of a row. How many of them have a <b>{x}</b> T-shirt <b>and</b> a "
            f"<b>{y}</b> card?")
    sol = f"Look at each child: only child number {positions(p1, p2, 6, x, y)[0]}. So {ans}."
    choices, ai = numeric_choices(ans, [0, 2, 3, 4, 6], rng, lo=0, order="asc")
    return Question(text=text, figure=children_pic(p1, p2, 6), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, ans))


@warmup
def w_same_again(rng, harder):
    """When do both patterns start again together?"""
    p1, p2 = _pats(rng, 2, 3)
    text = (f"Look at the children. Child 1 has a {p1[0]} T-shirt and a {p2[0]} card. Which is the "
            f"<b>next</b> child with a {p1[0]} T-shirt and a {p2[0]} card?")
    nxt = positions(p1, p2, 20, p1[0], p2[0])[1]
    sol = (f"The T-shirt pattern starts again at 3, 5, 7, ... and the card pattern at 4, 7, 10, ... "
           f"Both together: child {nxt}.")
    choices, ai = numeric_choices(nxt, [3, 4, 5, 6, 8], rng, lo=2, order="asc")
    choices = [f"child {c}" for c in choices]
    return Question(text=text, figure=children_pic(p1, p2, 8), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, nxt))


@warmup
def w_skip_count(rng, harder):
    """The matches go up in steps: how many up to n?"""
    step = 6
    first = rng.choice([1, 2, 3, 4, 5, 6])
    n = 60
    ans = len(range(first, n + 1, step))
    text = (f"In a row of {n} children, the children with a white T-shirt and a star card have the numbers "
            f"{first}, {first + step}, {first + 2 * step}, {first + 3 * step}, ... (always {step} more). "
            f"How many of them are there?")
    sol = f"One in every block of {step}: {n} ÷ {step} = {ans}."
    value = sum(1 for c in range(1, n + 1) if (c - first) % step == 0 and c >= first)
    choices, ai = numeric_choices(ans, [ans - 1, ans + 1, n // 2, n // 3, 6], rng, lo=1, order="asc")
    return Question(text=text, choices=choices, answer=ai, solution=sol, check=value_check(choices, value))
