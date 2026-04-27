from __future__ import annotations

import uuid

from app.agents.explainer_agent import ExplainerAgent
from app.agents.parser_agent import ParserAgent
from app.agents.solver_agent import SolverAgent
from app.agents.verifier_agent import VerifierAgent
from app.errors import NeedClarification
from app.schemas import PipelineResult


def run_orchestrator(
    user_input: str,
    *,
    max_retries: int = 1,
    parser: ParserAgent | None = None,
    solver: SolverAgent | None = None,
    verifier: VerifierAgent | None = None,
    explainer: ExplainerAgent | None = None,
) -> dict:
    run_id = str(uuid.uuid4())

    parser = parser or ParserAgent()
    solver = solver or SolverAgent()
    verifier = verifier or VerifierAgent()
    explainer = explainer or ExplainerAgent()

    try:
        problem = parser.run(user_input)
    except NeedClarification as exc:
        problem_struct = exc.problem
        result = PipelineResult(
            run_id=run_id,
            status="need_clarification",
            retries=0,
            problem=(problem_struct.problem if problem_struct else user_input),
            topic=(problem_struct.topic if problem_struct else ""),
            expression=(problem_struct.expression if problem_struct else ""),
            goal=(problem_struct.goal if problem_struct else ""),
            steps=[],
            final_expression="",
            answer="",
            verified_answer="Could not compute",
            explanation=exc.question,
        )
        return result.model_dump()

    retries = 0
    verifier_feedback: str | None = None

    while True:
        solution = solver.run(problem.expression, verifier_feedback=verifier_feedback)
        verification = verifier.run(problem, solution)

        if verification.status == "ok":
            final_answer = verification.verified_answer
            explanation = explainer.run(solution.steps, final_answer)
            result = PipelineResult(
                run_id=run_id,
                status="ok",
                retries=retries,
                problem=problem.problem,
                topic=problem.topic,
                expression=problem.expression,
                goal=problem.goal,
                steps=solution.steps,
                final_expression=solution.final_expression,
                answer=solution.answer,
                verified_answer=final_answer,
                explanation=explanation,
            )
            return result.model_dump()

        if verification.status == "need_clarification":
            # Provide a stable, structured response for HITL / UI.
            result = PipelineResult(
                run_id=run_id,
                status="need_clarification",
                retries=retries,
                problem=problem.problem,
                topic=problem.topic,
                expression=problem.expression,
                goal=problem.goal,
                steps=solution.steps,
                final_expression=solution.final_expression,
                answer=solution.answer,
                verified_answer=verification.verified_answer,
                explanation=verification.clarification_question or "Need clarification.",
            )
            return result.model_dump()

        if verification.status == "mismatch" and retries < max_retries:
            retries += 1
            verifier_feedback = verification.feedback
            continue

        # Mismatch with no retries left (or error): return structured failure.
        result = PipelineResult(
            run_id=run_id,
            status=verification.status,
            retries=retries,
            problem=problem.problem,
            topic=problem.topic,
            expression=problem.expression,
            goal=problem.goal,
            steps=solution.steps,
            final_expression=solution.final_expression,
            answer=solution.answer,
            verified_answer=verification.verified_answer,
            explanation=verification.feedback or "Verification failed.",
        )
        return result.model_dump()
