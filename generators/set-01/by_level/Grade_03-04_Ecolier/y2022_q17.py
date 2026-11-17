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

from kangaroo import Fig, Question, numeric_choices, text_choices, value_check, variant

META = {
    "source": "set-01/by_level/Grade_03-04_Ecolier/2022 Q17",
    "skill": "Fewest shapes for several rules: choose shapes that count for two rules at once, then check every \"exactly\"",
    "topics": ["logic", "counting"],
    "keywords": ["fewest shapes", "one shape, two rules", "exactly rules"],
    "sticker": ("🔺", "Shape picker"),   # earned when this skill is solid (website)
    "version": 2,
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
def draw(shapes):
    xs, x = [], 0.0
    for c, s, k in shapes:
        w = 1.0 if s == "big" else 0.38
        xs.append(x)
        x += w + 0.35
    f = Fig(x - 0.35, 1.0, max_px=min(330, 58 * (x - 0.35)), margin=6)
    for (c, s, k), x0 in zip(shapes, xs):
        w = 1.0 if s == "big" else 0.38
        fill = GREY if c == "grey" else colors.white
        if k == "square":
            f.rect(x0 + 0.04 * w, 0, 0.92 * w, 0.92 * w, fill=fill, width=1.0)
        elif k == "triangle":
            f.poly([(x0, 0), (x0 + w, 0), (x0 + w / 2, w * 0.9)], fill=fill, width=1.0)
        else:
            f.circle(x0 + w / 2, w / 2, w / 2, fill=fill, width=1.0)
    return f.drawing()


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


def most_solution(pz, free, used):
    """Why the largest number is what it is, in three steps the kids can follow."""
    rules = pz["rules"]
    words = [word(r) for r in rules]
    either = ", ".join(words[:-1]) + " or " + words[-1]
    caps = " + ".join(str(r[2]) for r in rules)
    total = sum(r[2] for r in rules)
    out = (f"Shapes that are not {either} break no rule, so take them all: "
           f"{', '.join(name(s) for s in free)} ({len(free)}). "
           f"Every other shape is {either}, and the rules allow exactly {rules_phrase(rules)}. "
           f"So at most {caps} = {total} more, and only if each of them is just one of these. ")
    if len(used) < total:
        short = [r for r in rules
                 if sum(1 for s in pz["shapes"] if fits(s, r) and sum(fits(s, q) for q in rules) == 1) < r[2]]
        r = short[0]
        only = [x for x in pz["shapes"] if fits(x, r) and sum(fits(x, q) for q in rules) == 1]
        rest = [w for w in words if w != word(r)]
        rest = ", ".join(rest[:-1]) + " or " + rest[-1] if len(rest) > 1 else rest[0]
        if only:
            out += (f"But only {name(only[0])} is just {word(r)}; every other shape that is {word(r)} "
                    f"is also {rest}. ")
        else:
            out += f"But no shape here is just {word(r)}: every shape that is {word(r)} is also {rest}. "
    tags = [f"{name(s)} ({' and '.join(word(r) for r in rules if fits(s, r))})" for s in used]
    out += (f"The best is {len(used)}: {', '.join(tags)}. "
            f"In all {len(free)} + {len(used)} = {len(free) + len(used)} shapes.")
    return out


# ------------------------------------------------------------------ variants
@variant(difficulty=1)
def two_rules(rng, harder):
    """Two rules only: one shape can do both."""
    pz = make(rng, rng.sample(list(ATTR), 2), 7 if harder else 6, 3 if harder else 2, tricky_min)
    who, text = intro(rng, pz)
    text += f"\n\nWhat is the smallest number of shapes {who} can have chosen?"
    ch, ans = numeric_choices(pz["min"], min_mistakes(pz), rng, lo=1)
    return Question(text=text, figure=draw(pz["shapes"]), choices=ch, answer=ans,
                    solution=min_solution(pz), difficulty=1,
                    check=value_check(ch, min(sizes(pz["shapes"], pz["rules"]))))


@variant(difficulty=2)
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


@variant(difficulty=2)
def most_shapes(rng, harder):
    """Turned around: the largest number. Shapes that fit no rule can always be added."""
    attrs = list(ATTR) if harder else rng.sample(list(ATTR), 2)
    pz = make(rng, attrs, 8 if harder else 7, 2,
              lambda z: z["max"] < len(z["shapes"]) and z["max"] > sum(r[2] for r in z["rules"])
              and z["max"] != z["min"])
    shapes, rules = pz["shapes"], pz["rules"]
    who, text = intro(rng, pz)
    text += f"\n\nWhat is the <b>largest</b> number of shapes {who} can have chosen?"
    free = [s for s in shapes if not any(fits(s, r) for r in rules)]
    group = next(g for g in combinations(shapes, pz["max"]) if ok(g, rules))
    used = [s for s in group if s not in free]
    sol = most_solution(pz, free, used)
    mistakes = [(len(shapes), "choose all the shapes"),
                (pz["min"], "find the smallest number instead of the largest"),
                (sum(r[2] for r in rules), "add up the numbers in the rules and forget the other shapes"),
                (len(free), "forget the shapes the rules talk about")]
    ch, ans = numeric_choices(pz["max"], mistakes, rng, lo=1)
    return Question(text=text, figure=draw(shapes), choices=ch, answer=ans, solution=sol,
                    difficulty=2, check=value_check(ch, max(sizes(shapes, rules))))


@variant(difficulty=3)
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
