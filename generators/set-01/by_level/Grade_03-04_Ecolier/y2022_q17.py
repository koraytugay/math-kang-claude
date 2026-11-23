"""2022 Q17 (Ecolier, Grade 3-4) - the fewest shapes that fit several "exactly" rules at once.

Original: Wanda chooses some of the following shapes (a small white square, a big grey
square, a small grey triangle, a big white triangle, a big white circle, a small grey circle).
She says: "I have chosen exactly 2 grey, 2 big and 2 round shapes."
What is the minimum number of shapes Wanda has chosen?  (A) 2 (B) 3 (C) 4 (D) 5 (E) 6
The two round shapes must be the big white circle and the small grey circle (1 grey, 1 big).
One more grey and one more big: the big grey square does both. 3 shapes.  Answer: B (3).

Core skill: one shape can count for several rules at once (the big grey square is grey AND
big). Children add the numbers (2 + 2 + 2 = 6) or forget the word "exactly" (then a shape
can make one rule go over). The method: start with
the rule that has the fewest shapes to choose from, then pick shapes that help with two rules
at once, and count every rule again at the end.
"""
from itertools import combinations

from reportlab.lib import colors

from kangaroo.choices import Choices
from kangaroo.figures import column, row

from kangaroo import Fig, Question, numeric_choices, text_choices, value_check, variant

META = {
    "source": "set-01/by_level/Grade_03-04_Ecolier/2022 Q17",
    "skill": "Fewest shapes for several rules: choose shapes that count for two rules at once, then check every \"exactly\"",
    "topics": ["logic", "counting"],
    "keywords": ["fewest shapes", "one shape, two rules", "exactly rules"],
    "sticker": ("🔺", "Shape picker"),   # earned when this skill is solid (website)
    "rungs": ("easier", "easier", "aligned", "harder"),   # vs the original contest question: steps 1, 2, 3, 3 harder (2026-11-23)
    "version": 3,
}

GREY = colors.Color(0.55, 0.55, 0.55)
KINDS = ["square", "triangle", "circle"]
NAMES = ["Wanda", "Lena", "Omar", "Pia", "Tim", "Zara", "Jonas", "Ella"]
ALL = [(c, s, k) for c in ("grey", "white") for s in ("big", "small") for k in KINDS]
ATTR = {"colour": 0, "size": 1, "kind": 2}
VALUES = {"colour": ["grey", "white"], "size": ["big", "small"], "kind": KINDS}


# ------------------------------------------------------------------ rules
def fits(shape, rule):
    attr, val, _ = rule
    return shape[ATTR[attr]] == val


def ok(chosen, rules, exact=True):
    for r in rules:
        n = sum(fits(s, r) for s in chosen)
        if (n != r[2]) if exact else (n < r[2]):
            return False
    return True


def sizes(shapes, rules, exact=True):
    """Answer check: every number of shapes that works (try every group of shapes)."""
    return {k for k in range(len(shapes) + 1)
            for group in combinations(shapes, k) if ok(group, rules, exact)}


def best(shapes, rules, exact=True, want=min):
    """Fewest (or most) shapes, by going through all subsets as bit masks."""
    found = []
    for mask in range(1 << len(shapes)):
        group = [s for i, s in enumerate(shapes) if mask >> i & 1]
        if ok(group, rules, exact):
            found.append(len(group))
    return want(found) if found else None


def rule_phrase(rule):
    attr, val, n = rule
    if attr == "kind":
        word = {"circle": "round shape", "triangle": "triangle", "square": "square"}[val]
    else:
        word = f"{val} shape"
    return f"{n} {word}{'' if n == 1 else 's'}"


def rules_phrase(rules):
    parts = [rule_phrase(r) for r in rules]
    return " and ".join(parts) if len(parts) < 3 else ", ".join(parts[:-1]) + " and " + parts[-1]


def name(shape):
    c, s, k = shape
    return f"the {s} {c} {k}"


# ------------------------------------------------------------------ picture
def _place(shapes):
    xs, x = [], 0.0
    for c, s, k in shapes:
        xs.append(x)
        x += (1.0 if s == "big" else 0.38) + 0.35
    return xs, x - 0.35


def _shapes(f, shapes, xs, dx=0.0, dy=0.0):
    for (c, s, k), x0 in zip(shapes, xs):
        w = 1.0 if s == "big" else 0.38
        x0 += dx
        fill = GREY if c == "grey" else colors.white
        if k == "square":
            f.rect(x0 + 0.04 * w, dy, 0.92 * w, 0.92 * w, fill=fill, width=1.0)
        elif k == "triangle":
            f.poly([(x0, dy), (x0 + w, dy), (x0 + w / 2, dy + w * 0.9)], fill=fill, width=1.0)
        else:
            f.circle(x0 + w / 2, dy + w / 2, w / 2, fill=fill, width=1.0)


def draw(shapes):
    xs, width = _place(shapes)
    f = Fig(width, 1.0, max_px=min(330, 58 * width), margin=6)
    _shapes(f, shapes, xs)
    return f.drawing()


