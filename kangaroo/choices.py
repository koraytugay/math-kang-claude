"""Helpers for building the 5 answer options."""
from __future__ import annotations

import random
import re


class Choices(list):
    """The 5 option labels (a normal list), plus `mistakes`: {option index: what the child did to get it}.

    A mistake text is a short verb phrase written to the child, in the base form, so it fits both
    "Did you ...?" and "This is what you get if you ...", e.g. "count only the cubes you can see".
    The registry copies it into Question.meta["mistakes"]; the practice website shows it.
    """
    mistakes: dict

    def __init__(self, items, mistakes=None):
        super().__init__(items)
        self.mistakes = mistakes or {}


def _split(items):
    """Mistakes may be plain values or (value, "what you did") pairs: -> values, {value: text}."""
    values, texts = [], {}
    for m in items:
        if isinstance(m, tuple) and len(m) == 2 and isinstance(m[1], str):
            values.append(m[0])
            texts.setdefault(m[0], m[1])
        else:
            values.append(m)
    return values, texts


def numeric_choices(correct: int, mistakes: list[int], rng: random.Random,
                    unit="", lo: int = 0, order: str = "random", step: int = 1) -> tuple[list[str], int]:
    """Build 5 numeric options: the correct value plus 4 wrong ones.

    `mistakes` are values a child would get from a plausible error (forgot to
    double, used the wrong side, ...), optionally as (value, "what you did") pairs, e.g.
    (front, "count only the cubes you can see"). They are preferred; nearby values fill
    any gaps (multiples of `step` away from the answer, so "round" answers get
    round distractors). `unit` is a string ("cm") or a (singular, plural) pair
    ("orange", "oranges"). Options are listed ascending or descending like the real contest,
    and the correct answer's position (A..E) is chosen uniformly at random so
    the answer key is not biased toward the middle letters.
    """
    mistakes, texts = _split(mistakes)
    mistakes = list(dict.fromkeys(m for m in mistakes
                                  if isinstance(m, int) and m != correct and m >= lo))
    rng.shuffle(mistakes)
    below_avail = correct - lo                # how many distinct integers fit below
    pos = rng.randint(0, 4)                   # number of options smaller than the answer
    pos = min(pos, below_avail)
    below = [m for m in mistakes if m < correct][:pos]
    above = [m for m in mistakes if m > correct][:4 - pos]
    spread = max(2, abs(correct) // (4 * step))
    tries = 0
    def st(t):  # fall back to finer steps if the round ones run out
        return step if t < 30 else (5 if step % 5 == 0 and t < 60 else 1)
    while len(below) < pos:
        tries += 1
        s = st(tries)
        m = correct - s * rng.randint(1, max(1, min((correct - lo) // s, spread + tries // 5)))
        if m < lo:
            m = correct - rng.randint(1, below_avail)
        if m not in below:
            below.append(m)
    tries = 0
    while len(above) < 4 - pos:
        tries += 1
        m = correct + st(tries) * rng.randint(1, spread + tries // 5)
        if m not in above:
            above.append(m)
    values = below + above + [correct]
    if order == "random":
        order = rng.choice(["asc", "desc"])
    values.sort(reverse=(order == "desc"))
    def label(v):
        if isinstance(unit, tuple):
            return f"{v} {unit[0] if v == 1 else unit[1]}"
        return f"{v}{(' ' + unit) if unit else ''}"
    labels = Choices([label(v) for v in values],
                     {i: texts[v] for i, v in enumerate(values) if v != correct and v in texts})
    return labels, values.index(correct)


def text_choices(correct: str, wrong: list[str], rng: random.Random) -> tuple[list[str], int]:
    """5 text options in random order (correct + 4 distinct wrong; wrong ones may be (text, "what you did"))."""
    wrong, texts = _split(wrong)
    wrong = [w for w in dict.fromkeys(wrong) if w != correct]
    if len(wrong) < 4:
        raise ValueError("need at least 4 distinct wrong options")
    opts = rng.sample(wrong, 4) + [correct]
    rng.shuffle(opts)
    return Choices(opts, {i: texts[o] for i, o in enumerate(opts) if o in texts}), opts.index(correct)


def number_in(label: str) -> int:
    """The (first) whole number written in an option label, e.g. "18 cubes" -> 18."""
    m = re.search(r"-?\d+", label)
    if not m:
        raise ValueError(f"no number in option {label!r}")
    return int(m.group())


def value_check(choices: list[str], value: int):
    """A Question.check for numeric options: option i is correct iff it shows `value`.

    Pass a value worked out independently (brute force, counting, simulation), not the
    same expression the generator used to build the options.
    """
    return lambda i: number_in(choices[i]) == value
