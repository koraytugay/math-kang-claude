#!/usr/bin/env python3
"""Build the exam website into _site/ (published on GitHub Pages by .github/workflows/pages.yml).

    python site/build.py            # needs: pip install -r requirements.txt pymupdf

For every pool question it renders one fixed example (an easy variant, same seed every build) as a PNG,
and writes questions.json with the contests, keywords and skills. The page itself (index.html, app.js)
and the password-locked token (token.json, made by site/lock-token.mjs) are copied as they are.
"""
from __future__ import annotations

import io
import json
import random
import shutil
import sys
import zlib
from pathlib import Path

import pymupdf
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm, inch
from reportlab.platypus import Paragraph, SimpleDocTemplate

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from check import CONTESTS, _contests, _level  # noqa: E402
from kangaroo.registry import load_generators, read_pool  # noqa: E402
from kangaroo.render import BASE, _question_block, clean  # noqa: E402

OUT = ROOT / "_site"
REPO = "koraytugay/math-kang-claude"
WORKFLOW = "generate-exam.yml"
STATIC = ["index.html", "app.js", "token.json", "practice.html", "practice.js", "secrets.js"]


def example(g):
    """The same example question on every build: an easy variant with a seed taken from the key."""
    easy = [v for v in g.variants if v._variant_difficulty == 1] or g.variants
    rng = random.Random(zlib.crc32(g.key.encode()))
    return g.generate(rng, only_variant=easy[0].__name__)


def png(q, path: Path) -> None:
    """Render one question on a tall page, then crop to what was drawn."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=(letter[0], 30 * inch), leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1 * cm, bottomMargin=1 * cm)
    block = _question_block(q, "", doc.width)
    block[0] = Paragraph(clean(q.text), BASE)       # no question number, so no hanging indent
    doc.build(block)
    page = pymupdf.open(stream=buf.getvalue(), filetype="pdf")[0]
    box = pymupdf.Rect()
    for _, r in page.get_bboxlog():
        box |= pymupdf.Rect(r)
    box = (box + (-6, -6, 6, 6)) & page.rect
    page.get_pixmap(dpi=130, clip=box).save(str(path))


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "examples").mkdir(parents=True)
    for name in STATIC:
        if (HERE / name).exists():
            shutil.copy(HERE / name, OUT / name)

    gens, pool = load_generators(), read_pool()
    contests = []
    for set_, year, level, gs in _contests(gens, pool):
        cname = CONTESTS.get(set_, (set_, set_))[1]
        items = []
        for g in gs:
            img = f"examples/{g.key.replace('/', '__')}.png"
            png(example(g), OUT / img)
            items.append({"key": g.key, "label": f"{year} Q{int(g.name[7:9])}",
                          "keywords": g.meta.get("keywords", []), "skill": g.meta.get("skill", ""),
                          "img": img})
        contests.append({"name": f"{cname} {year}", "level": _level(level), "questions": items,
                         "pill": f"Set {set_.split('-')[-1]} · {year}"})
        print(f"{cname} {year}: {len(items)} questions")
    (OUT / "questions.json").write_text(json.dumps(
        {"repo": REPO, "workflow": WORKFLOW, "contests": contests}, indent=1))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
