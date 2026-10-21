"""2007 Q3 - how many letters do KANGAROO and PROBLEM have in common?

Original: How many common letters do the words KANGAROO and PROBLEM have?
A 1  B 2  C 3  D 4  E 5.  Common letters: R and O.  Answer: B.

Core skill: comparing two collections carefully - check each different letter
once (KANGAROO has two O's and two A's, but O counts once), and do not stop
after the first match. Children count repeated letters twice or miss a letter.
"""
from kangaroo import Question, numeric_choices, text_choices, value_check, variant

META = {
    "source": "2007 Q3",
    "skill": "Comparing sets of letters: each different letter counts once; check them all",
    "topics": ["logic", "counting"],
    "version": 4,
}

WORDS = ["KANGAROO", "PROBLEM", "MATHEMATICS", "ELEPHANT", "GIRAFFE", "BANANA", "TEACHER",
         "SCHOOL", "PENCIL", "RAINBOW", "DINOSAUR", "CHOCOLATE", "BUTTERFLY", "PUZZLE",
         "TRIANGLE", "NUMBER", "SQUARE", "CASTLE", "DRAGON", "ROCKET", "PIRATE", "COMPUTER",
         "WINDOW", "GARDEN", "SANDWICH", "MONKEY", "TURTLE", "PLANET", "SPIDER", "LEMONADE"]


def tally(test):
    """Answer checks: go through the alphabet A to Z and count the letters that pass the test."""
    return sum(1 for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if test(ch))


def common(a, b):
    return sorted(set(a) & set(b))


def repeats_counted(a, b):
    """The mistake: count every letter of a that also appears in b, repeats included."""
    return sum(1 for ch in a if ch in b)


def _pair(rng, lo, hi, need_only=False):
    """Two words with lo..hi common letters (where counting repeats would give a different answer)."""
    for _ in range(500):
        a, b = rng.sample(WORDS, 2)
        c = common(a, b)
        if need_only and not set(a) - set(b):
            continue
        if lo <= len(c) <= hi and repeats_counted(a, b) != len(c):
            return a, b
    raise RuntimeError("no word pair found")


def _letters(xs):
    return ", ".join(xs[:-1]) + " and " + xs[-1] if len(xs) > 1 else xs[0]


@variant(difficulty=1)
def common_letters(rng, harder):
    """The original."""
    a, b = _pair(rng, 2, 5 if harder else 3)
    c = common(a, b)
    ans = len(c)
    text = f"How many letters do the words {a} and {b} have in common?"
    sol = (f"Check each different letter of {a}: only {_letters(c)} are also in {b}, so {ans}. "
           f"A letter that appears twice still counts once.")
    mistakes = [repeats_counted(a, b), repeats_counted(b, a), ans + 1, ans - 1]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=0)
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, tally(lambda ch: ch in a and ch in b)))


@variant(difficulty=1)
def different_letters(rng, harder):
    """How many different letters are used in a word?"""
    for _ in range(200):
        w = rng.choice(WORDS)
        if len(set(w)) < len(w):
            break
    ans = len(set(w))
    text = f"How many different letters are used to write the word {w}?"
    sol = f"The letters are {_letters(sorted(set(w)))}: {ans} different letters ({w} has {len(w)} letters in all)."
    mistakes = [len(w), len(w) - 1, ans - 1, ans + 1]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, tally(lambda ch: ch in w)))


@variant(difficulty=2)
def only_in_first(rng, harder):
    """Letters of the first word that do not appear in the second."""
    a, b = _pair(rng, 1, 4, need_only=True)
    only = sorted(set(a) - set(b))
    ans = len(only)
    name = rng.choice(["Mia", "Leo", "Sara", "Tom"])
    left = sum(1 for ch in a if ch not in b)
    text = (f"{name} writes the word {a}. Then {name} crosses out every letter that also appears "
            f"in the word {b}.")
    after = "How many different letters are <b>not</b> crossed out?"
    sol = (f"Crossed out: {_letters(common(a, b))} (they are in {b}). Left: {_letters(only)}, "
           f"so {ans} different letters" + (f" (a letter that is left twice counts once)." if left != ans else "."))
    mistakes = [left,                       # counted repeated letters
                len(set(b) - set(a)),       # did it the other way round
                len(common(a, b)), ans + 1, ans - 1]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=0)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, tally(lambda ch: ch in a and ch not in b)))


@variant(difficulty=2)
def which_word(rng, harder):
    """Which word has exactly k letters in common with a given word?"""
    for _ in range(500):
        base = rng.choice(WORDS)
        k = rng.randint(1, 3)
        others = [w for w in WORDS if w != base]
        good = [w for w in others if len(common(base, w)) == k]
        bad = [w for w in others if len(common(base, w)) != k]
        if good and len(bad) >= 4:
            break
    else:
        raise RuntimeError("no word found")
    w = rng.choice(good)
    wrong = rng.sample(bad, 4)
    text = f"Which word has exactly {k} different letter{'s' if k > 1 else ''} in common with {base}?"
    sol = (f"{w} shares {_letters(common(base, w))} with {base}. "
           + "; ".join(f"{x} shares {len(common(base, x))}" for x in wrong) + ".")
    choices, ai = text_choices(w, wrong, rng)
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=lambda i: tally(lambda ch: ch in base and ch in choices[i]) == k)


@variant(difficulty=3)
def letter_cards(rng, harder):
    """Union: different letters used in the two words together."""
    a, b = _pair(rng, 2, 4)
    ans = len(set(a) | set(b))
    text = f"How many different letters are used to write the two words {a} and {b}?"
    after = ""
    sol = (f"{a} uses {len(set(a))} different letters and {b} uses {len(set(b))}. "
           f"{_letters(common(a, b))} {'is' if len(common(a, b)) == 1 else 'are'} in both, so count "
           f"{'it' if len(common(a, b)) == 1 else 'them'} once: {len(set(a))} + {len(set(b))} − "
           f"{len(common(a, b))} = {ans}.")
    mistakes = [len(set(a)) + len(set(b)), len(a) + len(b), len(a) + len(b) - len(common(a, b)), ans - 1, ans + 1]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, tally(lambda ch: ch in a or ch in b)))
