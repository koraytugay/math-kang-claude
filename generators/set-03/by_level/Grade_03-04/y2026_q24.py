"""2026 Q24 (Canada, Grade 3-4) - drawing balls: how many must you draw to be SURE?

Original: Rachel has red, green and blue balls in a box. She must draw 13 balls to be sure she gets a red
one, 16 to be sure she gets a green one, and 14 to be sure she gets a blue one. How many blue balls are in
the box?  (A) 5 (B) 6 (C) 7 (D) 8 (E) 9.
To be sure of a red ball she must be ready for the worst luck: all the balls that are not red come out first,
so 13 draws mean 12 balls are not red. Likewise 15 are not green and 13 are not blue. Add the three:
each ball is "not" two colours, so 2 x all = 12 + 15 + 13 = 40, all = 20 and blue = 20 - 13 = 7.  Answer: C.
(The 2026 key in the repo is our own: solved by us; brute force over all boxes agrees.)

Core skill: "to be sure" means the worst luck: draw all the balls of the OTHER colours first, then one more.
So (draws needed) - 1 = the balls that are not that colour. Children say "13 red balls" or forget the +1.

Easy versions come first: the balls are drawn, one colour is asked, then two colours only, and the reverse
with one unknown colour; the contest question (three clues) is the hardest.
"""
from itertools import product

from reportlab.lib import colors

from kangaroo import Fig, Question, numeric_choices, value_check, variant

META = {
    "source": "set-03/by_level/Grade_03-04/2026 Q24",
    "skill": "To be sure you get a colour, imagine the worst luck: all the balls of the other colours come out first, "
             "then one more. So the number of draws minus 1 is the number of balls that are not that colour",
    "topics": ["logic", "counting", "arithmetic"],
    "keywords": ["sure to get", "worst luck", "drawing balls"],
    "sticker": ("🎩", "Sure-draw wizard"),   # earned when this skill is solid (website)
    "rungs": ("easier", "easier", "aligned", "harder"),   # vs the original contest question: steps 1, 2, 3, 3 harder (2026-11-23)
    "version": 1,
}

PEOPLE = ["Rachel", "Mia", "Lena", "Nora", "Sara", "Ella", "Zoe", "Maya"]
COLOURS = {"red": colors.Color(0.9, 0.15, 0.15), "green": colors.Color(0.2, 0.7, 0.25),
           "blue": colors.Color(0.2, 0.4, 0.9)}
NAMES = ["red", "green", "blue"]


# ------------------------------------------------------------------ the check: try every draw
def _reachable(sizes):
    """Every number of balls you can draw using none of the other colours' ... : all ways to take 0..n from each group."""
    reach = {0}
    for n in sizes:
        reach = {a + t for a in reach for t in range(n + 1)}
    return reach


def draws_needed(counts, colour):
    """Fewest draws that are SURE to give at least one ball of `colour`: the first number k for which no way
    of drawing k balls from the other colours exists (every way of taking 0..n from each other colour is tried)."""
    reach = _reachable([n for c, n in counts.items() if c != colour])
    for k in range(1, sum(counts.values()) + 1):
        if k not in reach:
            return k
    return None


def draws_all_colours(counts):
    """Fewest draws that are SURE to give every colour: the first k for which every way of drawing k balls
    (any numbers x, y, z within the counts adding to k) has all of x, y, z at least 1."""
    cs = list(counts.values())
    for k in range(1, sum(cs) + 1):
        ways = [(x, y, z) for x in range(min(cs[0], k) + 1) for y in range(min(cs[1], k) + 1)
                for z in range(min(cs[2], k) + 1) if x + y + z == k]
        if all(min(w) >= 1 for w in ways):
            return k
    return None


