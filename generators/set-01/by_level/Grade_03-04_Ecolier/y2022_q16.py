"""2022 Q16 (Ecolier, Grade 3-4) - which card goes to whom? Rule cards out with the clues.

Original: Jan sends five postcards to his friends during his holiday.
The card for Michael does not have ducks. The card for Clara shows the sun.
The card for Lexi shows a dog. The card for Heidi shows kangaroos.
The card for Paula shows exactly two animals.
Which card does Jan send to Michael?
Cards: (A) sunset over the sea, (B) two kangaroos, (C) a ladybird and a fly,
(D) ducks under a sun, (E) a dog.
Lexi gets E and Heidi B (only cards with a dog / kangaroos). Two animals: B or C, B is
Heidi's, so Paula gets C. Sun: A or D. Michael's card has no ducks, so it is not D: Michael
gets A (and Clara D).  Answer: A.

Core skill: some clues fit two cards (two animals: B and C; the sun: A and D). Children take
the first card that fits and get stuck. The method: start with the clues that fit only ONE
card, cross those cards out, then the other clues fit only one card too. No clue names
Michael's card - it is found by ruling the others out (and his clue is a "not" clue).

The parent asked for simple pictures (2026-11-16): the cards show small icons (sun, moon,
star, heart, flower), so only the logic is hard, not reading the picture.

Puzzles are built at random and kept only when a brute-force check over every way to hand
out the cards finds exactly one, every clue is needed, and the step-by-step method (cards
that fit only one clue, cards nobody else can have) solves it in enough steps.
"""
from itertools import permutations

from kangaroo import Question, variant
from kangaroo.choices import Choices
from kangaroo.figures import row
from kangaroo.pictures import ICONS, picture_card

META = {
    "source": "set-01/by_level/Grade_03-04_Ecolier/2022 Q16",
    "skill": "Start with the clue that fits only one card, cross that card out, then check the other clues again",
    "topics": ["logic"],
    "keywords": ["rule out cards", "only one fits", "postcard clues"],
    "sticker": ("📮", "Postcard sorter"),   # earned when this skill is solid (website)
    "version": 1,
}

SENDERS = ["Jan", "Mia", "Tom", "Ella", "Sam", "Nina"]
FRIENDS = ["Michael", "Clara", "Lexi", "Heidi", "Paula", "Omar", "Nora", "Ben", "Zoe", "Leo",
           "Ivy", "Max", "Rosa", "Finn", "Ada", "Hugo"]
NUM = {1: "one", 2: "two", 3: "three", 4: "four"}
STORIES = [
    ("postcards", "{s} sends five postcards to friends during the holiday.",
     "The card for {p}", "Which card does {s} send to {p}?"),
    ("birthday", "{s} gives out five birthday cards.",
     "The card for {p}", "Which card does {p} get?"),
    ("game", "Five friends each take one picture card.",
     "{p}'s card", "Which card does {p} take?"),
]


# ------------------------------------------------------------------ clues
def fits(clue, card):
    kind = clue[0]
    if kind == "has":
        return clue[1] in card
    if kind == "count":
        return len(card) == clue[1]
    if kind == "both":
        return clue[1] in card and clue[2] in card
    if kind == "no":
        return clue[1] not in card
    raise ValueError(clue)


def phrase(clue):
    kind = clue[0]
    if kind == "has":
        return f"shows a {clue[1]}"
    if kind == "count":
        return f"shows exactly {NUM[clue[1]]} thing{'s' if clue[1] > 1 else ''}"
    if kind == "both":
        return f"shows a {clue[1]} and a {clue[2]}"
    return f"does <b>not</b> show a {clue[1]}"


def positive_clues(card, harder):
    out = [("has", k) for k in card] * 3 + [("count", len(card))] * 2
    if harder and len(card) >= 2:
        out += [("both", a, b) for a in card for b in card if a < b]
    return out


# ------------------------------------------------------------------ solving
def solutions(cards, people, clues):
    """Every way to give each person a different card so that all clues hold (brute force)."""
    out = []
    for perm in permutations(range(len(cards)), len(people)):
        if all(clues[p] is None or fits(clues[p], cards[c]) for p, c in zip(people, perm)):
            out.append(dict(zip(people, perm)))
    return out


