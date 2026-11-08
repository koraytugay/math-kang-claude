"""2024 Q14 (Ecolier, Grade 3-4) - puzzle pieces with pegs and holes: how many chains can you build?

Original: Lucas has five puzzle pieces: a head (round hole on the right), an apple piece
(square peg left, square hole right), a cherry piece (round peg left, square hole right),
a grape piece (round peg left, round hole right) and a tail (square peg left). He wants to
lay a caterpillar of a head, a tail and 1, 2 or 3 parts in between. How many different
caterpillars can Lucas build?  A 3  B 4  C 5  D 6  E 7.
After the head: cherry or grape. After grape: cherry. After cherry: apple or tail.
After apple: tail. Caterpillars: H-cherry-T, H-cherry-apple-T, H-grape-cherry-T,
H-grape-cherry-apple-T.  Answer: B (4).

Core skill: counting systematically. Children try pieces at random and miss some chains or
count one twice. The method: first write down what can come right after each piece, then
build all chains from the start like a tree, one branch at a time, and only count the
branches that reach the end.
"""
from itertools import permutations

from reportlab.graphics.shapes import Rect
from reportlab.lib import colors

from kangaroo import Fig, Question, numeric_choices, value_check, variant, warmup

META = {
    "source": "set-01/by_level/Grade_03-04_Ecolier/2024 Q14",
    "skill": "Counting chains systematically: list what fits after what, then branch like a tree",
    "topics": ["counting", "logic"],
    "keywords": ["puzzle-piece chains", "counting with a tree"],
    "version": 1,
}

SHAPES = ["round", "square", "tri"]
SHAPE_WORD = {"round": "round", "square": "square", "tri": "triangle"}
GREEN = colors.Color(0.64, 0.82, 0.55)
BLUE = colors.Color(0.62, 0.76, 0.93)
NAMES = ["Lucas", "Mia", "Tom", "Anna", "Ben", "Sara", "Leo", "Emma"]

THEMES = {
    "caterpillar": dict(thing=("caterpillar", "caterpillars"), first="a head", last="a tail",
                        mid=("part", "parts"), First="the head", Last="the tail", fill=GREEN),
    "train": dict(thing=("train", "trains"), first="an engine", last="a last wagon",
                  mid=("wagon", "wagons"), First="the engine", Last="the last wagon", fill=BLUE),
}


# ------------------------------------------------------------------ counting
def fits(right, left):
    return right is not None and right == left


def chains(head_r, mids, tail_l, lengths, prefix=()):
    """All chains (tuples of middle-piece indices), built like a tree from the head."""
    out = []
    last_r = mids[prefix[-1]][1] if prefix else head_r
    if prefix and len(prefix) in lengths and fits(last_r, tail_l):
        out.append(prefix)
    if len(prefix) < max(lengths):
        for i, (l, r) in enumerate(mids):
            if i not in prefix and fits(last_r, l):
                out += chains(head_r, mids, tail_l, lengths, prefix + (i,))
    return out


def brute(head_r, mids, tail_l, lengths):
    """Answer check: try every ordering of every choice of middle pieces."""
    found = []
    for m in lengths:
        for perm in permutations(range(len(mids)), m):
            seq = [(None, head_r)] + [mids[i] for i in perm] + [(tail_l, None)]
            if all(seq[j][1] == seq[j + 1][0] for j in range(len(seq) - 1)):
                found.append(perm)
    return found


def with_repeats(head_r, mids, tail_l, lengths):
    """A mistake: using the same piece twice."""
    n = 0
    def go(r, depth):
        nonlocal n
        if depth in lengths and fits(r, tail_l):
            n += 1
        if depth < max(lengths):
            for l, rr in mids:
                if fits(r, l):
                    go(rr, depth + 1)
    go(head_r, 0)
    return n


