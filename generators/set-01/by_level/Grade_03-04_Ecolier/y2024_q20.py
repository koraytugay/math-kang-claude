"""2024 Q20 (Ecolier, Grade 3-4) - cards of different shapes hide digits (a little cryptarithm).

Original: Cards of the same shape hide the same digits, cards with different shapes hide
different digits. Kim lays out the cards so that the calculations are correct:
    triangle + triangle = [square][circle]      (a two-digit number)
    circle + triangle   = [square][square]
What number does Kim get for triangle · circle · square?  A 0  B 15  C 18  D 28  E 30.
Two digits add up to at most 9 + 9 = 18, so square = 1. Then circle + triangle = 11 and
triangle + triangle = 1circle: trying triangle = 5..9 gives triangle = 7, circle = 4.
7 · 4 · 1 = 28.  Answer: D.

Core skill: reading cards as digits (two cards side by side = tens and ones), finding the
step that is forced first (a sum of two digits is at most 18, so a two-digit result starts
with 1), then trying the few values that are left in a small table and checking every
equation.
"""
from itertools import permutations

from reportlab.lib import colors

from kangaroo import Fig, Question, numeric_choices, value_check, variant, warmup

META = {
    "source": "set-01/by_level/Grade_03-04_Ecolier/2024 Q20",
    "skill": "Cards hiding digits: find the forced digit first (two digits add to at most 18), then try and check",
    "topics": ["arithmetic", "logic"],
    "keywords": ["hiding digits", "digit figuring out", "cryptarithm"],
    "version": 1,
}

SHAPES = ["tri", "circle", "square", "diamond"]
WORD = {"tri": "triangle", "circle": "circle", "square": "square", "diamond": "diamond"}
FILL = {"tri": colors.Color(0.72, 0.72, 0.72), "circle": colors.Color(0.55, 0.55, 0.55),
        "square": colors.Color(0.82, 0.82, 0.82), "diamond": colors.Color(0.65, 0.65, 0.65)}
NAMES = ["Kim", "Lucas", "Mia", "Tom", "Anna", "Ben", "Sara", "Leo"]
OPS = {"+": "+", "-": "–", "*": "·"}


# ------------------------------------------------------------------ equations
# An equation is (terms, op, rhs): terms = list of shapes, op in "+-*", rhs = list of shapes
# read as a number (two shapes side by side = a two-digit number).
def value(terms, op, a):
    v = a[terms[0]]
    for t in terms[1:]:
        v = v + a[t] if op == "+" else v - a[t] if op == "-" else v * a[t]
    return v


def number(cards, a):
    v = 0
    for c in cards:
        v = 10 * v + a[c]
    return v


def holds(eq, a):
    terms, op, rhs = eq
    if len(rhs) > 1 and a[rhs[0]] == 0:
        return False
    return value(terms, op, a) == number(rhs, a)


def solve(eqs, syms):
    """Answer check: try every way to give the shapes different digits 0-9."""
    out = []
    for digs in permutations(range(10), len(syms)):
        a = dict(zip(syms, digs))
        if all(holds(e, a) for e in eqs):
            out.append(a)
    return out


def make_puzzle(rng, k, n_eq, ops, two_digit=True, n_terms=(2,), tries=400):
    """Random equations, true for a random choice of digits, until exactly one solution is left."""
    syms = rng.sample(SHAPES, k)
    for _ in range(tries):
        a = dict(zip(syms, rng.sample(range(10), k)))
        rev = {d: s for s, d in a.items()}
        eqs = []
        for _ in range(60):
            op = rng.choice(ops)
            terms = [rng.choice(syms) for _ in range(rng.choice(n_terms))]
            if op == "-" and len(set(terms)) < len(terms):
                continue          # triangle - triangle = 0 is no puzzle
            if any(a[t] == 0 for t in terms) or (op == "*" and any(a[t] == 1 for t in terms)):
                continue
            v = value(terms, op, a)
            if v < 0 or v > 99:
                continue
            ds = [int(c) for c in str(v)]
            if any(d not in rev for d in ds) or (two_digit and len(ds) < 2 and not eqs):
                continue
            rhs = [rev[d] for d in ds]
            if len(rhs) == 1 and rhs[0] in terms:
                continue          # e.g. square + square = square: too strange
            eq = (terms, op, rhs)
            key = lambda e: (tuple(sorted(e[0])) if e[1] in "+*" else tuple(e[0]), e[1], tuple(e[2]))
            if key(eq) not in {key(e) for e in eqs}:     # no "a + b" and "b + a" twice
                eqs.append(eq)
            if len(eqs) == n_eq:
                break
        if len(eqs) < n_eq or {s for e in eqs for s in e[0] + e[2]} != set(syms):
            continue
        if len(solve(eqs, syms)) == 1:
            return syms, eqs, a
    raise RuntimeError("no puzzle found")


