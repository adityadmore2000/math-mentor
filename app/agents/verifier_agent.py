from __future__ import annotations

from app.math_tool import compute_answer
from app.schemas import ProblemStructure, SolutionStructure, VerifierResult


def _stringify_tool_result(value) -> str:
    if isinstance(value, dict):
        try:
            items = sorted(value.items(), key=lambda kv: str(kv[0]))
        except Exception:
            items = list(value.items())
        parts = [f"{key}={val}" for key, val in items]
        return "{" + ", ".join(parts) + "}"
    if isinstance(value, (list, tuple, set)):
        # Stable representation for comparisons/logging.
        items = [_stringify_tool_result(item) for item in value]
        if not items:
            return "[]"
        try:
            items = sorted(items)
        except Exception:
            pass
        return ", ".join(items)
    return str(value)


def _canonicalize_answer(text: str) -> str | None:
    result = compute_answer(text)
    if result == "Could not compute":
        return None
    if isinstance(result, bool):
        return "True" if result else "False"
    return _stringify_tool_result(result)


def _try_constant_equation_truth(expression: str) -> str | None:
    # Deterministically evaluate equations like "9+5=17" (no variables).
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

    try:
        truth = bool(lhs.equals(rhs))
    except Exception:
        truth = bool(lhs == rhs)

    return "True" if truth else "False"


def _looks_like_system(expression: str) -> bool:
    # Heuristic: multiple equations separated by common delimiters.
    if "=" not in expression:
        return False
    return any(sep in expression for sep in (";", ",", "\n"))


def _try_parse_assignments(text: str) -> dict[str, str] | None:
    # Parse "x=1, y=-1, z=2" into a dict. Keep values as strings for stable comparison.
    parts = [p.strip() for p in text.split(",") if p.strip()]
    if not parts:
        return None
    assignments: dict[str, str] = {}
    for part in parts:
        if "=" not in part:
            return None
        lhs, rhs = (s.strip() for s in part.split("=", 1))
        if not lhs or not rhs:
            return None
        assignments[lhs] = rhs
    return assignments


class VerifierAgent:
    def run(self, problem: ProblemStructure, solution: SolutionStructure) -> VerifierResult:
        constant_truth = _try_constant_equation_truth(problem.expression)
        if constant_truth is not None:
            return VerifierResult(status="ok", verified_answer=constant_truth)

        if _looks_like_system(problem.expression):
            # Prefer the solver's computable form (often includes explicit multiplication),
            # but fall back to the parsed problem expression if needed.
            if _try_parse_assignments(solution.final_expression) is not None:
                verified = _canonicalize_answer(problem.expression)
            else:
                verified = _canonicalize_answer(solution.final_expression)
                if verified is None:
                    verified = _canonicalize_answer(problem.expression)
        else:
            verified = _canonicalize_answer(solution.final_expression)
        if verified is None:
            return VerifierResult(
                status="need_clarification",
                verified_answer="Could not compute",
                clarification_question="I couldn't compute the final expression reliably. Can you confirm the exact expression/equation?",
            )

        parsed = _try_parse_assignments(solution.answer)
        if parsed is not None:
            solver_claim = _stringify_tool_result(parsed)
        else:
            solver_claim = _canonicalize_answer(solution.answer)
        if solver_claim is None:
            # We can still trust the tool verification even if the model's "answer" isn't parseable by the tool.
            return VerifierResult(status="ok", verified_answer=verified)
        if solver_claim == verified:
            return VerifierResult(status="ok", verified_answer=verified)

        # If solver_claim couldn't be parsed, or it's different: treat as mismatch and provide feedback.
        feedback = (
            f"Tool verification disagrees.\n"
            f"- Verified (tool): {verified}\n"
            f"- Your answer: {solution.answer}\n"
            f"Return corrected steps and a final_expression that matches the verified result."
        )
        return VerifierResult(status="mismatch", verified_answer=verified, feedback=feedback)
