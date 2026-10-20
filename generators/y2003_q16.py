"""2003 Q16 - 35 digits were used to number the pages; how many pages?

Original: The number of digits used to write all the page numbers in a book is
35. How many pages is the book in total?  A 12  B 15  C 22  D 28  E 35.
Pages 1-9 use 9 digits; the other 26 digits are 13 two-digit pages (10-22).
Answer: C (22).

Core skill: counting digits in groups - one-digit, two-digit, three-digit
numbers use different amounts, so split the count at 9 and 99. Children treat
every page as one digit, or every page as two.
"""
from kangaroo import Question, numeric_choices, variant
from kangaroo.numbers import digits_upto

META = {
    "source": "2003 Q16",
    "skill": "Counting the digits in 1..N: split into one-, two- and three-digit numbers",
    "topics": ["counting", "arithmetic", "patterns"],
    "version": 1,
}

THINGS = [("book", "pages", "page numbers"), ("street", "houses", "house numbers"),
          ("theatre", "seats", "seat numbers"), ("hotel", "rooms", "room numbers")]


def _split(n):
    """'9 + 2 × 13' style breakdown of the digits in 1..n."""
    parts = [f"9 × 1"] if n >= 9 else [f"{n} × 1"]
    if n >= 10:
        parts.append(f"{min(n, 99) - 9} × 2")
    if n >= 100:
        parts.append(f"{n - 99} × 3")
    return " + ".join(parts)


@variant(difficulty=1)
def pages_from_digits(rng, harder):
    """The original: total digits -> number of pages (two-digit range)."""
    n = rng.randint(40, 99) if harder else rng.randint(12, 45)
    d = digits_upto(n)
    place, items, numbers = rng.choice(THINGS)
    text = (f"To write all the {numbers} in a {place}, starting from 1, exactly {d} digits are needed.")
    after = f"How many {items} are there?"
    sol = (f"1 to 9 use 9 digits. The other {d} − 9 = {d - 9} digits belong to two-digit numbers: "
           f"{d - 9} ÷ 2 = {n - 9} numbers, from 10 to {n}. So there are {n}.")
    mistakes = [d, (d - 9) // 2, d // 2, n + 9, n - 9 + 1, (d + 9) // 2]
    choices, ai = numeric_choices(n, mistakes, rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=1)
def digits_for_pages(rng, harder):
    """Forward: how many digits for pages 1..n?"""
    n = rng.randint(100, 160) if harder else rng.randint(15, 60)
    d = digits_upto(n)
    place, items, numbers = rng.choice(THINGS)
    name = rng.choice(["Mia", "Leo", "Sara", "Tom"])
    text = (f"A {place} has {n} {items}, numbered from 1 to {n}. {name} writes all the {numbers} "
            f"on cards, one digit on each card.")
    after = "How many cards does " + name + " need?"
    sol = f"{_split(n)} = {d}."
    mistakes = [n, 2 * n, 2 * n - 9, d - 9, d + 9, 3 * n if n >= 100 else d + n // 10]
    choices, ai = numeric_choices(d, mistakes, rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=2)
def count_one_digit(rng, harder):
    """How many times is the digit k written in 1..n?"""
    n = rng.randint(100, 150) if harder else rng.randint(25, 99)
    k = rng.randint(1, 9)
    c = sum(str(i).count(str(k)) for i in range(1, n + 1))
    nums = [i for i in range(1, n + 1) if str(k) in str(i)]
    place, items, numbers = rng.choice(THINGS)
    text = f"The {items} in a {place} are numbered from 1 to {n}."
    after = f"How many times is the digit {k} written?"
    ones = sum(1 for i in range(1, n + 1) if i % 10 == k)
    tens = sum(1 for i in range(1, n + 1) if (i // 10) % 10 == k and i >= 10)
    hund = sum(1 for i in range(1, n + 1) if i >= 100 and (i // 100) == k)
    sol = (f"As the last digit: {ones} times; as the tens digit: {tens} times"
           + (f"; as the hundreds digit: {hund} times" if hund else "") + f". Total {c}.")
    mistakes = [len(nums), ones, tens, c - 1, c + 1, ones + tens + 1]
    choices, ai = numeric_choices(c, mistakes, rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=2)
def from_page(rng, harder):
    """Numbering starts somewhere in the middle (chapter from page s to e)."""
    s = rng.randint(5, 30) if not harder else rng.randint(50, 95)
    e = rng.randint(s + 10, 99) if not harder else rng.randint(101, 140)
    d = digits_upto(e) - digits_upto(s - 1)
    name = rng.choice(["Mia", "Leo", "Sara", "Tom"])
    text = f"{name} reads a chapter from page {s} to page {e} (both included)."
    after = "How many digits are printed in the page numbers of this chapter?"
    one = len([p for p in range(s, e + 1) if p < 10])
    two = len([p for p in range(s, e + 1) if 10 <= p < 100])
    three = len([p for p in range(s, e + 1) if p >= 100])
    parts = [f"{x} × {w}" for x, w in ((one, 1), (two, 2), (three, 3)) if x]
    sol = (f"There are {e - s + 1} pages: " + " + ".join(parts) + f" = {d} digits.")
    mistakes = [e - s + 1, 2 * (e - s + 1), digits_upto(e), 2 * (e - s), d - 2, d + 2]
    choices, ai = numeric_choices(d, mistakes, rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=3)
def three_digit_pages(rng, harder):
    """Reverse with three-digit pages: digits -> pages."""
    n = rng.randint(110, 250) if harder else rng.randint(100, 140)
    d = digits_upto(n)
    place, items, numbers = rng.choice(THINGS[:2])
    text = f"Exactly {d} digits are used to write all the {numbers} in a {place}, starting from 1."
    after = f"How many {items} are there?"
    sol = (f"1-9 use 9 digits, 10-99 use 90 × 2 = 180, together 189. The other {d} − 189 = {d - 189} "
           f"digits are three-digit numbers: {d - 189} ÷ 3 = {n - 99}, from 100 to {n}.")
    mistakes = [(d - 9) // 2, d // 3, n - 99, n + 9, (d - 189) // 3 + 9, n - 1]
    choices, ai = numeric_choices(n, mistakes, rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol)
