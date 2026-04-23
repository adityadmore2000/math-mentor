from sympy import Eq, solve, symbols, sympify


def compute_answer(expr: str):
    try:
        if not isinstance(expr, str):
            return "Could not compute"

        normalized = expr.strip().replace("^", "**")
        if not normalized:
            return "Could not compute"

        x = symbols("x")

        if "=" in normalized:
            lhs_text, rhs_text = normalized.split("=", 1)
            lhs_text = lhs_text.strip()
            rhs_text = rhs_text.strip()

            if not lhs_text or not rhs_text:
                return "Could not compute"

            lhs = sympify(lhs_text)
            rhs = sympify(rhs_text)

            if lhs == x:
                return [rhs]

            equation = Eq(lhs, rhs)
            return solve(equation, x)

        return sympify(normalized)
    except Exception:
        return "Could not compute"

