"""2024 Q24 (Ecolier, Grade 3-4) - cookies on a tray, taken by three girls in an unknown order.

Original: a tray with 2 large white round cookies, 4 large brown hearts, 1 large white heart,
1 small white heart, 5 small brown hearts and 3 small white round cookies (16 cookies).
Tina takes all the heart-shaped cookies still on the tray, Emma all the white cookies still on
the tray, Rosa all the large cookies still on the tray (in an unknown order). One girl takes 3,
one 6 and one 7 cookies. Which of these groups did one of the girls take?
Only the order Rosa, Tina, Emma gives 3, 6, 7: Rosa takes the 7 large cookies, Tina the 6
small hearts, Emma the 3 small white round ones.  Answer: E (three small white round cookies).

Core skill: "takes all that are STILL on the tray" - what a girl gets depends on who went before
her. Try the orders one by one and keep track of what is left; a cookie that fits two girls goes
to whoever comes first.
Printed in black and white: the brown cookies are drawn dark, the white ones as outlines.
"""
from collections import Counter
from itertools import permutations

from reportlab.lib import colors

from kangaroo import Fig, Question, numeric_choices, value_check, variant

META = {
    "source": "set-01/by_level/Grade_03-04_Ecolier/2024 Q24",
    "skill": "Taking turns: what is still left depends on who went first - try the orders and keep track",
    "topics": ["logic", "counting"],
    "keywords": ["cookies on a tray", "who went first"],
    "version": 3,
}

# a cookie type is (shape, colour, size)
SHAPES, COLOURS, SIZES = ("heart", "round"), ("dark", "white"), ("large", "small")
TYPES = [(s, c, z) for z in SIZES for s in SHAPES for c in COLOURS]
ORIGINAL = Counter({("round", "white", "large"): 2, ("heart", "dark", "large"): 4,
                    ("heart", "white", "large"): 1, ("heart", "white", "small"): 1,
                    ("heart", "dark", "small"): 5, ("round", "white", "small"): 3})
GIRLS = ["Tina", "Emma", "Rosa", "Mia", "Lena", "Ida", "Zoe", "Nora"]
# what each girl takes: (attribute index, value, words)
RULES = [(0, "heart", "all the <b>heart-shaped</b> cookies"),
         (1, "white", "all the <b>white</b> cookies"),
         (2, "large", "all the <b>large</b> cookies")]
DARK = colors.Color(0.25, 0.25, 0.25)


# ------------------------------------------------------------------ the rules
def takes(tray, order):
    """Counts version: each girl in turn takes every cookie type that fits her rule."""
    left = Counter(tray)
    out = []
    for g in order:
        idx, val, _ = RULES[g]
        got = Counter({t: n for t, n in left.items() if t[idx] == val and n})
        for t in got:
            left[t] = 0
        out.append(got)
    return out, +left


def simulate(tray, order):
    """Answer check, written separately: a list of single cookies, removed one at a time."""
    cookies = [t for t in TYPES for _ in range(tray.get(t, 0))]
    got = []
    for g in order:
        idx, val, _ = RULES[g]
        mine = [c for c in cookies if c[idx] == val]
        cookies = [c for c in cookies if c[idx] != val]
        got.append(sorted(mine))
    return got, sorted(cookies)


def random_tray(rng, harder, leftover=False):
    kinds = [t for t in TYPES if not (t[0] == "round" and t[1] == "dark" and t[2] == "small")]
    k = rng.randint(5, 6) if harder else rng.randint(4, 5)
    chosen = rng.sample(kinds, k)
    tray = Counter({t: rng.randint(1, 4 if harder else 3) for t in chosen})
    if leftover:
        tray[("round", "dark", "small")] = rng.randint(1, 4)
    return tray


def unique_order(rng, harder):
    """A tray where the three numbers taken (in any order) give away the order."""
    while True:
        tray = ORIGINAL if (not harder and rng.random() < 0.3) else random_tray(rng, harder)
        res = {o: sorted(sum(c.values()) for c in takes(tray, o)[0]) for o in permutations(range(3))}
        for o, nums in res.items():
            if len(set(nums)) == 3 and min(nums) > 1 and sum(1 for v in res.values() if v == nums) == 1:
                return tray, o


# ------------------------------------------------------------------ picture
def heart(f, cx, cy, r, fill):
    import math
    pts = []
    for i in range(40):
        t = 2 * math.pi * i / 40
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + r * x / 17, cy + r * (y + 2) / 17))
    f.poly(pts, fill=fill, width=0.9)


