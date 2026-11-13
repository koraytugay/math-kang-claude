"""2023 Q19 (Ecolier, Grade 3-4) - count the orders that keep all the rules.

Original: Three boys enter a room one after the other. Hermann is not the first. Felix is not
the second. Clemens is not the third. How many different orders are there for the boys to enter
the room?  (A) 1  (B) 2  (C) 3  (D) 4  (E) 6.
All 6 orders: HFC, HCF, FHC, FCH, CHF, CFH. Crossing out the ones that break a rule leaves
FCH and CHF.  Answer: B (answer key: B).

Core skill: list ALL possible orders in a system (fix who is first, then who is second, ...) and
cross out the ones that break a rule. Children guess (6 - 3 = 3, or "take away 2 for each rule"
= 0) or stop after finding one order.
"""
from itertools import permutations

from kangaroo import Question, numeric_choices, text_choices, value_check, variant, warmup

META = {
    "source": "set-01/by_level/Grade_03-04_Ecolier/2023 Q19",
    "skill": "Write down every possible order in a system (who is first, then second, ...) "
             "and cross out the ones that break a rule",
    "topics": ["logic", "counting"],
    "keywords": ["counting orders", "list them all", "not first rules"],
    "version": 2,
}

BOYS = ["Hermann", "Felix", "Clemens", "Tom", "Max", "Leo", "Ben", "Paul"]
GIRLS = ["Anna", "Mia", "Lea", "Sara", "Emma", "Zoe", "Lena", "Nora"]
POS = ["first", "second", "third", "fourth", "fifth"]
STORIES = [
    ("{n} children, {who}, enter a room one after the other.", "enter the room"),
    ("{n} children, {who}, run a race. There are no ties.", "finish the race"),
    ("{n} children, {who}, stand in a queue at the ice cream van, one behind the other.", "stand in the queue"),
]
NUM = ["", "", "Two", "Three", "Four", "Five"]


def intro(story, names):
    return story.format(n=NUM[len(names)], who=", ".join(names[:-1]) + " and " + names[-1])


def clean(rules):
    """No repeated rules and no two rules about the same child's place."""
    if len(set(rules)) < len(rules):
        return False
    places = [(r[1], r[2]) for r in rules if r[0] in ("not", "is")]
    fixed = [r[1] for r in rules if r[0] == "is"]
    if len(set(places)) < len(places) or any(sum(1 for a, _ in places if a == f) > 1 for f in fixed):
        return False
    pairs = [frozenset(r[1:]) for r in rules if r[0] not in ("not", "is")]
    return len(set(pairs)) == len(pairs)


def _names(rng, n):
    return rng.sample(BOYS + GIRLS, n)


# ------------------------------------------------------------------ rules
def rule_text(r, n):
    kind = r[0]
    if kind == "not":
        _, a, p = r
        return f"{a} is not the {POS[p]}."
    if kind == "is":
        _, a, p = r
        return f"{a} is the {POS[p]}."
    if kind == "before":
        _, a, b = r
        return f"{a} is somewhere before {b}."
    if kind == "after":
        _, a, b = r
        return f"{a} comes right after {b}."
    if kind == "apart":
        _, a, b = r
        return f"{a} and {b} are not next to each other."
    raise ValueError(kind)


def keeps(order, r):
    """Brute force: does the order (a tuple of names) keep rule r?"""
    kind = r[0]
    if kind == "not":
        return order[r[2]] != r[1]
    if kind == "is":
        return order[r[2]] == r[1]
    if kind == "before":
        return order.index(r[1]) < order.index(r[2])
    if kind == "after":
        return order.index(r[1]) == order.index(r[2]) + 1
    if kind == "apart":
        return abs(order.index(r[1]) - order.index(r[2])) != 1
    raise ValueError(kind)


def count_orders(names, rules):
    """Check side: try every order."""
    return sum(1 for o in permutations(names) if all(keeps(o, r) for r in rules))