# ------------------------------------------------------------------ pictures
def _shape(f, kind, x, y, s, fill):
    if kind == "round":
        f.circle(x, y, s * 0.5, fill=fill, width=0.8)
    elif kind == "square":
        f.rect(x - s * 0.45, y - s * 0.45, s * 0.9, s * 0.9, fill=fill, width=0.8)
    else:   # triangle pointing left
        f.poly([(x - s * 0.55, y), (x + s * 0.45, y + s * 0.52), (x + s * 0.45, y - s * 0.52)],
               fill=fill, width=0.8)


def _white(f, x0, y0, x1, y1):
    (a, b), (c, d) = f.p(x0, y0), f.p(x1, y1)
    f.d.add(Rect(a, b, c - a, d - b, fillColor=colors.white, strokeColor=None))


def piece(f, cx, kind, left, right, label="", theme="caterpillar"):
    """One piece centred at (cx, 1): body radius 1, peg on the left, hole on the right."""
    fill = THEMES[theme]["fill"]
    s = 0.6
    y = 1.0
    if left:   # peg, drawn first so the body covers its neck
        f.rect(cx - 1.25, y - 0.12, 0.4, 0.24, fill=fill, width=0.8)
        _shape(f, left, cx - 1.3, y, s, fill)
    if theme == "train":
        f.rect(cx - 1, 0.35, 2, 1.3, fill=fill, width=1.0)
        f.circle(cx - 0.55, 0.3, 0.22, fill=colors.black, width=0.5)
        f.circle(cx + 0.55, 0.3, 0.22, fill=colors.black, width=0.5)
        if kind == "head":
            f.rect(cx - 0.85, 1.65, 0.3, 0.4, fill=fill, width=0.9)         # chimney
            f.rect(cx - 0.45, 1.0, 0.5, 0.45, fill=colors.white, width=0.8)  # window
        if kind == "tail":
            f.line((cx + 0.6, 1.65), (cx + 0.6, 2.15), width=1.0)
            f.poly([(cx + 0.6, 2.15), (cx + 0.6, 1.9), (cx + 0.95, 2.02)], fill=colors.Color(0.9, 0.2, 0.2),
                   width=0.6)
    else:
        f.circle(cx, y, 1.0, fill=fill, width=1.0)
        if kind == "head":
            f.circle(cx - 0.25, y + 0.3, 0.1, fill=colors.black, width=0.5)
            f.arc(cx - 0.15, y - 0.05, 0.45, 215, 300, width=1.0)
        if kind == "tail":
            f.poly([(cx + 0.95, y + 0.3), (cx + 1.55, y), (cx + 0.95, y - 0.3)], fill=fill, width=1.0)
            _white(f, cx + 0.8, y - 0.27, cx + 0.97, y + 0.27)
    if right:  # hole: a white shape with an opening to the right edge
        hx = cx + 1 - 0.42
        _shape(f, right, hx, y, s, colors.white)
        _white(f, hx, y - 0.13, cx + 1.08, y + 0.13)
    if label:
        f.text(cx - (0.3 if right else 0), y, label, size=14)


def pieces_pic(head_r, mids, tail_l, theme, labels=None, scale=17, head=True, tail=True):
    """All pieces in a row: head, the numbered middle pieces, tail."""
    labels = labels or [str(i + 1) for i in range(len(mids))]
    items = ([("head", None, head_r, "")] if head else []) + \
            [("mid", l, r, lab) for (l, r), lab in zip(mids, labels)] + \
            ([("tail", tail_l, None, "")] if tail else [])
    step = 3.3
    f = Fig(step * len(items), 2.3, scale=scale, margin=3)
    for i, (kind, l, r, lab) in enumerate(items):
        piece(f, 1.6 + step * i, kind, l, r, lab, theme)
    return f.drawing()


def one_piece(l, r, label, theme, scale=12):
    f = Fig(3.0, 2.3, scale=scale, margin=2)
    piece(f, 1.6, "mid", l, r, label, theme)
    return f.drawing()


