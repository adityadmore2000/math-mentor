from app.llm import clean_problem, explain_solution, solve_steps
from app.math_tool import compute_answer
from app.schemas import PipelineResult


def _get_value(structure, key: str):
    if isinstance(structure, dict):
        return structure[key]
    return getattr(structure, key)


def _stringify_answer(answer) -> str:
    if isinstance(answer, (list, tuple, set)):
        return ", ".join(str(item) for item in answer)
    return str(answer)


def run_pipeline(user_input: str) -> dict:
    structured_problem = clean_problem(user_input)
    solution = solve_steps(_get_value(structured_problem, "expression"))

    verified_answer = _stringify_answer(compute_answer(_get_value(solution, "final_expression")))
    explanation = explain_solution(_get_value(solution, "steps"), verified_answer)

    result = PipelineResult(
        problem=_get_value(structured_problem, "problem"),
        topic=_get_value(structured_problem, "topic"),
        expression=_get_value(structured_problem, "expression"),
        goal=_get_value(structured_problem, "goal"),
        steps=_get_value(solution, "steps"),
        final_expression=_get_value(solution, "final_expression"),
        answer=_get_value(solution, "answer"),
        verified_answer=verified_answer,
        explanation=explanation,
    )
    return result.model_dump()
