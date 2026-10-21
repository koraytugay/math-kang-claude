"""2007 Q5 - work backwards through a chain of calculations.

Original: Emma wrote her favourite number in the dark cloud and did the
calculations in the diagram: start -2, then :3, then +4, and got 5. What is
Emma's favourite number?  A 1  B 3  C 5  D 7  E 9.
Backwards: 5 - 4 = 1, 1 x 3 = 3, 3 + 2 = 5.  Answer: C (5).

Core skill: undoing a chain of operations - go backwards from the end and use
the opposite operation at each step (+ becomes -, : becomes x). Children run the
chain forwards on the end number, or undo the steps in the wrong order.
"""
from reportlab.graphics.shapes import Ellipse
from reportlab.lib import colors

from fractions import Fraction

from kangaroo import Fig, Question, numeric_choices, text_choices, value_check, variant
from kangaroo.choices import number_in

META = {
    "source": "2007 Q5",
    "skill": "Working backwards: undo each operation, last one first",
    "topics": ["arithmetic", "logic"],
    "version": 2,
}

NAMES = ["Emma", "Mia", "Leo", "Sara", "Tom", "Nina"]
SYM = {"+": "+", "-": "−", "*": "×", "/": "÷"}


def apply(x, op):
    o, k = op
    return {"+": x + k, "-": x - k, "*": x * k, "/": x // k}[o]


def undo(x, op):
    o, k = op
    return {"+": x - k, "-": x + k, "*": x // k, "/": x * k}[o]


def run_exact(x, ops):
    """Answer checks: do the arrows forwards with exact fractions; None if a step is not a whole
    number of at least 0 (a child could not do that step)."""
    x = Fraction(x)
    for o, k in ops:
        x = {"+": x + k, "-": x - k, "*": x * k, "/": x / k}[o]
        if x < 0 or x.denominator != 1:
            return None
    return x


def label(op):
    return f"{SYM[op[0]]} {op[1]}"


def _chain(rng, n, harder):
    """A start value and n operations that keep every step a whole number >= 0."""
    for _ in range(500):
        start = rng.randint(2, 30 if harder else 15)
        x, ops = start, []
        ok = True
        for _ in range(n):
            choices = [("+", rng.randint(1, 9)), ("-", rng.randint(1, 9)), ("*", rng.randint(2, 4))]
            divs = [d for d in (2, 3, 4, 5) if x % d == 0 and x > 0]
            if divs:
                choices.append(("/", rng.choice(divs)))
            op = rng.choice(choices)
            if op[0] in "+-" and ops and ops[-1][0] in "+-":
                op = rng.choice([c for c in choices if c[0] in "*/"] or choices)
            y = apply(x, op)
            if y < 0 or y > 99:
                ok = False
                break
            ops.append(op)
            x = y
        kinds = {o for o, _ in ops}
        if ok and len(kinds) >= 2 and ("*" in kinds or "/" in kinds):
            return start, ops, x
    raise RuntimeError("no chain found")


def chain_pic(ops, first="", last="", dark_first=True, hide=None, hide_number=False):
    """Clouds joined by arrows labelled with the operations. hide: index of an op shown as '?'
    (or, with hide_number, as its sign followed by '?')."""
    n = len(ops)
    cw, gap = 3.0, 3.4
    W = (n + 1) * cw + n * gap
    f = Fig(W, 2.6, scale=11, margin=4)
    for i in range(n + 1):
        cx = i * (cw + gap) + cw / 2
        fill = colors.Color(0.35, 0.35, 0.35) if (i == 0 and dark_first) else colors.white
        f.d.add(_ellipse(f, cx, 1.0, cw / 2, 0.8, fill))
        txt = first if i == 0 else (last if i == n else "")
        if txt:
            f.text(cx, 1.0, txt, size=12)
        if i < n:
            x0, x1 = cx + cw / 2 + 0.2, cx + cw / 2 + gap - 0.2
            f.line((x0, 1.0), (x1 - 0.3, 1.0), width=1.6)
            f.poly([(x1 - 0.5, 1.3), (x1, 1.0), (x1 - 0.5, 0.7)], fill=colors.black, width=0.5)
            shown = label(ops[i]) if hide != i else (f"{SYM[ops[i][0]]} ?" if hide_number else "?")
            f.text((x0 + x1) / 2, 2.15, shown, size=12)
    return f.drawing()


def _ellipse(f, cx, cy, rx, ry, fill):
    px, py = f.p(cx, cy)
    return Ellipse(px, py, rx * f.scale, ry * f.scale, fillColor=fill, strokeColor=colors.black,
                   strokeWidth=1.0)


def _back_steps(ops, end):
    x, parts = end, []
    for op in reversed(ops):
        y = undo(x, op)
        o = {"+": "−", "-": "+", "*": "÷", "/": "×"}[op[0]]
        parts.append(f"{x} {o} {op[1]} = {y}")
        x = y
    return parts


def _forward_on_end(ops, end):
    """The mistake of running the chain forwards on the end number."""
    x = end
    for op in ops:
        if op[0] == "/" and x % op[1]:
            return -1
        x = apply(x, op)
    return x


def _wrong_order(ops, end):
    """Undo the steps but starting from the first operation."""
    x = end
    for op in ops:
        if op[0] == "*" and x % op[1]:
            return -1
        x = undo(x, op)
    return x


@variant(difficulty=1)
def favourite_number(rng, harder):
    """The original: find the start."""
    n = 4 if harder else 3
    start, ops, end = _chain(rng, n, harder)
    name = rng.choice(NAMES)
    text = (f"{name} wrote a favourite number in the dark cloud and did the calculations shown by the "
            f"arrows, one after the other. The result was {end}.")
    after = f"What is {name}'s favourite number?"
    sol = "Go backwards and do the opposite: " + ", ".join(_back_steps(ops, end)) + "."
    mistakes = [_forward_on_end(ops, end), _wrong_order(ops, end), start + 1, start - 1, end]
    choices, ai = numeric_choices(start, [m for m in mistakes if m >= 0], rng, lo=0)
    return Question(text=text, figure=chain_pic(ops, last=str(end)), after_figure=after,
                    choices=choices, answer=ai, solution=sol,
                    check=lambda i: run_exact(number_in(choices[i]), ops) == end)


@variant(difficulty=1)
def forwards(rng, harder):
    """Warm-up: run the chain forwards."""
    n = 4 if harder else 3
    start, ops, end = _chain(rng, n, harder)
    text = "Follow the arrows and do each calculation in turn."
    after = "Which number comes out at the end?"
    x, parts = start, []
    for op in ops:
        y = apply(x, op)
        parts.append(f"{x} {SYM[op[0]]} {op[1]} = {y}")
        x = y
    sol = ", ".join(parts) + "."
    mistakes = [_wrong_order(ops, start), end + 1, end - 1, start]
    choices, ai = numeric_choices(end, [m for m in mistakes if m >= 0], rng, lo=0)
    return Question(text=text, figure=chain_pic(ops, first=str(start), dark_first=False),
                    after_figure=after, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, run_exact(start, ops)))


@variant(difficulty=2)
def think_of_a_number(rng, harder):
    """The same chain told as a story, no picture."""
    n = 3 if harder else 2
    start, ops, end = _chain(rng, n, harder)
    name = rng.choice(NAMES)
    words = {"+": "adds {k}", "-": "takes away {k}", "*": "multiplies by {k}", "/": "divides by {k}"}
    steps = [words[o].format(k=k) for o, k in ops]
    text = (f"{name} thinks of a number, " + ", then ".join(steps) + f", and gets {end}.")
    after = f"Which number did {name} think of?"
    sol = "Go backwards: " + ", ".join(_back_steps(ops, end)) + "."
    mistakes = [_forward_on_end(ops, end), _wrong_order(ops, end), start + 2, end]
    choices, ai = numeric_choices(start, [m for m in mistakes if m >= 0], rng, lo=0)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol,
                    check=lambda i: run_exact(number_in(choices[i]), ops) == end)