# ------------------------------------------------------------------ question text
def _intro(theme, name, k, lengths):
    t = THEMES[theme]
    ls = sorted(lengths)
    ln = ", ".join(str(x) for x in ls[:-1]) + f" or {ls[-1]}" if len(ls) > 1 else str(ls[0])
    return (f"{name} has these pieces: {t['first']}, {t['last']} and {k} {t['mid'][1]} with numbers. "
            f"A peg fits only into a hole of the <b>same shape</b>, and the pieces cannot be turned around. "
            f"A {t['thing'][0]} is {t['First']}, then {ln} {t['mid'][1]}, then {t['Last']}. "
            f"Each piece can be used only once. ")


def _random_set(rng, k, n_shapes):
    shapes = SHAPES[:n_shapes]
    mids = [(rng.choice(shapes), rng.choice(shapes)) for _ in range(k)]
    head_r, tail_l = rng.sample(shapes, 2)        # the head never fits the tail directly
    return head_r, mids, tail_l


def _solution_lines(head_r, mids, tail_l, lengths, theme):
    t = THEMES[theme]
    found = chains(head_r, mids, tail_l, lengths)
    names = lambda c: "–".join(["H"] + [str(i + 1) for i in c] + ["T"])
    return (f"Start at {t['First']} and try every piece that fits, one branch at a time "
            f"(H = {t['First'][4:]}, T = {t['Last'][4:]}): " + ", ".join(names(c) for c in found) +
            f". That is {len(found)}.")


# ------------------------------------------------------------------ variants
@variant(difficulty=1)
def count_all(rng, harder):
    """The original: how many chains can be built?"""
    theme = rng.choice(list(THEMES))
    k = 5 if harder else rng.choice([3, 4])
    lengths = list(range(1, k + 1)) if k <= 4 else [1, 2, 3, 4]
    lo, hi = (4, 9) if harder else (3, 7)
    while True:
        head_r, mids, tail_l = _random_set(rng, k, 2 if k == 3 else 3)
        ans = len(chains(head_r, mids, tail_l, lengths))
        if lo <= ans <= hi and len(set(mids)) == k:
            break
    name = rng.choice(NAMES)
    t = THEMES[theme]
    text = _intro(theme, name, k, lengths) + f"How many different {t['thing'][1]} can {name} build?"
    first = sum(1 for l, _ in mids if l == head_r)
    mistakes = [with_repeats(head_r, mids, tail_l, lengths), ans - 1, ans + 1, first, k, ans + 2]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1, order="asc")
    return Question(text=text, figure=pieces_pic(head_r, mids, tail_l, theme), choices=choices, answer=ai,
                    solution=_solution_lines(head_r, mids, tail_l, lengths, theme),
                    check=value_check(choices, len(brute(head_r, mids, tail_l, lengths))))


@variant(difficulty=2)
def exact_length(rng, harder):
    """Only chains with exactly m middle pieces."""
    theme = rng.choice(list(THEMES))
    k = 5 if harder else 4
    m = rng.choice([2, 3]) if not harder else rng.choice([3, 4])
    while True:
        head_r, mids, tail_l = _random_set(rng, k, 3)
        ans = len(chains(head_r, mids, tail_l, [m]))
        alls = len(chains(head_r, mids, tail_l, list(range(1, k + 1))))
        if 2 <= ans <= 6 and alls > ans and len(set(mids)) == k:
            break
    name = rng.choice(NAMES)
    t = THEMES[theme]
    text = (_intro(theme, name, k, list(range(1, k + 1))) +
            f"How many different {t['thing'][1]} with <b>exactly {m}</b> {t['mid'][1]} can {name} build?")
    mistakes = [alls, ans + 1, ans - 1, len(chains(head_r, mids, tail_l, [m - 1])),
                len(chains(head_r, mids, tail_l, [m + 1]))]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=0, order="asc")
    return Question(text=text, figure=pieces_pic(head_r, mids, tail_l, theme), choices=choices, answer=ai,
                    solution=_solution_lines(head_r, mids, tail_l, [m], theme),
                    check=value_check(choices, len(brute(head_r, mids, tail_l, [m]))))


