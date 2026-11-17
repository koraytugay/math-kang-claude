"""2022 Q20 (Ecolier, Grade 3-4) - road tiles: which hexagon joins the right houses?

Original: A road leads away from each of the six houses A-F (around a hexagon). A hexagon
showing the roads in the middle is missing. Five hexagon tiles 1-5 are shown.
Which hexagons fit in the middle so that one can travel from A to B and to E, but not to D?
(A) 1 and 2  (B) 1 and 4  (C) 1 and 5  (D) 2 and 3  (E) 4 and 5      Answer (key): C.

Core skill: reading which roads meet inside a tile (roads that meet are joined, a road that
stops at the edge goes nowhere) and checking every condition for every tile - the "but not
to D" one too. Children check A-B, find a tile that works and stop, or forget the "not".
The method: for each tile, follow the road from A and list all the houses you can reach,
then compare the list with every condition.

Our tiles are drawn the same way round as the board (they are never turned), roads that meet
have one meeting point, and roads never cross without meeting.
"""
import math
import re

from reportlab.graphics.shapes import Drawing, Group, Line, Polygon, String
from reportlab.lib import colors

from kangaroo import Fig, Question, numeric_choices, text_choices, variant
from kangaroo.choices import Choices
from kangaroo.figures import row

META = {
    "source": "set-01/by_level/Grade_03-04_Ecolier/2022 Q20",
    "skill": "Road tiles: from the start house, follow the roads that meet and list every house you reach, then check each rule (the \"not\" one too)",
    "topics": ["logic", "spatial"],
    "keywords": ["road tiles", "which roads meet", "travel from to"],
    "sticker": ("🛣️", "Road tiler"),   # earned when this skill is solid (website)
    "version": 1,
}

ROAD = colors.Color(0.78, 0.78, 0.78)
HOUSES = "AFEDCB"      # side k (direction 60*k degrees, k=0 is right) leads to this house
SIDE = {h: k for k, h in enumerate(HOUSES)}
APO = 1.0              # apothem of the hexagon
R = APO * 2 / math.sqrt(3)
NAMES = ["Ali", "Mia", "Tom", "Lena", "Sam", "Nora", "Ben", "Ida"]


# ------------------------------------------------------------------ tiles
def crossing(g, h):
    return any(a < c < b < d or c < a < d < b for a in g for b in g for c in h for d in h)


def _partitions(items):
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for part in _partitions(rest):
        yield [[first]] + part
        for i in range(len(part)):
            yield part[:i] + [[first] + part[i]] + part[i + 1:]


def _all_tiles(min_roads):
    """Every tile: groups of sides whose roads meet in one point (a side alone has no road),
    roads never cross without meeting."""
    out = set()
    for part in _partitions(list(range(6))):
        groups = [sorted(g) for g in part if len(g) >= 2]
        if not groups or any(crossing(g, h) for g in groups for h in groups if g is not h):
            continue
        tile = tuple(sorted(tuple(g) for g in groups))
        if sum(len(g) for g in groups) >= min_roads and apart(tile):
            out.add(tile)
    return sorted(out)


def _seg_dist(p, q, r, s):
    """Shortest distance between segments p-q and r-s (sampled, plenty for a picture check)."""
    def at(a, b, t):
        return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
    n = 40
    return min(math.dist(at(p, q, i / n), at(r, s, k / n)) for i in range(n + 1) for k in range(n + 1))


def apart(tile, gap=0.42):
    """Roads of different groups stay well apart in the picture (so they never seem to meet)."""
    segs = [(g, mid(k), j) for g, (k, j) in ((g, kj) for g in tile for kj in segments((g,)))]
    return all(_seg_dist(a1, b1, a2, b2) >= gap
               for i, (g1, a1, b1) in enumerate(segs) for g2, a2, b2 in segs[i + 1:] if g1 != g2)


_TILES = {}


def all_tiles(harder):
    if harder not in _TILES:
        _TILES[harder] = _all_tiles(5 if harder else 4)
    return _TILES[harder]


