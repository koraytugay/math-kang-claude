"""2002 Q18 - who has which pet? (logic deduction)

Original: Julien, Manon, Nicolas and Fabienne each have a different pet: a
cat, a dog, a parrot and a goldfish. Manon has a furry animal, Fabienne owns a
four-legged creature, Nicolas has a bird and Manon doesn't like cats. Which
statement is NOT true?  (Nicolas-parrot, Manon-dog, Fabienne-cat,
Julien-goldfish; the false statement is "Fabienne has a dog".)

Core skill: combining clues that describe a *property* (furry, four legs, ...)
rather than naming the item, and eliminating possibilities step by step.

The puzzle is built backwards: pick a secret matching, collect true clues,
keep adding clues until a brute-force solver finds exactly one solution, then
drop clues that are not needed. So every puzzle has exactly one solution.
"""
from itertools import permutations

from kangaroo import Question, text_choices, variant

META = {
    "source": "2002 Q18",
    "skill": "Logic: match people to things from property clues, find the (not) true statement",
    "topics": ["logic"],
    "version": 1,
}

NAMES = ["Julien", "Manon", "Nicolas", "Fabienne", "Lucas", "Emma", "Omar", "Mia", "Leo",
         "Sofia", "Noah", "Aisha", "Ben", "Chloe", "Ravi", "Hana", "Tom", "Zoe", "Ivan", "Nora"]

# Each theme: items {name: properties}, how to say "X has item", property phrases (yes, no),
# and how to introduce the puzzle.
THEMES = {
    "pets": {
        "items": {
            "cat": {"furry", "four legs"}, "dog": {"furry", "four legs", "barks"},
            "parrot": {"bird", "flies", "two legs"}, "goldfish": {"water", "no legs"},
            "hamster": {"furry", "four legs"}, "turtle": {"shell", "four legs"},
            "canary": {"bird", "flies", "two legs"}, "rabbit": {"furry", "four legs"},
        },
        "has": lambda p, it: f"{p} has {'an' if it[0] in 'aeiou' else 'a'} {it}",
        "article": lambda it: ("an " if it[0] in "aeiou" else "a ") + it,
        "intro": "each have a different pet:",
        "props": {
            "furry": ("has a furry animal", "has an animal without fur"),
            "four legs": ("owns a four-legged creature", "has a pet that does not have four legs"),
            "bird": ("has a bird", "does not have a bird"),
            "flies": ("has a pet that can fly", "has a pet that cannot fly"),
            "water": ("has a pet that lives in water", "has a pet that does not live in water"),
            "shell": ("has a pet with a shell", "has a pet without a shell"),
            "two legs": ("has a pet with two legs", "has a pet that does not have two legs"),
            "barks": ("has a pet that barks", "has a pet that never barks"),
            "no legs": ("has a pet with no legs at all", "has a pet with legs"),
        },
        "neg_item": lambda p, it: f"{p} doesn't like {plural(it)}",
    },
    "instruments": {
        "items": {
            "piano": {"keys"}, "guitar": {"strings"}, "violin": {"strings", "bow"},
            "drum": {"sticks"}, "flute": {"blow"}, "trumpet": {"blow"}, "harp": {"strings"},
            "xylophone": {"sticks"},
        },
        "has": lambda p, it: f"{p} plays the {it}",
        "article": lambda it: "the " + it,
        "intro": "each play a different instrument:",
        "props": {
            "strings": ("plays an instrument with strings", "plays an instrument without strings"),
            "blow": ("blows into the instrument", "does not blow into the instrument"),
            "sticks": ("plays with sticks", "never uses sticks"),
            "keys": ("presses keys", "plays an instrument without keys"),
            "bow": ("uses a bow", "does not need a bow"),
        },
        "neg_item": lambda p, it: f"{p} doesn't play the {it}",
    },
    "birthdays": {
        "items": {
            "January": {"winter", "J"}, "July": {"summer", "J"}, "April": {"spring"},
            "October": {"autumn"}, "December": {"winter"}, "August": {"summer"},
            "March": {"spring"}, "June": {"summer", "J"},
        },
        "has": lambda p, it: f"{p} was born in {it}",
        "article": lambda it: it,
        "intro": "were born in different months:",
        "props": {
            "winter": ("was born in winter", "was not born in winter"),
            "summer": ("has a birthday in summer", "does not have a birthday in summer"),
            "spring": ("was born in spring", "was not born in spring"),
            "autumn": ("was born in autumn", "was not born in autumn"),
            "J": ("was born in a month that starts with J", "was born in a month that doesn't start with J"),
        },
        "neg_item": lambda p, it: f"{p} was not born in {it}",
    },
}


def plural(it):
    if it == "goldfish":
        return "goldfish"
    if it.endswith("y"):
        return it[:-1] + "ies"
    return it + "s"


def join_and(xs):
    return ", ".join(xs[:-1]) + " and " + xs[-1] if len(xs) > 1 else xs[0]