def cookie(f, x, t, y=0):
    shape, col, size = t
    r = 0.45 if size == "large" else 0.27
    fill = DARK if col == "dark" else colors.white
    if shape == "heart":
        heart(f, x, y + 0.5, r, fill)
    else:
        f.circle(x, y + 0.5, r * 0.9, fill=fill, width=0.9)


def row_pic(cookie_list, scale=22, tray=True, per_row=None):
    """Cookies side by side (large ones first, as on the tray); per_row wraps them into rows."""
    rows = [cookie_list[i:i + per_row] for i in range(0, len(cookie_list), per_row)] if per_row else [cookie_list]
    widths = [0.3 + sum(1.0 if t[2] == "large" else 0.65 for t in r) for r in rows]
    W, H = max(widths), len(rows)
    f = Fig(W, H, scale=scale, margin=3)
    if tray:
        f.rect(0, 0, W, H, fill=colors.white, width=1.2)
    for j, r in enumerate(rows):
        x = 0.15
        for t in r:
            w = 1.0 if t[2] == "large" else 0.65
            cookie(f, x + w / 2, t, y=H - 1 - j)
            x += w
    return f.drawing()


def tray_pic(tray):
    order = sorted(tray.elements(), key=lambda t: (t[2] != "large", t[0], t[1]))
    return row_pic(order)


def _names(rng):
    return rng.sample(GIRLS, 3)


def _story(names, tray_text=True):
    lines = "\n".join(f"- {names[i]} takes {RULES[i][2]} that are still on the tray." for i in range(3))
    return ("This tray of cookies lies in the kitchen. Some cookies are dark (chocolate), some are white. "
            "Three girls take cookies from the tray, one after the other:\n" + lines + "\n\n")


def _list(names, idx):
    return ", ".join(names[i] for i in idx[:-1]) + " and then " + names[idx[-1]]


# ------------------------------------------------------------------ variants
@variant(difficulty=1)
def given_order(rng, harder):
    """The order is known: how many cookies does the last girl get?"""
    tray = random_tray(rng, harder) if rng.random() < 0.7 else ORIGINAL
    names = _names(rng)
    order = list(rng.sample(range(3), 3))
    who = 2 if harder else rng.choice([1, 2])
    got, _ = takes(tray, order)
    ans = sum(got[who].values())
    g = order[who]
    text = (_story(names) + f"First {names[order[0]]} goes, then {names[order[1]]}, then {names[order[2]]}. "
            f"How many cookies does <b>{names[g]}</b> take?")
    alone = sum(n for t, n in tray.items() if t[RULES[g][0]] == RULES[g][1])
    sol = (f"Cross out what the girls before {names[g]} take first. Of her cookies only {ans} {'is' if ans == 1 else 'are'} still on "
           f"the tray (she would get {alone} if she went first).")
    mistakes = [alone, ans + 1, ans - 1, ans + 2, sum(tray.values()) - ans]
    choices, ai = numeric_choices(ans, [m for m in mistakes if m >= 0], rng, lo=0, order="asc")
    return Question(text=text, figure=tray_pic(tray), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, len(simulate(tray, order)[0][who])))


@variant(difficulty=2)
def left_over(rng, harder):
    """Some cookies fit nobody: how many are left at the end, whatever the order?"""
    tray = random_tray(rng, harder, leftover=True)
    names = _names(rng)
    ans = tray[("round", "dark", "small")]
    text = (_story(names) + "We do not know in which order they go. How many cookies are still on the tray "
            "after all three girls have taken theirs?")
    sol = (f"A cookie stays only if it is not a heart, not white and not large: the small dark round ones. "
           f"There {'is' if ans == 1 else 'are'} {ans} of them - the order does not matter.")
    mistakes = [ans + 1, ans + 2, max(ans - 1, 0), 0, ans + tray[("round", "dark", "large")]]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=0, order="asc")
    lefts = {len(simulate(tray, o)[1]) for o in permutations(range(3))}
    value = lefts.pop() if len(lefts) == 1 else -1
    return Question(text=text, figure=tray_pic(tray), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, value))


def _numbers_text(nums):
    return f"One of the girls takes {nums[0]} cookies, one takes {nums[1]} and one takes {nums[2]}. "