@variant(difficulty=2)
def missing_number(rng, harder):
    """Start and end known; the number in one arrow is hidden."""
    n = 3
    for _ in range(200):
        start, ops, end = _chain(rng, n, harder)
        h = rng.randrange(n)
        o, k = ops[h]
        # the hidden number must be the only one that works
        works = [kk for kk in range(1, 30) if _run(start, ops[:h] + [(o, kk)] + ops[h + 1:]) == end]
        if works == [k]:
            break
    else:
        raise RuntimeError("no chain found")
    text = "The arrows show calculations done one after the other. One number is hidden."
    after = "Which number is hidden behind the question mark?"
    before = _run(start, ops[:h])
    after_val = apply(before, (o, k))
    sol = (f"Forwards from {start} we reach {before} before the hidden step; backwards from {end} we reach "
           f"{after_val} after it. {before} {SYM[o]} {k} = {after_val}.")
    mistakes = [k + 1, k - 1, k + 2, abs(end - start)]
    choices, ai = numeric_choices(k, [m for m in mistakes if m > 0], rng, lo=1)
    return Question(text=text, figure=chain_pic(ops, first=str(start), last=str(end), dark_first=False,
                                                hide=h, hide_number=True),
                    after_figure=after, choices=choices, answer=ai, solution=sol,
                    check=lambda i: run_exact(start, ops[:h] + [(o, number_in(choices[i]))] + ops[h + 1:]) == end)


def _run(x, ops):
    for op in ops:
        if op[0] == "/" and (x % op[1] or x < 0):
            return None
        x = apply(x, op)
        if x < 0:
            return None
    return x


@variant(difficulty=3)
def which_operation(rng, harder):
    """Which operation is missing so that start becomes end?"""
    for _ in range(300):
        start, ops, end = _chain(rng, 3, harder)
        h = rng.randrange(3)
        cands = [("+", k) for k in range(1, 10)] + [("-", k) for k in range(1, 10)] + \
                [("*", k) for k in (2, 3, 4, 5)] + [("/", k) for k in (2, 3, 4, 5)]
        good = [c for c in cands if _run(start, ops[:h] + [c] + ops[h + 1:]) == end]
        if good == [ops[h]]:
            wrong = [c for c in cands if c not in good and _run(start, ops[:h] + [c] + ops[h + 1:]) is not None]
            if len(wrong) >= 4:
                break
    else:
        raise RuntimeError("no chain found")
    near = sorted(wrong, key=lambda c: (c[1] != ops[h][1], c[0] == ops[h][0], rng.random()))[:4]
    choices, ai = text_choices(label(ops[h]), [label(c) for c in near], rng)
    text = ("The arrows show calculations done one after the other, but one arrow has lost its "
            "calculation: it shows a question mark.")
    after = "Which calculation belongs on that arrow?"
    before = _run(start, ops[:h])
    sol = (f"Before that arrow we have {before}; working back from {end}, after it we need "
           f"{apply(before, ops[h])}. Only {label(ops[h])} turns {before} into {apply(before, ops[h])}.")
    return Question(text=text, figure=chain_pic(ops, first=str(start), last=str(end), dark_first=False, hide=h),
                    after_figure=after, choices=choices, answer=ai, solution=sol,
                    check=lambda i: run_exact(start, ops[:h] + [{label(c): c for c in cands}[choices[i]]] + ops[h + 1:]) == end)