def step_by_step(cards, people, clues):
    """The method the kids should use. Returns (rounds, steps) or None if it gets stuck.
    A step is (person, card, how): how = "single" (only one card left that fits the clue)
    or "only" (nobody else can have this card - used only when every card is given out)."""
    dom = {p: {c for c in range(len(cards)) if fits(clues[p], cards[c])} for p in people}
    fixed, taken, steps, rounds = {}, set(), [], 0
    every_card = len(cards) == len(people)
    while len(fixed) < len(people):
        rounds += 1
        new = {}
        for p in people:
            if p not in fixed and len(dom[p] - taken) == 1:
                new[p] = next(iter(dom[p] - taken))
        if every_card:
            for c in range(len(cards)):
                who = [p for p in people if p not in fixed and c in dom[p] - taken]
                if c not in taken and len(who) == 1 and who[0] not in new:
                    new[who[0]] = c
        if not new or len(set(new.values())) < len(new):
            return None
        order = sorted(new, key=lambda p: (len(dom[p]), people.index(p)))
        for p in order:
            how = "single" if len(dom[p] - taken) == 1 else "only"
            steps.append((p, new[p], how, set(taken)))
        for p in order:
            fixed[p] = new[p]
            taken.add(new[p])
    return rounds, steps


def needed(cards, people, clues):
    """Clues without which the cards are no longer certain."""
    return [p for p in people if clues[p] is not None and
            len(solutions(cards, people, {**clues, p: None})) > 1]


def random_cards(rng, harder):
    lo, hi = (2, 4) if harder else (1, 3)
    cards = []
    while len(cards) < 5:
        c = tuple(sorted(rng.sample(ICONS, rng.randint(lo, hi))))
        if c not in cards:
            cards.append(c)
    return cards


def build(rng, harder, n_people=5, accept=lambda pz: True, tries=4000):
    """A random puzzle: 5 cards, n_people friends, one clue each; the last friend (the target)
    gets the only "not" clue. Clues are picked from all clues that fit 1-3 cards ("not" clues:
    rule out 1-2 cards). Keeps puzzles with exactly one way to hand out the cards where the
    step-by-step method works and every clue is needed - except one when every card is given
    out: then the last card is always clear without its clue (like Clara's sun in the original).
    The "not" clue is always needed."""
    for _ in range(tries):
        cards = random_cards(rng, harder)
        pos = sorted({c for card in cards for c in positive_clues(card, harder)})
        pos = [c for c in pos if 1 <= sum(fits(c, x) for x in cards) <= 3]
        nots = [("no", k) for k in ICONS if 1 <= sum(k in x for x in cards) <= 2]
        if len(pos) < n_people - 1 or not nots:
            continue
        for _ in range(40):
            people = rng.sample(FRIENDS, n_people)
            chosen = rng.sample(pos, n_people - 1) + [rng.choice(nots)]
            clues = dict(zip(people, chosen))
            sols = solutions(cards, people, clues)
            if len(sols) != 1:
                continue
            solved = step_by_step(cards, people, clues)
            if not solved:
                continue
            fit = {p: [c for c in range(5) if fits(clues[p], cards[c])] for p in people}
            pz = dict(cards=cards, people=people, truth=sols[0], clues=clues, target=people[-1],
                      rounds=solved[0], steps=solved[1], fit=fit,
                      amb=sum(len(fit[p]) >= 2 for p in people[:-1]))
            if not accept(pz):
                continue
            pz["needed"] = needed(cards, people, clues)
            if len(pz["needed"]) != n_people - (n_people == 5) or people[-1] not in pz["needed"]:
                continue
            pz["order"] = rng.sample(people, n_people)   # the order the clues are listed in
            return pz
    raise RuntimeError("no puzzle found")


# ------------------------------------------------------------------ wording
def or_list(xs):
    return ", ".join(xs[:-1]) + " or " + xs[-1] if len(xs) > 1 else xs[0]


def and_list(xs):
    return ", ".join(xs[:-1]) + " and " + xs[-1] if len(xs) > 1 else xs[0]


def owner_text(story, p):
    return story[2].format(p=p)


def clue_lines(pz, story, order=None):
    order = order or pz["order"]
    return "\n".join(f"- {owner_text(story, p)} {phrase(pz['clues'][p])}." for p in order)


def explain(pz, story, ref, stop=None):
    """The solution, step by step, until `stop` (a person) has a card."""
    out = []
    n_cards = len(pz["cards"])
    for p, c, how, taken in pz["steps"]:
        fit = sorted(pz["fit"][p], key=ref)
        clue = pz["clues"][p]
        if how == "only":
            out.append(f"Card {ref(c)} fits only the clue about {p}, so it is {p}'s.")
        elif clue[0] == "no":
            left = sorted((x for x in range(n_cards) if x not in taken), key=ref)
            if len(left) == 1:
                out.append(f"Card {ref(c)} is the only one left, so it is {p}'s.")
            else:
                out.append(f"Cards {and_list([ref(x) for x in left])} are left; only {ref(c)} has no "
                           f"{clue[1]}, so it is {p}'s.")
        elif len(fit) == 1:
            out.append(f"Only card {ref(c)} {phrase(clue)}, so it is {p}'s.")
        else:
            others = [ref(x) for x in fit if x != c]
            out.append(f"{owner_text(story, p)} {phrase(clue)}: {or_list([ref(x) for x in fit])}. "
                       f"{and_list(others)} {'is' if len(others) == 1 else 'are'} already taken, "
                       f"so {p} gets {ref(c)}.")
        if p == stop:
            break
    return " ".join(out)