def random_tile(rng, harder):
    return rng.choice(all_tiles(harder))


def mid(k, r=APO):
    a = math.radians(60 * k)
    return r * math.cos(a), r * math.sin(a)


def segments(tile):
    """The drawn roads: (side midpoint, meeting point) for every road of every group."""
    out = []
    for g in tile:
        pts = [mid(k) for k in g]
        pull = 0.5        # meeting point: towards the centre, away from the corners
        j = (round(pull * sum(p[0] for p in pts) / len(pts), 6), round(pull * sum(p[1] for p in pts) / len(pts), 6))
        out += [(k, j) for k in g]
    return out


def reach(tile, house):
    """Answer check: walk the drawn roads (side -> meeting point -> sides) and list the houses."""
    segs = segments(tile)
    start = SIDE[house]
    seen, todo = {start}, [start]
    while todo:
        s = todo.pop()
        for k, j in segs:
            if k == s:
                for k2, j2 in segs:
                    if j2 == j and k2 not in seen:
                        seen.add(k2)
                        todo.append(k2)
    return {HOUSES[k] for k in seen} - {house}


def joined(tile, a, b):
    return any(SIDE[a] in g and SIDE[b] in g for g in tile)


def fits(tile, rules):
    return all(joined(tile, a, b) == want for a, b, want in rules)


def broken(tile, rules):
    return [(a, b, want) for a, b, want in rules if joined(tile, a, b) != want]


# ------------------------------------------------------------------ pictures
def _hex(f, cx, cy, fill=colors.white):
    f.poly([(cx + R * math.cos(math.radians(30 + 60 * i)), cy + R * math.sin(math.radians(30 + 60 * i)))
            for i in range(6)], fill=fill, width=1.0)


def _road(f, a, b, w=0.24):
    (x1, y1), (x2, y2) = f.p(*a), f.p(*b)
    base = Line(x1, y1, x2, y2, strokeColor=ROAD, strokeWidth=w * f.scale)
    base.strokeLineCap = 1
    f.d.add(base)
    centre = Line(x1, y1, x2, y2, strokeColor=colors.white, strokeWidth=0.8)
    centre.strokeDashArray = [2.5, 2]
    f.d.add(centre)


def _tile_roads(f, tile, cx=0.0, cy=0.0):
    segs = segments(tile)
    for k, j in segs:
        m = mid(k)
        _road(f, (cx + m[0], cy + m[1]), (cx + j[0], cy + j[1]))
    for k, j in segs:            # draw the centre lines again on top, so meeting points look joined
        m = mid(k)
        (x1, y1), (x2, y2) = f.p(cx + m[0], cy + m[1]), f.p(cx + j[0], cy + j[1])
        ln = Line(x1, y1, x2, y2, strokeColor=colors.white, strokeWidth=0.8)
        ln.strokeDashArray = [2.5, 2]
        f.d.add(ln)


def tile_picture(tile, label="", max_px=62):
    f = Fig(2 * R, 2 * R, max_px=max_px, margin=10)
    _hex(f, R, R)
    _tile_roads(f, tile, R, R)
    _hex(f, R, R, fill=None)
    if label:
        f.text(0.05, 2 * R - 0.05, label, size=11)
    return f.drawing()


def board(tile=None, max_px=165):
    """The six houses around the middle hexagon (empty, or with `tile` in it)."""
    span = 2.6
    f = Fig(2 * span, 2 * span, max_px=max_px, margin=6)
    c = (span, span)
    for k, h in enumerate(HOUSES):
        m = mid(k)
        far = mid(k, 2.05)
        _road(f, (c[0] + m[0], c[1] + m[1]), (c[0] + far[0], c[1] + far[1]))
    _hex(f, *c)
    if tile:
        _tile_roads(f, tile, *c)
    _hex(f, *c, fill=None)
    for k, h in enumerate(HOUSES):
        x, y = mid(k, 2.2)
        x, y = c[0] + x, c[1] + y
        s = 0.42
        f.rect(x - s / 2, y - s / 2, s, s, fill=colors.white, width=1.0)
        f.poly([(x - s / 2 - 0.05, y + s / 2), (x + s / 2 + 0.05, y + s / 2), (x, y + s / 2 + 0.25)],
               fill=colors.white, width=1.0)
        f.text(x, y - 0.02, h, size=12)
    return f.drawing()


