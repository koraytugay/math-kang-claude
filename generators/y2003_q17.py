"""2003 Q17 - a bar code of 17 black and white bars.

Original: A bar code is formed using 17 black and white bars (the first and last
bars are black). The black bars are wide or narrow. The number of white bars is
3 more than the number of wide black bars. The number of narrow black bars is:
A 1  B 2  C 3  D 4  E 5.
Black and white alternate: 9 black, 8 white. Wide = 8 - 3 = 5, narrow = 9 - 5 = 4.
Answer: D.

Core skill: in an alternating row that starts and ends with the same colour there
is one more of that colour (like fence posts and gaps); then split a group into
two parts using a "3 more than" clue. (Nice fact: the narrow bars are always
"3 + 1", however long the code is.)
"""
from reportlab.lib import colors

from kangaroo import Fig, Question, numeric_choices, value_check, variant
from kangaroo.solve import only

META = {
    "source": "2003 Q17",
    "skill": "Alternating rows: starts and ends the same, so one more of that kind; then split a group",
    "topics": ["counting", "logic", "patterns"],
    "version": 1,
}

NAMES = ["Mia", "Leo", "Sara", "Tom", "Nina", "Omar"]


def barcode_pic(rng):
    """A small sample bar code with dots in the middle (just to show what is meant)."""
    f = Fig(16, 5, scale=5.5, margin=3)
    x = 0.0
    for part in range(2):
        for _ in range(4):
            w = rng.choice([0.6, 1.4])
            f.rect(x, 0, w, 5, fill=colors.black, width=0.1)
            x += w + 0.7
        if part == 0:
            for k in range(5):
                f.circle(x + 0.3 + k * 0.6, 2.5, 0.12, fill=colors.black, width=0.1)
            x += 3.6
    return f.drawing()


def lay_out(n):
    """Answer checks: actually lay out n bars, black first, taking turns -> (#black, #white)."""
    row = ["black" if i % 2 == 0 else "white" for i in range(n)]
    return row.count("black"), row.count("white")


def wide_narrow(n, d):
    """Try every number of wide black bars; keep the one with d more white bars than wide ones."""
    black, white = lay_out(n)
    wide = only(w for w in range(black + 1) if white - w == d)
    return wide, black - wide


def _code(rng, harder, lo, hi):
    n = rng.choice(range(lo + 4, hi + 10, 2) if harder else range(lo, hi, 2))
    black, white = (n + 1) // 2, (n - 1) // 2
    d = rng.randint(1, white - 1)
    return n, black, white, d


@variant(difficulty=1)
def narrow_bars(rng, harder):
    """The original."""
    n, black, white, d = _code(rng, harder, 9, 21)
    wide = white - d
    narrow = black - wide
    text = (f"A bar code is made of {n} black and white bars, black and white taking turns. The first "
            f"and the last bar are black. Each black bar is either wide or narrow. There are {d} more "
            f"white bars than wide black bars.")
    after = "How many narrow black bars are there?"
    sol = (f"Black is at both ends, so there are {black} black and {white} white bars. "
           f"Wide: {white} − {d} = {wide}. Narrow: {black} − {wide} = {narrow}.")
    mistakes = [d,                      # forgot the extra black bar
                wide, n // 2 - wide,    # used n ÷ 2 black bars
                d + 2, black - d]
    choices, ai = numeric_choices(narrow, mistakes, rng, lo=0)
    return Question(text=text, figure=barcode_pic(rng), after_figure=after, choices=choices, answer=ai,
                    solution=sol,
                    check=value_check(choices, wide_narrow(n, d)[1]))


@variant(difficulty=1)
def fence(rng, harder):
    """Posts and boards: one more post than boards."""
    n = rng.choice(range(11, 41, 2) if harder else range(7, 25, 2))
    posts = (n + 1) // 2
    ask = rng.choice(["posts", "boards"])
    ans = posts if ask == "posts" else posts - 1
    name = rng.choice(NAMES)
    text = (f"{name} builds a straight fence from {n} pieces: posts and boards take turns, and the "
            f"fence starts and ends with a post.")
    after = f"How many {ask} are there?"
    sol = (f"Post, board, post, ..., post: there is one more post than boards. "
           f"{n} = {posts} + {posts - 1}, so {posts} posts and {posts - 1} boards.")
    mistakes = [n // 2, posts + 1, posts - 1, posts, n, n // 2 + 2]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, lay_out(n)[0] if ask == "posts" else lay_out(n)[1]))


@variant(difficulty=2)
def wide_bars(rng, harder):
    """Ask for the wide bars instead - now the length really matters."""
    n, black, white, d = _code(rng, harder, 11, 25)
    wide = white - d
    text = (f"A bar code is made of {n} black and white bars taking turns, with a black bar at each "
            f"end. Each black bar is wide or narrow. There are {d} more white bars than wide black bars.")
    after = "How many wide black bars are there?"
    sol = f"There are {black} black and {white} white bars. Wide: {white} − {d} = {wide}."
    mistakes = [black - d, white + d, n // 2 - d + 1, wide - 1, d + 1, black - wide]
    choices, ai = numeric_choices(wide, mistakes, rng, lo=0)
    return Question(text=text, figure=barcode_pic(rng), after_figure=after, choices=choices, answer=ai,
                    solution=sol,
                    check=value_check(choices, wide_narrow(n, d)[0]))


@variant(difficulty=2)
def necklace(rng, harder):
    """Same structure, different story: beads on a string."""
    n, red, blue, d = _code(rng, harder, 11, 25)
    big = blue - d
    small = red - big
    ask_small = rng.random() < 0.5
    name = rng.choice(NAMES)
    text = (f"{name} threads {n} beads on a string: red and blue take turns, and the string starts and "
            f"ends with a red bead. Each red bead is big or small. There are {d} more blue beads than "
            f"big red beads.")
    after = f"How many {'small' if ask_small else 'big'} red beads are there?"
    ans = small if ask_small else big
    sol = (f"There are {red} red and {blue} blue beads. Big red: {blue} − {d} = {big}. "
           + (f"Small red: {red} − {big} = {small}." if ask_small else ""))
    mistakes = ([d, big, small + 1, n // 2 - big] if ask_small else [small, red - d, big + 1, n // 2 - d])
    choices, ai = numeric_choices(ans, mistakes, rng, lo=0)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, wide_narrow(n, d)[1 if ask_small else 0]))


@variant(difficulty=3)
def ends_differ(rng, harder):
    """Twist: starts black but ends white - now there are as many black bars as white."""
    n = rng.choice(range(14, 32, 2) if harder else range(10, 22, 2))
    black = white = n // 2
    d = rng.randint(1, white - 1)
    wide = white - d
    narrow = black - wide
    text = (f"A bar code is made of {n} black and white bars taking turns. It starts with a black bar "
            f"and ends with a <b>white</b> bar. Each black bar is wide or narrow. There are {d} more "
            f"white bars than wide black bars.")
    after = "How many narrow black bars are there?"
    sol = (f"Starting black and ending white, the bars come in pairs: {black} black and {white} white. "
           f"Wide: {white} − {d} = {wide}. Narrow: {black} − {wide} = {narrow}.")
    mistakes = [d + 1,                  # answered as if black were at both ends
                wide, d - 1, d + 2, black - d - 1]
    choices, ai = numeric_choices(narrow, mistakes, rng, lo=0)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, wide_narrow(n, d)[1]))
