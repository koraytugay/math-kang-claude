"""2023 Q22 (Ecolier, Grade 3-4) - a turning machine and a printing machine: in which order?

Original: Else has two machines R and S. If she puts a square piece of paper into machine R it is
rotated (picture: a quarter turn clockwise - the little black corner mark goes from bottom left to
top left). If she puts the piece of paper in machine S it is printed on (an upright club appears in
the middle). She wants to produce the following picture: (mark top right, club lying on its side
with the stem to the left). In which order does Else use the two machines so that she gets this
picture?  (A) SRR  (B) RSR  (C) RSS  (D) RRS  (E) SRS.
The mark turned 2 quarter turns, so R is used twice; the club turned 1 quarter turn, so exactly one
R comes after S: R S R.  Answer: B (answer key: B).

Core skill: follow two things at once (or work backwards): the corner mark counts ALL the turns,
the club counts only the turns AFTER printing. Children check only the club, or only the mark.
"""
import math

from reportlab.lib import colors

from kangaroo import Fig, Question, numeric_choices, text_choices, value_check, variant, warmup
from kangaroo.choices import Choices
from kangaroo.figures import column, row

META = {
    "source": "set-01/by_level/Grade_03-04_Ecolier/2023 Q22",
    "skill": "Turning machine and printing machine: the corner mark counts all the turns, the picture "
             "only the turns after it was printed",
    "topics": ["spatial", "logic"],
    "keywords": ["turning machine", "quarter turns", "machine order"],
    "version": 2,
}

NAMES = ["Else", "Mia", "Tom", "Anna", "Leo", "Sara"]
GREY = colors.Color(0.78, 0.78, 0.78)


# ------------------------------------------------------------------ the machines
def run(seq, start=0):
    """Simulate: returns (mark turns, [turns of each print]) - all as quarter turns clockwise.
    R = quarter turn clockwise, L = quarter turn anticlockwise, S = print an upright club."""
    mark, prints = start, []
    for m in seq:
        if m == "R":
            mark += 1
            prints = [p + 1 for p in prints]
        elif m == "L":
            mark -= 1
            prints = [p - 1 for p in prints]
        elif m == "S":
            prints.append(0)
    return mark % 4, [p % 4 for p in prints]


# ------------------------------------------------------------------ drawing
def _rot(pt, k):
    """Turn a point of the unit square k quarter turns clockwise around the middle."""
    x, y = pt[0] - 0.5, pt[1] - 0.5
    for _ in range(k % 4):
        x, y = y, -x
    return x + 0.5, y + 0.5


def paper(mark, prints, size=34):
    """A square sheet with its corner mark (turned `mark` times) and clubs (each turned)."""
    f = Fig(1, 1, max_px=size, margin=2)
    f.rect(0, 0, 1, 1, fill=colors.white, width=1.0)
    m = 0.13
    f.poly([_rot(p, mark) for p in [(0, 0), (m, 0), (m, m), (0, m)]], fill=colors.black, width=0.3)
    for k in prints:
        for cx, cy in [(0.5, 0.64), (0.36, 0.47), (0.64, 0.47)]:
            x, y = _rot((cx, cy), k)
            f.circle(x, y, 0.135, fill=colors.black, width=0.3)
        f.poly([_rot(p, k) for p in [(0.5, 0.5), (0.41, 0.2), (0.59, 0.2)]], fill=colors.black, width=0.3)
    return f.drawing()


def machine(letter, size=34):
    f = Fig(1, 1, max_px=size, margin=2, font_size=size * 0.55)
    f.rect(0, 0, 1, 1, fill=GREY, width=1.0)
    f.text(0.5, 0.5, letter, size=size * 0.55)
    return f.drawing()


def arrow(size=16):
    f = Fig(1, 0.6, max_px=size, margin=1)
    f.line((0, 0.3), (0.75, 0.3), width=1.1)
    f.poly([(1, 0.3), (0.7, 0.45), (0.7, 0.15)], fill=colors.black, width=0.5)
    return f.drawing()


def chain(items):
    out = []
    for i, it in enumerate(items):
        if i:
            out.append(arrow())
        out.append(it)
    return row(out, gap=3)


def legend(machines=("R", "S")):
    rows = []
    for m in machines:
        mark, prints = run(m)
        rows.append(chain([paper(0, []), machine(m), paper(mark, prints)]))
    return column(rows, gap=6)


def _picture_text(machines):
    t = (f"There are {'three' if 'L' in machines else 'two'} machines for square sheets of paper "
         "(see the pictures):\n"
         "- Machine R turns the sheet a quarter turn clockwise.\n"
         "- Machine S prints a club in the middle.\n")
    if "L" in machines:
        t += "- Machine L turns the sheet a quarter turn anticlockwise.\n"
    return t + "\n"


# ------------------------------------------------------------------ variants
def _all(length, letters="RS"):
    out = [""]
    for _ in range(length):
        out = [s + c for s in out for c in letters]
    return out


