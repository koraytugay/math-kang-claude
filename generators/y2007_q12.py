"""2007 Q12 - Basil is older than Peter by one year and one day.

Original: Basil, who is older than Peter by one year and one day, was born on
January 1, 2002. What is the date of Peter's birthday?
A January 2, 2003  B January 2, 2001  C December 31, 2000  D December 31, 2002
E December 31, 2003.  Older means born earlier, so Peter was born one year and
one day later: January 2, 2003.  Answer: A.

Core skill: "older" means "born earlier" - so the younger person's date is
later. Then add (or subtract) days across the end of a month or year carefully.
Children go the wrong way in time, or change only the year.
"""
from datetime import date, timedelta

from kangaroo import Question, numeric_choices, text_choices, variant

META = {
    "source": "2007 Q12",
    "skill": "Dates: older = born earlier; adding days across month and year ends",
    "topics": ["time", "logic"],
    "version": 1,
}

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December"]
PAIRS = [("Basil", "Peter"), ("Anna", "Lucy"), ("Omar", "Leo"), ("Mia", "Sara"), ("Tom", "Ben")]


def fmt(d):
    return f"{MONTHS[d.month - 1]} {d.day}, {d.year}"


def shift(d, years=0, days=0):
    """Move a date by whole years (same day and month) and then by days."""
    y = d.year + years
    try:
        d2 = d.replace(year=y)
    except ValueError:                 # February 29 in a non-leap year
        d2 = date(y, 3, 1)
    return d2 + timedelta(days=days)


def _near_end(rng):
    """A date close to the end/start of a month or year, where children slip."""
    y = rng.randint(1998, 2015)
    kind = rng.choice(["year", "month", "month", "plain"])
    if kind == "year":
        return rng.choice([date(y, 12, 31), date(y, 1, 1), date(y, 12, 30)])
    if kind == "month":
        m = rng.randint(1, 11)
        last = (date(y, m + 1, 1) - timedelta(days=1))
        return rng.choice([last, date(y, m + 1, 1)])
    return date(y, rng.randint(1, 12), rng.randint(2, 27))


def _date_options(correct, wrong, rng):
    wrong = [w for w in dict.fromkeys(wrong) if w != correct]
    choices, ai = text_choices(fmt(correct), [fmt(w) for w in wrong], rng)
    return choices, ai


@variant(difficulty=1)
def younger_birthday(rng, harder):
    """The original: the older child's birthday is known."""
    old, young = rng.choice(PAIRS)
    born = _near_end(rng) if harder or rng.random() < 0.6 else date(2002, 1, 1)
    yrs = rng.choice([1, 2, 3]) if harder else 1
    dd = rng.choice([1, 2, 3]) if harder else 1
    ans = shift(born, yrs, dd)
    gap = f"{yrs} year{'s' if yrs > 1 else ''} and {dd} day{'s' if dd > 1 else ''}"
    text = f"{old}, who is older than {young} by {gap}, was born on {fmt(born)}."
    after = f"When was {young} born?"
    sol = (f"Older means born earlier, so {young} was born {gap} <i>after</i> {fmt(born)}: "
           f"{yrs} year{'s' if yrs > 1 else ''} later is {fmt(shift(born, yrs))}, then {dd} more "
           f"day{'s' if dd > 1 else ''}: {fmt(ans)}.")
    wrong = [shift(born, -yrs, -dd),        # went back in time
             shift(born, yrs, -dd), shift(born, -yrs, dd), shift(born, yrs + 1, dd), shift(born, yrs, dd + 1),
             shift(born, yrs, 0)]
    choices, ai = _date_options(ans, wrong, rng)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=1)
def older_birthday(rng, harder):
    """Reverse: the younger child's birthday is known."""
    old, young = rng.choice(PAIRS)
    born = _near_end(rng)
    yrs = rng.choice([1, 2]) if harder else 1
    dd = rng.choice([1, 2, 3]) if harder else 1
    ans = shift(born, -yrs, -dd)
    gap = f"{yrs} year{'s' if yrs > 1 else ''} and {dd} day{'s' if dd > 1 else ''}"
    text = f"{young} was born on {fmt(born)}. {old} is {gap} older than {young}."
    after = f"When was {old} born?"
    sol = (f"Older means born earlier: go back {gap} from {fmt(born)}. "
           f"{fmt(shift(born, -yrs))}, then {dd} day{'s' if dd > 1 else ''} earlier: {fmt(ans)}.")
    wrong = [shift(born, yrs, dd), shift(born, -yrs, dd), shift(born, yrs, -dd), shift(born, -yrs, 0),
             shift(born, -yrs - 1, -dd)]
    choices, ai = _date_options(ans, wrong, rng)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=2)