@variant(difficulty=2)
def never_used(rng, harder):
    """Which piece can never be part of a chain?"""
    theme = rng.choice(list(THEMES))
    k = 5 if harder else 4
    lengths = list(range(1, k + 1))
    while True:
        head_r, mids, tail_l = _random_set(rng, k, 3)
        found = chains(head_r, mids, tail_l, lengths)
        used = {i for c in found for i in c}
        unused = [i for i in range(k) if i not in used]
        if len(found) >= 2 and len(unused) == 1 and len(set(mids)) == k:
            break
    bad = unused[0]
    name = rng.choice(NAMES)
    t = THEMES[theme]
    text = (_intro(theme, name, k, lengths) +
            f"Which {t['mid'][0]} can <b>never</b> be part of one of {name}'s {t['thing'][1]}?")
    choices = [f"{t['mid'][0]} {i + 1}" for i in range(k)]
    if k == 4:
        choices.append(f"each {t['mid'][0]} can be used")
    sol = (_solution_lines(head_r, mids, tail_l, lengths, theme) +
           f" {t['mid'][0].capitalize()} {bad + 1} is in none of them: it is a dead end, or nothing leads to it.")
    found_b = brute(head_r, mids, tail_l, lengths)
    used_b = {i for c in found_b for i in c}
    return Question(text=text, figure=pieces_pic(head_r, mids, tail_l, theme), choices=choices, answer=bad,
                    solution=sol,
                    check=lambda i: (i < k and i not in used_b) or (i == k and len(used_b) == k))


@variant(difficulty=3)
def extra_piece(rng, harder):
    """Reverse: which extra piece gives exactly N chains?"""
    theme = rng.choice(list(THEMES))
    k = 4 if harder else 3
    shapes = SHAPES
    name = rng.choice(NAMES)
    t = THEMES[theme]
    for _ in range(1000):
        head_r, mids, tail_l = _random_set(rng, k, 3)
        if len(set(mids)) < k:
            continue
        lengths = list(range(1, k + 2))
        base = len(chains(head_r, mids, tail_l, lengths))
        cands = [(l, r) for l in shapes for r in shapes if (l, r) not in mids]
        rng.shuffle(cands)
        cands = cands[:5]
        counts = [len(chains(head_r, mids + [c], tail_l, lengths)) for c in cands]
        uniq = [c for c in set(counts) if counts.count(c) == 1 and c > base and c >= 3]
        if uniq and base >= 1:
            target = max(uniq) if harder else rng.choice(uniq)
            break
    else:
        raise RuntimeError("no set found")
    ai = counts.index(target)
    text = (_intro(theme, name, k, lengths) +
            f"Now {name} can build {base} {t['thing'][1] if base != 1 else t['thing'][0]}. "
            f"{name} gets one more {t['mid'][0]} (number {k + 1}) and then can build exactly {target}. "
            f"Which {t['mid'][0]} did {name} get?")
    ch = chains(head_r, mids + [cands[ai]], tail_l, lengths)
    names = lambda c: "–".join(["H"] + [str(i + 1) for i in c] + ["T"])
    sol = (f"Try each new piece and count again with a tree. With {'ABCDE'[ai]}: "
           + ", ".join(names(c) for c in ch) + f", that is {target}.")
    lab = str(k + 1)
    return Question(text=text, figure=pieces_pic(head_r, mids, tail_l, theme),
                    choices=[f"{l}-{r}" for l, r in cands],
                    choice_figures=[one_piece(l, r, lab, theme, scale=15) for l, r in cands], answer=ai,
                    solution=sol,
                    check=lambda i: len(brute(head_r, mids + [cands[i]], tail_l, lengths)) == target)