def build_puzzle(rng, n, allow_direct):
    """Return (theme, people, items, truth dict person->item, clue sentences)."""
    for _ in range(500):
        tname = rng.choice(list(THEMES))
        th = THEMES[tname]
        items = rng.sample(list(th["items"]), n)
        people = rng.sample(NAMES, n)
        truth = dict(zip(people, rng.sample(items, n)))
        props = {it: th["items"][it] for it in items}
        useful = [pr for pr in th["props"] if 0 < sum(pr in props[it] for it in items) < n]
        # candidate clues: (sentence, predicate on an assignment dict, weight)
        cands = []
        for p in people:
            for pr in useful:
                if pr in props[truth[p]]:
                    cands.append((f"{p} {th['props'][pr][0]}", lambda a, p=p, pr=pr: pr in props[a[p]], 3))
                else:
                    cands.append((f"{p} {th['props'][pr][1]}", lambda a, p=p, pr=pr: pr not in props[a[p]], 2))
            for it in items:
                if truth[p] != it:
                    cands.append((th["neg_item"](p, it), lambda a, p=p, it=it: a[p] != it, 1))
                elif allow_direct:
                    cands.append((th["has"](p, it), lambda a, p=p, it=it: a[p] == it, 1))
        for p, q in permutations(people, 2):
            if p < q:
                for pr in useful:
                    if pr in props[truth[p]] and pr in props[truth[q]]:
                        cands.append((f"{p} and {q} both {th['props'][pr][0].replace('has ', 'have ', 1).replace('owns ', 'own ', 1).replace('was ', 'were ', 1).replace('plays ', 'play ', 1).replace('blows ', 'blow ', 1).replace('presses ', 'press ', 1).replace('uses ', 'use ', 1)}",
                                      lambda a, p=p, q=q, pr=pr: pr in props[a[p]] and pr in props[a[q]], 2))
        rng.shuffle(cands)
        cands.sort(key=lambda c: -c[2] - rng.random() * 2)
        all_assign = [dict(zip(people, perm)) for perm in permutations(items)]
        chosen, alive = [], all_assign
        for c in cands:
            nxt = [a for a in alive if c[1](a)]
            if len(nxt) < len(alive):
                chosen.append(c)
                alive = nxt
            if len(alive) == 1:
                break
        if len(alive) != 1:
            continue
        # drop clues that are not needed
        for c in list(chosen):
            rest = [x for x in chosen if x is not c]
            if sum(all(x[1](a) for x in rest) for a in all_assign) == 1:
                chosen = rest
        if len(chosen) > n + 1:
            continue
        # present clues in a mixed but readable order
        rng.shuffle(chosen)
        return th, people, items, truth, [(c[0], c[1]) for c in chosen]
    raise RuntimeError("could not build a puzzle")


def _intro(th, people, items, clues):
    return (f"{join_and(people)} {th['intro']} {join_and([th['article'](i) for i in items])}. "
            + ". ".join(c[0] for c in clues) + ".")


def _solution(th, truth):
    return "The only possible matching: " + "; ".join(f"{p} – {it}" for p, it in truth.items()) + "."


@variant(difficulty=1)
def who_has(rng, harder):
    """Find who has one particular thing (or say it can't be determined - but it always can)."""
    th, people, items, truth, clues = build_puzzle(rng, 5 if harder else 4, allow_direct=False)
    target = rng.choice(items)
    owner = next(p for p, it in truth.items() if it == target)
    q = th["has"]("Who", target) + "?"
    sol = _solution(th, truth)
    # Sometimes drop a clue so that the owner can no longer be determined.
    if rng.random() < 0.2:
        assigns = [dict(zip(people, perm)) for perm in permutations(items)]
        for c in rng.sample(clues, len(clues)):
            rest = [x for x in clues if x is not c]
            sols = [a for a in assigns if all(x[1](a) for x in rest)]
            owners = sorted({next(p for p in people if a[p] == target) for a in sols})
            if len(owners) > 1:
                clues, owner = rest, None
                sol = ("The clues allow more than one answer: "
                       + " or ".join(th["has"](o, target) for o in owners)
                       + ". So it is impossible to determine.")
                break
    others = [p for p in people if p != owner]
    opts = rng.sample(others, 3 if owner else 4) + ([owner] if owner else [])
    rng.shuffle(opts)
    choices = opts + ["Impossible to determine"]
    ans = choices.index(owner) if owner else 4
    return Question(text=_intro(th, people, items, clues), after_figure=q, choices=choices,
                    answer=ans, solution=sol)


@variant(difficulty=2)
def which_true(rng, harder):
    """Exactly one of five statements is true."""
    th, people, items, truth, clues = build_puzzle(rng, 5 if harder else 4, allow_direct=False)
    p = rng.choice(people)
    correct = th["has"](p, truth[p])
    wrong = [th["has"](x, it) for x in people for it in items if truth[x] != it]
    choices, ai = text_choices(correct, wrong, rng)
    return Question(text=_intro(th, people, items, clues), after_figure="Which statement is true?",
                    choices=choices, answer=ai, solution=_solution(th, truth))


@variant(difficulty=3)
def which_not_true(rng, harder):
    """The original: four true statements and one false one."""
    n = 5 if harder else 4
    th, people, items, truth, clues = build_puzzle(rng, n, allow_direct=False)
    true_st = [th["has"](p, truth[p]) for p in people]
    trues = rng.sample(true_st, 4)
    # the false statement swaps two people's things - a tempting mistake
    p, q = rng.sample(people, 2)
    false = th["has"](p, truth[q])
    opts = trues + [false]
    rng.shuffle(opts)
    return Question(text=_intro(th, people, items, clues),
                    after_figure="Which statement is <b>not</b> true?", choices=opts,
                    answer=opts.index(false), solution=_solution(th, truth))
