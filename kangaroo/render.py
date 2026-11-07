"""Turns a list of Questions into a contest-style PDF with an answer key."""
from __future__ import annotations

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

from .question import LETTERS, Question

POINTS = {1: 3, 2: 4, 3: 5}
PART = {1: "A", 2: "B", 3: "C"}

BASE = ParagraphStyle("base", fontName="Times-Roman", fontSize=12, leading=15)
TITLE = ParagraphStyle("title", parent=BASE, fontName="Times-Bold", fontSize=15,
                       leading=19, alignment=TA_CENTER)
SUB = ParagraphStyle("sub", parent=BASE, alignment=TA_CENTER)
PART_H = ParagraphStyle("part", parent=BASE, fontName="Times-BoldItalic", spaceBefore=8,
                        spaceAfter=6)
QTEXT = ParagraphStyle("q", parent=BASE, leftIndent=0.7 * cm, firstLineIndent=-0.7 * cm)
INDENT = ParagraphStyle("qi", parent=BASE, leftIndent=0.7 * cm)
OPT = ParagraphStyle("opt", parent=BASE)
SMALL = ParagraphStyle("small", parent=BASE, fontSize=10.5, leading=13)


def clean(s: str) -> str:
    """Characters the built-in PDF fonts lack or space badly."""
    return s.replace("\u2212", "\u2013")   # minus sign -> en dash


def _options(q: Question, width: float):
    indent = 0.7 * cm
    if q.choice_figures:
        cells = []
        for i, d in enumerate(q.choice_figures):
            inner = Table([[Paragraph(f"<b><i>{LETTERS[i]}.</i></b>", OPT), d]], colWidths=[16, None])
            inner.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                       ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                       ("RIGHTPADDING", (0, 0), (-1, -1), 2)]))
            cells.append(inner)
        t = Table([[""] + cells], colWidths=[indent] + [(width - indent) / 5] * 5)
        t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0),
                               ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
        return t
    cells = [Paragraph(f"<b><i>{LETTERS[i]}.</i></b> {clean(c)}", OPT) for i, c in enumerate(q.choices)]
    longest = max(len(c) for c in q.choices)
    if longest <= 12:
        rows, ncol = [cells], 5
    elif longest <= 30:
        rows, ncol = [cells[:3], cells[3:] + [""]], 3
    else:
        rows, ncol = [[c] for c in cells], 1
    rows = [[""] + r for r in rows]
    t = Table(rows, colWidths=[indent] + [(width - indent) / ncol] * ncol)
    t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0),
                           ("TOPPADDING", (0, 0), (-1, -1), 1),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
    return t


def _figure(drawing):
    t = Table([[drawing]])
    t.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    return t


TEACH_H = ParagraphStyle("teach_h", parent=BASE, fontName="Times-Bold", fontSize=13, leading=16,
                         spaceBefore=8, spaceAfter=3)
TEACH_P = ParagraphStyle("teach_p", parent=BASE, spaceAfter=4)
TEACH_B = ParagraphStyle("teach_b", parent=TEACH_P, leftIndent=0.6 * cm, bulletIndent=0.15 * cm)
TIP = ParagraphStyle("tip", parent=TEACH_P, backColor=colors.Color(0.94, 0.96, 1.0), borderPadding=5,
                     spaceBefore=6, spaceAfter=8)


def _teach(items, width):
    """Teaching page items:
        "text"              a paragraph (mini-HTML)
        ("h", "text")       a heading
        ("-", "text")       a bullet point
        ("tip", "text")     a shaded box
        ("table", rows)     a small table, first row is the header
        Drawing             a centred figure
    """
    out = []
    for it in items:
        if isinstance(it, str):
            out.append(Paragraph(clean(it), TEACH_P))
        elif isinstance(it, tuple) and it[0] == "h":
            out.append(Paragraph(clean(it[1]), TEACH_H))
        elif isinstance(it, tuple) and it[0] == "-":
            out.append(Paragraph(clean(it[1]), TEACH_B, bulletText="\u2022"))
        elif isinstance(it, tuple) and it[0] == "tip":
            out += [Spacer(1, 4), Paragraph(clean(it[1]), TIP)]
        elif isinstance(it, tuple) and it[0] == "table":
            rows = [[Paragraph(clean(str(c)), OPT) for c in r] for r in it[1]]
            t = Table(rows, hAlign="CENTER")
            t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                                   ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.92, 0.92, 0.92)),
                                   ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
            out += [Spacer(1, 3), t, Spacer(1, 6)]
        else:
            out += [Spacer(1, 3), _figure(it), Spacer(1, 3)]
    return out


