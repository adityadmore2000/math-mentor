from app.llm import explain_solution


class ExplainerAgent:
    def run(self, steps: list[str], final_answer: str) -> str:
        return explain_solution(steps, final_answer)

