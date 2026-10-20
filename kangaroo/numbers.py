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