def _tree(names, rules):
    """Generator side: build the orders place by place (like a tree), checking 'not'/'is' rules as soon
    as the place is filled and the other rules at the end."""
    out = []
    def go(prefix):
        k = len(prefix)
        if k and any(r[0] in ("not", "is") and r[2] == k - 1 and not keeps(prefix + (None,) * (len(names) - k), r)
                     for r in rules):
            return
        if k == len(names):
            if all(keeps(prefix, r) for r in rules):
                out.append(prefix)
            return
        for x in names:
            if x not in prefix:
                go(prefix + (x,))
    go(())
    return out


def _rules(rules, n):
    """The rules as a bulleted list (see kangaroo.layout), then the question in a new paragraph."""
    return "\n" + "\n".join(f"- {rule_text(r, n)}" for r in rules) + "\n\n"


def _fmt(order):
    return ", ".join(order)


# ------------------------------------------------------------------ variants
@variant(difficulty=1)
def not_rules(rng, harder):
    """The original: each child has a place they are not in; how many orders?"""
    n = 4 if harder else 3
    names = _names(rng, n)
    while True:
        k = rng.choice([2, 3]) if not harder else rng.choice([3, 4])
        who = rng.sample(names, k)
        rules = [("not", a, rng.randrange(n)) for a in who]
        ans = len(_tree(names, rules))
        if 1 <= ans and len({r[2] for r in rules}) >= 2 and clean(rules):
            break
    story, verb = rng.choice(STORIES)
    text = (intro(story, names) + _rules(rules, n) +
            f"How many different orders are there for the children to {verb}?")
    total = len(list(permutations(names)))
    per = total // n
    sol = (f"Write down all {total} orders, for example sorted by who is first. Then cross out every order "
           f"that breaks a rule. {ans} {'order is' if ans == 1 else 'orders are'} left"
           + (f": {'; '.join(_fmt(o) for o in _tree(names, rules))}." if n == 3 else "."))
    mistakes = [(total, "forget the rules"), (total - k, "cross out only one order for each rule"),
                (max(total - per * k, 0), "cross out the orders for each rule, but count some orders twice"),
                (1, "stop after finding one order")]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=0, order="asc")
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, count_orders(names, rules)))


@variant(difficulty=1)
def which_order(rng, harder):
    """Which of these orders keeps all the rules?"""
    n = 4 if harder else 3
    while True:
        names = _names(rng, n)
        kinds = ["not", "not", "before", "is"] + (["after", "apart"] if harder else [])
        rules = []
        for _ in range(3 if harder else 2):
            kd = rng.choice(kinds)
            a, b = rng.sample(names, 2)
            rules.append((kd, a, rng.randrange(n)) if kd in ("not", "is") else (kd, a, b))
        good = _tree(names, rules)
        bad = [o for o in permutations(names) if o not in good]
        if len(good) >= 1 and len(bad) >= 4 and clean(rules):
            break
    right = rng.choice(good)
    # wrong options: orders that break exactly one rule if possible
    one = [o for o in bad if sum(not keeps(o, r) for r in rules) == 1]
    pool = one if len(one) >= 4 else bad
    wrong = rng.sample(pool, 4)
    story, verb = rng.choice(STORIES)
    text = (intro(story, names) + _rules(rules, n) +
            "In which order can they be?")
    choices, ai = text_choices(_fmt(right), [(_fmt(o), "miss one of the rules") for o in wrong], rng)
    sol = f"Check each order against every rule. Only {_fmt(right)} keeps all of them."
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=lambda i: all(keeps(tuple(choices[i].split(", ")), r) for r in rules))


@variant(difficulty=2)
def four_children(rng, harder):
    """Four (or five) children with mixed rules: how many orders?"""
    n = 5 if harder else 4
    while True:
        names = _names(rng, n)
        rules = []
        for _ in range(rng.choice([2, 3])):
            kd = rng.choice(["not", "not", "before", "after", "is"])
            a, b = rng.sample(names, 2)
            rules.append((kd, a, rng.randrange(n)) if kd in ("not", "is") else (kd, a, b))
        if not clean(rules):
            continue
        ans = len(_tree(names, rules))
        if 2 <= ans <= (12 if harder else 8):
            break
    story, verb = rng.choice(STORIES)
    text = (intro(story, names) + _rules(rules, n) +
            f"How many different orders are there for the children to {verb}?")
    sol = (f"Go step by step: first use the strongest rule (a fixed place or 'right after'), then try the "
           f"others in a system. Exactly {ans} orders keep all the rules.")
    total = len(list(permutations(names)))
    mistakes = [(ans - 1, "miss one of the orders"), (ans + 1, "count one order twice"),
                (ans * 2, "let two children swap who should not"), (1, "stop after finding one order")]
    if total <= 30:
        mistakes.append((total, "forget the rules"))
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1, order="asc")
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, count_orders(names, rules)))


