#!/usr/bin/env python3
"""Export the question bank for the practice page into _site/bank/ (run after site/build.py).

    python site/bank.py               # BANK_SEEDS=20 seeds per variant, normal + harder

Every generator x variant x seed (normal and harder) becomes one question with its figures as inline SVG.
The id "<generator>|<variant>|<seed>|h0/h1" always rebuilds the same question. generate() runs
Question.validate(), so every exported answer has passed the generator's independent answer check.

    _site/bank/index.json            the skills: key, label, contest, keywords, skill, topics, file, count
    _site/bank/<key with __>.json    the questions of one generator
"""
from __future__ import annotations

import json
import os
import random
import re
import sys
import zlib
from pathlib import Path

from reportlab.graphics import renderSVG

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from check import CONTESTS, _contests, _level  # noqa: E402
from kangaroo.registry import load_generators, read_pool  # noqa: E402

OUT = ROOT / "_site" / "bank"
SEEDS = int(os.environ.get("BANK_SEEDS", "20"))


def svg(drawing) -> str | None:
    """A reportlab Drawing as inline SVG (no XML header), scaled by CSS."""
    if drawing is None:
        return None
    s = renderSVG.drawToString(drawing)
    s = s[s.index("<svg"):]
    return re.sub(r"\s+", " ", s)


def export(g) -> list[dict]:
    out, seen = [], set()
    for v in g.variants:
        for harder in (False, True):
            for seed in range(SEEDS):
                qid = f"{g.key}|{v.__name__}|{seed}|h{int(harder)}"
                q = g.generate(random.Random(zlib.crc32(qid.encode())), harder=harder, only_variant=v.__name__)
                sig = (q.text, q.after_figure, tuple(q.choices))
                if sig in seen:
                    continue
                seen.add(sig)
                out.append({
                    "id": qid, "variant": v.__name__, "harder": harder, "difficulty": q.difficulty,
                    "text": q.text, "after": q.after_figure or "", "figure": svg(q.figure),
                    "choices": q.choices,
                    "choice_figures": [svg(d) for d in q.choice_figures] if q.choice_figures else None,
                    "answer": q.answer, "solution": q.solution,
                })
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    gens, pool = load_generators(), read_pool()
    index, total = [], 0
    for set_, year, level, gs in _contests(gens, pool):
        cname = CONTESTS.get(set_, (set_, set_))[1]
        for g in gs:
            qs = export(g)
            name = g.key.replace("/", "__") + ".json"
            (OUT / name).write_text(json.dumps(qs, separators=(",", ":")))
            index.append({"key": g.key, "label": f"{year} Q{int(g.name[7:9])}",
                          "contest": f"{cname} {year}", "pill": f"Set {set_.split('-')[-1]} · {year}",
                          "level": _level(level), "keywords": g.meta.get("keywords", []),
                          "skill": g.meta.get("skill", ""), "topics": g.meta.get("topics", []),
                          "file": f"bank/{name}", "count": len(qs)})
            total += len(qs)
    (OUT / "index.json").write_text(json.dumps({"generators": index}, indent=1))
    size = sum(f.stat().st_size for f in OUT.iterdir()) // 1024
    print(f"Wrote {OUT}: {len(index)} generators, {total} questions, {size} KB")


if __name__ == "__main__":
    main()