# ------------------------------------------------------------------ pictures
def card(f, kind, x, y, s=1.0):
    """A card shape in the box (x, y)-(x+s, y+s)."""
    fill = FILL[kind]
    if kind == "tri":
        f.poly([(x, y), (x + s, y), (x + s / 2, y + s * 0.95)], fill=fill, width=1.0)
    elif kind == "circle":
        f.circle(x + s / 2, y + s / 2, s / 2, fill=fill, width=1.0)
    elif kind == "square":
        f.rect(x + 0.04, y + 0.04, s - 0.08, s - 0.08, fill=fill, width=1.0)
    else:
        f.poly([(x + s / 2, y), (x + s, y + s / 2), (x + s / 2, y + s), (x, y + s / 2)], fill=fill, width=1.0)


def _row_items(eq):
    terms, op, rhs = eq
    items = []
    for i, t in enumerate(terms):
        if i:
            items.append(("op", OPS[op]))
        items.append(("card", t))
    items.append(("op", "="))
    items.append(("num", rhs))
    return items


def _width(items):
    w = 0.0
    for kind, v in items:
        w += 1.1 if kind == "card" else 0.9 if kind == "op" else (1.05 * len(v) if isinstance(v, list) else 0.9)
    return w


def eq_pic(rows, scale=20):
    """rows: equations, or ("ask", shapes, op) for the line with '= ?'."""
    lines = []
    for r in rows:
        if r[0] == "ask":
            _, syms, op = r
            items = []
            for i, s in enumerate(syms):
                if i:
                    items.append(("op", OPS[op]))
                items.append(("card", s))
            items += [("op", "="), ("num", "?")]
        else:
            items = _row_items(r)
        lines.append(items)
    W = max(_width(l) for l in lines)
    H = 1.5 * len(lines)
    f = Fig(W, H, scale=scale, margin=4, font_size=16)
    for li, items in enumerate(lines):
        y = H - 1.5 * (li + 1) + 0.25
        x = 0.0
        for kind, v in items:
            if kind == "card":
                card(f, v, x, y)
                x += 1.1
            elif kind == "op":
                f.text(x + 0.45, y + 0.5, v, size=16)
                x += 0.9
            elif v == "?":
                f.text(x + 0.3, y + 0.5, "?", size=16)
                x += 0.9
            else:
                for c in v:
                    card(f, c, x, y)
                    x += 1.05
    return f.drawing()


def _intro(name):
    return (f"Cards of the same shape hide the same digit, and cards with different shapes hide different "
            f"digits. Two cards side by side make a two-digit number. {name} lays out the cards so that the "
            f"calculations are correct. ")


def _sol_digits(a, syms):
    return ", ".join(f"{WORD[s]} = {a[s]}" for s in syms)


def _forced_hint(eqs):
    """A sentence about the first forced step, if there is one (sum of two digits with a 2-digit answer)."""
    for terms, op, rhs in eqs:
        if op == "+" and len(terms) == 2 and len(rhs) == 2:
            return (f"Two digits add up to at most 9 + 9 = 18, so the {WORD[rhs[0]]} at the front of the "
                    f"two-digit answer must be 1. ")
    return ""


