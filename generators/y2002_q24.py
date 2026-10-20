"""2002 Q24 - when will the odometer show all different digits again?

Original: The odometer of my car shows 187569. All its digits are different.
After how many more kilometres will this happen again?
A 1  B 21  C 431  D 12431  E 13776.
187570-187589 all repeat a digit (7, 8 or 5 twice); 187590 works: 21 km.  Answer: B.

Core skill: finding the next number with a property by thinking about place value -
keep the left digits if you can and change as few digits on the right as
possible, checking each candidate instead of guessing.
"""
from itertools import combinations, permutations

from kangaroo import Question, numeric_choices, value_check, variant

META = {
    "source": "2002 Q24",
    "skill": "Next number with a digit property: change the rightmost digits as little as possible",
    "topics": ["arithmetic", "patterns", "logic"],
    "version": 2,
}


def distinct(n):
    s = str(n)
    return len(set(s)) == len(s)


def palindrome(n):
    return str(n) == str(n)[::-1]


def increasing(n):
    s = str(n)
    return all(a < b for a, b in zip(s, s[1:]))


def _next(n, ok, k=1):
    """The k-th number after n with property ok (same number of digits)."""
    m, found = n, 0
    while True:
        m += 1
        if len(str(m)) != len(str(n)):
            return None
        if ok(m):
            found += 1
            if found == k:
                return m


def _prev(n, ok):
    m = n - 1
    while m >= 10 ** (len(str(n)) - 1):
        if ok(m):
            return m
        m -= 1
    return None


def _start(rng, digits, ok, min_gap, max_gap):
    """A number with property ok whose next one is between min_gap and max_gap away."""
    for _ in range(4000):
        n = rng.randint(10 ** (digits - 1), 10 ** digits - 1)
        if ok(n):
            nx = _next(n, ok)
            if nx and min_gap <= nx - n <= max_gap:
                return n, nx
    raise RuntimeError("no start found")


def _mistakes(n, ok, ans):
    """Gaps to the 2nd/3rd next numbers, plus 'just add 1' and off-by-ten slips."""
    out = [1, ans + 10, ans - 10, ans + 9, ans - 1, ans + 1]
    for k in (2, 3):
        m = _next(n, ok, k)
        if m:
            out.append(m - n)
    return out


# Answer checks: build every number with the property directly (not by counting up).
def built_distinct(d):
    return {int("".join(p)) for p in permutations("0123456789", d) if p[0] != "0"}


def built_palindromes(d):
    half = (d + 1) // 2
    return {int(str(h) + str(h)[:d - half][::-1]) for h in range(10 ** (half - 1), 10 ** half)}


def built_increasing(d):
    return {int("".join(c)) for c in combinations("123456789", d)}


def built_same(d):
    return {int(str(k) * d) for k in range(1, 10)}


def gap_after(n, built):
    return min(m for m in built if m > n) - n


@variant(difficulty=1)
def all_different(rng, harder):
    """The original."""
    digits = 6 if harder else rng.choice([4, 5])
    n, nx = _start(rng, digits, distinct, 8, 200 if harder else 60)
    ans = nx - n
    text = (f"The odometer of a car shows {n} km. All the digits of this number are different.")
    after = "After how many more kilometres will all the digits be different again?"
    sol = (f"Counting up, every number before {nx} repeats a digit. {nx} has all different digits: "
           f"{nx} − {n} = {ans}.")
    choices, ai = numeric_choices(ans, _mistakes(n, distinct, ans), rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, gap_after(n, built_distinct(digits))))


@variant(difficulty=1)
def next_palindrome(rng, harder):
    """Next number that reads the same backwards."""
    digits = 5 if harder else rng.choice([3, 4])
    n, nx = _start(rng, digits, palindrome, 10, 1100)
    ans = nx - n
    text = (f"The odometer of a bike shows {n} km. This number reads the same forwards and backwards.")
    after = "After how many more kilometres will this happen again?"
    sol = f"The next such number is {nx}, so {nx} − {n} = {ans}."
    choices, ai = numeric_choices(ans, _mistakes(n, palindrome, ans) + [100, 10, 11, 110], rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, gap_after(n, built_palindromes(digits))))


@variant(difficulty=2)
def last_time(rng, harder):
    """Reverse: how many kilometres ago were all digits different?"""
    digits = 6 if harder else rng.choice([4, 5])
    for _ in range(4000):
        n = rng.randint(10 ** (digits - 1), 10 ** digits - 1)
        if distinct(n):
            continue
        p = _prev(n, distinct)
        if p and 5 <= n - p <= (300 if harder else 80):
            break
    else:
        raise RuntimeError("no start found")
    ans = n - p
    text = f"The odometer of a car shows {n} km. Some of its digits are the same."
    after = "How many kilometres ago did the odometer last show a number with all different digits?"
    sol = (f"Counting down from {n}, the first number with all different digits is {p}: "
           f"{n} − {p} = {ans}.")
    mistakes = [1, ans + 10, ans - 10, ans + 1, ans - 1]
    nx = _next(n, distinct)
    if nx:
        mistakes.append(nx - n)
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, n - max(m for m in built_distinct(digits) if m < n)))


@variant(difficulty=2)
def same_digits(rng, harder):
    """Next number with all digits the same - many children change only the last digit."""
    digits = rng.choice([4, 5] if harder else [3, 4])
    d = rng.randint(1, 8)
    rep = int(str(d) * digits)
    nxt = int(str(d + 1) * digits)
    n = rng.randint(rep + 1, nxt - 2)
    ans = nxt - n
    text = f"A counter shows {n}. Every second it goes up by 1."
    after = f"How many seconds until it shows a number whose {digits} digits are all the same?"
    sol = (f"The numbers with all digits the same are {rep}, {nxt}, ... The next one after {n} is "
           f"{nxt}: {nxt} − {n} = {ans}.")
    last_only = (int(str(n)[0]) - int(str(n)[-1])) % 10
    mistakes = [last_only, ans + 1, ans - 1, int(str(d + 2) * digits) - n if d + 2 <= 9 else -1,
                n - rep]
    choices, ai = numeric_choices(ans, mistakes, rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, gap_after(n, built_same(digits))))


@variant(difficulty=3)
def going_up(rng, harder):
    """Next number whose digits go up from left to right."""
    digits = 4 if harder else 3
    n, nx = _start(rng, digits, increasing, 8, 700)
    ans = nx - n
    text = (f"The odometer of a scooter shows {n} km. Each digit is bigger than the digit before it.")
    after = "After how many more kilometres will this happen again?"
    sol = (f"Keep as many digits on the left as possible. The next such number is {nx}: "
           f"{nx} − {n} = {ans}.")
    choices, ai = numeric_choices(ans, _mistakes(n, increasing, ans), rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol,
                    check=value_check(choices, gap_after(n, built_increasing(digits))))
