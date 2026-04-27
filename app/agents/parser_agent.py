from app.errors import NeedClarification
from app.llm import clean_problem
from app.schemas import ProblemStructure


class ParserAgent:
    def run(self, user_input: str) -> ProblemStructure:
        stripped = user_input.strip()
        if not stripped:
            raise NeedClarification("Please paste the full math problem (the input was empty).")

        if _looks_like_unclear_ocr(stripped):
            raise NeedClarification(
                "I may be seeing OCR/scan artifacts. Can you re-type the expression clearly (or upload a clearer image)?"
            )

        problem = clean_problem(stripped)
        ambiguity = _ambiguity_reason(problem)
        if ambiguity:
            raise NeedClarification(ambiguity, problem=problem)
        return problem

def _looks_like_unclear_ocr(text: str) -> bool:
    if "�" in text:
        return True
    if not text.isprintable():
        return True
    if text.count("?") >= 2:
        return True
    return False


def _has_balanced_parens(expr: str) -> bool:
    depth = 0
    for ch in expr:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def _ambiguity_reason(problem: ProblemStructure) -> str | None:
    expr = problem.expression.strip()
    if not expr:
        return "I couldn't extract a valid expression. Can you re-type the exact equation/expression?"
    if not _has_balanced_parens(expr):
        return "The expression looks incomplete (unbalanced parentheses). Can you confirm the exact expression?"

    # Missing variables / unclear goal.
    goal = problem.goal.lower()
    if "solve" in goal and not any(ch.isalpha() for ch in expr):
        return (
            "This looks like a 'solve' problem, but I don't see any variables in the expression. "
            "Which variable should I solve for (e.g., x)?"
        )

    # Very basic sanity for equations.
    if "=" in expr:
        lhs, rhs = (part.strip() for part in expr.split("=", 1))
        if not lhs or not rhs:
            return "The equation seems incomplete (missing LHS or RHS). Can you re-type it?"

    return None
