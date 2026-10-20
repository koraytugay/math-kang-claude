"""2003 Q10 - a jump of 50 dm 50 cm 50 mm, plus 123 cm.

Original: Jumpy's longest training jump was 50 dm 50 cm and 50 mm. His winning
jump was 123 cm longer. How long was the winning jump?
A 6 m 78 cm  B 5 m 73 cm  C 5 m 55 cm  D 11 m 28 cm  E 7 m 23 cm.
50 dm = 5 m, 50 cm, 50 mm = 5 cm: 5 m 55 cm + 123 cm = 6 m 78 cm.  Answer: A.

Core skill: converting between m, dm, cm and mm before adding or comparing -
"50" means very different lengths depending on the unit. Children add the bare
numbers, or mix up how many of one unit make the next.
"""
from kangaroo import Question, numeric_choices, value_check, variant

META = {
    "source": "2003 Q10",
    "skill": "Lengths in m, dm, cm, mm: convert to one unit before adding or comparing",
    "topics": ["arithmetic", "measurement"],
    "version": 2,
}

MM = {"m": 1000, "dm": 100, "cm": 10, "mm": 1}
ANIMALS = ["Jumpy the kangaroo", "Hoppy the frog", "Skip the grasshopper", "Bounce the rabbit"]


def to_mm(s):
    """Answer checks: read a length like '6 m 78 cm' or '4 dm 5 cm and 20 mm' back into mm."""
    parts = s.replace(" and ", " ").split()
    return sum(int(parts[i]) * MM[parts[i + 1]] for i in range(0, len(parts), 2))


def m_cm(mm):
    """A whole number of cm (given in mm) written as 'x m y cm'."""
    m, c = divmod(mm // 10, 100)
    if m and c:
        return f"{m} m {c} cm"
    return f"{m} m" if m else f"{c} cm"


def _length_choices(correct_mm, wrong_mm, rng):
    """5 lengths (whole cm), shortest first; distractors from real mistakes, then near misses."""
    vals = [w for w in dict.fromkeys(wrong_mm) if w > 0 and w != correct_mm and w % 10 == 0]
    rng.shuffle(vals)
    vals = vals[:4]
    step = 100
    while len(vals) < 4:
        v = correct_mm + rng.choice([-1, 1]) * step * rng.randint(1, 9)
        if v > 0 and v != correct_mm and v not in vals:
            vals.append(v)
    vals = sorted(vals + [correct_mm])
    return [m_cm(v) for v in vals], vals.index(correct_mm)


@variant(difficulty=1)
def jump(rng, harder):
    """The original: a length in dm, cm and mm, plus some cm."""
    dm = rng.choice([30, 40, 50, 60] if harder else [20, 30, 40, 50])
    cm = rng.choice([20, 30, 40, 50, 60])
    mm = rng.choice([20, 30, 40, 50, 60, 70])
    add = rng.randint(105, 190) if harder else rng.randint(102, 150)
    who = rng.choice(ANIMALS)
    first = dm * 100 + cm * 10 + mm
    ans = first + add * 10
    text = (f"{who}'s longest jump in training was {dm} dm {cm} cm and {mm} mm long. "
            f"At the competition the jump was {add} cm longer.")
    after = "How long was the jump at the competition?"
    sol = (f"{dm} dm = {dm // 10} m and {mm} mm = {mm // 10} cm, so the training jump was {m_cm(first)}. "
           f"Adding {add} cm gives {m_cm(ans)}.")
    wrong = [(dm + cm + mm + add) * 10,     # added the bare numbers as if all were cm
             first,                         # forgot to add the extra
             ans + 9 * mm,                  # read the mm as cm
             ans - 90 * dm,                 # read the dm as cm
             first + add * 100,             # added the cm as if they were dm
             ans + 1000]
    choices, ai = _length_choices(ans, wrong, rng)
    target = to_mm(f"{dm} dm {cm} cm {mm} mm") + to_mm(f"{add} cm")
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol,
                    check=lambda i: to_mm(choices[i]) == target)


