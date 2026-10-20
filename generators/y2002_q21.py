"""2002 Q21 - who cannot make 20 from their three cards?

Original: The digits 1 to 9 are written on 9 cards. Alex has 7, 2, 4; Martha has
6, 5, 1; Fred has 8, 3, 9. Each uses some of + - x : and each of their own cards
exactly once. Who cannot obtain 20?
A Alex  B Martha  C Fred  D All can get 20  E Alex and Martha.
Alex (7 - 2) x 4 = 20, Fred 8 + 3 + 9 = 20, Martha cannot.  Answer: B.

Core skill: combining numbers with + - x : (and brackets) in a systematic way -
trying multiplication, not only addition - and being sure when something is
impossible because every combination has been tried.
"""
from fractions import Fraction
from functools import lru_cache
from itertools import combinations

from kangaroo import Question, numeric_choices, text_choices, variant

META = {
    "source": "2002 Q21",
    "skill": "Reach a target with + − × ÷ using each card once; know when it is impossible",
    "topics": ["arithmetic", "logic"],
    "version": 1,
}

NAMES = ["Alex", "Martha", "Fred", "Mia", "Leo", "Sara", "Tom", "Nina", "Omar", "Lily"]
PREC = {"+": 1, "−": 1, "×": 2, "÷": 2, None: 3}


def _join(a, op, b):
    """Write a op b with only the brackets that are needed."""
    (ea, pa), (eb, pb) = a, b
    if PREC[pa] < PREC[op]:
        ea = f"({ea})"
    if PREC[pb] < PREC[op] or (PREC[pb] == PREC[op] and op in "−÷"):
        eb = f"({eb})"
    return f"{ea} {op} {eb}", op