def _question_block(q: Question, label: str, width: float):
    block = [Paragraph(f"<b>{label}</b>&nbsp;&nbsp;{clean(q.text)}", QTEXT)]
    if q.figure is not None:
        block += [Spacer(1, 4), _figure(q.figure), Spacer(1, 2)]
    if q.after_figure:
        block.append(Paragraph(clean(q.after_figure), INDENT))
    block += [Spacer(1, 3), _options(q, width), Spacer(1, 12)]
    return block


def build_pdf(questions: list[Question], path: str, title: str, subtitle: str = "",
              show_sources: bool = True, teach: list | None = None,
              warmups: list[Question] | None = None) -> None:
    """teach: items for a "How to think about it" page (see _teach), shown first.
    warmups: easy lead-in questions, numbered W1, W2, ... before Part A."""
    doc = SimpleDocTemplate(path, pagesize=letter, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.6 * cm, bottomMargin=1.6 * cm, title=title)
    width = doc.width
    story = [Paragraph(title, TITLE)]
    if subtitle:
        story.append(Paragraph(subtitle, SUB))
    story.append(Spacer(1, 10))

    if teach:
        story += _teach(teach, width)
        story.append(PageBreak())
    if warmups:
        story.append(Paragraph("Warm-up: small steps first (no points)", PART_H))
        for i, q in enumerate(warmups, 1):
            story.append(KeepTogether(_question_block(q, f"W{i}.", width)))

    current_part = None
    for i, q in enumerate(questions, 1):
        block = []
        if q.difficulty != current_part:   # part header stays on the page with its first question
            current_part = q.difficulty
            block.append(Paragraph(f"Part {PART[current_part]}: Each question is worth "
                                   f"{POINTS[current_part]} points", PART_H))
        block += _question_block(q, f"{i}.", width)
        story.append(KeepTogether(block))

    # ---- answer key -------------------------------------------------------
    story += [PageBreak(), Paragraph("Answer Key", TITLE), Spacer(1, 6)]
    keyed = [(f"W{i}", q) for i, q in enumerate(warmups or [], 1)] + \
            [(f"{i}", q) for i, q in enumerate(questions, 1)]
    grid = [[n, LETTERS[q.answer]] for n, q in keyed]
    # compact grid: 6 columns of (number, letter)
    cols = 6
    rows = []
    for r in range(0, len(grid), cols):
        row = []
        for n, letter_ in grid[r:r + cols]:
            row += [f"{n}.", letter_]
        row += [""] * (2 * cols - len(row))
        rows.append(row)
    t = Table(rows, colWidths=[1.0 * cm, 1.4 * cm] * cols)
    t.setStyle(TableStyle([("FONTNAME", (0, 0), (-1, -1), "Times-Roman"),
                           ("FONTNAME", (1, 0), (-1, -1), "Times-Bold"),
                           ("FONTSIZE", (0, 0), (-1, -1), 12),
                           ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                           ("BOX", (0, 0), (-1, -1), 0.5, colors.grey)]))
    for c in range(1, 2 * cols, 2):
        t.setStyle(TableStyle([("FONTNAME", (c, 0), (c, -1), "Times-Bold"),
                               ("ALIGN", (c, 0), (c, -1), "LEFT")]))
    story += [t, Spacer(1, 14), Paragraph("Solutions", PART_H)]
    for i, q in keyed:
        src = (f" <font color='#888888' size='8.5'>[{q.source} · {q.variant}]</font>"
               if show_sources else "")
        shown = "" if q.choice_figures else f" ({clean(q.choices[q.answer])})"
        story.append(Paragraph(f"<b>{i}. {LETTERS[q.answer]}</b>{shown} — "
                               f"{clean(q.solution)}{src}", SMALL))
        story.append(Spacer(1, 5))
    doc.build(story)
