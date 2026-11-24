"""2021 Q21 (Ecolier, Grade 3-4; Brazilian copy of the Kangaroo paper) - cookies shared between children.

Original: A box has fewer than 50 cookies in. The cookies can be divided evenly between 2, 3, or 4
children. However, they cannot be divided evenly between 7 children because 6 more cookies would be
needed. How many cookies are there in the box?   (A) 12  (B) 24  (C) 30  (D) 36  (E) 48
Answer key (Ecolier row): D.
Numbers that 2, 3 and 4 all fit are the multiples of 12: 12, 24, 36, 48. For 7 children they need
2, 4, 6 and 1 more cookies (14, 28, 42, 49 are the next numbers in the 7 times table). Only 36 needs 6.

Core skill: combine "fits evenly" clues (common multiples) with a clue that is told backwards
("6 MORE would be needed" is not "6 left over"): list the numbers that fit the first clues, then test
each one against the last clue. Traps: stopping after the first clues (several numbers fit), and mixing
up "k more needed" with "k left over" (24 and 48 are right next to a multiple of 7, 36 is just past it).
"""
from math import lcm

from kangaroo import Question, numeric_choices, variant
from kangaroo.choices import number_in

META = {
    "source": "set-01/by_level/Grade_03-04_Ecolier/2021 Q21",
    "skill": "List the numbers that fit the 'divides evenly' clues (multiples), then test each one against the last clue",
    "topics": ["arithmetic", "logic", "multiples"],
    "keywords": ["fair sharing", "common multiples", "more needed"],
    "sticker": ("🍰", "Fair sharer"),   # earned when this skill is solid (website)
    "rungs": ("aligned", "aligned", "harder", "harder"),   # vs the original contest question: steps 1, 2, 3, 3 harder (2026-11-24)
    "version": 1,
}

# (things, one thing, group of people)
STORIES = [("cookies", "cookie", "children"), ("sweets", "sweet", "children"), ("stickers", "sticker", "friends"),
           ("marbles", "marble", "friends"), ("pencils", "pencil", "kids")]
NAMES = ["Tom", "Mia", "Ben", "Anna", "Leo", "Sara"]


# ------------------------------------------------------------------ checks by simulation
def deal(n, c):
    """Deal n things out one by one to c people: how many each gets."""
    got = [0] * c
    for i in range(n):
        got[i % c] += 1
    return got


def even(n, c):
    return len(set(deal(n, c))) == 1


def left_over(n, c):
    return n - c * min(deal(n, c))


def more_needed(n, c):
    m = 0
    while not even(n + m, c):
        m += 1
    return m


# ------------------------------------------------------------------ a problem and its words
class Spec:
    """`ds`: the numbers of people it divides evenly between; `needs`: [(p, k)] clues that it does NOT divide
    evenly between p people (k more needed, or k left over); lo < n < hi."""

    def __init__(self, ds, needs, lo, hi, mode="need"):
        self.ds, self.needs, self.lo, self.hi, self.mode = ds, needs, lo, hi, mode

    def value(self, n, p):
        return more_needed(n, p) if self.mode == "need" else left_over(n, p)

    def ok(self, n):
        """Answer check, by dealing the things out (not by the formula the generator used to search)."""
        return (self.lo < n < self.hi and all(even(n, d) for d in self.ds)
                and all(self.value(n, p) == k for p, k in self.needs))


def find(rng, ds_opts, p_opts, ranges, n_needs=1, mode="need", min_cands=3, max_cands=9):
    """Random clues with exactly one number that fits them all (formulas here; the question's check
    deals the things out instead)."""
    for _ in range(5000):
        ds = rng.choice(ds_opts)
        ps = rng.sample([p for p in p_opts if p not in ds], n_needs)
        ks = [rng.randint(1, p - 1) for p in ps]
        lo, hi = rng.choice(ranges)
        cands = [n for n in range(lo + 1, hi) if all(n % d == 0 for d in ds)]
        sols = [n for n in cands if all((((-n) % p) if mode == "need" else (n % p)) == k for p, k in zip(ps, ks))]
        if len(sols) == 1 and min_cands <= len(cands) <= max_cands:
            return Spec(ds, list(zip(ps, ks)), lo, hi, mode), sols[0]
    raise RuntimeError("no clues found")


def listing(xs):
    xs = list(xs)
    return ", ".join(map(str, xs[:-1])) + " and " + str(xs[-1]) if len(xs) > 1 else str(xs[0])


