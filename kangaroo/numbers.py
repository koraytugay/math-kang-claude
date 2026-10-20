"""Small number helpers shared by several generators."""
from __future__ import annotations


def digits_upto(n: int) -> int:
    """How many digits are needed to write 1, 2, ..., n."""
    return sum(len(str(k)) for k in range(1, n + 1))


def digits_between(a: int, b: int) -> int:
    """Digits needed to write a, a+1, ..., b."""
    return sum(len(str(k)) for k in range(a, b + 1))


def split_by_length(a: int, b: int) -> list[tuple[int, int]]:
    """[(how many numbers, digits each), ...] for the numbers a..b, shortest first."""
    out = {}
    for k in range(a, b + 1):
        out[len(str(k))] = out.get(len(str(k)), 0) + 1
    return [(c, d) for d, c in sorted(out.items())]


# ---------------------------------------------------------------- answer checks (write it all out)
def written(a: int, b: int, sep: str = "") -> str:
    """The numbers a..b actually written one after the other."""
    return sep.join(str(k) for k in range(a, b + 1))


def last_page_for(digits: int) -> list[int]:
    """Every n such that writing 1..n uses exactly `digits` digits (write and count)."""
    out, used, n = [], 0, 0
    while used < digits:
        n += 1
        used += len(str(n))
        if used == digits:
            out.append(n)
    return out