def numbered(tiles):
    pics = [tile_picture(t, str(i + 1)) for i, t in enumerate(tiles)]
    return pics


def board_and_tiles(tiles):
    pics = numbered(tiles)
    top, bottom = row(pics[:3], gap=8), row(pics[3:], gap=8)
    w = max(top.width, bottom.width)
    right = Drawing(w, top.height + bottom.height + 6)
    g = Group(*bottom.contents)
    g.translate((w - bottom.width) / 2, 0)
    right.add(g)
    g = Group(*top.contents)
    g.translate(0, bottom.height + 6)
    right.add(g)
    return row([board(max_px=130), right], gap=20)


# ------------------------------------------------------------------ words
def rules_text(rules):
    start = rules[0][0]
    yes = [b for a, b, w in rules if w]
    no = [b for a, b, w in rules if not w]
    s = f"one can travel from {start} to " + " and to ".join(yes)
    if no:
        s += ", but <b>not</b> to " + " or ".join(no)
    return s


def make_rules(rng, harder, n_yes=None):
    start = rng.choice(HOUSES)
    others = [h for h in HOUSES if h != start]
    rng.shuffle(others)
    n_yes = n_yes or (2 if harder else rng.choice([1, 2]))
    yes, no = others[:n_yes], others[n_yes:n_yes + (2 if harder and n_yes == 1 else 1)]
    return [(start, b, True) for b in yes] + [(start, b, False) for b in no]


def failure(rules, tile):
    a, b, want = broken(tile, rules)[0]
    if not want:
        return f"forget the \"not\": this hexagon joins {a} to {b} too"
    return f"check only some of the houses: this hexagon does not join {a} to {b}"


def pick_tiles(rng, harder, n_yes, n_good, n=5):
    """Rules and n distinct tiles: exactly n_good of them fit, the others miss just one rule
    (near misses), at least one breaks the "not" rule and one misses a "yes" rule."""
    for _ in range(500):
        rules = make_rules(rng, harder, n_yes)
        good = [t for t in all_tiles(harder) if fits(t, rules)]
        near = [t for t in all_tiles(harder) if len(broken(t, rules)) == 1]
        no_kind = [t for t in near if not broken(t, rules)[0][2]]
        yes_kind = [t for t in near if broken(t, rules)[0][2]]
        if len(good) < n_good or not no_kind or not yes_kind or len(near) < n - n_good:
            continue
        bad = [rng.choice(no_kind), rng.choice(yes_kind)]
        bad += rng.sample([t for t in near if t not in bad], n - n_good - 2)
        tiles = rng.sample(good, n_good) + bad
        rng.shuffle(tiles)
        return rules, tiles
    raise RuntimeError("no tiles")


def check_rules(tile, rules):
    """Independent: from the start house, walk the drawn roads; compare with the rules."""
    start = rules[0][0]
    got = reach(tile, start)
    return all((b in got) == want for _, b, want in rules)


# ------------------------------------------------------------------ variants
@variant(difficulty=1)
def visit(rng, harder):
    """One tile is in place: which house can you reach (or not reach) from a house?"""
    cannot = rng.random() < 0.5
    while True:
        tile = random_tile(rng, harder)
        start = rng.choice(HOUSES)
        r = reach(tile, start)
        if (cannot and len(r) == 4) or (not cannot and len(r) == 1):
            break
    who = rng.choice(NAMES)
    others = [h for h in HOUSES if h != start]
    if cannot:
        right = next(h for h in others if h not in r)
        text = (f"{who} lives in house {start}. The roads in the middle are shown.\n\n"
                f"To which house can {who} <b>not</b> travel?")
        wrong = [(h, "forget the \"not\": you can travel to this house") for h in others if h != right]
        sol = (f"From {start} the roads lead to {', '.join(sorted(r))}. "
               f"Only house {right} is not joined to {start}.")
    else:
        right = next(iter(r))
        text = (f"{who} lives in house {start}. The roads in the middle are shown.\n\n"
                f"To which house can {who} travel?")
        wrong = [(h, "follow a road that does not meet the road from " + start) for h in others if h != right]
        sol = f"The road from {start} meets only the road to {right}."
    ch, ans = text_choices(right, wrong, rng)
    check = (lambda i: (ch[i] not in reach(tile, start))) if cannot else (lambda i: ch[i] in reach(tile, start))
    return Question(text=text, figure=board(tile), choices=ch, answer=ans, solution=sol,
                    difficulty=1, check=check)