@variant(difficulty=1)
def longest(rng, harder):
    """Which length is the longest? All written in different units."""
    base = rng.randint(2, 9 if harder else 6) * 1000
    vals_mm = rng.sample(range(base - 600, base + 700, 100), 5)    # whole dm, all different
    units = rng.sample(["m cm", "dm", "cm", "mm", "dm cm"], 5)
    best = max(vals_mm)

    def show(v, u):
        if u == "m cm":
            return m_cm(v)
        if u == "dm cm":
            d, c = divmod(v // 10, 10)
            return f"{d} dm {c} cm" if c else f"{d} dm"
        return f"{v // MM[u]} {u}"

    labels = [show(v, u) for v, u in zip(vals_mm, units)]
    text = "Five ribbons have these lengths."
    after = "Which ribbon is the longest?"
    sol = ("In cm: " + ", ".join(f"{l} = {v // 10} cm" for l, v in zip(labels, vals_mm))
           + f". The longest is {labels[vals_mm.index(best)]}.")
    return Question(text=text, after_figure=after, choices=labels, answer=vals_mm.index(best),
                    solution=sol, check=lambda i: to_mm(labels[i]) == max(map(to_mm, labels)))


@variant(difficulty=2)
def how_much_longer(rng, harder):
    """Difference of two lengths given in different units, answer in cm."""
    a_dm = rng.randint(12, 40) if harder else rng.randint(10, 25)
    a_cm = rng.randint(1, 9)
    b_mm = (a_dm * 100 + a_cm * 10) - rng.randint(5, 60 if harder else 40) * 10
    diff = (a_dm * 100 + a_cm * 10 - b_mm) // 10
    name1, name2 = rng.sample(["Ana", "Ben", "Cleo", "Dan", "Eva", "Finn"], 2)
    text = (f"{name1}'s snake toy is {a_dm} dm {a_cm} cm long. {name2}'s snake toy is {b_mm} mm long.")
    after = f"How many centimetres longer is {name1}'s snake?"
    sol = (f"{a_dm} dm {a_cm} cm = {a_dm * 10 + a_cm} cm and {b_mm} mm = {b_mm // 10} cm. "
           f"{a_dm * 10 + a_cm} − {b_mm // 10} = {diff} cm.")
    mistakes = [diff * 10, abs(a_dm + a_cm - b_mm // 10), a_dm * 10 + a_cm - b_mm // 100,
                diff + 10, diff - 10, diff + a_cm]
    choices, ai = numeric_choices(diff, mistakes, rng, unit="cm", lo=1)
    gap = to_mm(f"{a_dm} dm {a_cm} cm") - to_mm(f"{b_mm} mm")
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol,
                    check=lambda i: to_mm(choices[i]) == gap)


@variant(difficulty=2)
def pieces(rng, harder):
    """A rope in metres cut into pieces given in cm (or dm)."""
    piece_cm = rng.choice([20, 25, 40, 50] if not harder else [15, 20, 25, 40])
    n = rng.randint(4, 12)
    total_cm = piece_cm * n
    while total_cm % 100:
        n += 1
        total_cm = piece_cm * n
    m = total_cm // 100
    in_dm = harder and piece_cm % 10 == 0 and rng.random() < 0.5
    piece = f"{piece_cm // 10} dm" if in_dm else f"{piece_cm} cm"
    name = rng.choice(["Ana", "Ben", "Cleo", "Dan", "Eva", "Finn"])
    text = f"{name} has a rope {m} m long and cuts it into pieces that are each {piece} long."
    after = "How many pieces does " + name + " get?"
    sol = (f"{m} m = {total_cm} cm" + (f" and {piece} = {piece_cm} cm" if in_dm else "")
           + f". {total_cm} ÷ {piece_cm} = {n}.")
    mistakes = [m * 10 // piece_cm if (m * 10) % piece_cm == 0 else -1, n * 10, n // 10 if n >= 20 else -1,
                n + 1, n - 1, total_cm // (piece_cm // 10) if in_dm else n * 2]
    choices, ai = numeric_choices(n, mistakes, rng, lo=1)
    whole, part = to_mm(f"{m} m"), to_mm(piece)
    assert whole % part == 0
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, whole // part))


@variant(difficulty=3)
def not_equal(rng, harder):
    """Which of these is NOT the same length? (Four are equal.)"""
    m = rng.randint(1, 4)
    c = rng.choice([5, 6, 7, 8, 9]) if harder else rng.choice([5, 20, 30, 40, 50])
    mm = m * 1000 + c * 10
    same = [f"{m * 100 + c} cm", f"{mm} mm", f"{m * 10 + c // 10} dm {c % 10} cm" if c % 10 else f"{m * 10 + c // 10} dm",
            f"{m} m {c * 10} mm", f"{m * 10} dm {c} cm"]
    same = list(dict.fromkeys(same))
    wrong_opts = [f"{m * 10 + c} cm", f"{m} m {c} mm", f"{m * 10 + c} dm", f"{m * 100 + c} mm",
                  f"{m * 100 + c * 10} cm"]
    # keep only wrong options that really are a different length
    def val(s):
        parts = s.split()
        return sum(int(parts[i]) * MM[parts[i + 1]] for i in range(0, len(parts), 2))
    wrong_opts = [w for w in wrong_opts if val(w) != mm]
    bad = rng.choice(wrong_opts)
    pick = rng.sample(same, 4)
    choices = pick + [bad]
    rng.shuffle(choices)
    assert all(val(s) == mm for s in pick) and val(bad) != mm
    name = rng.choice(["Ana", "Ben", "Cleo", "Dan", "Eva", "Finn"])
    text = f"{name}'s new rug is {m_cm(mm)} long. Four of these lengths are the same as that."
    after = "Which one is <b>not</b> the same?"
    sol = (f"{m_cm(mm)} = {mm // 10} cm = {mm} mm. But {bad} = "
           + (f"{val(bad) // 10} cm" if val(bad) % 10 == 0 else f"{val(bad)} mm") + ".")
    return Question(text=text, after_figure=after, choices=choices, answer=choices.index(bad), solution=sol,
                    check=lambda i: to_mm(choices[i]) != to_mm(m_cm(mm)))
