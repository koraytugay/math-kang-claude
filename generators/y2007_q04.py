"""2007 Q4 - the first number after 2007 with the same digit sum.

Original: 34 and 142 have the same digit sum (7). What is the first number
greater than 2007 whose digit sum is the same as that of 2007 (9)?
A 2016  B 2115  C 2008  D 7002  E 2070.  Answer: A (2016).

Core skill: to keep a digit sum while making the number a little bigger, move
1 from one digit to a digit further left, changing the rightmost digits as
little as possible. Children pick a "nice-looking" number (2070, 7002) or one
that is bigger but not the first.
"""
from itertools import product

from kangaroo import Question, numeric_choices, value_check, variant
from kangaroo.choices import number_in

META = {
    "source": "2007 Q4",
    "skill": "Digit sums: find the next/previous number with the same digit sum",
    "topics": ["arithmetic", "patterns", "logic"],
    "version": 1,
}


def dsum(n):
    return sum(int(c) for c in str(n))


def digit_total(n):
    """Answer checks: digit sum by arithmetic (not via the written number like dsum)."""
    t = 0
    while n:
        t, n = t + n % 10, n // 10
    return t


def first_from(start, stop, s, step):
    """Is the first number with digit sum s, going from start towards stop, equal to stop?"""
    return digit_total(stop) == s and all(digit_total(k) != s for k in range(start, stop, step))


def _after(n, k=1):
    """The k-th number after n with the same digit sum."""
    s, m, found = dsum(n), n, 0
    while True:
        m += 1
        if dsum(m) == s:
            found += 1
            if found == k:
                return m


def _plus(n):
    return " + ".join(str(n))


@variant(difficulty=1)
def next_same_sum(rng, harder):
    """The original."""
    n = rng.randint(1000, 9899) if harder else rng.randint(100, 989)
    m = _after(n)
    s = dsum(n)
    text = (f"The numbers 34 and 142 have the same sum of digits (3 + 4 = 7 and 1 + 4 + 2 = 7). "
            f"What is the first number greater than {n} whose sum of digits is the same as for {n}?")
    sol = f"{_plus(n)} = {s}. Going up from {n}, the first number with digit sum {s} is {m} ({_plus(m)} = {s})."
    mistakes = [_after(n, 2), _after(n, 3), n + 1, int(str(n)[::-1]) if int(str(n)[::-1]) > n else -1,
                n + 9, n + 10]
    choices, ai = numeric_choices(m, [x for x in mistakes if x != m], rng, lo=n + 1)
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=lambda i: first_from(n + 1, number_in(choices[i]), s, 1))


@variant(difficulty=1)
def which_same_sum(rng, harder):
    """Which of these numbers has the same digit sum as n?"""
    n = rng.randint(1000, 9999) if harder else rng.randint(100, 999)
    s = dsum(n)
    good = [m for m in range(n - 300, n + 300) if m != n and m > 9 and dsum(m) == s]
    bad = [m for m in range(n - 300, n + 300) if m > 9 and dsum(m) in (s - 1, s + 1)]
    m = rng.choice(good)
    wrong = rng.sample(bad, 4)
    vals = sorted(wrong + [m])
    text = f"Which number has the same sum of digits as {n}?"
    sol = f"{_plus(n)} = {s} and {_plus(m)} = {s}. The others add up to {s - 1} or {s + 1}."
    return Question(text=text, choices=[str(v) for v in vals], answer=vals.index(m), solution=sol,
                    check=lambda i: vals[i] != n and digit_total(vals[i]) == s)


@variant(difficulty=2)
def smallest_with_sum(rng, harder):
    """Smallest number whose digits add up to s - put the big digits at the end."""
    s = rng.randint(19, 30) if harder else rng.randint(10, 20)
    m = 1
    while dsum(m) != s:
        m += 1
    text = f"What is the smallest number whose digits add up to {s}?"
    sol = (f"Use as few digits as possible: as many 9s as possible, with the smallest digit in front. "
           f"{m}: {_plus(m)} = {s}.")
    # every other number with this digit sum is bigger, so these are all wrong
    alt = [int(str(m)[::-1]),       # small digit put at the end
           _after(m), _after(m, 2), m + 1]
    choices, ai = numeric_choices(m, [x for x in alt if x != m], rng, lo=1)
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=lambda i: first_from(1, number_in(choices[i]), s, 1))


@variant(difficulty=2)
def before_same_sum(rng, harder):
    """Reverse direction: the last number before n with the same digit sum."""
    while True:      # n must not be the smallest number with its digit sum
        n = rng.randint(1000, 9999) if harder else rng.randint(120, 999)
        s = dsum(n)
        smaller = [k for k in range(n - 1, 0, -1) if dsum(k) == s][:2]
        if len(smaller) == 2:
            break
    m, m2 = smaller
    text = f"What is the biggest number smaller than {n} whose sum of digits is the same as for {n}?"
    sol = f"{_plus(n)} = {s}. Counting down from {n}, the first number with digit sum {s} is {m}."
    mistakes = [m2, n - 1, n - 9, n - 10, _after(n)]
    choices, ai = numeric_choices(m, [x for x in mistakes if x != m], rng, lo=1)
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=lambda i: number_in(choices[i]) < n and first_from(n - 1, number_in(choices[i]), s, -1))


@variant(difficulty=3)
def count_with_sum(rng, harder):
    """How many two-digit (or three-digit) numbers have digit sum s?"""
    if harder:
        s = rng.randint(4, 8)
        nums = [m for m in range(100, 1000) if dsum(m) == s]
        kind = "three-digit"
    else:
        s = rng.randint(5, 14)
        nums = [m for m in range(10, 100) if dsum(m) == s]
        kind = "two-digit"
    ans = len(nums)
    text = f"How many {kind} numbers have digits that add up to {s}?"
    if not harder:
        sol = (f"List them by the first digit: {', '.join(map(str, nums))}. That is {ans}.")
    else:
        rows = [len([m for m in nums if m // 100 == h]) for h in range(1, 10)]
        sol = (f"Count by the first digit: " + " + ".join(str(r) for r in rows if r) + f" = {ans}.")
    mistakes = [ans + 1, ans - 1, s, s + 1, ans * 2]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, sum(1 for ds in product(range(10), repeat=3 if harder else 2)
                                                  if ds[0] > 0 and sum(ds) == s)))
