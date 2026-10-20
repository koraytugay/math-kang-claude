"""2002 Q11 - cracked clock face with consecutive sums.

Original: the face of a clock is cracked into 4 pieces; the sums of the
numbers in the pieces are consecutive numbers. Which picture shows the clock?
(Total 1+...+12 = 78 = 18+19+20+21.)

Core skill: using the total (78) to predict the piece sums before checking
pictures, and adding runs of neighbouring numbers on a circle carefully.

Every variant searches *all* ways to crack the wheel (pieces = runs of
neighbouring numbers, as made by cracks from the centre or straight cracks
across), so the answer is proved to be unique. Note: on a real clock there is
NO way to get 4 consecutive sums with runs of neighbours, but exactly one for
3 pieces (25, 26, 27); other wheels give more possibilities.
"""
from functools import lru_cache
from itertools import combinations

from kangaroo import Question, numeric_choices, text_choices, variant
from kangaroo.pictures import number_wheel

META = {
    "source": "2002 Q11",
    "skill": "Sums of numbers around a circle: use the total, split into equal/consecutive parts",
    "topics": ["arithmetic", "logic", "spatial"],
    "version": 1,
}

CLOCK = [12] + list(range(1, 12))


def wheels(harder):
    """(numbers in clockwise order from the top, short name, intro sentence)"""
    out = [(CLOCK, "clock", "The face of a clock")]
    for n in ([8, 9, 10, 11, 12, 13, 14, 15, 16] if harder else [6, 7, 8, 9, 10]):
        out.append((list(range(1, n + 1)), "wheel", f"{{thing}} with the numbers 1 to {n} around its edge"))
    return out


THINGS = ["A round cake", "A round plate", "A wheel of fortune", "A round cookie"]


def dress(rng, nums, intro, cuts=()):
    """Give a non-clock wheel a random story and rotate it (sums and answers don't change)."""
    if "{thing}" not in intro:
        return list(nums), intro, tuple(cuts)
    n = len(nums)
    r = rng.randrange(n)
    nums = list(nums[r:]) + list(nums[:r])
    cuts = tuple(sorted((c - r) % n for c in cuts))
    return nums, intro.format(thing=rng.choice(THINGS)), cuts


def pieces(nums, cuts):
    """cuts: sorted indices; a crack sits just before nums[i]. Returns lists of numbers."""
    n, out = len(nums), []
    for a, b in zip(cuts, list(cuts[1:]) + [cuts[0] + n]):
        out.append([nums[j % n] for j in range(a, b)])
    return out


def all_cuts(nums, k):
    return list(combinations(range(len(nums)), k))


def consecutive(sums):
    s = sorted(sums)
    return all(b - a == 1 for a, b in zip(s, s[1:]))


def equal(sums):
    return len(set(sums)) == 1


def gap_name(nums, i):
    return f"{nums[i - 1]} and {nums[i]}"


# ------------------------------------------------------------------ variants
@variant(difficulty=1)
def biggest_piece(rng, harder):
    """Cracks are drawn - add up each piece and compare."""
    for _ in range(500):
        nums, kind, intro = rng.choice(wheels(harder)[:4])
        nums, intro, _ = dress(rng, nums, intro)
        cuts = sorted(rng.sample(range(len(nums)), 5))
        ps = pieces(nums, cuts)
        sums = [sum(p) for p in ps]
        if len(set(sums)) == 5:
            break
    want_big = rng.random() < 0.6
    target = sums.index(max(sums) if want_big else min(sums))
    labels = [f"the piece with the {max(p)}" for p in ps]
    order = list(range(5))
    rng.shuffle(order)
    choices = [labels[i] for i in order]
    fig = number_wheel(nums, cuts, scale=10, jagged_seed=rng.randint(0, 999))
    text = f"{intro} is cracked into 5 pieces as shown."
    after = f"Which piece has the {'largest' if want_big else 'smallest'} sum of numbers?"
    detail = ", ".join(f"{'+'.join(map(str, p))} = {s}" for p, s in zip(ps, sums))
    sol = f"The sums are: {detail}."
    return Question(text=text, figure=fig, after_figure=after, choices=choices,
                    answer=order.index(target), solution=sol)


@lru_cache(maxsize=None)
def _unique_setups(harder):
    """All (wheel, k, condition) with exactly one cracking: (nums, intro, k, cond, cuts)."""
    options = []
    for nums, kind, intro in wheels(harder):
        for k in (2, 3, 4):
            for name in ("consecutive", "equal"):
                f = consecutive if name == "consecutive" else equal
                sols = [c for c in all_cuts(nums, k) if f([sum(p) for p in pieces(nums, c)])]
                if len(sols) == 1:
                    options.append((tuple(nums), intro, k, name, sols[0]))
    return options


@lru_cache(maxsize=None)
def _unique_halves(harder):
    return [(nums, intro, cuts) for nums, intro, k, cond, cuts in _unique_setups(harder)
            if k == 2 and cond == "equal"]


def _find_unique(rng, harder):
    nums, intro, k, cond, cuts = rng.choice(_unique_setups(harder))
    nums, intro, cuts = dress(rng, nums, intro, cuts)
    return nums, intro, k, cond, cuts


