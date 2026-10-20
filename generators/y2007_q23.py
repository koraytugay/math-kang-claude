"""2007 Q23 - how many digits are needed to write all numbers from 1 to 100?

Original: How many digits are needed to write down all numbers from 1 to 100?
A 100  B 150  C 190  D 192  E 200.
1-9: 9 digits, 10-99: 90 x 2 = 180, 100: 3.  9 + 180 + 3 = 192.  Answer: D.

Core skill: counting in groups by length - how many one-, two- and three-digit
numbers there are (90 two-digit numbers, not 89 or 99!) - and not forgetting
the last number when it starts a new group (100 has 3 digits).
"""
from kangaroo import Question, numeric_choices, variant
from kangaroo.numbers import digits_between, digits_upto, split_by_length

META = {
    "source": "2007 Q23",
    "skill": "Counting digits by groups (1-, 2-, 3-digit numbers); how many numbers are in a range",
    "topics": ["counting", "arithmetic", "patterns"],
    "version": 1,
}


def _groups(a, b):
    parts = split_by_length(a, b)
    return " + ".join(f"{c} × {d}" for c, d in parts)


@variant(difficulty=1)
def one_to_round(rng, harder):
    """The original, and its big brothers 1-200, 1-1000."""
    n = rng.choice([200, 300, 1000]) if harder else rng.choice([100, 100, 110, 120])
    ans = digits_upto(n)
    text = f"How many digits are needed to write down all the numbers from 1 to {n}?"
    sol = (f"Numbers with 1, 2, 3, ... digits: {_groups(1, n)} = {ans}. "
           f"(There are 90 two-digit numbers: 10 to 99.)")
    mistakes = [digits_upto(n - 1) if n % 100 == 0 else -1,   # forgot the last number
                n * 2, 9 + 89 * 2 + 3 * (n - 99) if n >= 100 else -1,   # 89 two-digit numbers
                9 + 99 * 2 + 3 * (n - 99) if n >= 100 else -1,          # 99 two-digit numbers
                n, n * 3 if n < 1000 else -1, ans + 1]
    choices, ai = numeric_choices(ans, [m for m in mistakes if m > 0 and m != ans], rng, lo=1)
    return Question(text=text, choices=choices, answer=ai, solution=sol)


@variant(difficulty=1)
def across_hundred(rng, harder):
    """A short range that crosses 100 (or 1000)."""
    if harder:
        a, b = rng.randint(985, 996), rng.randint(1003, 1015)
    else:
        a, b = rng.randint(90, 97), rng.randint(101, 108)
    ans = digits_between(a, b)
    name = rng.choice(["Mia", "Leo", "Sara", "Tom"])
    text = f"{name} writes all the numbers from {a} to {b}."
    after = f"How many digits does {name} write?"
    count = b - a + 1
    sol = f"There are {count} numbers: {_groups(a, b)} = {ans} digits."
    mistakes = [count * len(str(a)), count * len(str(b)), (b - a) * len(str(a)), ans - 1, ans + 1, count]
    choices, ai = numeric_choices(ans, [m for m in mistakes if m != ans], rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=2)
def count_zeros(rng, harder):
    """How many zeros are written from 1 to N?"""
    n = rng.choice([200, 300, 500]) if harder else rng.choice([60, 80, 100, 100])
    ans = sum(str(k).count("0") for k in range(1, n + 1))
    text = f"All the numbers from 1 to {n} are written down."
    after = "How many times is the digit 0 written?"
    tens = sum(1 for k in range(1, n + 1) if k % 10 == 0)
    extra = ans - tens
    sol = (f"A 0 at the end: 10, 20, ..., {n - n % 10}: {tens} numbers. "
           + (f"Plus the zeros in the middle of 100-{min(n, 999)} (like 101 or 100 itself): {extra} more. "
              if extra else "") + f"Total {ans}.")
    mistakes = [tens, n // 10 - 1, ans + 1, ans - 1, tens + 1]
    choices, ai = numeric_choices(ans, [m for m in mistakes if m != ans], rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=2)
def even_only(rng, harder):
    """Only the even numbers from 2 to N."""
    n = rng.choice([120, 150, 200]) if harder else rng.choice([40, 60, 100])
    nums = list(range(2, n + 1, 2))
    ans = sum(len(str(k)) for k in nums)
    one = len([k for k in nums if k < 10]); two = len([k for k in nums if 10 <= k < 100])
    three = len([k for k in nums if k >= 100])
    text = f"Only the even numbers from 2 to {n} are written down: 2, 4, 6, ..., {n}."
    after = "How many digits are written?"
    parts = [f"{c} × {d}" for c, d in ((one, 1), (two, 2), (three, 3)) if c]
    sol = (f"Even one-digit numbers: {one}; even two-digit numbers: {two}"
           + (f"; even three-digit numbers: {three}" if three else "") + f". " + " + ".join(parts) + f" = {ans}.")
    mistakes = [digits_upto(n) // 2, len(nums) * 2, len(nums), ans + 2, ans - 2]
    choices, ai = numeric_choices(ans, [m for m in mistakes if m != ans], rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=3)
def with_commas(rng, harder):
    """Typing 1, 2, 3, ..., N with commas: digits plus commas."""
    n = rng.choice([100, 120, 150]) if harder else rng.choice([20, 30, 50])
    d = digits_upto(n)
    ans = d + (n - 1)
    name = rng.choice(["Mia", "Leo", "Sara", "Tom"])
    text = (f"{name} types the numbers from 1 to {n} on a computer, with a comma between two numbers "
            f"and no spaces: 1,2,3,...,{n}.")
    after = f"How many keys does {name} press (each digit and each comma is one key)?"
    sol = (f"Digits: {_groups(1, n)} = {d}. Commas: one fewer than the numbers, {n - 1}. "
           f"{d} + {n - 1} = {ans}.")
    mistakes = [d + n, d, d + n - 2, n * 2, ans + 9]
    choices, ai = numeric_choices(ans, [m for m in mistakes if m != ans], rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol)