# ------------------------------------------------------------------ pictures
def balls_pic(counts, rng, per_row=6, max_px=150):
    """A box with all the balls, mixed up."""
    balls = [c for c, n in counts.items() for _ in range(n)]
    rng.shuffle(balls)
    rows = (len(balls) + per_row - 1) // per_row
    f = Fig(per_row + 0.4, rows + 0.4, max_px=max_px, margin=6)
    f.rect(0, 0, per_row + 0.4, rows + 0.4, fill=colors.Color(0.97, 0.94, 0.86), width=1.2)
    for i, c in enumerate(balls):
        r, k = divmod(i, per_row)
        f.circle(0.5 + k, rows - 0.3 - r, 0.4, fill=COLOURS[c], width=0.9)
    return f.drawing()


def _plural(n, word="ball"):
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def _list(counts):
    parts = [f"{n} {c}" for c, n in counts.items()]
    return ", ".join(parts[:-1]) + " and " + parts[-1] if len(parts) > 1 else parts[0]


# ------------------------------------------------------------------ variants
@variant(difficulty=1, rungs=("easier", "easier"))
def pictured_two(rng, harder):
    """Easiest: two colours, all balls drawn. How many must she draw to be sure of one blue ball?"""
    name = rng.choice(PEOPLE)
    a, b = (rng.randint(3, 6), rng.randint(2, 5)) if not harder else (rng.randint(5, 8), rng.randint(3, 6))
    pair = rng.sample(["red", "green", "blue"], 2)
    counts = {pair[0]: a, pair[1]: b}
    want = rng.choice(pair)
    other = pair[1] if want == pair[0] else pair[0]
    ans = counts[other] + 1
    text = (f"{name} has a box with {_list(counts)} balls, as shown. She draws balls from the box without looking."
            f"\n\nHow many balls must she draw to be <b>sure</b> to get a {want} one?")
    sol = (f"With bad luck she draws all the {counts[other]} {other} balls first. The next ball must be {want}. "
           f"So she needs {counts[other]} + 1 = {ans} draws.")
    mistakes = [(counts[want], f"count the {want} balls"), (counts[other], "forget the one more ball"),
                (sum(counts.values()), "think she must draw all the balls")]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1, order="asc")
    return Question(text=text, figure=balls_pic(counts, rng), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, draws_needed(counts, want)))


@variant(difficulty=1, rungs=("easier", "easier"))
def pictured_three(rng, harder):
    """Three colours, all balls drawn: how many to be sure of one of a colour?"""
    name = rng.choice(PEOPLE)
    counts = {c: rng.randint(2, 5 if not harder else 6) for c in NAMES}
    want = rng.choice(NAMES)
    others = {c: n for c, n in counts.items() if c != want}
    ans = sum(others.values()) + 1
    text = (f"{name} has a box with {_list(counts)} balls, as shown. She draws balls from the box without looking."
            f"\n\nHow many balls must she draw to be <b>sure</b> to get a {want} one?")
    sol = (f"With bad luck she first draws all the balls that are not {want}: "
           + " + ".join(str(n) for n in others.values()) + f" = {sum(others.values())} balls. "
           f"The next ball must be {want}. So she needs {sum(others.values())} + 1 = {ans} draws.")
    mistakes = [(counts[want], f"count the {want} balls"), (sum(others.values()), "forget the one more ball"),
                (sum(counts.values()), "think she must draw all the balls"),
                (max(others.values()) + 1, "count only one other colour")]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1, order="asc")
    return Question(text=text, figure=balls_pic(counts, rng), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, draws_needed(counts, want)))


@variant(difficulty=1, rungs=("easier", "easier"))
def first_ball_sure(rng, harder):
    """Easy reverse: the box has only one colour of balls apart from the asked one; how many other balls?"""
    name = rng.choice(PEOPLE)
    others = rng.sample(NAMES, 2)
    want = [c for c in NAMES if c not in others][0]
    known = rng.randint(2, 5)
    needed = rng.randint(known + 2, known + (5 if not harder else 8))
    ans = needed - 1 - known
    text = (f"{name} has a box with red, green and blue balls. She must draw {needed} balls to be <b>sure</b> to get a "
            f"{want} one. The box has {known} {others[0]} balls.\n\nHow many {others[1]} balls are in the box?")
    sol = (f"To be sure of a {want} ball she must draw all the balls that are not {want}, and then one more. "
           f"So {needed} - 1 = {needed - 1} balls are not {want}. {known} of them are {others[0]}, so "
           f"{needed - 1} - {known} = {ans} are {others[1]}.")
    mistakes = [(needed - known, "forget the one more ball"), (needed, "think all the draws are balls of that colour"),
                (known, "give the number you were told")]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1, order="asc")
    sols = {b for b in range(1, 40) if _consistent({want: 1, others[0]: known, others[1]: b}, want, needed)}
    # (the number of {want} balls does not change the answer: at least 1 ball of it must be in the box)
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=lambda i: sols == {int(choices[i])})