@variant(difficulty=2)
def which_picture(rng, harder):
    """The original: five cracked wheels, only one has consecutive (or equal) sums."""
    nums, intro, k, cond, good = _find_unique(rng, harder)
    # wrong pictures: other crackings into k pieces, preferring near misses
    bad = [c for c in all_cuts(nums, k) if c != good]
    spread = lambda c: max(map(sum, pieces(nums, c))) - min(map(sum, pieces(nums, c)))
    bad.sort(key=lambda c: (spread(c), rng.random()))
    wrong = rng.sample(bad[:12], 4)
    cutsets = wrong + [good]
    rng.shuffle(cutsets)
    figs = [number_wheel(nums, c, scale=7.2, radius=5, jagged_seed=i, font_size=7)
            for i, c in enumerate(cutsets)]
    words = {2: "two", 3: "three", 4: "four"}
    if cond == "consecutive":
        rule = f"The sums of the numbers in the pieces are {words[k]} consecutive numbers."
    else:
        rule = "All the pieces have the same sum of numbers."
    total = sum(nums)
    text = f"{intro} is cracked into {k} pieces. {rule}"
    after = "Which picture shows how it is cracked?"
    sums = sorted(map(sum, pieces(nums, good)))
    sol = (f"All numbers add up to {total}, so the pieces must be "
           + " + ".join(map(str, sums)) + f" = {total}. Only this picture gives "
           + ", ".join(map(str, sums)) + ".")
    return Question(text=text, after_figure=after, choices=[f"picture {c}" for c in "ABCDE"],
                    answer=cutsets.index(good), choice_figures=figs, solution=sol)


@variant(difficulty=2)
def largest_sum(rng, harder):
    """No cracks drawn: work out the sums from the total alone."""
    while True:
        nums, kind, intro = rng.choice(wheels(harder))
        nums, intro, _ = dress(rng, nums, intro)
        k = rng.choice([2, 3, 4, 5] if harder else [2, 3, 4])
        total = sum(nums)
        rest = total - k * (k - 1) // 2
        if rest % k:
            continue
        a = rest // k
        if any(consecutive([sum(p) for p in pieces(nums, c)]) for c in all_cuts(nums, k)):
            break
    words = {2: "two", 3: "three", 4: "four", 5: "five"}
    ask_small = rng.random() < 0.35
    ans = a if ask_small else a + k - 1
    fig = number_wheel(nums, (), scale=9)
    text = (f"{intro} is cracked into {k} pieces. The sums of the numbers in the pieces are "
            f"{words[k]} consecutive numbers.")
    after = f"What is the {'smallest' if ask_small else 'largest'} of these sums?"
    sol = (f"All the numbers add up to {total}. {words[k].capitalize()} consecutive numbers that add up to "
           f"{total}: " + " + ".join(str(a + i) for i in range(k)) + f" = {total}. "
           f"The {'smallest' if ask_small else 'largest'} is {ans}.")
    mistakes = [total // k, a + k, a - 1, a + k - 2, a + 1, total // (k + 1), a if not ask_small else a + k - 1]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, figure=fig, after_figure=after, choices=choices, answer=ai,
                    solution=sol)


@variant(difficulty=3)
def straight_crack(rng, harder):
    """One straight crack makes two pieces with equal sums - where does it go?"""
    nums, intro, good = rng.choice(_unique_halves(harder))
    nums, intro, good = dress(rng, nums, intro, good)
    n = len(nums)
    name = lambda c: f"between {gap_name(nums, c[0])}, and between {gap_name(nums, c[1])}"
    # near-miss wrong answers: shift one end of the crack by one or two places
    wrong = set()
    for d1 in (-2, -1, 0, 1, 2):
        for d2 in (-2, -1, 0, 1, 2):
            c = tuple(sorted(((good[0] + d1) % n, (good[1] + d2) % n)))
            if c != good and c[0] != c[1]:
                wrong.add(c)
    wrong = sorted(wrong)
    rng.shuffle(wrong)
    choices, ai = text_choices(name(good), [name(c) for c in wrong[:8]], rng)
    fig = number_wheel(nums, (), scale=9)
    total = sum(nums)
    p1, p2 = pieces(nums, good)
    text = (f"{intro} is broken by one straight crack into two pieces. "
            f"The sums of the numbers on the two pieces are equal.")
    after = "Where does the crack go?"
    sol = (f"Total {total}, so each piece has {total // 2}: "
           f"{'+'.join(map(str, p1))} = {sum(p1)} and {'+'.join(map(str, p2))} = {sum(p2)}.")
    return Question(text=text, figure=fig, after_figure=after, choices=choices, answer=ai,
                    solution=sol)


@variant(difficulty=3)
def count_ways(rng, harder):
    """Odd wheels: how many straight cracks give two equal halves?"""
    for _ in range(2000):
        n = rng.randint(6, 8 if not harder else 10)
        nums = [rng.randint(1, 9) for _ in range(n)]
        if sum(nums) % 2:
            continue
        sols = [c for c in all_cuts(nums, 2) if equal([sum(p) for p in pieces(nums, c)])]
        if 1 <= len(sols) <= 4:
            break
    ans = len(sols)
    fig = number_wheel(nums, (), scale=9)
    text = (f"Numbers are written around a round plate as shown. Tom wants to break the plate "
            f"with one straight line so that the two pieces have the same sum of numbers.")
    after = "In how many different ways can he do it?"
    detail = "; ".join(" | ".join("+".join(map(str, p)) for p in pieces(nums, c)) for c in sols)
    sol = f"Each half must have {sum(nums) // 2}. The ways: {detail}."
    counts = [c for c in range(0, 6) if c != ans]
    counts.remove(rng.choice(counts))
    counts = sorted(counts + [ans])
    return Question(text=text, figure=fig, after_figure=after, choices=[str(c) for c in counts],
                    answer=counts.index(ans), solution=sol)
