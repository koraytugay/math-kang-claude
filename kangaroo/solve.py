"""Brute-force solvers used by answer checks (independent of how a generator builds its answer)."""
from __future__ import annotations

import itertools
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import permutations


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


def expression_values(cards) -> frozenset:
    """Every value of an expression using each card once with + − × ÷ and any brackets
    (fractions and negative steps allowed). Brute force over orders and bracketings."""
    return _expression_values(tuple(sorted(cards)))


@lru_cache(maxsize=None)
def _trees(seq):
    """Values of seq (in this order) under every bracketing and choice of operations."""
    if len(seq) == 1:
        return frozenset({Fraction(seq[0])})
    out = set()
    for i in range(1, len(seq)):
        for a in _trees(seq[:i]):
            for b in _trees(seq[i:]):
                out |= {a + b, a - b, a * b}
                if b:
                    out.add(a / b)
    return frozenset(out)


@lru_cache(maxsize=None)
def _expression_values(cards: tuple) -> frozenset:
    vals = set()
    for order in set(permutations(cards)):
        vals |= _trees(order)
    return frozenset(vals)
