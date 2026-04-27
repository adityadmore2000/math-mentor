from __future__ import annotations

from dataclasses import dataclass

from app.schemas import ProblemStructure


@dataclass(frozen=True)
class NeedClarification(Exception):
    question: str
    problem: ProblemStructure | None = None