@variant(difficulty=1)
def which_order(rng, harder):
    """The original: which order of machines gives this picture?"""
    n = 4 if harder else 3
    while True:
        seqs = [s for s in _all(n) if s.count("S") == 1]
        right = rng.choice(seqs)
        target = run(right)
        good = [s for s in seqs if run(s) == target]
        if len(good) != 1:
            continue
        others = [s for s in _all(n) if run(s) != target and s.count("S") >= 1]
        # the traps: right number of turns but S in the wrong place; S in the right place, wrong turns
        same_mark = [s for s in others if run(s)[0] == target[0]]
        same_club = [s for s in others if run(s)[1][-1:] == target[1]]
        wrong = []
        for pool in (same_mark, same_club, others, others):
            c = [s for s in pool if s not in wrong]
            if c:
                wrong.append(rng.choice(c))
        if len(wrong) == 4:
            break
    name = rng.choice(NAMES)
    labels = []
    for w in wrong:
        if run(w)[0] == target[0]:
            labels.append((w, "check only the corner mark"))
        elif run(w)[1][-1:] == target[1]:
            labels.append((w, "check only the club"))
        else:
            labels.append((w, "lose count of the quarter turns"))
    choices, ai = text_choices(right, labels, rng)
    fig = column([legend(), chain([paper(0, []), machine("?"), machine("?"), machine("?")] +
                                  ([machine("?")] if n == 4 else []) + [paper(*target)])], gap=12)
    text = (_picture_text("RS") + f"{name} uses the machines {n} times in a row and gets the picture at the end "
            f"of the bottom row. In which order does {name} use the machines?")
    after = right[right.index("S") + 1:].count("R")
    club = ("The club stands upright, so S comes last" if after == 0 else
            f"The club turned {after} quarter turn{'s' if after != 1 else ''}, so {after} R "
            f"come{'s' if after == 1 else ''} after S")
    sol = (f"The corner mark turned {target[0]} quarter turn{'s' if target[0] != 1 else ''}, so machine R is used "
           f"{right.count('R')} time{'s' if right.count('R') != 1 else ''}. {club}: {right}.")
    return Question(text=text, figure=fig, choices=choices, answer=ai, solution=sol,
                    check=lambda i: run(choices[i]) == target)


@variant(difficulty=2)
def which_picture(rng, harder):
    """Forwards: the order is given; which picture comes out?"""
    n = 5 if harder else 4
    while True:
        seq = "".join(rng.choice("RRS") for _ in range(n))
        if seq.count("S") == 1 and "R" in seq[seq.index("S"):] and seq.count("R") >= 2:
            break
    mark, prints = run(seq)
    k = prints[0]
    opts = {(mark, k)}
    labels = {}
    for m2, k2, why in [(mark, seq.count("R") % 4, "turn the club with all the turns"),
                        (k, k, "turn the mark only after printing"),
                        ((mark + 2) % 4, k, "lose count of the turns"),
                        (mark, (k + 1) % 4, "turn the club the wrong way"),
                        ((mark + 1) % 4, k, "lose count of the turns"),
                        (mark, (k + 2) % 4, "lose count of the turns of the club")]:
        if (m2, k2) not in opts and len(opts) < 5:
            opts.add((m2, k2))
            labels[(m2, k2)] = why
    opts = sorted(opts)
    rng.shuffle(opts)
    ai = opts.index((mark, k))
    name = rng.choice(NAMES)
    text = (_picture_text("RS") + f"{name} puts a sheet in the machines in this order: "
            f"<b>{' '.join(seq)}</b>. What does the sheet look like at the end?")
    after = seq[seq.index("S") + 1:].count("R")
    sol = (f"The mark turns with every R: {seq.count('R')} quarter turns. The club is printed upright and then "
           f"turns only with the {after} R after S.")
    choices = Choices([f"picture {c}" for c in "ABCDE"],
                      {i: labels[o] for i, o in enumerate(opts) if i != ai})
    return Question(text=text, figure=legend(), choices=choices,
                    choice_figures=[paper(m2, [k2], size=40) for m2, k2 in opts], answer=ai, solution=sol,
                    check=lambda i: (opts[i][0], [opts[i][1]]) == run(seq))


@variant(difficulty=3)
def fewest_turns(rng, harder):
    """How often at least must machine R be used to get this picture?"""
    mark, k = rng.randrange(4), rng.randrange(4)
    if mark == k == 0:
        k = rng.randint(1, 3)
    name = rng.choice(NAMES)
    text = (_picture_text("RS") + f"{name} uses machine S once and machine R as often as needed. "
            f"How many times at least must {name} use machine R to get this picture?")
    before = (mark - k) % 4
    ans = before + k
    club = ("The club stands upright, so no R comes after S." if k == 0 else
            f"The club is turned {k} quarter turn{'s' if k != 1 else ''}, so {k} R "
            f"come{'s' if k == 1 else ''} after S.")
    sol = (f"{club} The mark needs {before} more quarter turn{'s' if before != 1 else ''} before S. "
           f"Together {ans}.")
    mistakes = [(k, "count only the turns of the club"), (mark, "count only the turns of the mark"),
                (mark + k, "add the turns of the mark and of the club"), ans + 4]
    # check: brute force over all orders with one S and up to 9 machines
    best = min(s.count("R") for L in range(1, 10) for s in _all(L) if s.count("S") == 1 and run(s) == (mark, [k]))
    choices, ai = numeric_choices(ans, mistakes, rng, lo=0, order="asc")
    fig = column([legend(), paper(mark, [k], size=44)], gap=10)
    return Question(text=text, figure=fig, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, best))


