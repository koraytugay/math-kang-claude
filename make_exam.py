#!/usr/bin/env python3
"""Generate a random practice exam (PDF with answer key).

Examples:
    python make_exam.py                     # 20 questions, random seed
    python make_exam.py -n 24 --harder      # tougher mix
    python make_exam.py --seed 1234         # reproduce an exact exam
    python make_exam.py --from 2002         # only questions modelled on the 2002 test
    python make_exam.py --topic perimeter   # only generators with that topic
"""
from __future__ import annotations

import argparse
import datetime as dt
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from kangaroo.registry import load_generators, read_pool  # noqa: E402
from kangaroo.render import build_pdf  # noqa: E402


def pick_generators(args):
    gens = load_generators()
    pool = read_pool()
    chosen = [gens[k] for k in pool if k in gens]
    missing = [k for k in pool if k not in gens]
    if args.source:
        chosen = [g for g in chosen if any(g.key.startswith(f"y{s}") or g.key == s
                                           for s in args.source)]
    if args.topic:
        chosen = [g for g in chosen if args.topic in g.meta.get("topics", [])]
    return chosen, missing


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-n", type=int, default=20, help="number of questions (default 20)")
    ap.add_argument("--seed", type=int, help="random seed (printed on the exam)")
    ap.add_argument("--harder", action="store_true", help="more Part C style questions, bigger numbers")
    ap.add_argument("--from", dest="source", nargs="+",
                    help="restrict to source years (2002) or generator keys (y2002_q06)")
    ap.add_argument("--topic", help="restrict to a topic, e.g. perimeter")
    ap.add_argument("-o", "--out", help="output PDF path (default output/exam-<date>-<seed>.pdf)")
    ap.add_argument("--hide-sources", action="store_true", help="don't print generator names in the key")
    args = ap.parse_args()

    seed = args.seed if args.seed is not None else random.randrange(10_000, 99_999)
    rng = random.Random(seed)
    gens, missing = pick_generators(args)
    if not gens:
        sys.exit("No generators match. Run `python check.py` to see coverage.")

    questions, seen, used = [], set(), {}
    order: list = []
    tries = 0
    while len(questions) < args.n and tries < args.n * 50:
        tries += 1
        if not order:                       # cycle through generators so they share the exam evenly
            order = gens[:]
            rng.shuffle(order)
        g = order.pop()
        q = g.generate(rng, harder=args.harder, used=used)
        key = (q.text, q.after_figure)
        if key in seen:
            continue
        seen.add(key)
        questions.append(q)
    questions.sort(key=lambda q: q.difficulty)   # Part A, then B, then C

    out = Path(args.out) if args.out else ROOT / "output" / f"exam-{dt.date.today()}-{seed}.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    mode = "harder" if args.harder else "standard"
    build_pdf(questions, str(out), title="Math Kangaroo Practice",
              subtitle=f"Grade 3-4 · {len(questions)} questions · {mode} · seed {seed}",
              show_sources=not args.hide_sources)
    print(f"Wrote {out}  ({len(questions)} questions from {len(gens)} generator(s), seed {seed})")
    if missing:
        print(f"Note: {len(missing)} pool question(s) have no generator yet (python check.py lists them).")


if __name__ == "__main__":
    main()
