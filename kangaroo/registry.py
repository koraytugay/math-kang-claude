"""Finds generator modules and runs them.

A generator is a Python file under generators/ (e.g. generators/set-03/by_level/Grade_03-04/y2002_q06.py)
that defines:

    META = {"source": "2002 Q6", "skill": "...", "topics": [...], "version": 1}

and one or more variant functions decorated with @variant(difficulty=1|2|3).
Each variant takes (rng, harder: bool) and returns a Question.
"""
from __future__ import annotations

import importlib.util
import random
import re
import sys
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
    key: str            # e.g. "set-03/by_level/Grade_03-04/y2002_q06"
    module: object

    @property
    def name(self) -> str:
        """Base name of the generator, e.g. 'y2002_q06'."""
        return Path(self.key).name

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


class GeneratorsDict(dict):
    """Dictionary of generators with fuzzy/short-key lookup support."""

    def __getitem__(self, key: str) -> Generator:
        if super().__contains__(key):
            return super().__getitem__(key)
        # Search by suffix / basename (e.g. y2002_q06 or 2002_q06)
        matches = [v for k, v in self.items()
                   if k == key or k.endswith(f"/{key}") or Path(k).name == key or Path(k).stem == key]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise KeyError(f"Ambiguous generator key '{key}' matches: {[m.key for m in matches]}")
        raise KeyError(key)

    def get(self, key: str, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key: object) -> bool:
        if super().__contains__(key):
            return True
        if isinstance(key, str):
            matches = [k for k in self.keys()
                       if k == key or k.endswith(f"/{key}") or Path(k).name == key or Path(k).stem == key]
            return len(matches) == 1
        return False


def pool_key(year: int, num: int, prefix: str = "") -> str:
    base = f"y{year}_q{num:02d}"
    return f"{prefix}/{base}" if prefix else base


def load_generators() -> GeneratorsDict:
    """Find and load all generator modules under generators/ recursively."""
    gen_dir = ROOT / "generators"
    out = GeneratorsDict()
    for py_file in sorted(gen_dir.rglob("*.py")):
        if py_file.name == "__init__.py":
            continue
        if not re.fullmatch(r"y\d{4}_q\d{2}\.py", py_file.name):
            continue
        rel = py_file.relative_to(gen_dir).with_suffix("")
        key = str(rel).replace("\\", "/")
        safe_mod_name = f"generators.{key.replace('/', '.').replace('-', '_')}"
        spec = importlib.util.spec_from_file_location(safe_mod_name, py_file)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            sys.modules[safe_mod_name] = mod
            spec.loader.exec_module(mod)
            out[key] = Generator(key, mod)
    return out


def read_pool(path: Path | None = None) -> list[str]:
    """Parse question-pool.txt lines into generator keys.

    Supports:
        set-03/by_level/Grade_03-04/2002: 1, 6, 7
    or section headers:
        [set-03/by_level/Grade_03-04]
        2002: 1, 6, 7
    or legacy:
        2002: 1, 6, 7
    """
    path = path or ROOT / "question-pool.txt"
    keys = []
    current_prefix = ""
    for line in path.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        # Section header e.g. [set-03/by_level/Grade_03-04]
        if line.startswith("[") and line.endswith("]"):
            current_prefix = line[1:-1].strip().strip("/")
            continue
        if ":" not in line:
            continue
        prefix_or_year, nums = line.split(":", 1)
        prefix_or_year = prefix_or_year.strip()
        if "/" in prefix_or_year:
            prefix, year_str = prefix_or_year.rsplit("/", 1)
            prefix = prefix.strip()
        else:
            prefix = current_prefix
            year_str = prefix_or_year
        m = re.search(r"\d{4}", year_str)
        if not m:
            continue
        year = int(m.group(0))
        for n in re.findall(r"\d+", nums):
            keys.append(pool_key(year, int(n), prefix=prefix))
    return keys