def group_box(group, number, inner_w, scale=26):
    """One chosen group in a numbered box; every box has the same size and scale."""
    xs, width = _place(group)
    pad = 0.3
    f = Fig(inner_w + 2 * pad, 1.0 + 2 * pad + 0.35, scale=scale, margin=4)
    f.rect(0, 0, inner_w + 2 * pad, 1.0 + 2 * pad + 0.35, width=0.8)
    f.text(0.25, 1.0 + 2 * pad + 0.1, str(number), anchor="start", size=11)
    _shapes(f, group, xs, dx=pad + (inner_w - width) / 2, dy=pad)
    return f.drawing()


def groups_figure(shapes, groups):
    """The shapes to choose from, then the five groups in numbered boxes (3 + 2)."""
    inner = max(_place(g)[1] for g in groups)
    boxes = [group_box(g, i + 1, inner) for i, g in enumerate(groups)]
    return column([draw(shapes), row(boxes[:3], gap=10), row(boxes[3:], gap=10)], gap=10)


# ------------------------------------------------------------------ puzzles
def make(rng, attrs, n_shapes, max_n, accept):
    for _ in range(2000):
        shapes = rng.sample(ALL, n_shapes)
        rules = [(a, rng.choice(VALUES[a]), rng.randint(1, max_n)) for a in attrs]
        lo = best(shapes, rules)
        if lo is None:
            continue
        pz = {"shapes": shapes, "rules": rules, "min": lo, "max": best(shapes, rules, want=max),
              "loose": best(shapes, rules, exact=False)}
        if accept(pz):
            return pz
    raise RuntimeError("no puzzle")


def tricky_min(pz):
    counts = [r[2] for r in pz["rules"]]
    return max(counts) < pz["min"] < sum(counts)


def intro(rng, pz):
    who = rng.choice(NAMES)
    return who, (f"{who} chooses some of these shapes. {who} says: "
                 f"“I have chosen exactly {rules_phrase(pz['rules'])}.”")


def min_solution(pz):
    shapes, rules = pz["shapes"], pz["rules"]
    group = next(g for g in combinations(shapes, pz["min"]) if ok(g, rules))
    lines = []
    for r in rules:
        ins = [name(s) for s in group if fits(s, r)]
        lines.append(f"{rule_phrase(r)}: {', '.join(ins) if ins else 'none'}")
    many = [s for s in group if sum(fits(s, r) for r in rules) >= 2]
    tip = (f" {name(many[0]).capitalize()} counts for {sum(fits(many[0], r) for r in rules)} rules at once." if many else "")
    return (f"Fewest: {pz['min']} shapes, e.g. {', '.join(name(s) for s in group)}.{tip} "
            f"Check: {'; '.join(lines)}. With fewer shapes some rule is not met.")


def min_mistakes(pz):
    counts = [r[2] for r in pz["rules"]]
    m = [(sum(counts), "add up the numbers, as if each shape could count for one rule only"),
         (max(counts), "take the biggest number in the rules"),
         (len(pz["shapes"]), "choose all the shapes")]
    if pz["loose"] < pz["min"]:
        m.append((pz["loose"], "forget the word \"exactly\": one rule gets too many shapes"))
    return m


def word(rule):
    """The rule in one word: grey, small, round, triangle ..."""
    attr, val, _ = rule
    return {"circle": "round", "triangle": "a triangle", "square": "a square"}.get(val, val)


# ------------------------------------------------------------------ variants
@variant(difficulty=1, rungs=("easier", "easier"))
def two_rules(rng, harder):
    """Two rules only: one shape can do both."""
    pz = make(rng, rng.sample(list(ATTR), 2), 7 if harder else 6, 3 if harder else 2, tricky_min)
    who, text = intro(rng, pz)
    text += f"\n\nWhat is the smallest number of shapes {who} can have chosen?"
    ch, ans = numeric_choices(pz["min"], min_mistakes(pz), rng, lo=1)
    return Question(text=text, figure=draw(pz["shapes"]), choices=ch, answer=ans,
                    solution=min_solution(pz), difficulty=1,
                    check=value_check(ch, min(sizes(pz["shapes"], pz["rules"]))))


@variant(difficulty=2, rungs=("aligned", "aligned"))
def three_rules(rng, harder):
    """The original: colour, size and kind, each with an "exactly"."""
    pz = make(rng, list(ATTR), 8 if harder else 6, 3 if harder else 2,
              lambda z: tricky_min(z) and (z["min"] >= 4 or not harder))
    who, text = intro(rng, pz)
    text += f"\n\nWhat is the smallest number of shapes {who} can have chosen?"
    ch, ans = numeric_choices(pz["min"], min_mistakes(pz), rng, lo=1)
    return Question(text=text, figure=draw(pz["shapes"]), choices=ch, answer=ans,
                    solution=min_solution(pz), difficulty=2,
                    check=value_check(ch, min(sizes(pz["shapes"], pz["rules"]))))