def story_text(spec, story, lead_extra=""):
    things, one, group = story
    if spec.lo:
        lead = f"A box has more than {spec.lo} and fewer than {spec.hi} {things} in it."
    else:
        lead = f"A box has fewer than {spec.hi} {things} in it."
    bullets = []
    for i, d in enumerate(spec.ds):
        bullets.append(f"- The {things} can be divided evenly between {d} {group}." if i == 0 else
                       f"- They can also be divided evenly between {d} {group}.")
    for i, (p, k) in enumerate(spec.needs):
        either = " either" if i else ""
        if spec.mode == "need":
            more = f"{k} more {one if k == 1 else things} would be needed"
            bullets.append(f"- They cannot be divided evenly between {p} {group}{either}, because {more}.")
        else:
            left = f"{k} {one} is" if k == 1 else f"{k} {things} are"
            bullets.append(f"- If they are shared out between {p} {group}{either}, {left} left over.")
    return f"{lead} What we know:\n\n" + "\n".join(bullets) + f"\n\nHow many {things} are in the box?"


def solution_text(spec, ans, story):
    things, one, group = story
    L = lcm(*spec.ds)
    cands = [n for n in range(spec.lo + 1, spec.hi) if n % L == 0]
    first = (f"Numbers that divide evenly between {listing(spec.ds)} {group} are the multiples of {L}: "
             f"{listing(cands)}.") if len(spec.ds) > 1 else f"Numbers that divide evenly between {spec.ds[0]} {group} are the multiples of {spec.ds[0]}: {listing(cands)}."
    out = [first]
    alive = cands
    for p, k in spec.needs:
        if spec.mode == "need":
            show = ", ".join(f"{n} needs {(-n) % p} more" if (-n) % p else f"{n} needs none (it fits)" for n in alive)
            keep = [n for n in alive if (-n) % p == k]
            out.append(f"For {p} {group} (count up in the {p} times table): {show}. "
                       f"Only {listing(keep)} needs {k}." if len(keep) == 1 else
                       f"For {p} {group} (count up in the {p} times table): {show}. {listing(keep)} need {k}.")
        else:
            show = ", ".join(f"{n} leaves {n % p}" if n % p else f"{n} leaves nothing" for n in alive)
            keep = [n for n in alive if n % p == k]
            out.append(f"Share between {p} {group}: {show}. "
                       f"Only {listing(keep)} leaves {k}." if len(keep) == 1 else
                       f"Share between {p} {group}: {show}. {listing(keep)} leave {k}.")
        alive = keep
    return " ".join(out)


def mistakes_for(spec, ans, story):
    """Labelled wrong answers: only some of the clues used, or 'more needed' mixed up with 'left over'."""
    things, one, group = story
    L = lcm(*spec.ds)
    ns = range(spec.lo + 1, spec.hi)
    out = []
    p0, k0 = spec.needs[0]
    other = "left over" if spec.mode == "need" else "more needed"
    mine = "more needed" if spec.mode == "need" else "left over"
    for n in ns:       # the clue about p0 mixed up
        if n % L == 0 and n != ans and (left_over(n, p0) if spec.mode == "need" else more_needed(n, p0)) == k0:
            out.append((n, f"mix up '{k0} {mine}' with '{k0} {other}'"))
    for n in ns:       # forgot one of the "divides evenly" numbers
        if n % L and n != ans and all(spec.value(n, p) == k for p, k in spec.needs):
            miss = [d for d in spec.ds if n % d]
            if len(miss) == 1:
                out.append((n, f"forget to check the {miss[0]} {group}"))
    for n in ns:       # used only one of the clues about not dividing evenly
        if n % L == 0 and n != ans and len(spec.needs) > 1:
            fit = [p for p, k in spec.needs if spec.value(n, p) == k]
            if len(fit) == 1:
                rest = [p for p, k in spec.needs if p != fit[0]][0]
                out.append((n, f"forget to test the clue about {rest} {group}"))
    for n in ns:       # stopped before the last clue(s)
        if n % L == 0 and n != ans:
            last = spec.needs[-1][0]
            out.append((n, f"stop at a number that fits the first clues and forget to test the {last} {group}"))
    seen, uniq = set(), []
    for n, t in out:
        if n not in seen:
            seen.add(n)
            uniq.append((n, t))
    return uniq


def build(rng, spec, ans, story, diff):
    text = story_text(spec, story)
    choices, ai = numeric_choices(ans, mistakes_for(spec, ans, story), rng, lo=1, order="asc")
    return Question(text=text, choices=choices, answer=ai, solution=solution_text(spec, ans, story),
                    difficulty=diff, check=lambda i: spec.ok(number_in(choices[i])))