def letter(c, order):
    return "ABCDE"[order.index(c)]


def card_mistakes(pz, asked, order):
    """Labels for wrong picture options when the question asks for `asked`'s card."""
    owner = {c: p for p, c in pz["truth"].items()}
    labels = {}
    ac = pz["clues"][asked]
    for i, c in enumerate(order):
        if c == pz["truth"].get(asked):
            continue
        q = owner.get(c)
        if ac[0] == "no" and not fits(ac, pz["cards"][c]):
            labels[i] = f"miss the word \"not\" in the clue about {asked}"
        elif ac[0] != "no" and c in pz["fit"][asked]:
            labels[i] = (f"take a card that fits the clue about {asked} without checking "
                         f"if it is someone else's")
        elif q and len(pz["fit"][q]) == 1:
            labels[i] = f"take the card that must go to {q}"
        elif q and pz["clues"][q][0] != "no":
            labels[i] = f"give {q} a different card that also fits the clue about {q}"
    return labels


def ask_card(rng, pz, story, sender, asked, intro=None, ask=None):
    """Question with the five cards as picture options: which card is `asked`'s?"""
    order = list(range(5))
    rng.shuffle(order)
    cards = pz["cards"]
    ai = order.index(pz["truth"][asked])
    text = ((intro or story[1].format(s=sender)) + "\n" + clue_lines(pz, story) + "\n\n"
            + (ask or story[3].format(s=sender, p=asked)))
    sol = explain(pz, story, lambda c: letter(c, order), stop=asked)
    people, clues = pz["people"], pz["clues"]

    def check(i):   # brute force: in every way that fits all clues, asked gets this card
        return {s[asked] for s in solutions(cards, people, clues)} == {order[i]}
    return Question(text=text, choices=Choices([f"card {L}" for L in "ABCDE"], card_mistakes(pz, asked, order)),
                    choice_figures=[picture_card(cards[c]) for c in order], answer=ai,
                    solution=sol, check=check)


def numbered_cards(cards):
    return row([picture_card(c, label=str(i + 1)) for i, c in enumerate(cards)], gap=10)


# ------------------------------------------------------------------ variants
@variant(difficulty=1)
def postcards(rng, harder):
    """The original: some clues fit two cards; the asked friend has only a "not" clue."""
    story = rng.choice(STORIES)
    sender = rng.choice(SENDERS)
    pz = build(rng, harder, accept=lambda z: z["rounds"] >= 2 and z["amb"] >= (2 if harder else 1) and any(
        p != z["target"] and fits(z["clues"][p], z["cards"][z["truth"][z["target"]]]) for p in z["people"]))
    return ask_card(rng, pz, story, sender, pz["target"])


@variant(difficulty=1)
def two_cards_fit(rng, harder):
    """Ask about the friend whose clue fits two cards: one of them is already someone else's."""
    story = rng.choice(STORIES)
    sender = rng.choice(SENDERS)

    def candidates(z):   # settled by "fits two cards, one is already taken"
        return [p for p, c, how, taken in z["steps"]
                if how == "single" and len(z["fit"][p]) >= 2 and z["clues"][p][0] != "no"]
    pz = build(rng, harder, accept=lambda z: z["rounds"] >= 2 and candidates(z))
    return ask_card(rng, pz, story, sender, rng.choice(candidates(pz)))


@variant(difficulty=2)
def chain(rng, harder):
    """Two clues fit two cards each: you can only settle one after the other."""
    story = rng.choice(STORIES)
    sender = rng.choice(SENDERS)
    pz = build(rng, harder, accept=lambda z: z["rounds"] >= 3 and z["amb"] >= (3 if harder else 2))
    return ask_card(rng, pz, story, sender, pz["target"])


