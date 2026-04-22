import json
import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

def clean_problem(user_input: str) -> dict:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_prompt = (
        "You convert raw math problems into strict JSON.\n"
        "Return only valid JSON with exactly these keys:\n"
        "type, expression, goal\n"
        "Rules:\n"
        "- Always return valid JSON.\n"
        "- Make multiplication explicit: 2x -> 2*x.\n"
        "- Standardize operators consistently: use ** for exponents.\n"
        '- If the input is an equation, set type to "equation" and goal to "solve for x".\n'
        '- If the input is an arithmetic expression, set type to "arithmetic" and goal to "evaluate".\n'
        "- Do not include markdown, explanations, or extra text."
    )

    def _call_llm() -> dict:
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            temperature=0,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
        )
        return json.loads(response.output_text.strip())

    try:
        return _call_llm()
    except Exception:
        try:
            return _call_llm()
        except Exception as exc:
            raise exc


def solve_steps(expression: str) -> tuple[str, str]:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_prompt = (
        "You are a math tutor.\n"
        "Given a math expression or equation, return the result in exactly this format:\n\n"
        "Steps:\n"
        "1. ...\n"
        "2. ...\n\n"
        "Final expression:\n"
        "...\n\n"
        "Rules:\n"
        "- Output only those two sections.\n"
        "- Keep the reasoning concise and step-by-step.\n"
        "- The final expression must be directly computable by SymPy.\n"
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

    content = response.output_text.strip()
    if "Final expression:" not in content:
        raise ValueError("Missing 'Final expression:' in model output")

    steps, final_expression = content.split("Final expression:", 1)
    return steps.strip(), final_expression.strip()


def explain_solution(steps: str, answer) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_prompt = (
        "You are a patient math mentor.\n"
        "Turn the provided solution steps and final answer into a clear, simple, "
        "student-friendly explanation.\n"
        "Keep the explanation readable and concise.\n"
        "Do not include markdown code fences."
    )

    user_prompt = f"Steps:\n{steps}\n\nAnswer:\n{answer}"

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        temperature=0,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.output_text.strip()

