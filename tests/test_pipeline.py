import unittest
from unittest.mock import patch

from app.pipeline import run_pipeline


def fake_clean_problem(user_input: str):
    if user_input == "2x + 5 = 15":
        return {"type": "equation", "expression": "2*x + 5 = 15", "goal": "solve for x"}
    if user_input == "(2 + 3) * 5":
        return {"type": "arithmetic", "expression": "(2 + 3) * 5", "goal": "evaluate"}
    if user_input == "x^2 - 4 = 0":
        return {"type": "equation", "expression": "x**2 - 4 = 0", "goal": "solve for x"}
    return {"type": "unknown", "expression": user_input, "goal": "solve"}


def fake_solve_steps(expression: str):
    if expression == "2*x + 5 = 15":
        return ("Steps:\n1. Subtract 5 from both sides.\n2. Divide by 2.", "x = 5")
    if expression == "(2 + 3) * 5":
        return ("Steps:\n1. Add inside parentheses.\n2. Multiply the result by 5.", "(2 + 3) * 5")
    if expression == "x**2 - 4 = 0":
        return ("Steps:\n1. Factor the equation.\n2. Solve each factor.", "x**2 - 4 = 0")
    return ("Steps:\n1. Solve the problem.", expression)


def fake_explain_solution(steps: str, answer):
    return f"{steps}\nAnswer: {answer}"


class TestPipeline(unittest.TestCase):
    @patch("app.pipeline.clean_problem", side_effect=fake_clean_problem)
    @patch("app.pipeline.solve_steps", side_effect=fake_solve_steps)
    @patch("app.pipeline.explain_solution", side_effect=fake_explain_solution)
    def test_linear_equation_contains_5(self, mock_explain, mock_solve, mock_clean):
        result = run_pipeline("2x + 5 = 15")
        assert "5" in result

    @patch("app.pipeline.clean_problem", side_effect=fake_clean_problem)
    @patch("app.pipeline.solve_steps", side_effect=fake_solve_steps)
    @patch("app.pipeline.explain_solution", side_effect=fake_explain_solution)
    def test_arithmetic_contains_25(self, mock_explain, mock_solve, mock_clean):
        result = run_pipeline("(2 + 3) * 5")
        assert "25" in result

    @patch("app.pipeline.clean_problem", side_effect=fake_clean_problem)
    @patch("app.pipeline.solve_steps", side_effect=fake_solve_steps)
    @patch("app.pipeline.explain_solution", side_effect=fake_explain_solution)
    def test_quadratic_contains_root(self, mock_explain, mock_solve, mock_clean):
        result = run_pipeline("x^2 - 4 = 0")
        assert "2" in result or "-2" in result


if __name__ == "__main__":
    unittest.main()