@variant(difficulty=3)
def start_given(rng, harder):
    """Some pieces are already laid: how many ways to finish?"""
    theme = rng.choice(list(THEMES))
    k = 5 if harder else 4
    lengths = list(range(1, k + 1))
    while True:
        head_r, mids, tail_l = _random_set(rng, k, 3)
        found = chains(head_r, mids, tail_l, lengths)
        firsts = sorted({c[0] for c in found})
        if len(set(mids)) < k or not firsts:
            continue
        p = rng.choice(firsts)
        ans = sum(1 for c in found if c[0] == p)
        if 2 <= ans <= 6 and len(found) > ans:
            break
    name = rng.choice(NAMES)
    t = THEMES[theme]
    text = (_intro(theme, name, k, lengths) +
            f"{name} has already put {t['mid'][0]} {p + 1} right after {t['First']}. "
            f"In how many different ways can {name} finish the {t['thing'][0]}?")
    sol = ("Look only at the branch that starts with " + f"{t['mid'][0]} {p + 1}: " +
           ", ".join("–".join(["H"] + [str(i + 1) for i in c] + ["T"]) for c in found if c[0] == p) +
           f". That is {ans}.")
    value = sum(1 for c in brute(head_r, mids, tail_l, lengths) if c[0] == p)
    choices, ai = numeric_choices(ans, [len(found), ans + 1, ans - 1, k - 1], rng, lo=1, order="asc")
    return Question(text=text, figure=pieces_pic(head_r, mids, tail_l, theme), choices=choices, answer=ai,
                    solution=sol, check=value_check(choices, value))


# ------------------------------------------------------------------ teaching page
ORIG = dict(head_r="round", tail_l="square",
            mids=[("square", "square"), ("round", "square"), ("round", "round")],
            names=["apple", "cherry", "grape"])


def _tree_pic(head_r, mids, tail_l, names, lengths):
    """The counting tree: each branch is one way to go on; finished chains are numbered."""
    rows = []          # (depth, label, y) filled by layout
    edges = []
    count = [0]

    def build(prefix, last_r, depth):
        kids = []
        if prefix and len(prefix) in lengths and fits(last_r, tail_l):
            kids.append(("tail", None))
        if len(prefix) < max(lengths):
            for i, (l, r) in enumerate(mids):
                if i not in prefix and fits(last_r, l):
                    kids.append(("mid", i))
        return kids

    leaves = []

    def layout(prefix, last_r, depth, label):
        kids = build(prefix, last_r, depth)
        node = {"label": label, "depth": depth, "kids": []}
        if label == "tail":
            count[0] += 1
            node["n"] = count[0]
        if not kids and label != "tail":
            node["dead"] = True
        for kind, i in kids:
            if kind == "tail":
                child = {"label": "tail", "depth": depth + 1, "kids": []}
                count[0] += 1
                child["n"] = count[0]
                leaves.append(child)
            else:
                child = layout(prefix + (i,), mids[i][1], depth + 1, names[i])
            node["kids"].append(child)
        if not node["kids"]:
            if node not in leaves:
                leaves.append(node)
        return node

    root = layout((), head_r, 0, "head")

    def set_y(node):
        if not node["kids"]:
            node["y"] = -leaves.index(node)
        else:
            for c in node["kids"]:
                set_y(c)
            node["y"] = sum(c["y"] for c in node["kids"]) / len(node["kids"])
    set_y(root)
    depth = max(n["depth"] for n in leaves)
    W, gap = 1.9, 0.8
    f = Fig((depth + 1) * (W + gap) + 1.0, len(leaves) * 0.85 + 0.4, scale=30, margin=4, font_size=10.5)
    top = len(leaves) * 0.85

    def pos(node):
        return node["depth"] * (W + gap), top + node["y"] * 0.85 - 0.2

    def draw(node):
        x, y = pos(node)
        fill = colors.Color(0.85, 0.95, 0.82) if node["label"] == "tail" else colors.white
        f.rect(x, y - 0.3, W, 0.6, fill=fill, width=0.8)
        f.text(x + W / 2, y, node["label"], size=10.5)
        if "n" in node:
            f.text(x + W + 0.15, y, f"= caterpillar {node['n']}", anchor="start", size=10, italic=True)
        for c in node["kids"]:
            cx, cy = pos(c)
            f.line((x + W, y), (cx, cy), width=0.8)
            draw(c)
    draw(root)
    return f.drawing()


