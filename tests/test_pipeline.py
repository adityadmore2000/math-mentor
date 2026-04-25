import unittest
from unittest.mock import patch

from app.pipeline import run_pipeline


def fake_clean_problem(user_input: str):
    if user_input == "2x + 5 = 15":
        return {
            "problem": "2x + 5 = 15",
            "topic": "algebra",
            "expression": "2*x + 5 = 15",
            "goal": "solve for x",
        }
    if user_input == "(2 + 3) * 5":
        return {
            "problem": "(2 + 3) * 5",
            "topic": "arithmetic",
            "expression": "(2 + 3) * 5",
            "goal": "evaluate",
        }
    if user_input == "x^2 - 4 = 0":
        return {
            "problem": "x^2 - 4 = 0",
            "topic": "algebra",
            "expression": "x**2 - 4 = 0",
            "goal": "solve for x",
        }
    if user_input == "9+5=17":
        return {
            "problem": "9+5=17",
            "topic": "arithmetic",
            "expression": "9+5=17",
            "goal": "check if true",
        }
    return {"problem": user_input, "topic": "unknown", "expression": user_input, "goal": "solve"}


def fake_solve_steps(expression: str):
    if expression == "2*x + 5 = 15":
        return {
            "steps": ["Subtract 5 from both sides.", "Divide by 2."],
            "final_expression": "x = 5",
            "answer": "x = 5",
        }
    if expression == "(2 + 3) * 5":
        return {
            "steps": ["Add inside parentheses.", "Multiply the result by 5."],
            "final_expression": "(2 + 3) * 5",
            "answer": "25",
        }
    if expression == "x**2 - 4 = 0":
        return {
            "steps": ["Factor the equation.", "Solve each factor."],
            "final_expression": "x**2 - 4 = 0",
            "answer": "x = -2, 2",
        }
    return {"steps": ["Solve the problem."], "final_expression": expression, "answer": expression}


def fake_explain_solution(steps: str, answer):
    return f"{steps}\nAnswer: {answer}"


class TestPipeline(unittest.TestCase):
    @patch("app.pipeline.clean_problem", side_effect=fake_clean_problem)
    @patch("app.pipeline.solve_steps", side_effect=fake_solve_steps)
    @patch("app.pipeline.explain_solution", side_effect=fake_explain_solution)
    def test_linear_equation_contains_5(self, mock_explain, mock_solve, mock_clean):
        result = run_pipeline("2x + 5 = 15")
        assert result["problem"] == "2x + 5 = 15"
        assert result["answer"] == "x = 5"
        assert result["verified_answer"] == "5"
        assert result["steps"] == ["Subtract 5 from both sides.", "Divide by 2."]

    @patch("app.pipeline.clean_problem", side_effect=fake_clean_problem)
    @patch("app.pipeline.solve_steps", side_effect=fake_solve_steps)
    @patch("app.pipeline.explain_solution", side_effect=fake_explain_solution)
    def test_arithmetic_contains_25(self, mock_explain, mock_solve, mock_clean):
        result = run_pipeline("(2 + 3) * 5")
        assert result["topic"] == "arithmetic"
        assert result["verified_answer"] == "25"

    @patch("app.pipeline.clean_problem", side_effect=fake_clean_problem)
    @patch("app.pipeline.solve_steps", side_effect=fake_solve_steps)
    @patch("app.pipeline.explain_solution", side_effect=fake_explain_solution)
    def test_quadratic_contains_root(self, mock_explain, mock_solve, mock_clean):
        result = run_pipeline("x^2 - 4 = 0")
        assert result["goal"] == "solve for x"
        assert "-2" in result["verified_answer"] or "2" in result["verified_answer"]

    @patch("app.pipeline.clean_problem", side_effect=fake_clean_problem)
    @patch("app.pipeline.solve_steps", side_effect=fake_solve_steps)
    @patch("app.pipeline.explain_solution", side_effect=fake_explain_solution)
    def test_constant_equation_is_checked(self, mock_explain, mock_solve, mock_clean):
        result = run_pipeline("9+5=17")
        assert result["goal"] == "check if true"
        assert result["answer"] == "False"
        assert result["verified_answer"] == "False"


if __name__ == "__main__":
    unittest.main()