def days_between(rng, harder):
    """Two birthdays in the same year, across a month end: how many days apart?"""
    y = rng.randint(2001, 2015)
    m = rng.randint(1, 11)
    last = (date(y, m + 1, 1) - timedelta(days=1)).day
    d1 = date(y, m, rng.randint(last - 6, last))
    gap = rng.randint(5, 20) if not harder else rng.randint(20, 45)
    d2 = d1 + timedelta(days=gap)
    a, b = rng.choice(PAIRS)
    text = f"{a} was born on {fmt(d1)} and {b} on {fmt(d2)}."
    after = f"By how many days is {a} older than {b}?"
    days_left = last - d1.day
    sol = (f"{MONTHS[m - 1]} has {last} days, so from {MONTHS[m - 1]} {d1.day} to the end of the month is "
           f"{days_left} days" + (f", then {gap - days_left} more days to {fmt(d2)}" if d2.month != m else "")
           + f": {gap} days.")
    naive = (d2.day + 30 - d1.day) if d2.month != d1.month else gap
    mistakes = [naive, gap + 1, gap - 1, abs(d2.day - d1.day), naive + 1]
    choices, ai = numeric_choices(gap, mistakes, rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=2)
def age_on_day(rng, harder):
    """How old is someone on a given day - has the birthday come yet that year?"""
    a, b = rng.choice(PAIRS)
    y = rng.randint(2008, 2016)
    da = date(y, rng.randint(1, 6), rng.randint(1, 28))
    db = date(y + 1, rng.randint(7, 12), rng.randint(1, 28))
    today = date(y + rng.randint(7, 9), rng.randint(da.month + 1, 12) if da.month < 12 else 12, 15)
    if today < db.replace(year=today.year):
        age_b = today.year - db.year - 1
    else:
        age_b = today.year - db.year
    age_a = today.year - da.year - (1 if today < da.replace(year=today.year) else 0)
    text = (f"{a} was born on {fmt(da)} and {b} on {fmt(db)}.")
    after = f"How many years old is {b} on {fmt(today)}?"
    passed = today >= db.replace(year=today.year)
    sol = (f"{today.year} − {db.year} = {today.year - db.year}, but {b}'s birthday ({MONTHS[db.month - 1]} "
           f"{db.day}) " + ("has already passed, so " if passed else "has not come yet that year, so ")
           + f"{b} is {age_b}.")
    mistakes = [today.year - db.year, age_b + 1, age_b - 1, age_a]
    choices, ai = numeric_choices(age_b, mistakes, rng, lo=1)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol)


@variant(difficulty=3)
def new_year_twins(rng, harder):
    """Twins born on either side of midnight on New Year's Eve."""
    a, b = rng.choice(PAIRS)
    y = rng.randint(2005, 2016)
    mins_before = rng.randint(3, 25)
    later = rng.randint(mins_before + 5, mins_before + 40)
    born_a = f"11:{60 - mins_before:02d} p.m."
    ans = date(y + 1, 1, 1)
    text = (f"{a} and {b} are twins. {a} was born at {born_a} on {fmt(date(y, 12, 31))}. "
            f"{b} was born {later} minutes later.")
    after = f"What is {b}'s date of birth?"
    sol = (f"{mins_before} minutes after {born_a} it is midnight, and a new day and a new year start. "
           f"{b} was born {later - mins_before} minutes after midnight, on {fmt(ans)}. "
           f"So {a} is older, but they have different birthdays and were even born in different years.")
    wrong = [date(y, 12, 31), date(y, 1, 1), date(y + 1, 12, 31), date(y - 1, 1, 1), date(y + 1, 1, 2)]
    choices, ai = _date_options(ans, wrong, rng)
    return Question(text=text, after_figure=after, choices=choices, answer=ai, solution=sol)