@variant(difficulty=2)
def who_is(rng, harder):
    """The rules allow only one order: who is in a given place?"""
    n = 4 if harder else 3
    while True:
        names = _names(rng, n)
        rules = []
        for _ in range(n if harder else 3):
            kd = rng.choice(["not", "not", "before", "after"])
            a, b = rng.sample(names, 2)
            rules.append((kd, a, rng.randrange(n)) if kd == "not" else (kd, a, b))
        good = _tree(names, rules)
        if len(good) == 1 and clean(rules):
            break
    order = good[0]
    p = rng.randrange(n)
    story, verb = rng.choice(STORIES)
    text = (intro(story, names) + _rules(rules, n) +
            f"Who is the {POS[p]}?")
    extra = [x for x in BOYS + GIRLS if x not in names]
    wrong = [(x, "mix up the places") for x in names if x != order[p]]
    wrong += [(x, "pick a name that is not in the story") for x in rng.sample(extra, 5 - n)]
    choices, ai = text_choices(order[p], wrong, rng)
    sol = f"Only one order keeps all the rules: {_fmt(order)}. So the {POS[p]} is {order[p]}."
    def check(i):
        ok = [o for o in permutations(names) if all(keeps(o, r) for r in rules)]
        return len(ok) == 1 and ok[0][p] == choices[i]
    return Question(text=text, choices=choices, answer=ai, solution=sol, check=check)


@variant(difficulty=3)
def one_more_rule(rng, harder):
    """Reverse: which extra rule leaves exactly one order?"""
    n = 4 if harder else 3
    while True:
        names = _names(rng, n)
        rules = [("not", a, rng.randrange(n)) for a in rng.sample(names, 2)]
        if not clean(rules):
            continue
        if harder:
            a, b = rng.sample(names, 2)
            rules.append(("before", a, b))
        good = _tree(names, rules)
        if not 2 <= len(good) <= 6:
            continue
        cands = set()
        for a in names:
            for p in range(n):
                cands |= {("is", a, p), ("not", a, p)}
            for b in names:
                if a != b:
                    cands |= {("before", a, b), ("after", a, b)}
        cands = sorted(c for c in cands if clean(rules + [c]))
        res = {c: sum(1 for o in good if keeps(o, c)) for c in cands}
        right = [c for c in cands if res[c] == 1]
        wrong0 = [c for c in cands if res[c] == 0]
        wrong2 = [c for c in cands if res[c] >= 2]
        if right and len(wrong2) >= 3 and wrong0:
            break
    r = rng.choice(right)
    wrong = rng.sample(wrong2, 3 if len(wrong0) == 0 else 2) + rng.sample(wrong0, 1 if len(wrong0) else 0)
    while len(wrong) < 4:
        wrong.append(rng.choice([w for w in wrong2 if w not in wrong]))
    story, verb = rng.choice(STORIES)
    text = (intro(story, names) + _rules(rules, n) +
            "Which extra sentence makes sure that there is exactly <b>one</b> possible order?")
    labels = [(rule_text(w, n), "check only one order" if res[w] >= 2 else "make a rule that leaves no order at all")
              for w in wrong]
    choices, ai = text_choices(rule_text(r, n), labels, rng)
    sol = (f"First list the {len(good)} orders that keep the rules: {'; '.join(_fmt(o) for o in good)}. "
           f"Only the sentence \"{rule_text(r, n)}\" leaves exactly one of them.")
    by_text = {rule_text(c, n): c for c in cands}
    def check(i):
        c = by_text[choices[i]]
        return count_orders(names, rules + [c]) == 1
    return Question(text=text, choices=choices, answer=ai, solution=sol, check=check)