def _consistent(counts, colour, needed):
    return draws_needed(counts, colour) == needed


@variant(difficulty=2, rungs=("easier", "easier"))
def two_clues(rng, harder):
    """Two clues and the number of blue balls: how many balls are in the box?"""
    name = rng.choice(PEOPLE)
    while True:
        r, g, b = (rng.randint(2, 6 if not harder else 9) for _ in range(3))
        break
    counts = {"red": r, "green": g, "blue": b}
    c1, c2 = rng.sample(NAMES, 2)
    third = [c for c in NAMES if c not in (c1, c2)][0]
    n1, n2 = draws_needed(counts, c1), draws_needed(counts, c2)
    total = r + g + b
    text = (f"{name} has red, green and blue balls in a box. She must draw {n1} balls to be <b>sure</b> to get a {c1} "
            f"one, and {n2} to be sure to get a {c2} one. The box has {counts[third]} {third} balls."
            f"\n\nHow many balls are in the box?")
    sol = (f"To be sure of {c1} she draws all the balls that are not {c1} and one more, so {n1 - 1} balls are not {c1}: "
           f"the {c2} and the {third} balls. In the same way {n2 - 1} balls are not {c2}: the {c1} and the {third} balls. "
           f"Take away the {counts[third]} {third} balls: {n1 - 1} - {counts[third]} = {counts[c2]} {c2} balls and "
           f"{n2 - 1} - {counts[third]} = {counts[c1]} {c1} balls. All together: "
           f"{counts[c1]} + {counts[c2]} + {counts[third]} = {total}.")
    mistakes = [(n1 + n2, "add the two numbers of draws"), (n1 + n2 - 2, "add the two numbers but forget the third colour"),
                (n1 - 1 + n2 - 1 - counts[third], "forget the balls of the third colour"),
                (counts[c1] + counts[c2], "leave out the balls of the colour you were told")]
    choices, ai = numeric_choices(total, mistakes, rng, lo=3, order="asc")
    # every box that fits the clues (try them all)
    fits = {x + y + counts[third] for x in range(1, 30) for y in range(1, 30)
            if draws_needed({c1: x, c2: y, third: counts[third]}, c1) == n1
            and draws_needed({c1: x, c2: y, third: counts[third]}, c2) == n2}
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=lambda i: fits == {int(choices[i])})


@variant(difficulty=2, rungs=("easier", "easier"))
def all_colours(rng, harder):
    """Twist: how many to be sure of getting every colour? (the two biggest groups come out first)"""
    name = rng.choice(PEOPLE)
    while True:
        counts = {c: rng.randint(1, 4 if not harder else 6) for c in NAMES}
        if len(set(counts.values())) == 3:
            break
    ans = sum(counts.values()) - min(counts.values()) + 1
    small = min(counts, key=counts.get)
    text = (f"{name} has a box with {_list(counts)} balls, as shown. She draws balls without looking."
            f"\n\nHow many balls must she draw to be <b>sure</b> to get a ball of <b>each</b> colour?")
    others = sum(counts.values()) - counts[small]
    sol = (f"The worst luck is that she draws every ball of the two colours with the most balls before the first "
           f"{small} one ({small} has the fewest). That is {others} balls, and the next ball must be the {small}: "
           f"{others} + 1 = {ans} draws.")
    mistakes = [(others, "forget the one more ball"), (sum(counts.values()), "think she must draw all the balls"),
                (3, "think three draws are enough"), (max(counts.values()) + 1, "look at only one colour")]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=3, order="asc")
    return Question(text=text, figure=balls_pic(counts, rng), choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, draws_all_colours(counts)))