@variant(difficulty=2, rungs=("easier", "easier"))
def which_group(rng, harder):
    """Check every "exactly": which group of shapes is exactly what she says?"""
    attrs = list(ATTR) if harder else rng.sample(list(ATTR), 2)
    for _ in range(200):
        pz = make(rng, attrs, 7 if harder else 6, 2, tricky_min)
        shapes, rules = pz["shapes"], pz["rules"]
        useful = [x for x in shapes if any(fits(x, r) for r in rules)]
        groups = [g for k in range(2, 5) for g in combinations(useful, k)]
        rights = [g for g in groups if ok(g, rules)]

        def off(g):   # the rules this group gets wrong, with how many it has
            return [(r, sum(fits(x, r) for x in g)) for r in rules if sum(fits(x, r) for x in g) != r[2]]
        near = [g for g in groups if len(off(g)) == 1 and abs(off(g)[0][1] - off(g)[0][0][2]) == 1]
        if rights and len(near) >= 4:
            break
    right = rng.choice(rights)
    rng.shuffle(near)
    # near misses that share shapes with the right group look the most tempting
    near.sort(key=lambda g: -len(set(g) & set(right)))
    wrong = near[:4]
    options = [right] + wrong
    rng.shuffle(options)
    ans = options.index(right)
    mistakes = {}
    for i, g in enumerate(options):
        if g != right:
            r, n = off(g)[0]
            mistakes[i] = f"miss that this group has {rule_phrase((r[0], r[1], n))}, not {r[2]}"
    who, text = intro(rng, pz)
    text += f"\n\nWhich group of shapes can {who} have chosen?"
    lines = [f"{rule_phrase((r[0], r[1], sum(fits(x, r) for x in right)))} "
             f"({', '.join(name(x) for x in right if fits(x, r))})" for r in rules]
    sol = (f"Count every rule for every group - one shape can count for two rules. "
           f"Group {ans + 1} has {'; '.join(lines)}. "
           + " ".join(f"Group {i + 1}: {rule_phrase((off(g)[0][0][0], off(g)[0][0][1], off(g)[0][1]))}."
                      for i, g in enumerate(options) if g != right))
    ch = Choices([f"group {i + 1}" for i in range(5)], mistakes)

    def check(i):   # count each rule again, shape by shape, for the drawn group
        return all(sum(1 for x in options[i] if x[ATTR[a]] == v) == n for a, v, n in rules)
    return Question(text=text, figure=groups_figure(shapes, options), choices=ch, answer=ans,
                    solution=sol, difficulty=2, check=check)


@variant(difficulty=3, rungs=("aligned", "harder"))
def must_choose(rng, harder):
    """Which shape is in every smallest choice? (It counts for two rules at once.)"""
    def accept(z):
        if not tricky_min(z):
            return False
        groups = [g for g in combinations(z["shapes"], z["min"]) if ok(g, z["rules"])]
        must = [s for s in z["shapes"] if all(s in g for g in groups)]
        never = [s for s in z["shapes"] if s not in must]
        z["groups"], z["must"] = groups, must
        return len(must) >= 1 and len(never) >= 4 and \
            any(sum(fits(s, r) for r in z["rules"]) >= 2 for s in must)
    pz = make(rng, list(ATTR), 8 if harder else 7, 2, accept)
    shapes, rules = pz["shapes"], pz["rules"]
    right = next(s for s in pz["must"] if sum(fits(s, r) for r in rules) >= 2)
    others = [s for s in shapes if s not in pz["must"]]
    wrong = []
    for s in others:
        hits = sum(fits(s, r) for r in rules)
        if hits >= 2:
            wrong.append((name(s), "pick a shape that fits two rules without checking all the rules for the whole choice"))
        elif hits == 1:
            wrong.append((name(s), "pick a shape that helps with only one rule"))
        else:
            wrong.append((name(s), "pick a shape that fits none of the rules"))
    rng.shuffle(wrong)
    who, text = intro(rng, pz)
    text += (f" {who} has chosen as few shapes as possible."
             f"\n\nWhich shape has {who} <b>surely</b> chosen?")
    ch, ans = text_choices(name(right), wrong[:4], rng)
    groups = pz["groups"]
    sol = (f"The fewest is {pz['min']} shapes. {name(right).capitalize()} counts for "
           f"{sum(fits(right, r) for r in rules)} rules at once and is in every way to do it with "
           f"{pz['min']} shapes, e.g. {', '.join(name(s) for s in groups[0])}.")

    def check(i):   # in every smallest group that fits all rules (found again by brute force)
        lo = min(sizes(shapes, rules))
        shape = next(s for s in shapes if name(s) == ch[i])
        return all(shape in g for g in combinations(shapes, lo) if ok(g, rules))
    return Question(text=text, figure=draw(shapes), choices=ch, answer=ans, solution=sol,
                    difficulty=3, check=check)
