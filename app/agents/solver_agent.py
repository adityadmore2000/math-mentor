from app.llm import solve_steps
from app.schemas import SolutionStructure


class SolverAgent:
    def run(self, expression: str, verifier_feedback: str | None = None) -> SolutionStructure:
        return solve_steps(expression, verifier_feedback=verifier_feedback)

