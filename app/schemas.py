from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProblemStructure(BaseModel):
    model_config = ConfigDict(extra="forbid")

    problem: str = Field(min_length=1)
    topic: str = Field(min_length=1)
    expression: str = Field(min_length=1)
    goal: str = Field(min_length=1)


class SolutionStructure(BaseModel):
    model_config = ConfigDict(extra="forbid")

    steps: list[str] = Field(min_length=1)
    final_expression: str = Field(min_length=1)
    answer: str = Field(min_length=1)


class VerifierResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok", "mismatch", "need_clarification", "error"]
    verified_answer: str = Field(min_length=1)
    feedback: str | None = None
    clarification_question: str | None = None


class PipelineResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    status: Literal["ok", "mismatch", "need_clarification", "error"]
    retries: int = 0

    problem: str
    topic: str
    expression: str
    goal: str
    steps: list[str]
    final_expression: str
    answer: str
    verified_answer: str
    explanation: str