@variant(difficulty=3)
def left_machine(rng, harder):
    """Twist: a third machine L turns anticlockwise."""
    n = 4 if harder else 3
    while True:
        seqs = [s for s in _all(n, "RLS") if s.count("S") == 1]
        right = rng.choice(seqs)
        target = run(right)
        if right.count("L") == 0 or target == (0, [0]):
            continue
        cands = [s for s in seqs if run(s) == target]
        others = [s for s in _all(n, "RLS") if s.count("S") >= 1 and run(s) != target]
        if len(cands) >= 1 and len(others) >= 4:
            break
    right = rng.choice(cands)
    same_mark = [s for s in others if run(s)[0] == target[0]]
    wrong = rng.sample(same_mark, min(2, len(same_mark)))
    wrong += rng.sample([s for s in others if s not in wrong], 4 - len(wrong))
    labels = [(w, "check only the corner mark" if run(w)[0] == target[0] else "mix up L and R") for w in wrong]
    choices, ai = text_choices(right, labels, rng)
    name = rng.choice(NAMES)
    fig = column([legend(("R", "L", "S")), chain([paper(0, [])] + [machine("?")] * n + [paper(*target)])], gap=12)
    text = (_picture_text("RLS") + f"{name} uses the machines {n} times in a row and gets the picture at the end "
            f"of the bottom row. Which order works?")
    sol = (f"Check each order: follow the corner mark through every machine and turn the club only with the "
           f"machines after S. Only {right} gives the picture.")
    return Question(text=text, figure=fig, choices=choices, answer=ai, solution=sol,
                    check=lambda i: run(choices[i]) == target)


# ------------------------------------------------------------------ teaching page
def teach():
    seq = []
    pics = [paper(0, [])]
    for m in "RSR":
        seq.append(m)
        pics += [machine(m), paper(*run("".join(seq)))]
    return [
        ("h", "How to think about it: a turning machine and a printing machine"),
        "Machine R turns the sheet a quarter turn clockwise. Machine S prints an upright club. Two things on "
        "the sheet tell you what happened:",
        ("-", "<b>The corner mark</b> is there from the start. It turns with <b>every</b> R. So it tells you how "
              "many times R was used in total."),
        ("-", "<b>The club</b> is printed upright. It only turns with the R machines <b>after</b> S."),
        ("h", "The contest question"),
        "The mark went from bottom left to top right: 2 quarter turns, so R is used twice. The club lies on its "
        "side (stem to the left): 1 quarter turn, so one R comes after S. Order: R, S, R.",
        chain(pics),
        ("tip", "Work backwards: the club shows the turns after printing, the mark shows all the turns."),
        ("h", "Watch out"),
        ("-", "Four quarter turns bring the sheet back to where it started."),
        ("-", "If you only look at the club, you miss the turns before S. If you only look at the mark, you do "
              "not know where S goes."),
        ("tip", "<b>Try it:</b> draw a little square in a corner of a sticky note and turn it in your hand."),
    ]


# ------------------------------------------------------------------ warm-ups
@warmup
def w_where_mark(rng, harder):
    """Where is the mark after some quarter turns?"""
    k = rng.randint(1, 3)
    corners = ["bottom left", "top left", "top right", "bottom right"]
    text = (f"A square sheet has a black mark in the bottom left corner. You turn it {k} quarter "
            f"turn{'s' if k > 1 else ''} clockwise. Where is the mark now?")
    wrong = [(c, "turn the wrong way" if i == (-k) % 4 else "lose count of the turns")
             for i, c in enumerate(corners) if i != k % 4]
    wrong.append(("in the middle", "think the mark moves to the middle"))
    choices, ai = text_choices(corners[k % 4], wrong, rng)
    x, y = _rot((0.05, 0.05), k)
    where = ("bottom" if y < 0.5 else "top") + " " + ("left" if x < 0.5 else "right")
    return Question(text=text, figure=paper(0, [], size=44), choices=choices, answer=ai,
                    solution="Clockwise the mark goes: bottom left, top left, top right, bottom right.",
                    check=lambda i: choices[i] == where)


@warmup
def w_club_after(rng, harder):
    """How many quarter turns does the club make?"""
    while True:
        seq = "".join(rng.choice("RRS") for _ in range(4))
        if seq.count("S") == 1:
            break
    ans = run(seq)[1][0]
    after = seq[seq.index("S") + 1:].count("R")
    text = (_picture_text("RS") + f"The sheet goes through <b>{' '.join(seq)}</b>. How many quarter turns "
            f"does the club make?")
    choices, ai = numeric_choices(after, [(seq.count("R"), "count all the turns")], rng, lo=0, order="asc")
    return Question(text=text, figure=legend(), choices=choices, answer=ai,
                    solution=f"The club only turns with the R after S: {after}.",
                    check=value_check(choices, ans))