@variant(difficulty=1)
def which_tile(rng, harder):
    """Pick the one tile that does all the rules."""
    rules, tiles = pick_tiles(rng, harder, 2 if harder else 1, 1)
    good = next(i for i, t in enumerate(tiles) if fits(t, rules))
    text = (f"A road leads away from each of the six houses. The hexagon in the middle is missing."
            f"\n\nWhich hexagon fits in the middle so that {rules_text(rules)}?")
    mistakes = {i: failure(rules, t) for i, t in enumerate(tiles) if i != good}
    ch = Choices([f"hexagon {i + 1}" for i in range(5)], mistakes)
    start = rules[0][0]
    sol = (f"Follow the road from {start} in each hexagon. Hexagon {good + 1} joins {start} to "
           f"{', '.join(sorted(reach(tiles[good], start)))} - just what is wanted. "
           + " ".join(f"Hexagon {i + 1}: {'joins' if not w else 'does not join'} {a} and {b}."
                      for i, t in enumerate(tiles) if i != good for a, b, w in broken(t, rules)[:1]))
    return Question(text=text, figure=board(max_px=130), choices=ch, answer=good,
                    choice_figures=[tile_picture(t) for t in tiles], solution=sol, difficulty=1,
                    check=lambda i: check_rules(tiles[i], rules))


@variant(difficulty=2)
def two_tiles(rng, harder):
    """The original: two of the five tiles fit; the options are pairs."""
    rules, tiles = pick_tiles(rng, harder, 2, 2)
    good = [i for i, t in enumerate(tiles) if fits(t, rules)]
    bad = [i for i in range(5) if i not in good]
    pairs = [tuple(good)]
    near = [tuple(sorted((g, b))) for g in good for b in bad]
    rng.shuffle(near)
    pairs += near[:3]
    rest = [(a, b) for a in bad for b in bad if a < b]
    pairs.append(rng.choice(rest))
    pairs.sort()
    labels = {}
    for i, (a, b) in enumerate(pairs):
        if (a, b) != tuple(good):
            wrong = b if a in good else a
            labels[i] = failure(rules, tiles[wrong]).replace("this hexagon", f"hexagon {wrong + 1}")
    ch = Choices([f"{a + 1} and {b + 1}" for a, b in pairs], labels)
    ans = pairs.index(tuple(good))
    start = rules[0][0]
    text = (f"A road leads away from each of the six houses. The hexagon in the middle is missing."
            f"\n\nWhich hexagons fit in the middle so that {rules_text(rules)}?")
    sol = (f"From {start}: " + "; ".join(
        f"hexagon {i + 1} reaches {', '.join(sorted(reach(t, start))) or 'no house'}" for i, t in enumerate(tiles))
        + f". Only {good[0] + 1} and {good[1] + 1} do every rule.")

    def check(i):
        a, b = (int(x) - 1 for x in ch[i].split(" and "))
        return check_rules(tiles[a], rules) and check_rules(tiles[b], rules)
    return Question(text=text, figure=board_and_tiles(tiles), choices=ch, answer=ans, solution=sol,
                    difficulty=2, check=check)


