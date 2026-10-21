#!/usr/bin/env python3
"""Generate a random practice exam (PDF with answer key).

Examples:
    python make_exam.py                     # 20 questions, saved as output/exams/001.pdf
    python make_exam.py -n 24 --harder      # tougher mix
    python make_exam.py --seed 1234         # reproduce an exact exam
    python make_exam.py --from 2002         # only questions from 2002
    python make_exam.py --from set-03/2002  # only questions from set-03 2002
    python make_exam.py --topic perimeter   # only generators with that topic
"""
from __future__ import annotations

import argparse
import random
import re
import sys
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


def matches_source(g, s: str) -> bool:
    s = s.strip()
    if not s:
        return False
    name = Path(g.key).name
    s_norm = re.sub(r"set[-_]0?(\d+)", r"set-\1", s.lower())
    key_norm = re.sub(r"set[-_]0?(\d+)", r"set-\1", g.key.lower())

    if s == g.key or s == name or s_norm == key_norm or s == Path(g.key).stem:
        return True

    if "/" in s:
        parts = [p.strip() for p in s.split("/") if p.strip()]
        return all(
            (re.sub(r"set[-_]0?(\d+)", r"set-\1", p.lower()) in key_norm
             or f"y{p}_" in g.key
             or (p.isdigit() and f"y{p}_" in g.key))
            for p in parts
        )

    if s.isdigit() and f"y{s}_" in g.key:
        return True
    if f"/y{s}_" in f"/{g.key}":
        return True
    if s_norm in key_norm:
        return True
    if s.lower() in [t.lower() for t in g.meta.get("topics", [])]:
        return True
    return False


def get_next_exam_path(exams_dir: Path | None = None) -> Path:
    exams_dir = exams_dir or ROOT / "output" / "exams"
    exams_dir.mkdir(parents=True, exist_ok=True)
    existing_nums = []
    for f in exams_dir.glob("*.pdf"):
        m = re.fullmatch(r"(\d+)\.pdf", f.name)
        if m:
            existing_nums.append(int(m.group(1)))
    next_num = max(existing_nums, default=0) + 1
    width = max(3, len(str(next_num)))
    return exams_dir / f"{next_num:0{width}d}.pdf"


def pick_generators(args):
    gens = load_generators()
    pool = read_pool()
    chosen = [gens[k] for k in pool if k in gens]
    missing = [k for k in pool if k not in gens]
    if args.source:
        chosen = [g for g in chosen if any(matches_source(g, s) for s in args.source)]
    if args.topic:
        chosen = [g for g in chosen if args.topic in g.meta.get("topics", [])]
    return chosen, missing


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-n", type=int, default=20, help="number of questions (default 20)")
    ap.add_argument("--seed", type=int, help="random seed (printed on the exam)")
    ap.add_argument("--harder", action="store_true", help="more Part C style questions, bigger numbers")
    ap.add_argument("--from", dest="source", nargs="+",
                     help="restrict to source years (2002), sets (set-03), or set/year (set-03/2002)")
    ap.add_argument("--topic", help="restrict to a topic, e.g. perimeter")
    ap.add_argument("-o", "--out", help="output PDF path (default output/exams/001.pdf, 002.pdf, etc.)")
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

    if args.out:
        out = Path(args.out)
        if out.is_dir() or str(args.out).endswith(("/", "\\")):
            out = get_next_exam_path(out)
    else:
        out = get_next_exam_path()

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
