"""Brute-force solvers used by answer checks (independent of how a generator builds its answer)."""
from __future__ import annotations

import itertools
from collections import Counter


def balance_weights(balances, kinds, fixed: dict, max_w: int = 60) -> list[dict]:
    """All whole-number weights (1..max_w) for `kinds` that make every balance level.

    balances: [(left items, right items), ...] where items are lists of kind names.
    fixed: weights already known, e.g. {"dot": 1}.
    """
    free = [k for k in kinds if k not in fixed]
    out = []
    counted = [(Counter(l), Counter(r)) for l, r in balances]
    for ws in itertools.product(range(1, max_w + 1), repeat=len(free)):
        w = dict(fixed, **dict(zip(free, ws)))
        if all(sum(w[k] * n for k, n in l.items()) == sum(w[k] * n for k, n in r.items()) for l, r in counted):
            out.append(w)
    return out


def only(xs):
    """The single element of xs (raises if there are none or several)."""
    xs = list(xs)
    if len(xs) != 1:
        raise ValueError(f"expected exactly one solution, got {xs[:5]}")
    return xs[0]
