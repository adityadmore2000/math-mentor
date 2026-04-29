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


def _try_eval_constant_equation(expression: str) -> dict | None:
    # Handle expressions like "9+5=17" deterministically (no variables to solve for).
    if "=" not in expression:
        return None

    lhs_text, rhs_text = expression.split("=", 1)
    lhs_text = lhs_text.strip()
    rhs_text = rhs_text.strip()
    if not lhs_text or not rhs_text:
        return None

    try:
        from sympy import sympify
    except Exception:
        return None

    try:
        lhs = sympify(lhs_text)
        rhs = sympify(rhs_text)
    except Exception:
        return None

    if getattr(lhs, "free_symbols", None) or getattr(rhs, "free_symbols", None):
        return None

    # For pure constants, a direct comparison is fine; `.equals` is more robust for SymPy objects.
    try:
        truth = bool(lhs.equals(rhs))
    except Exception:
        truth = bool(lhs == rhs)

    return {
        "lhs_value": str(lhs),
        "rhs_value": str(rhs),
        "truth": truth,
    }


def run_pipeline(user_input: str) -> dict:
    structured_problem = clean_problem(user_input)
    expression = _get_value(structured_problem, "expression")

    constant_eq = _try_eval_constant_equation(expression)
    if constant_eq is not None:
        answer = "True" if constant_eq["truth"] else "False"
        steps = [
            f"Evaluate left side: {constant_eq['lhs_value']}",
            f"Evaluate right side: {constant_eq['rhs_value']}",
            f"Compare both sides: {answer}",
        ]
        explanation = explain_solution(steps, answer)
        result = PipelineResult(
            problem=_get_value(structured_problem, "problem"),
            topic=_get_value(structured_problem, "topic"),
            expression=expression,
            goal="check if true",
            steps=steps,
            final_expression=expression,
            answer=answer,
            verified_answer=answer,
            explanation=explanation,
        )
        return result.model_dump()

    solution = solve_steps(expression)

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