def digit_choices(ans, mistakes, rng):
    """5 options that are all digits 0-9: the answer, the mistakes first, then other digits."""
    wrong = [m for m in dict.fromkeys(mistakes) if 0 <= m <= 9 and m != ans]
    rest = [d for d in range(10) if d != ans and d not in wrong]
    rng.shuffle(wrong)
    rng.shuffle(rest)
    opts = sorted((wrong + rest)[:4] + [ans])
    return [str(o) for o in opts], opts.index(ans)


# ------------------------------------------------------------------ variants
@variant(difficulty=1)
def find_digit(rng, harder):
    """Which digit is hidden under one shape?"""
    syms, eqs, a = make_puzzle(rng, 3, 2, ["+"])
    name = rng.choice(NAMES)
    s = rng.choice([x for x in syms if a[x] not in (0, 1)] or syms)
    ans = a[s]
    text = _intro(name) + f"Which digit is hidden under the <b>{WORD[s]}</b>?"
    sol = _forced_hint(eqs) + f"Then try the possible digits and check both calculations: {_sol_digits(a, syms)}."
    sol_check = solve(eqs, syms)[0][s]
    choices, ai = digit_choices(ans, [a[x] for x in syms if x != s] + [ans + 1, ans - 1, 10 - ans], rng)
    return Question(text=text, figure=eq_pic(eqs), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, sol_check))


@variant(difficulty=1)
def product_all(rng, harder):
    """The original: what is shape · shape · shape?"""
    syms, eqs, a = make_puzzle(rng, 3, 2, ["+", "-"] if harder else ["+"])
    name = rng.choice(NAMES)
    op = "*" if rng.random() < 0.7 else "+"
    ask = rng.sample(syms, 3)
    ans = value(ask, op, a)
    word = "·" if op == "*" else "+"
    text = _intro(name) + f"What number does {name} get for the last calculation?"
    sol = (_forced_hint(eqs) + f"Try the possible digits and check every calculation: {_sol_digits(a, syms)}. "
           f"So {f' {word} '.join(str(a[s]) for s in ask)} = {ans}.")
    b = solve(eqs, syms)[0]
    other = value(ask, "+" if op == "*" else "*", a)
    choices, ai = numeric_choices(ans, [other, ans + 1, ans - 1, 0, 2 * ans], rng, lo=0, order="asc")
    return Question(text=text, figure=eq_pic(eqs + [("ask", ask, op)]), choices=choices, answer=ai,
                    solution=sol, check=value_check(choices, value(ask, op, b)))


@variant(difficulty=2)
def plus_minus(rng, harder):
    """Plus and minus mixed: find a two-digit number made of cards."""
    syms, eqs, a = make_puzzle(rng, 3 if not harder else 4, 2 if not harder else 3, ["+", "-"])
    name = rng.choice(NAMES)
    while True:
        two = rng.sample(syms, 2)
        if a[two[0]] != 0:
            break
    ans = number(two, a)
    text = _intro(name) + f"Which two-digit number do the cards {WORD[two[0]]} and {WORD[two[1]]} make?"
    sol = (_forced_hint(eqs) + f"Try the possible digits and check every calculation: {_sol_digits(a, syms)}. "
           f"So the {WORD[two[0]]} is the tens digit and the {WORD[two[1]]} the ones digit: {ans}.")
    b = solve(eqs, syms)[0]
    rev = 10 * a[two[1]] + a[two[0]]
    choices, ai = numeric_choices(ans, [rev, a[two[0]] + a[two[1]], ans + 1, ans - 1, ans + 10], rng, lo=1,
                                  order="asc")
    fig = eq_pic(eqs)
    return Question(text=text, figure=fig, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, number(two, b)))


@variant(difficulty=2)
def times(rng, harder):
    """Multiplication cards, e.g. circle · circle = [triangle][circle]."""
    syms, eqs, a = make_puzzle(rng, 3, 2, ["*", "+"] if harder else ["*"])
    name = rng.choice(NAMES)
    ask = list(syms)
    ans = sum(a[s] for s in ask)
    text = _intro(name) + "What do you get if you add the digits of all three shapes?"
    sol = (f"Try the possible digits (start with the multiplication: which times-table result has these "
           f"digits?) and check every calculation: {_sol_digits(a, syms)}. {' + '.join(str(a[s]) for s in ask)} "
           f"= {ans}.")
    b = solve(eqs, syms)[0]
    choices, ai = numeric_choices(ans, [ans + 1, ans - 1, ans + 2, ans - 3], rng, lo=1, order="asc")
    return Question(text=text, figure=eq_pic(eqs + [("ask", ask, "+")]), choices=choices, answer=ai,
                    solution=sol, check=value_check(choices, sum(b[s] for s in ask)))