@variant(difficulty=2)
def which_order(rng, harder):
    """The three numbers are known: in which order did the girls go?"""
    tray, order = unique_order(rng, harder)
    names = _names(rng)
    nums = sorted(sum(c.values()) for c in takes(tray, order)[0])
    others = [o for o in permutations(range(3)) if o != order]
    rng.shuffle(others)
    opts = others[:4] + [order]
    rng.shuffle(opts)
    text = (_story(names) + _numbers_text(nums) + "In which order did the girls take their cookies?")
    got = takes(tray, order)[0]
    sol = (f"Try the orders and count what is still on the tray. Only {_list(names, order)} gives "
           + ", ".join(f"{names[g]} {sum(got[i].values())}" for i, g in enumerate(order)) + ".")

    def check(i):
        return sorted(len(x) for x in simulate(tray, opts[i])[0]) == nums
    return Question(text=text, figure=tray_pic(tray), choices=[_list(names, o) for o in opts],
                    answer=opts.index(order), solution=sol, check=check)


@variant(difficulty=3)
def how_many_one(rng, harder):
    """The three numbers are known: how many did one named girl take?"""
    tray, order = unique_order(rng, harder)
    names = _names(rng)
    got = takes(tray, order)[0]
    nums = sorted(sum(c.values()) for c in got)
    g = rng.randrange(3)
    ans = sum(got[order.index(g)].values())
    text = _story(names) + _numbers_text(nums) + f"How many cookies did <b>{names[g]}</b> take?"
    alone = sum(n for t, n in tray.items() if t[RULES[g][0]] == RULES[g][1])
    sol = (f"Try the orders one by one. Only {_list(names, order)} gives {nums[0]}, {nums[1]} and {nums[2]}. "
           f"So {names[g]} took {ans}.")
    mistakes = [n for n in nums if n != ans] + [alone, ans + 1, ans - 1]
    choices, ai = numeric_choices(ans, [m for m in mistakes if m > 0], rng, lo=1, order="asc")

    def value():
        fits = [o for o in permutations(range(3))
                if sorted(len(x) for x in simulate(tray, o)[0]) == nums]
        vals = {len(simulate(tray, o)[0][o.index(g)]) for o in fits}
        return vals.pop() if len(vals) == 1 else -1
    return Question(text=text, figure=tray_pic(tray), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, value()))


@variant(difficulty=3)
def which_group(rng, harder):
    """The original: which group of cookies did one of the girls take?"""
    tray, order = unique_order(rng, harder)
    names = _names(rng)
    got = takes(tray, order)[0]
    nums = sorted(sum(c.values()) for c in got)
    real = [frozenset(c.items()) for c in got]
    small = [r for r in real if sum(n for _, n in r) <= 8]
    if not small:
        return which_group(rng, harder)
    right = rng.choice(small)
    pool = set()
    for o in permutations(range(3)):
        for c in takes(tray, o)[0]:
            fc = frozenset(c.items())
            if sum(c.values()) and fc not in real:
                pool.add(fc)
    for c in got:                               # near misses: one cookie more or less
        for t in TYPES:
            for d in (1, -1):
                cc = Counter(c)
                cc[t] += d
                if cc[t] >= 0 and cc[t] <= tray.get(t, 0):
                    fc = frozenset((+cc).items())
                    if fc not in real and sum(cc.values()) > 0:
                        pool.add(fc)
    pool = sorted((p for p in pool if sum(n for _, n in p) <= 8), key=lambda s: sorted(s))
    if len(pool) < 4:
        return which_group(rng, harder)
    rng.shuffle(pool)
    opts = pool[:4] + [right]
    rng.shuffle(opts)
    text = (_story(names) + _numbers_text(nums) + "Which of these groups of cookies did one of the girls take?")
    sol = (f"Try the orders. Only {_list(names, order)} gives {nums[0]}, {nums[1]} and {nums[2]}: "
           + ", ".join(f"{names[g]} takes {sum(got[i].values())}" for i, g in enumerate(order)) + ".")

    def draw(fc):
        return row_pic(sorted(Counter(dict(fc)).elements(), key=lambda t: (t[2] != "large", t[0], t[1])),
                       scale=17, tray=False, per_row=4)

    def check(i):
        want = sorted(Counter(dict(opts[i])).elements())
        for o in permutations(range(3)):
            got_o = simulate(tray, o)[0]
            if sorted(len(x) for x in got_o) == nums and any(x == want for x in got_o):
                return True
        return False
    return Question(text=text, figure=tray_pic(tray), choices=list("ABCDE"),
                    choice_figures=[draw(o) for o in opts], answer=opts.index(right), solution=sol, check=check)
