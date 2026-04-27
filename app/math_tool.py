from __future__ import annotations

from sympy import Eq, denom, solve, symbols, sympify, together


def _split_top_level(text: str, separators: set[str]) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    for ch in text:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(0, depth - 1)

        if depth == 0 and ch in separators:
            part = "".join(buf).strip()
            if part:
                parts.append(part)
            buf = []
            continue
        buf.append(ch)

    last = "".join(buf).strip()
    if last:
        parts.append(last)
    return parts


def compute_answer(expr: str):
    try:
        if isinstance(expr, list):
            equations = [str(item).strip() for item in expr if str(item).strip()]
            if not equations:
                return "Could not compute"
            return _solve_equation_system(equations)

        if not isinstance(expr, str):
            return "Could not compute"

        normalized = expr.strip().replace("^", "**")
        if not normalized:
            return "Could not compute"

        if any(sep in normalized for sep in (";", ",", "\n")):
            equations = _split_top_level(normalized, separators={";", ",", "\n"})
            if len(equations) > 1 and all("=" in part for part in equations):
                return _solve_equation_system(equations)

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
            solutions = solve(equation, x)
            if not isinstance(solutions, (list, tuple, set)):
                return solutions
            return _filter_solutions(equation, x, list(solutions))

        return sympify(normalized)
    except Exception:
        return "Could not compute"


def _solve_equation_system(equations: list[str]):
    try:
        eqs = []
        symbols_set = set()
        for text in equations:
            if "=" not in text:
                return "Could not compute"
            lhs_text, rhs_text = text.split("=", 1)
            lhs = sympify(lhs_text.strip())
            rhs = sympify(rhs_text.strip())
            eq = Eq(lhs, rhs)
            eqs.append(eq)
            symbols_set |= set(eq.free_symbols)

        if not symbols_set:
            # Constant-only system: all equations must be true.
            all_true = all(bool(eq.lhs.equals(eq.rhs)) for eq in eqs)
            return all_true

        unknowns = sorted(symbols_set, key=lambda s: s.name)
        # dict=True gives stable structured results.
        result = solve(eqs, unknowns, dict=True)
        if isinstance(result, (list, tuple, set)) and not result:
            return []
        return result
    except Exception:
        return "Could not compute"


def _is_defined_at(expr, symbol, value) -> bool:
    try:
        d = denom(together(expr))
        d_sub = d.subs(symbol, value)
        if d_sub == 0:
            return False
        if getattr(d_sub, "is_zero", None) is True:
            return False
    except Exception:
        # Best-effort: if we can't analyze, don't reject.
        return True
    return True


def _equation_holds(eq: Eq, symbol, value) -> bool:
    try:
        lhs = eq.lhs.subs(symbol, value)
        rhs = eq.rhs.subs(symbol, value)
        diff = (lhs - rhs)
        if diff == 0:
            return True
        if getattr(diff, "is_zero", None) is True:
            return True
        try:
            return bool(diff.equals(0))
        except Exception:
            return False
    except Exception:
        return False


def _filter_solutions(eq: Eq, symbol, solutions: list):
    filtered = []
    seen = set()
    for sol in solutions:
        # Prefer real solutions for typical school-math unless SymPy is unsure.
        if getattr(sol, "is_real", None) is False:
            continue
        if not _is_defined_at(eq.lhs, symbol, sol) or not _is_defined_at(eq.rhs, symbol, sol):
            continue
        if not _equation_holds(eq, symbol, sol):
            continue
        key = str(sol)
        if key in seen:
            continue
        seen.add(key)
        filtered.append(sol)
    return filtered
