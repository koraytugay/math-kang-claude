"""The common data shape every generator returns."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

LETTERS = "ABCDE"


@dataclass
class Question:
    text: str                      # question text (reportlab mini-HTML allowed: <i>, <b>, <sup>)
    choices: list[str]             # exactly 5 options, in display order (A..E)
    answer: int                    # index into choices of the correct option
    solution: str                  # short worked solution for the answer key
    difficulty: int = 1            # 1 = Part A (3 pts), 2 = Part B (4 pts), 3 = Part C (5 pts)
    figure: Optional[Any] = None   # a reportlab Drawing, or None
    after_figure: str = ""         # optional text shown below the figure (like "How many ... ?")
    choice_figures: Optional[list] = None  # 5 Drawings shown as the options (choices = short labels)
    source: str = ""               # filled in by the registry, e.g. "2002 Q6"
    variant: str = ""              # filled in by the registry, name of the variant used
    meta: dict = field(default_factory=dict)
    # Independent re-check, separate from how the answer was built: check(i) says whether
    # option i is correct (re-solve from the shown data: brute force, simulation, a solver).
    # validate() demands that exactly one option passes, and that it is `answer`.
    check: Optional[Callable[[int], bool]] = field(default=None, repr=False)

    @property
    def answer_letter(self) -> str:
        return LETTERS[self.answer]

    def validate(self) -> None:
        """Raise ValueError if the question is malformed."""
        if len(self.choices) != 5:
            raise ValueError(f"need 5 choices, got {len(self.choices)}")
        if len(set(self.choices)) != 5:
            raise ValueError(f"duplicate choices: {self.choices}")
        if not 0 <= self.answer < 5:
            raise ValueError(f"answer index out of range: {self.answer}")
        if not self.text.strip() or not self.solution.strip():
            raise ValueError("empty text or solution")
        if self.choice_figures is not None and len(self.choice_figures) != 5:
            raise ValueError("choice_figures needs exactly 5 drawings")
        if self.difficulty not in (1, 2, 3):
            raise ValueError(f"difficulty must be 1..3, got {self.difficulty}")
        if self.check is not None:
            ok = [i for i in range(5) if self.check(i)]
            if ok != [self.answer]:
                raise ValueError(f"check: correct options are {[LETTERS[i] for i in ok]}, "
                                 f"answer says {LETTERS[self.answer]} (choices {self.choices})")
