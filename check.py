#!/usr/bin/env python3
"""Coverage report + self-test for all generators.

    python check.py                    # coverage table + stress-test every generator
    python check.py --preview y2002_q06  # PDF showing every variant of one generator, for review
"""
from __future__ import annotations

import argparse
import random
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

try:
    import reportlab  # noqa: F401
except ImportError:
    sys.exit("reportlab is not installed. One-time setup (in this folder):\n"
             "    python3 -m venv .venv\n"
             "    .venv/bin/pip install -r requirements.txt\n"
             "then run:  .venv/bin/python " + Path(sys.argv[0]).name + " ...")

from kangaroo.registry import load_generators, read_pool  # noqa: E402
from kangaroo.render import build_pdf  # noqa: E402


def stress(gen, runs: int) -> list[str]:
    errors = []
    for v in gen.variants:
        for harder in (False, True):
            for i in range(runs):
                rng = random.Random(i * 7919 + harder)
                try:
                    gen.generate(rng, harder=harder, only_variant=v.__name__)
                except Exception as e:  # noqa: BLE001
                    errors.append(f"{v.__name__} harder={harder} seed={i}: {e!r}")
                    if len(errors) > 5:
                        return errors
    return errors


def preview(gen, per_variant: int = 2):
    qs = []
    rng = random.Random(1)
    for v in gen.variants:
        for k in range(per_variant):
            qs.append(gen.generate(rng, harder=(k % 2 == 1), only_variant=v.__name__))
    qs.sort(key=lambda q: q.difficulty)
    out = ROOT / "output" / f"preview-{gen.key}.pdf"
    out.parent.mkdir(exist_ok=True)
    build_pdf(qs, str(out), title=f"Preview: {gen.key} (v{gen.meta.get('version', 1)})",
              subtitle=gen.meta.get("skill", ""))
    print(f"Wrote {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", metavar="KEY")
    ap.add_argument("--runs", type=int, default=200)
    args = ap.parse_args()
    gens = load_generators()

    if args.preview:
        preview(gens[args.preview])
        return

    pool = read_pool()
    print(f"{'pool question':<14} {'generator':<10} {'ver':<4} {'variants':<9} self-test")
    print("-" * 60)
    bad = 0
    for key in pool:
        g = gens.get(key)
        if not g:
            print(f"{key:<14} {'MISSING':<10}")
            continue
        try:
            errs = stress(g, args.runs)
        except Exception:  # noqa: BLE001
            errs = [traceback.format_exc()]
        bad += bool(errs)
        status = "ok" if not errs else f"FAIL ({len(errs)})"
        print(f"{key:<14} {'yes':<10} {g.meta.get('version', 1):<4} {len(g.variants):<9} {status}")
        for e in errs:
            print("      " + e)
    extra = [k for k in gens if k not in pool]
    done = sum(k in gens for k in pool)
    print("-" * 60)
    print(f"Coverage: {done}/{len(pool)} pool questions have generators. Failing: {bad}.")
    if extra:
        print(f"Generators not in the pool (unused): {', '.join(extra)}")


if __name__ == "__main__":
    main()