@variant(difficulty=3, rungs=("aligned", "harder"))
def three_clues(rng, harder):
    """The original: three clues, how many balls of one colour?"""
    name = rng.choice(PEOPLE)
    r, g, b = (rng.randint(3, 9 if not harder else 12) for _ in range(3))
    counts = {"red": r, "green": g, "blue": b}
    need = {c: draws_needed(counts, c) for c in NAMES}
    ask = rng.choice(NAMES)
    total = (sum(need.values()) - 3) // 2
    text = (f"{name} has red, green and blue balls in a box. She must draw {need['red']} balls to be <b>sure</b> she "
            f"gets a red one, {need['green']} to be sure she gets a green one, and {need['blue']} to be sure she gets "
            f"a blue one.\n\nHow many {ask} balls are in the box?")
    ans = counts[ask]
    sol = (f"To be sure of a colour she must draw all the balls of the other colours and one more. So "
           f"{need['red'] - 1} balls are not red, {need['green'] - 1} are not green and {need['blue'] - 1} are not blue. "
           f"Every ball is 'not' two of the colours, so these three numbers add up to twice the number of balls: "
           f"{need['red'] - 1} + {need['green'] - 1} + {need['blue'] - 1} = {sum(need.values()) - 3}, "
           f"so the box has {total} balls. The {ask} balls are the rest: {total} - {need[ask] - 1} = {ans}.")
    mistakes = [(need[ask], f"think the number of draws is the number of {ask} balls"),
                (need[ask] - 1, f"count the balls that are not {ask}"),
                (total, "give the number of all the balls"),
                (sum(need.values()) - 3 - (need[ask] - 1), "forget to halve")]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1, order="asc")
    fits = set()
    for x, y, z in product(range(1, 22), repeat=3):          # every box that fits the three clues
        box = {"red": x, "green": y, "blue": z}
        if all(draws_needed(box, c) == need[c] for c in NAMES):
            fits.add(box[ask])
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=lambda i: fits == {int(choices[i])})


@variant(difficulty=3, rungs=("aligned", "harder"))
def three_clues_total(rng, harder):
    """The contest clues, asking for all the balls (the middle step of the contest question)."""
    name = rng.choice(PEOPLE)
    r, g, b = (rng.randint(3, 9 if not harder else 12) for _ in range(3))
    counts = {"red": r, "green": g, "blue": b}
    need = {c: draws_needed(counts, c) for c in NAMES}
    notsum = sum(need.values()) - 3
    total = notsum // 2
    text = (f"{name} has red, green and blue balls in a box. She must draw {need['red']} balls to be <b>sure</b> she "
            f"gets a red one, {need['green']} to be sure she gets a green one, and {need['blue']} to be sure she gets "
            f"a blue one.\n\nHow many balls are in the box?")
    sol = (f"To be sure of a colour she must draw all the balls of the other colours and one more. So "
           f"{need['red'] - 1} balls are not red, {need['green'] - 1} are not green and {need['blue'] - 1} are not blue. "
           f"Every ball is 'not' two of the colours, so these add up to twice the number of balls: "
           f"{need['red'] - 1} + {need['green'] - 1} + {need['blue'] - 1} = {notsum}. The box has {notsum} / 2 = {total} balls.")
    mistakes = [(notsum, "forget to halve"),
                (sum(need.values()), "add the three numbers of draws"),
                (max(need.values()), "take the biggest number of draws"),
                (total - 1, "stop one short of the last ball")]
    choices, ai = numeric_choices(total, mistakes, rng, lo=1, order="asc")
    fits = set()
    for x, y, z in product(range(1, 22), repeat=3):          # every box that fits the three clues
        box = {"red": x, "green": y, "blue": z}
        if all(draws_needed(box, c) == need[c] for c in NAMES):
            fits.add(sum(box.values()))
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=lambda i: fits == {int(choices[i])})
