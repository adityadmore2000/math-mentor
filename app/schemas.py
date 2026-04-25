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


class PipelineResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    problem: str
    topic: str
    expression: str
    goal: str
    steps: list[str]
    final_expression: str
    answer: str
    verified_answer: str
    explanation: str
