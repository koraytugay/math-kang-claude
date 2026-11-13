"""Paragraphs and bullet lists in question text, for both the PDF and the website.

Question text may use three plain-text markers:

    blank line ("\\n\\n")     starts a new paragraph
    line starting "- "        a bullet point
    single newline ("\\n")    a line break inside a paragraph

On top of that, the final question sentence ("How many ...?") is put in a paragraph of its
own when it follows a story, so it stands out (`split_question`).
"""
from __future__ import annotations

import re

# A sentence end followed by the start of a new sentence ("... tray. Which ...").
# Requires an upper-case letter, a tag or a quote next, so "fig. 1" is not a boundary.
_BOUNDARY = re.compile(r'[.!?]["”)]?\s+(?=[A-Z<"“])')


def blocks(text: str, split_question: bool = True) -> list[tuple[str, str]]:
    """The text as [("p", html) | ("li", html)], in order.
    split_question: put the last question sentence of the last paragraph on its own."""
    out: list[tuple[str, str]] = []
    for para in re.split(r"\n\s*\n", text.strip()):
        lines: list[str] = []
        for line in para.split("\n"):
            line = line.strip()
            if line.startswith("- "):
                if lines:
                    out.append(("p", "<br/>".join(lines)))
                    lines = []
                out.append(("li", line[2:].strip()))
            elif line:
                lines.append(line)
        if lines:
            out.append(("p", "<br/>".join(lines)))
    if split_question and out and out[-1][0] == "p":
        out[-1:] = [("p", s) for s in _split_last_question(out[-1][1])]
    return out


def _split_last_question(p: str) -> list[str]:
    q = p.rfind("?")
    if q < 0:
        return [p]
    starts = [m.end() for m in _BOUNDARY.finditer(p, 0, q)]
    if not starts:
        return [p]
    cut = starts[-1]
    return [p[:cut].rstrip(), p[cut:]]


def html(text: str, split_question: bool = True) -> str:
    """The text as HTML for the website: <p> and <ul><li> elements."""
    parts, items = [], []
    for kind, s in blocks(text, split_question) + [("end", "")]:
        if kind == "li":
            items.append(f"<li>{s}</li>")
            continue
        if items:
            parts.append("<ul>" + "".join(items) + "</ul>")
            items = []
        if kind == "p":
            parts.append(f"<p>{s}</p>")
    return "\n".join(parts)
