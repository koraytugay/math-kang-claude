"""Finds generator modules and runs them.

A generator is a file generators/y<YEAR>_q<NN>.py that defines:

    META = {"source": "2002 Q6", "skill": "...", "topics": [...], "version": 1}

and one or more variant functions decorated with @variant(difficulty=1|2|3).
Each variant takes (rng, harder: bool) and returns a Question.
"""
from __future__ import annotations

import importlib
import pkgutil
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .question import Question

ROOT = Path(__file__).resolve().parent.parent

# How likely each difficulty is picked: normal mode vs --harder
WEIGHTS = {False: {1: 3, 2: 2, 3: 1}, True: {1: 1, 2: 2, 3: 4}}


def variant(difficulty: int):
    def deco(fn: Callable):
        fn._variant_difficulty = difficulty
        return fn
    return deco


@dataclass
class Generator:
    key: str            # e.g. "y2002_q06"
    module: object

    @property
    def meta(self) -> dict:
        return self.module.META

    @property
    def variants(self) -> list[Callable]:
        return [v for v in vars(self.module).values()
                if callable(v) and hasattr(v, "_variant_difficulty")]

    def generate(self, rng: random.Random, harder: bool = False,
                 only_variant: str | None = None, used: dict | None = None) -> Question:
        """`used` counts variants already in this exam, so repeats become unlikely."""
        vs = self.variants
        if only_variant:
            vs = [v for v in vs if v.__name__ == only_variant]
        used = used if used is not None else {}
        w = [WEIGHTS[harder][v._variant_difficulty] / (1 + used.get(f"{self.key}.{v.__name__}", 0)) ** 2
             for v in vs]
        fn = rng.choices(vs, weights=w)[0]
        q = fn(rng, harder)
        q.difficulty = fn._variant_difficulty
        q.source = self.meta["source"]
        q.variant = fn.__name__
        q.validate()
        used[f"{self.key}.{fn.__name__}"] = used.get(f"{self.key}.{fn.__name__}", 0) + 1
        return q


def pool_key(year: int, num: int) -> str:
    return f"y{year}_q{num:02d}"


def load_generators() -> dict[str, Generator]:
    import generators  # the package next to this one
    out = {}
    for info in pkgutil.iter_modules(generators.__path__):
        if re.fullmatch(r"y\d{4}_q\d{2}", info.name):
            mod = importlib.import_module(f"generators.{info.name}")
            out[info.name] = Generator(info.name, mod)
    return dict(sorted(out.items()))


def read_pool(path: Path | None = None) -> list[str]:
    """Parse question-pool.txt lines like '2002: 6, 7, 9' into generator keys."""
    path = path or ROOT / "question-pool.txt"
    keys = []
    for line in path.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        year, nums = line.split(":", 1)
        for n in re.findall(r"\d+", nums):
            keys.append(pool_key(int(year.strip()), int(n)))
    return keys