@lru_cache(maxsize=None)
def results(cards: tuple) -> dict:
    """All whole numbers (>= 0) reachable using every card once -> one short way to write it."""
    if len(cards) == 1:
        return {cards[0]: (str(cards[0]), None)}
    out = {}
    idx = range(len(cards))
    for k in range(1, len(cards)):
        for left in combinations(idx, k):
            if 0 not in left:          # each split once: card 0 is always on the left
                continue
            L = tuple(sorted(cards[i] for i in left))
            R = tuple(sorted(cards[i] for i in idx if i not in left))
            for a, ea in results(L).items():
                for b, eb in results(R).items():
                    for (x, y, ex, ey) in ((a, b, ea, eb), (b, a, eb, ea)):
                        cand = {x + y: "+", x * y: "×"}
                        if x >= y:
                            cand[x - y] = cand.get(x - y, "−")
                        if y and x % y == 0:
                            cand.setdefault(x // y, "÷")
                        for v, op in cand.items():
                            e = _join(ex, op, ey)
                            if v not in out or len(e[0]) < len(out[v][0]):
                                out[v] = e
    return out


@lru_cache(maxsize=None)
def _any_results(cards: tuple) -> frozenset:
    """Everything reachable when fractions and negative numbers are allowed along the way."""
    if len(cards) == 1:
        return frozenset({Fraction(cards[0])})
    out = set()
    idx = range(len(cards))
    for k in range(1, len(cards)):
        for left in combinations(idx, k):
            if 0 not in left:
                continue
            L = tuple(sorted(cards[i] for i in left))
            R = tuple(sorted(cards[i] for i in idx if i not in left))
            for a in _any_results(L):
                for b in _any_results(R):
                    out |= {a + b, a - b, b - a, a * b}
                    if b:
                        out.add(a / b)
                    if a:
                        out.add(b / a)
    return frozenset(out)


def reach(cards) -> dict:
    """Whole-number results only (what the solutions show)."""
    return results(tuple(sorted(cards)))


def impossible(cards, t) -> bool:
    """True only if t cannot be reached even through fractions or negative steps."""
    return Fraction(t) not in _any_results(tuple(sorted(cards)))


def expr(cards, v) -> str:
    return reach(cards)[v][0]


def cards_str(cards):
    return ", ".join(map(str, cards[:-1])) + " and " + str(cards[-1])


def _closest(cards, t):
    r = reach(cards)
    lo = max((v for v in r if v < t), default=None)
    hi = min((v for v in r if v > t), default=None)
    return lo, hi


def _no_way(cards, t):
    lo, hi = _closest(cards, t)
    near = " and ".join(f"{v} = {expr(cards, v)}" for v in (lo, hi) if v is not None)
    return f"with {cards_str(cards)} nothing gives {t} (the closest are {near})"


def _sorted_choices(correct, wrong, rng):
    vals = sorted(set(wrong[:4]) | {correct}, reverse=rng.random() < 0.5)
    return [str(v) for v in vals], vals.index(correct)


@variant(difficulty=1)
def who_cannot(rng, harder):
    """The original: three children share the cards 1-9; who cannot reach the target?"""
    for _ in range(500):
        digits = list(range(1, 10))
        rng.shuffle(digits)
        hands = [sorted(digits[i:i + 3], reverse=rng.random() < 0.5) for i in (0, 3, 6)]
        t = rng.randint(20, 45) if harder else rng.randint(10, 24)
        fail = [i for i, h in enumerate(hands) if t not in reach(h)]
        if any(not impossible(hands[i], t) for i in fail):
            continue
        if len(fail) == 1 or (harder and len(fail) in (0, 2)):
            break
    else:
        raise RuntimeError("no card split found")
    names = rng.sample(NAMES, 3)
    others = [i for i in range(3) if i not in fail]
    pair = fail if len(fail) == 2 else sorted(rng.sample(range(3), 2))
    all_opt = f"All can get {t}"
    pair_opt = f"{names[pair[0]]} and {names[pair[1]]}"
    choices = names + [all_opt, pair_opt]
    correct = {0: all_opt, 1: names[fail[0]] if fail else "", 2: pair_opt}[len(fail)]
    text = (f"The digits from 1 to 9 are written on 9 cards. "
            + "; ".join(f"{n} has {cards_str(h)}" for n, h in zip(names, hands)) + ". "
            f"Each of them uses some of +, −, ×, ÷ (and brackets) and each of their own cards "
            f"exactly once.")
    after = f"Who <i>cannot</i> get {t} as the result?"
    can = "; ".join(f"{names[i]}: {expr(hands[i], t)} = {t}" for i in others)
    cannot = "; ".join(f"{names[i]}: {_no_way(hands[i], t)}" for i in fail)
    sol = ". ".join(s for s in (can, cannot) if s) + "."
    return Question(text=text, after_figure=after, choices=choices, answer=choices.index(correct),
                    solution=sol)


def _hand(rng, harder):
    n = 4 if harder and rng.random() < 0.5 else 3
    return sorted(rng.sample(range(1, 10), n))


@variant(difficulty=1)
def which_can(rng, harder):
    """Which of these numbers can she make? (Only one can be made.)"""
    for _ in range(500):
        cards = _hand(rng, harder)
        r = reach(cards)
        good = [v for v in r if 10 <= v <= 60]
        if not good:
            continue
        v = rng.choice(good)
        near = [u for u in range(max(1, v - 8), v + 9) if impossible(cards, u)]
        if len(near) >= 4:
            break
    else:
        raise RuntimeError("no hand found")
    name = rng.choice(NAMES)
    wrong = rng.sample(near, 4)
    choices, ai = _sorted_choices(v, wrong, rng)
    text = (f"{name} has the cards {cards_str(cards)}. {name} must use every card exactly once, "
            f"with +, −, ×, ÷ and brackets.")
    after = f"Which of these numbers can {name} get?"
    sol = f"{expr(cards, v)} = {v}. None of the other numbers can be made."
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=2)
def which_cannot(rng, harder):
    """Four of the numbers can be made, one cannot."""
    for _ in range(500):
        cards = _hand(rng, harder)
        r = reach(cards)
        top = max(r)
        holes = [u for u in range(10, min(top, 60)) if impossible(cards, u)]
        if not holes:
            continue
        u = rng.choice(holes)
        near = [v for v in r if v != u and abs(v - u) <= 10 and v >= 2]
        if len(near) >= 4:
            break
    else:
        raise RuntimeError("no hand found")
    name = rng.choice(NAMES)
    wrong = rng.sample(near, 4)
    choices, ai = _sorted_choices(u, wrong, rng)
    text = (f"{name} has the cards {cards_str(cards)}. {name} must use every card exactly once, "
            f"with +, −, ×, ÷ and brackets.")
    after = f"Which number can {name} <i>not</i> get?"
    sol = ("; ".join(f"{expr(cards, w)} = {w}" for w in sorted(wrong)) + f". But {_no_way(cards, u)}.")
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=2)
def hidden_card(rng, harder):
    """Two cards are known; which card must the third one be to reach the target?"""
    for _ in range(500):
        a, b = rng.sample(range(1, 10), 2)
        t = rng.randint(15, 50) if harder else rng.randint(10, 30)
        rest = [c for c in range(1, 10) if c not in (a, b)]
        ok = [c for c in rest if t in reach([a, b, c])]
        bad = [c for c in rest if impossible([a, b, c], t)]
        if ok and len(bad) >= 4 and t not in reach([a, b]):
            break
    else:
        raise RuntimeError("no hand found")
    name = rng.choice(NAMES)
    c = rng.choice(ok)
    wrong = rng.sample(bad, 4)
    choices, ai = _sorted_choices(c, wrong, rng)
    text = (f"{name} has three cards with different digits. Two of them are {a} and {b}; the third "
            f"is face down. Using each card exactly once, with +, −, ×, ÷ and brackets, "
            f"{name} gets {t}.")
    after = "Which of these digits can be on the hidden card?"
    sol = f"{expr([a, b, c], t)} = {t}. The other digits do not work with {a} and {b}."
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=3)
def biggest(rng, harder):
    """Largest result - the twist: with a 1, adding it beats multiplying by it."""
    n = 4 if harder else 3
    cards = sorted([1] + rng.sample(range(2, 10), n - 1))
    best = max(reach(cards))
    rest = cards[1:]
    prod = 1
    for c in rest:
        prod *= c
    name = rng.choice(NAMES)
    text = (f"{name} has the cards {cards_str(cards)}. Using every card exactly once, with +, −, ×, ÷ "
            f"and brackets, {name} wants to get the biggest possible number.")
    after = f"What is the biggest number {name} can get?"
    sol = (f"{expr(cards, best)} = {best}. Multiplying by 1 changes nothing, so it is better to "
           f"add the 1 to the smallest other card first.")
    mistakes = [prod, prod + 1, sum(cards), prod - 1, (rest[-1] + 1) * prod // rest[-1]]
    choices, ai = numeric_choices(best, mistakes, rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol)