@variant(difficulty=3)
def four_cards(rng, harder):
    """Four shapes, three calculations."""
    syms, eqs, a = make_puzzle(rng, 4, 3, ["+", "-"] if not harder else ["+", "-", "*"], tries=300)
    name = rng.choice(NAMES)
    ask = rng.sample(syms, 3 if not harder else 4)
    op = "+"
    ans = value(ask, op, a)
    text = _intro(name) + f"What number does {name} get for the last calculation?"
    sol = (_forced_hint(eqs) + f"Start with the calculation where the fewest digits are possible, then check "
           f"all three: {_sol_digits(a, syms)}. {' + '.join(str(a[s]) for s in ask)} = {ans}.")
    b = solve(eqs, syms)[0]
    choices, ai = numeric_choices(ans, [ans + 1, ans - 1, ans + 2, ans - 2, ans + 9], rng, lo=0, order="asc")
    return Question(text=text, figure=eq_pic(eqs + [("ask", ask, op)]), choices=choices, answer=ai,
                    solution=sol, check=value_check(choices, value(ask, op, b)))


# ------------------------------------------------------------------ teaching page
def teach():
    orig = [(["tri", "tri"], "+", ["square", "circle"]), (["circle", "tri"], "+", ["square", "square"])]
    rows = [["triangle", "triangle + triangle", "so circle is", "circle + triangle", "is it 11?"]]
    for t in range(5, 10):
        c = 2 * t - 10
        rows.append([str(t), str(2 * t), str(c), str(c + t), "yes!" if c + t == 11 else "no"])
    return [
        ("h", "How to think about it: cards that hide digits"),
        "Each shape hides one digit (0 to 9). The same shape always hides the same digit, and different shapes "
        "hide different digits. Two cards side by side are a <b>two-digit number</b>: if the square is 1 and the "
        "circle is 4, then [square][circle] is 14.",
        ("tip", "<b>The big idea:</b> don't start guessing everywhere. First find the card that can only be "
                "<b>one</b> digit. Then try the few digits that are left, and <b>check every calculation</b>."),
        ("h", "Step by step: the contest question"),
        eq_pic(orig + [("ask", ["tri", "circle", "square"], "*")], scale=18),
        ("-", "<b>1. Find the forced card.</b> The biggest two digits are 9 + 9 = 18. So when two digits add up to "
              "a two-digit number, it starts with <b>1</b>. That means the square is <b>1</b>."),
        ("-", "<b>2. Write what you know.</b> Now the second line says circle + triangle = 11, and the first line "
              "says triangle + triangle = 1circle (a number from 10 to 18)."),
        ("-", "<b>3. Try the digits that are left in a table.</b> Triangle + triangle must be 10 or more, so the "
              "triangle is 5, 6, 7, 8 or 9."),
        ("table", rows),
        ("-", "<b>4. Only one row works:</b> triangle = 7, circle = 4, square = 1. Check: 7 + 7 = 14 and "
              "4 + 7 = 11. Both are right."),
        ("-", "<b>5. Answer the question.</b> 7 · 4 · 1 = <b>28</b>. (The dot · means times.)"),
        ("h", "Watch out"),
        ("-", "Different shapes = different digits. If two shapes come out the same, that try is wrong."),
        ("-", "A two-digit number never starts with 0."),
        ("-", "Always check your digits in <b>every</b> calculation, not only in one."),
        ("tip", "<b>Try it yourself:</b> make your own puzzle. Pick digits for a triangle and a circle, write two "
                "sums with the answers, then cover the digits with paper shapes. Can someone else solve it?"),
    ]


