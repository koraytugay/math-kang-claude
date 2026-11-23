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


# How hard a question is compared with the ORIGINAL contest question it comes from (the practice website
# picks questions by this, see site/smart.js). Our four steps (variant difficulty 1, 2, 3 and 3 with
# harder=True) are each rated once per skill with META["rungs"] = (step1, step2, step3, step3_harder).
RUNG_NAMES = ("easier", "aligned", "harder")


def default_rungs(key: str) -> tuple:
    """Rungs of the four steps when a generator does not rate them itself: from the contest part of the
    original (Q1-8 = Part A, Q9-16 = Part B, Q17-24 = Part C). Our step 1 stays close to the original, so for
    a Part C original it is much easier than the contest question; for a Part A original it is the same."""
    m = re.search(r"_q(\d+)$", key)
    num = int(m.group(1)) if m else 17
    if num > 16:
        return ("easier", "easier", "aligned", "harder")
    if num > 8:
        return ("aligned", "aligned", "harder", "harder")
    return ("aligned", "harder", "harder", "harder")


def variant(difficulty: int):
    def deco(fn: Callable):
        fn._variant_difficulty = difficulty
        return fn
    return deco


def warmup(fn: Callable):
    """An easy step-by-step question that leads up to the real skill. Warm-ups are shown in
    previews (after the teaching page), not in exams. Same signature as a variant."""
    fn._warmup = True
    return fn


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

    @property
    def rungs(self) -> tuple:
        """(step 1, step 2, step 3, step 3 harder) as 'easier' | 'aligned' | 'harder'. See RUNG_NAMES."""
        r = tuple(self.meta.get("rungs") or default_rungs(self.key))
        if len(r) != 4 or any(x not in RUNG_NAMES for x in r):
            raise ValueError(f'{self.key}: META["rungs"] must be 4 of {RUNG_NAMES}, got {r!r}')
        return r

    def rung_variants(self) -> dict:
        """How many variants can produce a question on each rung (a difficulty-3 variant gives one question
        with normal numbers and one with harder=True)."""
        r, out = self.rungs, {n: 0 for n in RUNG_NAMES}
        for v in self.variants:
            d = v._variant_difficulty
            for rung in {r[d - 1]} | ({r[3]} if d == 3 else set()):
                out[rung] += 1
        return out

    @property
    def warmups(self) -> list[Callable]:
        return [v for v in vars(self.module).values() if callable(v) and getattr(v, "_warmup", False)]

    def teach(self) -> list:
        """The teaching page: the module's teach() items (see render.build_pdf), or []."""
        fn = getattr(self.module, "teach", None)
        return fn() if callable(fn) else []

    def make_warmup(self, fn: Callable, rng: random.Random) -> Question:
        q = fn(rng, False)
        q.difficulty = 1
        q.source = self.meta.get("source", "")
        q.variant = fn.__name__
        q.validate()
        return q

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
        folder = str(Path(self.key).parent)
        src = self.meta.get("source", "")
        if folder and folder != "." and not src.startswith(folder):
            q.source = f"{folder}/{src}" if src else folder
        else:
            q.source = src
        q.variant = fn.__name__
        if getattr(q.choices, "mistakes", None):           # labelled wrong options (kangaroo.choices)
            q.meta.setdefault("mistakes", dict(q.choices.mistakes))
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