def teach():
    o = ORIG
    labels = ["A", "C", "G"]
    after = []
    for nm, (l, r) in [("head", (None, o["head_r"]))] + list(zip(o["names"], o["mids"])):
        nxt = [o["names"][j] for j, (l2, _) in enumerate(o["mids"]) if l2 == r and o["names"][j] != nm]
        if r == o["tail_l"]:
            nxt.append("tail")
        after.append([nm, f"{SHAPE_WORD[r]} hole", ", ".join(nxt)])
    return [
        ("h", "How to think about it: counting all the ways, without missing one"),
        "In these questions you build a chain (a caterpillar, a train, ...) from pieces that must fit together, "
        "and you have to find out <b>how many</b> different chains there are. If you just try pieces in any "
        "order, it is very easy to forget one or to count one twice.",
        ("tip", "<b>The big idea:</b> don't guess. First find out <b>what can come right after each piece</b>. "
                "Then build every chain from the start, <b>one branch at a time</b>, like a tree."),
        ("h", "Step by step: the contest question"),
        "Lucas has a head, a tail and three middle pieces: apple (A), cherry (C) and grape (G). "
        "A peg only fits into a hole of the same shape.",
        pieces_pic(o["head_r"], o["mids"], o["tail_l"], "caterpillar", labels=labels, scale=17),
        ("-", "<b>1. Make a list: what fits right after each piece?</b> Look at the hole on the right of the "
              "piece, then find all pegs of the same shape."),
        ("table", [["Piece", "Its hole", "What can come next"]] + after),
        ("-", "<b>2. Grow a tree from the head.</b> Write every piece that can come next as a new branch. "
              "Then do the same for each branch, until you reach the tail."),
        _tree_pic(o["head_r"], o["mids"], o["tail_l"], o["names"], [1, 2, 3]),
        ("-", "<b>3. Count the branches that end with the tail.</b> Here there are <b>4</b> caterpillars."),
        ("h", "Watch out"),
        ("-", "Every piece can be used <b>only once</b> in a chain. Cross out pieces you already used on a branch."),
        ("-", "A branch that gets stuck before the tail (nothing fits) is a <b>dead end</b>: don't count it."),
        ("-", "Count only <b>finished</b> chains, with the head at the start and the tail at the end."),
        ("tip", "<b>Try it yourself:</b> cut out paper pieces and draw a different peg on each side. Make a tree on "
                "paper first, then lay all the chains you found. Did the tree find every one?"),
    ]


# ------------------------------------------------------------------ warm-ups
@warmup
def w_fits_after(rng, harder):
    """Which piece can go right after the head?"""
    theme = rng.choice(list(THEMES))
    t = THEMES[theme]
    head_r = rng.choice(SHAPES)
    right = (head_r, rng.choice(SHAPES))
    others = [(l, r) for l in SHAPES for r in SHAPES if l != head_r]
    opts = rng.sample(others, 4) + [right]
    rng.shuffle(opts)
    ai = opts.index(right)
    f = Fig(3.3, 2.3, scale=17, margin=3)
    piece(f, 1.6, "head", None, head_r, "", theme)
    text = (f"A peg fits only into a hole of the <b>same shape</b>. Which piece can go right after "
            f"{t['First']}?")
    sol = (f"{t['First'].capitalize()} has a {SHAPE_WORD[head_r]} hole, so the next piece needs a "
           f"{SHAPE_WORD[head_r]} peg on its left: {'ABCDE'[ai]}.")
    return Question(text=text, figure=f.drawing(), choices=[f"{l}-{r}" for l, r in opts],
                    choice_figures=[one_piece(l, r, "", theme, scale=15) for l, r in opts], answer=ai,
                    solution=sol, check=lambda i: opts[i][0] == head_r)