# ------------------------------------------------------------------ warm-ups
@warmup
def w_read_number(rng, harder):
    """Two cards side by side are tens and ones."""
    t, o = rng.sample(range(1, 10), 2)
    s1, s2 = rng.sample(SHAPES, 2)
    ans = 10 * t + o
    text = (f"The {WORD[s1]} hides the digit {t} and the {WORD[s2]} hides the digit {o}. "
            f"Which number do these two cards make?")
    f = Fig(2.2, 1.2, scale=24, margin=3)
    card(f, s1, 0, 0.1)
    card(f, s2, 1.05, 0.1)
    sol = f"The left card is the tens digit, the right card the ones digit: {t} tens and {o} ones = {ans}."
    choices, ai = numeric_choices(ans, [10 * o + t, t + o, t * o, 100 * t + o], rng, lo=1, order="asc")
    return Question(text=text, figure=f.drawing(), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, int(f"{t}{o}")))


@warmup
def w_biggest_sum(rng, harder):
    """The biggest sum of two different digits."""
    same = rng.random() < 0.5
    ans = 18 if same else 17
    text = ("What is the <b>biggest</b> number you can get by adding two digits?" if same else
            "What is the <b>biggest</b> number you can get by adding two <b>different</b> digits?")
    sol = "9 + 9 = 18." if same else "9 + 8 = 17 (9 + 9 is not allowed, the digits must be different)."
    value_ = max(a + b for a in range(10) for b in range(10) if same or a != b)
    choices, ai = numeric_choices(ans, [9, 19, 81, 99, 16, 18, 17], rng, lo=1, order="asc")
    return Question(text=text, choices=choices, answer=ai, solution=sol, check=value_check(choices, value_))


@warmup
def w_forced_one(rng, harder):
    """A two-digit sum of two digits starts with 1."""
    s1, s2, s3 = rng.sample(SHAPES, 3)
    eq = ([s1, s1], "+", [s2, s3])
    text = ("Cards of the same shape hide the same digit, different shapes hide different digits. "
            f"Which digit is hidden under the <b>{WORD[s2]}</b>?")
    sol = (f"{WORD[s1].capitalize()} + {WORD[s1]} is at most 9 + 9 = 18. A two-digit answer from 10 to 18 starts "
           f"with 1, so the {WORD[s2]} is 1.")
    tens = {sol_[s2] for sol_ in solve([eq], [s1, s2, s3])}
    opts = [0, 1, 2, 5, 9]
    return Question(text=text, figure=eq_pic([eq]), choices=[str(o) for o in opts], answer=1, solution=sol,
                    check=lambda i: tens == {opts[i]})


@warmup
def w_one_step(rng, harder):
    """One card is known: find the other."""
    s1, s2 = rng.sample(SHAPES, 2)
    t = rng.randint(6, 9)
    c = 2 * t - 10
    if c == 1 or c == t:
        t, c = 7, 4
    text = (f"The {WORD[s1]} hides {t}. It is true that {WORD[s1]} + {WORD[s1]} = 1 followed by the "
            f"{WORD[s2]} (a number between 10 and 19). Which digit is hidden under the {WORD[s2]}?")
    sol = f"{t} + {t} = {2 * t}, so the {WORD[s2]} is {c}."
    choices, ai = digit_choices(c, [t, c + 1, c - 1, 10 - c, 1], rng)
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, (t + t) % 10))


@warmup
def w_three_same(rng, harder):
    """circle + circle + circle = [square][circle]: only one digit works."""
    s1, s2 = rng.sample(SHAPES, 2)
    eq = ([s1, s1, s1], "+", [s2, s1])
    sols = solve([eq], [s1, s2])
    text = ("Cards of the same shape hide the same digit, different shapes hide different digits. "
            f"Which digit is hidden under the <b>{WORD[s1]}</b>?")
    sol = (f"Try the digits: 3 × {WORD[s1]} must end with the same digit as the {WORD[s1]}. "
           f"5 + 5 + 5 = 15 works (and 0 does not, because then the {WORD[s2]} would be 0 too). So it is 5.")
    choices, ai = digit_choices(5, [0, 3, 1, 9], rng)
    return Question(text=text, figure=eq_pic([eq]), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, sols[0][s1] if len(sols) == 1 else -1))
