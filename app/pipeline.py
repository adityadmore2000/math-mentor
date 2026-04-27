def run_pipeline(user_input: str) -> dict:
    from app.orchestrator import run_orchestrator

    return run_orchestrator(user_input)
