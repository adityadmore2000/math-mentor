import json
import os

from dotenv import load_dotenv
from openai import OpenAI

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
        data["final_expression"] = str(data["final_expression"])
    if "steps" in data:
        data["steps"] = [str(step) for step in data["steps"]]
    return model.model_validate(data)


def clean_problem(user_input: str) -> ProblemStructure:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_prompt = (
        "You convert raw math problems into strict JSON.\n"
        "Return only valid JSON with exactly these keys:\n"
        "problem, topic, expression, goal\n"
        "Rules:\n"
        "- Always return valid JSON.\n"
        "- Make multiplication explicit: 2x -> 2*x.\n"
        "- Standardize operators consistently: use ** for exponents.\n"
        '- If the input is an equation, set topic to "algebra" and goal to "solve for x".\n'
        '- If the input is an equation with no variables, set topic to "arithmetic" and goal to "check if true".\n'
        '- If the input is an arithmetic expression, set topic to "arithmetic" and goal to "evaluate".\n'
        "- Do not include markdown, explanations, or extra text."
    )

    def _call_llm() -> ProblemStructure:
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            temperature=0,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
        )
        return _parse_structured_response(response.output_text, ProblemStructure)

    try:
        return _call_llm()
    except Exception:
        try:
            return _call_llm()
        except Exception as exc:
            raise exc


def solve_steps(expression: str) -> SolutionStructure:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_prompt = (
        "You are a math tutor.\n"
        "Given a math expression or equation, return strict JSON with exactly these keys:\n"
        "steps, final_expression, answer\n"
        "Rules:\n"
        "- Output only valid JSON.\n"
        "- steps must be a JSON array of short strings.\n"
        "- final_expression must be directly computable by SymPy.\n"
        "- answer should be the model's final answer for the expression.\n"
        "- Do not include markdown fences or extra commentary."
    )

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        temperature=0,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": expression},
        ],
    )

    return _parse_structured_response(response.output_text, SolutionStructure)


def explain_solution(steps: list[str], answer: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_prompt = (
        "You are a patient math mentor.\n"
        "Turn the provided solution steps and final answer into a clear, simple, "
        "student-friendly explanation.\n"
        "Keep the explanation readable and concise.\n"
        "Do not include markdown code fences."
    )

    steps_text = "\n".join(f"{index}. {step}" for index, step in enumerate(steps, start=1))
    user_prompt = f"Steps:\n{steps_text}\n\nAnswer:\n{answer}"

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        temperature=0,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.output_text.strip()