@warmup
def w_how_many_next(rng, harder):
    """How many pieces can come right after piece p?"""
    theme = rng.choice(list(THEMES))
    t = THEMES[theme]
    while True:
        head_r, mids, tail_l = _random_set(rng, 4, 2)
        p = rng.randrange(4)
        r = mids[p][1]
        ans = sum(1 for j, (l, _) in enumerate(mids) if j != p and l == r) + (tail_l == r)
        if 1 <= ans <= 3 and len(set(mids)) == 4:
            break
    text = (f"A peg fits only into a hole of the same shape. How many of the other pieces (also "
            f"{t['Last']}) could go right after {t['mid'][0]} {p + 1}?")
    sol = (f"{t['mid'][0].capitalize()} {p + 1} has a {SHAPE_WORD[r]} hole. Count the pieces with a "
           f"{SHAPE_WORD[r]} peg: {ans}.")
    value = len([1 for (l, _) in [m for j, m in enumerate(mids) if j != p] + [(tail_l, None)] if fits(r, l)])
    choices, ai = numeric_choices(ans, [0, 1, 2, 3, 4], rng, lo=0, order="asc")
    return Question(text=text, figure=pieces_pic(head_r, mids, tail_l, theme), choices=choices, answer=ai,
                    solution=sol, check=value_check(choices, value))


@warmup
def w_small(rng, harder):
    """Only two middle pieces: list them all."""
    theme = rng.choice(list(THEMES))
    t = THEMES[theme]
    while True:
        head_r, mids, tail_l = _random_set(rng, 2, 2)
        ans = len(chains(head_r, mids, tail_l, [1, 2]))
        if ans >= 2 and len(set(mids)) == 2:
            break
    name = rng.choice(NAMES)
    text = _intro(theme, name, 2, [1, 2]) + f"How many different {t['thing'][1]} can {name} build?"
    choices, ai = numeric_choices(ans, [1, 2, 3, 4, 0], rng, lo=0, order="asc")
    return Question(text=text, figure=pieces_pic(head_r, mids, tail_l, theme), choices=choices, answer=ai,
                    solution=_solution_lines(head_r, mids, tail_l, [1, 2], theme),
                    check=value_check(choices, len(brute(head_r, mids, tail_l, [1, 2]))))


@warmup
def w_tree_branch(rng, harder):
    """Follow one branch of the tree: start fixed, how many ways to finish?"""
    theme = rng.choice(list(THEMES))
    t = THEMES[theme]
    while True:
        head_r, mids, tail_l = _random_set(rng, 3, 2)
        found = chains(head_r, mids, tail_l, [1, 2, 3])
        if len(set(mids)) < 3 or not found:
            continue
        p = rng.choice(sorted({c[0] for c in found}))
        ans = sum(1 for c in found if c[0] == p)
        if ans >= 2:
            break
    name = rng.choice(NAMES)
    text = (_intro(theme, name, 3, [1, 2, 3]) +
            f"{name} puts {t['mid'][0]} {p + 1} right after {t['First']}. How many ways are there to finish?")
    sol = (f"Follow only this branch: " +
           ", ".join("–".join(["H"] + [str(i + 1) for i in c] + ["T"]) for c in found if c[0] == p) + ".")
    value = sum(1 for c in brute(head_r, mids, tail_l, [1, 2, 3]) if c[0] == p)
    choices, ai = numeric_choices(ans, [1, 2, 3, 4, 5], rng, lo=1, order="asc")
    return Question(text=text, figure=pieces_pic(head_r, mids, tail_l, theme), choices=choices, answer=ai,
                    solution=sol, check=value_check(choices, value))