# ------------------------------------------------------------------ variants
@variant(difficulty=1, rungs=("aligned", "harder"))
def more_needed_clue(rng, harder):
    """The contest question: divides evenly between a few numbers, but 'k more would be needed' for p."""
    if harder:
        spec, ans = find(rng, [(2, 3, 4), (3, 4), (2, 3, 5), (4, 5), (3, 4, 6)], [5, 7, 8, 9, 11],
                         [(0, 100), (0, 120), (0, 150)], max_cands=9)
    else:
        spec, ans = find(rng, [(2, 3, 4), (2, 3), (3, 4), (2, 5), (2, 4)], [5, 7, 8, 9, 11],
                         [(0, 50), (0, 40), (0, 60)])
    return build(rng, spec, ans, rng.choice(STORIES), 1)


@variant(difficulty=1, rungs=("easier", "aligned"))
def left_over_clue(rng, harder):
    """The same search, but the last clue says how many are LEFT OVER (no backwards thinking)."""
    if harder:
        spec, ans = find(rng, [(2, 3, 4), (3, 4), (2, 3, 5), (4, 5)], [5, 7, 8, 9, 11],
                         [(0, 100), (0, 120), (0, 150)], mode="left")
    else:
        spec, ans = find(rng, [(2, 3, 4), (2, 3), (3, 4), (2, 5)], [5, 7, 8, 9],
                         [(0, 50), (0, 40), (0, 60)], mode="left")
    return build(rng, spec, ans, rng.choice(STORIES), 1)


@variant(difficulty=2, rungs=("easier", "aligned"))
def how_many_to_add(rng, harder):
    """Reverse: a box has some, how many must be added so it divides evenly between all of them?"""
    name = rng.choice(NAMES)
    things, one, group = rng.choice(STORIES)
    ds = rng.choice([(2, 3, 4), (3, 4, 6), (2, 3, 5), (4, 5), (3, 4), (2, 3, 4, 5)] if harder
                    else [(2, 3, 4), (2, 3), (3, 4), (2, 5), (4, 6)])
    L = lcm(*ds)
    while True:
        n = rng.randint(2 * L + 1, 4 * L - 1) if harder else rng.randint(L + 1, 2 * L - 1)
        add = (-n) % L
        if add >= 2 and n % L and add != n % L:
            break
    text = (f"A box has {n} {things} in it. {name} wants to be able to divide them evenly between "
            f"{listing(ds)} {group}: "
            f"every one of these must work.\n\nWhat is the smallest number of {things} {name} can add to the box?")
    multiples = [L * i for i in range(1, n // L + 3)]
    sol = (f"A number that divides evenly between {listing(ds)} {group} is a multiple of {L}: {listing(multiples)}. "
           f"{n} lies between {n - n % L} and {n + add}, so {name} must reach {n + add}: "
           f"{n + add} − {n} = {add} more {things}.")
    big = max(ds)
    mistakes = [(n % L, "count back to the multiple below instead of on to the next one"),
                (L, "give the first number that works instead of how many more are needed"),
                (n + add, f"give how many {things} there will be, not how many to add"),
                ((-n) % big, f"make it work for {big} {group} only")]
    choices, ai = numeric_choices(add, mistakes, rng, lo=1, order="asc")

    def check(i):                      # add cookies one at a time until all the sharings work
        v = number_in(choices[i])
        works = lambda m: all(even(n + m, d) for d in ds)
        return works(v) and not any(works(m) for m in range(v))
    return Question(text=text, choices=choices, answer=ai, solution=sol, difficulty=2, check=check)


@variant(difficulty=2, rungs=("aligned", "harder"))
def between_numbers(rng, harder):
    """The same clues, but the box holds 'more than ... and fewer than ...' so the numbers do not start at 1."""
    if harder:
        spec, ans = find(rng, [(2, 3, 4), (3, 4), (2, 3), (4, 5)], [5, 7, 8, 9, 11],
                         [(50, 150), (60, 160), (100, 200)], max_cands=9)
    else:
        spec, ans = find(rng, [(2, 3, 4), (2, 3), (3, 4), (2, 5)], [5, 7, 8, 9],
                         [(20, 80), (30, 90), (40, 100), (30, 80)])
    return build(rng, spec, ans, rng.choice(STORIES), 2)


@variant(difficulty=3, rungs=("harder", "harder"))
def two_backwards_clues(rng, harder):
    """Twist: two 'cannot be divided evenly' clues, so the search needs a second test."""
    if harder:
        spec, ans = find(rng, [(3, 4), (4, 5), (3, 5), (2, 3, 4)], [5, 7, 8, 9, 11],
                         [(0, 150), (0, 200)], n_needs=2, min_cands=5, max_cands=12)
    else:
        spec, ans = find(rng, [(3, 4), (2, 3, 4), (4, 6)], [5, 7, 8, 9, 11],
                         [(0, 100), (0, 120)], n_needs=2, min_cands=4, max_cands=10)
    return build(rng, spec, ans, rng.choice(STORIES), 3)
