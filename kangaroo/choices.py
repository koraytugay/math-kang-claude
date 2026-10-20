"""Helpers for building the 5 answer options."""
from __future__ import annotations

import random


def numeric_choices(correct: int, mistakes: list[int], rng: random.Random,
                    unit: str = "", lo: int = 0, order: str = "random") -> tuple[list[str], int]:
    """Build 5 numeric options: the correct value plus 4 wrong ones.

    `mistakes` are values a child would get from a plausible error (forgot to
    double, used the wrong side, ...). They are preferred; nearby values fill
    any gaps. Options are listed ascending or descending like the real contest,
    and the correct answer's position (A..E) is chosen uniformly at random so
    the answer key is not biased toward the middle letters.
    """
    mistakes = list(dict.fromkeys(m for m in mistakes
                                  if isinstance(m, int) and m != correct and m >= lo))
    rng.shuffle(mistakes)
    below_avail = correct - lo                # how many distinct integers fit below
    pos = rng.randint(0, 4)                   # number of options smaller than the answer
    pos = min(pos, below_avail)
    below = [m for m in mistakes if m < correct][:pos]
    above = [m for m in mistakes if m > correct][:4 - pos]
    spread = max(2, abs(correct) // 4)
    tries = 0
    while len(below) < pos:
        tries += 1
        m = correct - rng.randint(1, min(below_avail, spread + tries // 5))
        if m not in below:
            below.append(m)
    tries = 0
    while len(above) < 4 - pos:
        tries += 1
        m = correct + rng.randint(1, spread + tries // 5)
        if m not in above:
            above.append(m)
    values = below + above + [correct]
    if order == "random":
        order = rng.choice(["asc", "desc"])
    values.sort(reverse=(order == "desc"))
    labels = [f"{v}{(' ' + unit) if unit else ''}" for v in values]
    return labels, values.index(correct)


def text_choices(correct: str, wrong: list[str], rng: random.Random) -> tuple[list[str], int]:
    """5 text options in random order (correct + 4 distinct wrong)."""
    wrong = [w for w in dict.fromkeys(wrong) if w != correct]
    if len(wrong) < 4:
        raise ValueError("need at least 4 distinct wrong options")
    opts = rng.sample(wrong, 4) + [correct]
    rng.shuffle(opts)
    return opts, opts.index(correct)
