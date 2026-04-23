from app.llm import clean_problem, explain_solution, solve_steps
from app.math_tool import compute_answer


def run_pipeline(user_input: str) -> str:
    structured = clean_problem(user_input)
    steps, final_expr = solve_steps(structured["expression"])
    answer = compute_answer(final_expr)
    explanation = explain_solution(steps, answer)
    return explanation

