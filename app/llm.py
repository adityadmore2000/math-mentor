import json
import os
import socket
import urllib.error
import urllib.request

from dotenv import load_dotenv

from app.schemas import ProblemStructure, SolutionStructure

load_dotenv()


def _parse_structured_response(content: str, model):
    normalized = content.strip()
    if normalized.startswith("```"):
        normalized = normalized.removeprefix("```json").removeprefix("```").strip()
        if normalized.endswith("```"):
            normalized = normalized.removesuffix("```").strip()

    data = json.loads(normalized)
    if "answer" in data and not isinstance(data["answer"], str):
        data["answer"] = str(data["answer"])
    if "final_expression" in data and not isinstance(data["final_expression"], str):
        if isinstance(data["final_expression"], list):
            data["final_expression"] = ";".join(str(item).strip() for item in data["final_expression"])
        else:
            data["final_expression"] = str(data["final_expression"])
    if "steps" in data:
        data["steps"] = [str(step) for step in data["steps"]]
    if "expression" in data and not isinstance(data["expression"], str):
        if isinstance(data["expression"], list):
            data["expression"] = ";".join(str(item).strip() for item in data["expression"])
        else:
            data["expression"] = str(data["expression"])
    return model.model_validate(data)


def _provider() -> str:
    return os.getenv("LLM_PROVIDER", "openai").strip().lower()


def _openai_response_text(*, system_prompt: str, user_content: str) -> str:
    try:
        from openai import OpenAI
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("OpenAI provider selected but the `openai` package is not installed.") from exc

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        temperature=0,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    )
    return response.output_text


def _ollama_response_text(*, system_prompt: str, user_content: str) -> str:
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    timeout_s = float(os.getenv("OLLAMA_TIMEOUT", "90"))

    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "options": {"temperature": 0},
    }

    req = urllib.request.Request(
        f"{host}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except socket.timeout as exc:
        raise RuntimeError(
            "Ollama request timed out. This often happens on the first request while a large model is loading. "
            "Try warming the model with `ollama run <model> \"hi\"`, switching to a smaller model, "
            "or increasing `OLLAMA_TIMEOUT` (seconds) in your environment."
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "Ollama provider selected but the Ollama server is not reachable. "
            "Start it (e.g. `ollama serve`) and ensure OLLAMA_HOST is correct."
        ) from exc

    message = (data or {}).get("message") or {}
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("Ollama returned an empty response.")
    return content


def _llm_text(*, system_prompt: str, user_content: str) -> str:
    provider = _provider()
    if provider == "ollama":
        return _ollama_response_text(system_prompt=system_prompt, user_content=user_content)
    if provider == "openai":
        return _openai_response_text(system_prompt=system_prompt, user_content=user_content)
    raise ValueError(f"Unknown LLM_PROVIDER: {provider!r} (expected 'openai' or 'ollama').")


def clean_problem(user_input: str) -> ProblemStructure:
    system_prompt = (
        "You convert raw math problems into strict JSON.\n"
        "Return only valid JSON with exactly these keys:\n"
        "problem, topic, expression, goal\n"
        "Rules:\n"
        "- Always return valid JSON.\n"
        "- Make multiplication explicit: 2x -> 2*x.\n"
        "- Standardize operators consistently: use ** for exponents.\n"
        "- If the input is a word problem, introduce variables and translate it into equations.\n"
        "- For systems of equations, put them in ONE string separated by semicolons (;).\n"
        "- If the input is an equation (single variable), set topic to \"algebra\" and goal to \"solve\".\n"
        "- If the input is a system, set topic to \"algebra\" and goal to \"solve system\".\n"
        "- If the input is an equation with no variables, set topic to \"arithmetic\" and goal to \"check if true\".\n"
        "- If the input is an arithmetic expression, set topic to \"arithmetic\" and goal to \"evaluate\".\n"
        "- Keep currency/units out of the expression (e.g., $5.13 -> 5.13).\n"
        "- Do not include markdown, explanations, or extra text."
    )

    def _call_llm() -> ProblemStructure:
        text = _llm_text(system_prompt=system_prompt, user_content=user_input)
        return _parse_structured_response(text, ProblemStructure)

    try:
        return _call_llm()
    except Exception:
        try:
            return _call_llm()
        except Exception as exc:
            raise exc


def solve_steps(expression: str, verifier_feedback: str | None = None) -> SolutionStructure:
    system_prompt = (
        "You are a math tutor.\n"
        "Given a math expression or equation, return strict JSON with exactly these keys:\n"
        "steps, final_expression, answer\n"
        "Rules:\n"
        "- Output only valid JSON.\n"
        "- steps must be a JSON array of short strings.\n"
        "- final_expression must be directly computable by SymPy.\n"
        "- If the input is a system of equations, keep final_expression as the system (same equations), not assignments.\n"
        "- answer should be the final answer (for systems: variable assignments like \"x=1, y=2\").\n"
        "- Do not include markdown fences or extra commentary."
    )

    user_content = expression
    if verifier_feedback:
        user_content = f"{expression}\n\nVerifier feedback:\n{verifier_feedback}"

    text = _llm_text(system_prompt=system_prompt, user_content=user_content)
    return _parse_structured_response(text, SolutionStructure)


def explain_solution(steps: list[str], answer: str) -> str:
    system_prompt = (
        "You are a patient math mentor.\n"
        "Turn the provided solution steps and final answer into a clear, simple, "
        "student-friendly explanation.\n"
        "Keep the explanation readable and concise.\n"
        "Do not include markdown code fences."
    )

    steps_text = "\n".join(f"{index}. {step}" for index, step in enumerate(steps, start=1))
    user_prompt = f"Steps:\n{steps_text}\n\nAnswer:\n{answer}"

    return _llm_text(system_prompt=system_prompt, user_content=user_prompt).strip()