@variant(difficulty=2)
def whose_card(rng, harder):
    """Turned around: who gets card number k? The card fits the clues of several friends."""
    story = rng.choice(STORIES)
    sender = rng.choice(SENDERS)

    def tempting(z, c):
        return [p for p in z["people"] if fits(z["clues"][p], z["cards"][c])]
    def candidates(z):   # cards that fit several clues and are not settled in the first step
        first = {c for p, c, how, taken in z["steps"] if how == "single" and len(z["fit"][p]) == 1}
        return [c for c in range(5) if c not in first and len(tempting(z, c)) >= (3 if harder else 2)]
    pz = build(rng, harder, accept=lambda z: z["rounds"] >= (3 if harder else 2) and candidates(z))
    cards, people, clues = pz["cards"], pz["people"], pz["clues"]
    k = rng.choice(candidates(pz))
    right = next(p for p in people if pz["truth"][p] == k)
    names = list(people)
    rng.shuffle(names)
    labels = {i: f"give card {k + 1} to {p} because it fits the clue about {p} too"
              for i, p in enumerate(names) if p != right and p in tempting(pz, k)}
    intro = story[1].format(s=sender) + " The cards are numbered 1 to 5."
    text = (intro + "\n" + clue_lines(pz, story) + "\n\n" + f"Who gets card {k + 1}?")
    sol = explain(pz, story, lambda c: str(c + 1), stop=right)

    def check(i):   # brute force: in every way that fits all clues, card k goes to this friend
        return {p for s in solutions(cards, people, clues) for p in people if s[p] == k} == {names[i]}
    return Question(text=text, figure=numbered_cards(cards), choices=Choices(names, labels),
                    answer=names.index(right), solution=sol, check=check)


@variant(difficulty=3)
def card_left_over(rng, harder):
    """Five cards, four friends: which card does nobody get?"""
    sender = rng.choice(SENDERS)
    story = ("postcards", "", "The card for {p}", "")

    def ok(z):
        return z["rounds"] >= (3 if harder else 2) and z["amb"] >= 2
    pz = build(rng, harder, n_people=4, accept=ok)
    cards, people, clues = pz["cards"], pz["people"], pz["clues"]
    spare = next(c for c in range(5) if c not in pz["truth"].values())
    order = list(range(5))
    rng.shuffle(order)
    ai = order.index(spare)
    owner = {c: p for p, c in pz["truth"].items()}
    labels = {}
    for i, c in enumerate(order):
        q = owner.get(c)
        if c == spare or q is None:
            continue
        if clues[q][0] == "no":
            labels[i] = f"miss the word \"not\" in the clue about {q}"
        elif len(pz["fit"][q]) == 1:
            labels[i] = f"forget that card {letter(c, order)} must go to {q}"
        else:
            labels[i] = f"give {q} a different card that also fits the clue about {q}"
    text = (f"{sender} has five postcards and sends four of them to friends.\n" + clue_lines(pz, story)
            + f"\n\nWhich card does {sender} <b>not</b> send?")
    sol = explain(pz, story, lambda c: letter(c, order))
    sol += f" Card {letter(spare, order)} is left over."

    def check(i):
        return {next(c for c in range(5) if c not in s.values())
                for s in solutions(cards, people, clues)} == {order[i]}
    return Question(text=text, choices=Choices([f"card {L}" for L in "ABCDE"], labels),
                    choice_figures=[picture_card(cards[c]) for c in order], answer=ai,
                    solution=sol, check=check)


@variant(difficulty=3)
def clue_not_needed(rng, harder):
    """Which clue could be left out, and you would still know every card?"""
    story = rng.choice(STORIES)
    sender = rng.choice(SENDERS)
    pz = build(rng, harder, accept=lambda z: z["rounds"] >= (3 if harder else 2))
    cards, people, clues = pz["cards"], pz["people"], pz["clues"]
    spare = [p for p in people if p not in pz["needed"]]
    order = pz["order"]        # options in the order the clues are listed
    ai = order.index(spare[0])
    choices = Choices([f"the clue about {p}" for p in order],
                      {i: "leave out a clue that is still needed" for i in range(5) if i != ai})
    text = (story[1].format(s=sender) + " The cards are numbered 1 to 5.\n" + clue_lines(pz, story)
            + f"\n\nOne clue could be left out, and you would still know who gets which card. "
              f"Which clue?")
    only = solutions(cards, people, {**clues, spare[0]: None})[0]
    sol = (f"Without the clue about {spare[0]}, the other clues still give every card: "
           + ", ".join(f"card {only[p] + 1} is {p}'s" for p in sorted(people, key=lambda p: only[p])) + ". "
           + "Without any other clue, the cards could be handed out in more than one way.")

    def check(i):
        return len(solutions(cards, people, {**clues, order[i]: None})) == 1
    return Question(text=text, figure=numbered_cards(cards), choices=choices, answer=ai,
                    solution=sol, check=check)