@variant(difficulty=3)
def how_many_fit(rng, harder):
    """Count the tiles that fit - every tile must be checked, there is no stopping early."""
    n_good = rng.choice([0, 1, 2, 3])
    rules, tiles = pick_tiles(rng, harder, 2 if harder else rng.choice([1, 2]), n_good)
    no_not = [r for r in rules if r[2]]
    loose = sum(fits(t, no_not) for t in tiles)
    first = [(rules[0][0], rules[0][1], True)]
    only_first = sum(fits(t, first) for t in tiles)
    text = (f"A road leads away from each of the six houses. The hexagon in the middle is missing."
            f"\n\nHow many of the hexagons 1 to 5 fit in the middle so that {rules_text(rules)}?")
    mistakes = [(loose, "forget the \"not\" rule"),
                (only_first, f"check only the way from {rules[0][0]} to {rules[0][1]}"),
                (5, "count all the hexagons")]
    ch, ans = numeric_choices(n_good, mistakes, rng, lo=0)
    start = rules[0][0]
    fit_list = [str(i + 1) for i, t in enumerate(tiles) if fits(t, rules)]
    sol = (f"From {start}: " + "; ".join(f"hexagon {i + 1} reaches {', '.join(sorted(reach(t, start))) or 'no house'}"
                     for i, t in enumerate(tiles))
           + f". Fitting: {', '.join(fit_list) if fit_list else 'none'} - that is {n_good}.")
    count = sum(check_rules(t, rules) for t in tiles)
    return Question(text=text, figure=board_and_tiles(tiles), choices=ch, answer=ans, solution=sol,
                    difficulty=3, check=lambda i: int(ch[i]) == count)


@variant(difficulty=3)
def true_sentence(rng, harder):
    """One tile in place, five sentences with "can" and "cannot": only one is true."""
    while True:          # enough pairs that are joined and that are not
        tile = random_tile(rng, True)
        n_joined = sum(len(g) * (len(g) - 1) // 2 for g in tile)
        if 3 <= n_joined <= 9:
            break
    pairs = [(a, b) for i, a in enumerate(HOUSES) for b in HOUSES[i + 1:]]
    rng.shuffle(pairs)
    trues, falses = [], []
    for a, b in pairs:
        can = joined(tile, a, b)
        for say in (True, False):
            sentence = f"You can{'' if say else '<b>not</b>'} travel from {a} to {b}."
            (trues if say == can else falses).append((sentence, say, a, b))
    rng.shuffle(trues)
    rng.shuffle(falses)
    if not harder:          # easier: all sentences say "can"
        trues = [t for t in trues if t[1]]
        falses = [f for f in falses if f[1]]
    say_can = (not harder) or rng.random() < 0.5
    right = next((t for t in trues if t[1] == say_can), trues[0])
    falses = [f for f in falses if {f[2], f[3]} != {right[2], right[3]}]
    # harder: 2 or 3 of the five sentences say "cannot", so the odd one out is no hint
    n_not = rng.choice([2, 3]) - (0 if right[1] else 1) if harder else 0
    falses = [f for f in falses if not f[1]][:n_not] + [f for f in falses if f[1]]
    wrong = []
    for s, say, a, b in falses:
        if s in [w[0] for w in wrong]:
            continue
        if say:
            wrong.append((s, f"think the roads from {a} and {b} meet when they do not"))
        else:
            wrong.append((s, f"miss that the roads from {a} and {b} meet"))
        if len(wrong) == 4:
            break
    ch, ans = text_choices(right[0], wrong, rng)
    text = "The roads in the middle are shown.\n\nWhich sentence is true?"
    groups = ["-".join(HOUSES[k] for k in sorted(g, key=lambda k: HOUSES[k])) for g in tile]
    sol = (f"The roads that meet join these houses: {'; '.join(groups)}. "
           f"So “{right[0].replace('<b>', '').replace('</b>', '')}” is the true sentence.")

    def check(i):
        a, b = re.findall(r"from (\w) to (\w)", ch[i])[0]
        says_can = "not" not in ch[i]
        return (b in reach(tile, a)) == says_can
    return Question(text=text, figure=board(tile), choices=ch, answer=ans, solution=sol,
                    difficulty=3, check=check)