# ------------------------------------------------------------------ teaching page
def teach():
    names = ["Hermann", "Felix", "Clemens"]
    rules = [("not", "Hermann", 0), ("not", "Felix", 1), ("not", "Clemens", 2)]
    rows = [["first", "second", "third", "breaks a rule?"]]
    for o in permutations(names):
        broken = [rule_text(r, 3)[:-1] for r in rules if not keeps(o, r)]
        rows.append(list(o) + [("yes: " + "; ".join(broken)) if broken else "<b>no - this order works</b>"])
    return [
        ("h", "How to think about it: count the orders"),
        "When you have to count orders, do not guess. <b>Write down every order</b>, in a system, and then "
        "cross out the ones that break a rule.",
        ("-", "<b>A system:</b> first all orders where Hermann is first, then all where Felix is first, then all "
              "where Clemens is first. For 3 children there are 3 × 2 = <b>6 orders</b>."),
        ("-", "<b>Check every order with every rule.</b> One order can break two rules at the same time."),
        ("h", "The contest question"),
        "Hermann is not the first. Felix is not the second. Clemens is not the third.",
        ("table", rows),
        ("tip", "Two orders are left: Felix, Clemens, Hermann and Clemens, Hermann, Felix. The answer is <b>2</b>."),
        ("h", "Watch out"),
        ("-", "\"3 rules, so 6 − 3 = 3\" is wrong: a rule does not cross out just one order."),
        ("-", "\"Each rule crosses out 2 orders, so 6 − 6 = 0\" is wrong too: some orders break two rules, so you "
              "would cross them out twice."),
        ("-", "With 4 children there are 4 × 3 × 2 = 24 orders. Then start with the strongest rule "
              "(\"... is the first\", \"... comes right after ...\") so you have less to write."),
    ]


# ------------------------------------------------------------------ warm-ups
@warmup
def w_all_orders(rng, harder):
    """How many orders are there without rules?"""
    n = rng.choice([2, 3])
    names = _names(rng, n)
    total = len(list(permutations(names)))
    text = f"{' and '.join(names) if n == 2 else ', '.join(names[:-1]) + ' and ' + names[-1]} stand in a row. " \
           f"How many different orders are there?"
    sol = f"Write them all down: {'; '.join(_fmt(o) for o in permutations(names))}. That is {total}."
    choices, ai = numeric_choices(total, [(n, "count the children"), (n * 2 if n == 3 else 3, "miss some orders")],
                                  rng, lo=1, order="asc")
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, len(set(permutations(names)))))


@warmup
def w_one_rule(rng, harder):
    """One rule: cross out the orders that break it."""
    names = _names(rng, 3)
    a = rng.choice(names)
    p = rng.randrange(3)
    rules = [("not", a, p)]
    ans = len(_tree(names, rules))
    text = (f"{', '.join(names[:2])} and {names[2]} stand in a row. {rule_text(rules[0], 3)} "
            f"How many different orders are there?")
    sol = (f"There are 6 orders. In 2 of them {a} is the {POS[p]}. 6 − 2 = {ans}.")
    choices, ai = numeric_choices(ans, [(6, "forget the rule"), (5, "cross out only one order"), 2], rng, lo=1,
                                  order="asc")
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, count_orders(names, rules)))


@warmup
def w_check_order(rng, harder):
    """Does this order keep the rules? Spot the one that does."""
    names = ["Hermann", "Felix", "Clemens"]
    rules = [("not", "Hermann", 0), ("not", "Felix", 1), ("not", "Clemens", 2)]
    good = _tree(names, rules)
    right = rng.choice(good)
    bad = [o for o in permutations(names) if o not in good]
    text = ("Hermann, Felix and Clemens enter a room one after the other.\n"
            "- Hermann is not the first.\n- Felix is not the second.\n- Clemens is not the third.\n\nIn which order can they enter?")
    choices, ai = text_choices(_fmt(right), [(_fmt(o), "miss one of the rules") for o in bad], rng)
    return Question(text=text, choices=choices, answer=ai,
                    solution=f"{_fmt(right)}: Hermann is not first, Felix is not second, Clemens is not third.",
                    check=lambda i: all(keeps(tuple(choices[i].split(", ")), r) for r in rules))
