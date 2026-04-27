import unittest
from unittest.mock import patch

from app.agents.verifier_agent import VerifierAgent
from app.errors import NeedClarification
from app.orchestrator import run_orchestrator
from app.schemas import ProblemStructure, SolutionStructure, VerifierResult


class FakeParser:
    def __init__(self, problem: ProblemStructure):
        self.problem = problem

    def run(self, user_input: str) -> ProblemStructure:
        return self.problem


class FakeSolver:
    def __init__(self, solutions: list[SolutionStructure]):
        self.solutions = solutions
        self.calls: list[str | None] = []

    def run(self, expression: str, verifier_feedback: str | None = None) -> SolutionStructure:
        self.calls.append(verifier_feedback)
        return self.solutions[min(len(self.calls) - 1, len(self.solutions) - 1)]


class FakeVerifier:
    def __init__(self, results: list[VerifierResult]):
        self.results = results
        self.calls = 0

    def run(self, problem: ProblemStructure, solution: SolutionStructure) -> VerifierResult:
        self.calls += 1
        return self.results[min(self.calls - 1, len(self.results) - 1)]


class FakeExplainer:
    def run(self, steps: list[str], final_answer: str) -> str:
        return f"Answer: {final_answer}"


class ClarifyingParser:
    def run(self, user_input: str) -> ProblemStructure:
        raise NeedClarification("Need variable name to solve.")


class TestOrchestrator(unittest.TestCase):
    def test_ok_path_returns_verified_answer(self):
        problem = ProblemStructure(
            problem="2x + 5 = 15",
            topic="algebra",
            expression="2*x + 5 = 15",
            goal="solve for x",
        )
        solution = SolutionStructure(
            steps=["Subtract 5.", "Divide by 2."],
            final_expression="x = 5",
            answer="x = 5",
        )
        verifier = FakeVerifier([VerifierResult(status="ok", verified_answer="5")])

        result = run_orchestrator(
            "ignored",
            parser=FakeParser(problem),
            solver=FakeSolver([solution]),
            verifier=verifier,
            explainer=FakeExplainer(),
        )

        assert result["status"] == "ok"
        assert result["verified_answer"] == "5"
        assert result["retries"] == 0
        assert result["run_id"]

    def test_mismatch_triggers_retry_with_feedback(self):
        problem = ProblemStructure(
            problem="2 + 3",
            topic="arithmetic",
            expression="2 + 3",
            goal="evaluate",
        )

        wrong = SolutionStructure(
            steps=["Compute."],
            final_expression="2 + 3",
            answer="6",
        )
        corrected = SolutionStructure(
            steps=["Compute."],
            final_expression="2 + 3",
            answer="5",
        )

        feedback = "Tool verification disagrees. Return corrected output."
        verifier = FakeVerifier(
            [
                VerifierResult(status="mismatch", verified_answer="5", feedback=feedback),
                VerifierResult(status="ok", verified_answer="5"),
            ]
        )

        solver = FakeSolver([wrong, corrected])
        result = run_orchestrator(
            "ignored",
            max_retries=1,
            parser=FakeParser(problem),
            solver=solver,
            verifier=verifier,
            explainer=FakeExplainer(),
        )

        assert result["status"] == "ok"
        assert result["retries"] == 1
        assert solver.calls == [None, feedback]

    def test_need_clarification_returns_structured_response(self):
        problem = ProblemStructure(
            problem="weird",
            topic="unknown",
            expression="(2+",
            goal="evaluate",
        )
        solution = SolutionStructure(steps=["Try."], final_expression="(2+", answer="(2+")
        verifier = FakeVerifier(
            [
                VerifierResult(
                    status="need_clarification",
                    verified_answer="Could not compute",
                    clarification_question="Confirm the exact expression.",
                )
            ]
        )

        result = run_orchestrator(
            "ignored",
            parser=FakeParser(problem),
            solver=FakeSolver([solution]),
            verifier=verifier,
            explainer=FakeExplainer(),
        )

        assert result["status"] == "need_clarification"
        assert "Confirm the exact expression" in result["explanation"]

    def test_parser_can_trigger_hitl_need_clarification(self):
        result = run_orchestrator(
            "2 + ?",
            parser=ClarifyingParser(),
            solver=FakeSolver(
                [
                    SolutionStructure(
                        steps=["N/A"],
                        final_expression="0",
                        answer="0",
                    )
                ]
            ),
            verifier=FakeVerifier([VerifierResult(status="error", verified_answer="Could not compute")]),
            explainer=FakeExplainer(),
        )

        assert result["status"] == "need_clarification"
        assert "Need variable name" in result["explanation"]
        assert result["steps"] == []


class TestVerifierAgent(unittest.TestCase):
    def test_constant_equation_is_checked(self):
        verifier = VerifierAgent()
        problem = ProblemStructure(
            problem="9+5=17",
            topic="arithmetic",
            expression="9+5=17",
            goal="check if true",
        )
        # Solution content doesn't matter for constant truth checks.
        solution = SolutionStructure(steps=["N/A"], final_expression="9+5=17", answer="False")
        result = verifier.run(problem, solution)
        assert result.status == "ok"
        assert result.verified_answer == "False"

    def test_system_of_equations_is_supported(self):
        verifier = VerifierAgent()
        problem = ProblemStructure(
            problem="system",
            topic="algebra",
            expression="x-2*y+3*z=9;-x+3*y-z=-6;2*x-5*y+5*z=17",
            goal="solve system",
        )
        # Verifier trusts the tool result even if `answer` is not tool-parseable.
        solution = SolutionStructure(
            steps=["Solve the system."],
            final_expression="x-2*y+3*z=9;-x+3*y-z=-6;2*x-5*y+5*z=17",
            answer="x=1, y=-1, z=2",
        )
        result = verifier.run(problem, solution)
        assert result.status == "ok"
        assert "x" in result.verified_answer

    def test_system_with_commas_is_supported_and_assignments_compare(self):
        verifier = VerifierAgent()
        problem = ProblemStructure(
            problem="system",
            topic="algebra",
            expression="x-2*y+3*z=9, -x+3*y-z=-6, 2*x-5*y+5*z=17",
            goal="solve system",
        )
        solution = SolutionStructure(
            steps=["Solve."],
            final_expression="x=1, y=2, z=3",
            answer="x=1, y=-1, z=2",
        )
        result = verifier.run(problem, solution)
        assert result.status == "ok"
        assert "x" in result.verified_answer


class TestParserHeuristics(unittest.TestCase):
    def test_word_problem_with_currency_is_not_blocked_as_ocr(self):
        from app.agents.parser_agent import ParserAgent

        agent = ParserAgent()
        stub = ProblemStructure(problem="p", topic="algebra", expression="x=1", goal="solve")
        with patch("app.agents.parser_agent.clean_problem", return_value=stub) as mocked:
            result = agent.run(
                "Michael buys two bags of chips for $5.13 and then buys another for $3.09. Find each cost."
            )
            assert result.expression == "x=1"
            mocked.assert_called_once()


if __name__ == "__main__":
    unittest.main()
