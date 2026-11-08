#!/usr/bin/env python3
"""Coverage report + self-test for all generators.

    python check.py                    # coverage table + stress-test every generator
    python check.py --preview y2002_q06  # PDF showing every variant of one generator, for review
"""
from __future__ import annotations

import argparse
import random
import re
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
    """Generate every variant `runs` times (normal and harder); validate() runs each answer check."""
    errors = []
    for v in gen.variants:
        for harder in (False, True):
            for i in range(runs):
                rng = random.Random(i * 7919 + harder)
                try:
                    q = gen.generate(rng, harder=harder, only_variant=v.__name__)
                    if q.check is None:
                        raise ValueError("no answer check (set Question.check)")
                except Exception as e:  # noqa: BLE001
                    errors.append(f"{v.__name__} harder={harder} seed={i}: {e!r}")
                    if len(errors) > 5:
                        return errors
                    break
    for w in gen.warmups:
        for i in range(runs):
            try:
                q = gen.make_warmup(w, random.Random(i * 7919))
                if q.check is None:
                    raise ValueError("no answer check (set Question.check)")
            except Exception as e:  # noqa: BLE001
                errors.append(f"warm-up {w.__name__} seed={i}: {e!r}")
                break
    gen.teach()
    return errors


def preview(gen, per_variant: int = 2) -> Path:
    qs = []
    rng = random.Random(1)
    for v in gen.variants:
        for k in range(per_variant):
            qs.append(gen.generate(rng, harder=(k % 2 == 1), only_variant=v.__name__))
    qs.sort(key=lambda q: q.difficulty)
    warm = [gen.make_warmup(w, rng) for w in gen.warmups]
    out = ROOT / "output" / "previews" / f"{gen.key}.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    build_pdf(qs, str(out), title=f"Preview: {gen.key} (v{gen.meta.get('version', 1)})",
              subtitle=gen.meta.get("skill", ""), teach=gen.teach(), warmups=warm)
    print(f"Wrote {out}")
    return out


CONTESTS = {"set-03": ("canada", "Canada Math Kangaroo"), "set-01": ("austria", "Austrian Kangaroo")}
WORKFLOW = ROOT / ".github" / "workflows" / "generate-exam.yml"


def _contests(gens, pool):
    """[(set, year, level, [generators])] in pool order."""
    out = {}
    for key in pool:
        g = gens.get(key)
        if not g:
            continue
        set_, _, level, name = key.split("/")[:4] if key.count("/") >= 3 else (key.split("/")[0], "", "", key)
        year = Path(key).name[1:5]
        out.setdefault((set_, year, level), []).append(g)
    return [(s, y, l, gs) for (s, y, l), gs in out.items()]


def _level(level: str) -> str:
    m = re.match(r"Grade_0?(\d+)-0?(\d+)(?:_(\w+))?", level)
    if not m:
        return level
    return (f"{m.group(3)} " if m.group(3) else "") + f"Grade {m.group(1)}-{m.group(2)}"


def catalog(gens) -> None:
    """Write QUESTIONS.md and the contest checkboxes of the exam workflow from the pool + keywords."""
    pool = read_pool()
    contests = _contests(gens, pool)
    lines = ["# Practice questions",
             "",
             "Made by `python check.py --catalog` from `question-pool.txt` and the generators' keywords.",
             "",
             "**Pick questions** in the GitHub Actions exam form (or `python make_exam.py --from \"...\"`): type",
             "keywords or question names separated by commas, e.g. `cube counting, hiding digits, 2024 Q19`.",
             "A part of a keyword is enough (`cube` finds every cube question). Topics like `patterns` work too.",
             ""]
    for set_, year, level, gs in contests:
        cid, cname = CONTESTS.get(set_, (set_.replace("-", "_"), set_))
        lines += [f"## {cname} {year}, {_level(level)}", "",
                  "| Question | Keywords | What it practises | Preview |", "|---|---|---|---|"]
        for g in gs:
            q = f"{year} Q{int(Path(g.key).name[7:9])}"
            kws = ", ".join(g.meta.get("keywords", []))
            prev = f"[PDF](output/previews/{g.key}.pdf)"
            lines.append(f"| {q} | {kws} | {g.meta.get('skill', '')} | {prev} |")
        lines.append("")
    (ROOT / "QUESTIONS.md").write_text("\n".join(lines))
    print(f"Wrote {ROOT / 'QUESTIONS.md'}")

    inputs, picks = [], []
    for set_, year, level, gs in contests:
        cid, cname = CONTESTS.get(set_, (set_.replace("-", "_"), set_))
        kws = ", ".join(g.meta.get("keywords", ["?"])[0] for g in gs)
        desc = f"{cname} {year}, {_level(level)}: {kws}".replace("'", "")
        inputs += [f"      {cid}_{year}:", f"        description: '{desc}'", "        type: boolean",
                   "        default: false"]
        picks.append(f'          if [ "${{{{ inputs.{cid}_{year} }}}}" = "true" ]; then SOURCES+=("{set_}/{year}"); fi')
    wf = WORKFLOW.read_text()
    for tag, body in (("contests", inputs), ("contest-sources", picks)):
        start, end = f"# BEGIN {tag}", f"# END {tag}"
        i, j = wf.index(start), wf.index(end)
        i = wf.index("\n", i) + 1
        j = wf.rindex("\n", 0, j) + 1
        wf = wf[:i] + "\n".join(body) + "\n" + wf[j:]
    WORKFLOW.write_text(wf)
    print(f"Updated the contest checkboxes in {WORKFLOW.relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", metavar="KEY", help="Preview one generator (e.g. y2002_q06)")
    ap.add_argument("--preview-all", action="store_true", help="Re-generate previews for all generators")
    ap.add_argument("--runs", type=int, default=200)
    ap.add_argument("--catalog", action="store_true",
                    help="Write QUESTIONS.md and the exam workflow's contest checkboxes from the pool")
    args = ap.parse_args()
    gens = load_generators()

    if args.catalog:
        catalog(gens)
        return

    if args.preview_all:
        print(f"Generating previews for all {len(gens)} generators...")
        for g in gens.values():
            preview(g)
        return

    if args.preview:
        preview(gens[args.preview])
        return

    pool = read_pool()
    print(f"{'pool question':<45} {'generator':<10} {'ver':<4} {'variants':<9} self-test")
    print("-" * 85)
    bad = 0
    for key in pool:
        g = gens.get(key)
        if not g:
            print(f"{key:<45} {'MISSING':<10}")
            continue
        try:
            errs = stress(g, args.runs)
        except Exception:  # noqa: BLE001
            errs = [traceback.format_exc()]
        bad += bool(errs)
        status = "ok" if not errs else f"FAIL ({len(errs)})"
        print(f"{key:<45} {'yes':<10} {g.meta.get('version', 1):<4} {len(g.variants):<9} {status}")
        for e in errs:
            print("      " + e)
    extra = [k for k in gens if k not in pool]
    done = sum(k in gens for k in pool)
    print("-" * 85)
    print(f"Coverage: {done}/{len(pool)} pool questions have generators. Failing: {bad}.")
    if extra:
        print(f"Generators not in the pool (unused): {', '.join(extra)}")


if __name__ == "__main__":
    main()
