# 🧠 Math Mentor — LLM + Tool-Based Math Reasoning System

Math Mentor is a minimal **LLM + SymPy** system for solving math problems with verification. The LLM produces structured reasoning, SymPy recomputes deterministically, and the pipeline returns a structured result suitable for a UI or API.

---

## 🚀 What It Does

```
User Input
   ↓
Parser → structured problem (clean expression + goal)
   ↓
Solver → step-by-step solution + a computable final form
   ↓
Verifier → recompute with SymPy + compare (+ retry / ask user)
   ↓
Explainer → student-friendly explanation
```

---

## 🧪 Usage

```python
from app.pipeline import run_pipeline

print(run_pipeline("2x + 5 = 15"))
```

`run_pipeline()` returns a dict (a `PipelineResult`-shaped payload) with fields like `status`, `steps`, `verified_answer`, and `explanation`.

---

## ⚙️ Setup

```bash
python3 -m pip install -r requirements.txt
```

### LLM configuration

**OpenAI (default)**

- Set `OPENAI_API_KEY`
- Optional: `OPENAI_MODEL`

**Ollama (local)**

- Set `LLM_PROVIDER=ollama`
- Set `OLLAMA_MODEL` (example: `llama3.1:8b`)
- Optional: `OLLAMA_HOST` (default: `http://localhost:11434`)

---

## 🧩 Architecture (Current)

The system is split into four responsibilities:

- **Parser**: cleans the user’s input, extracts a clear mathematical representation, and detects ambiguity early.
- **Solver**: generates solution steps and a final form that SymPy can evaluate.
- **Verifier**: recomputes deterministically with SymPy and acts as the correctness gate.
- **Explainer**: turns the verified result into a student-friendly explanation.

An orchestrator ties these parts together, including retry logic (when the solver and verifier disagree) and “ask for clarification” behavior (when the input or computation is not reliable).

---

## 🧭 Phases (Milestones)

These phases describe the behavior of the system at each milestone. They’re written so you can paste them into ChatGPT and it can quickly understand what the project currently does, what it returns, and what failure modes exist.

### Phase 1 — End-to-end pipeline (foundation)

Goal: prove the core loop works end-to-end: raw input → LLM reasoning → SymPy compute → explanation.

What “working” means in Phase 1:

- The system accepts a raw math prompt (expression or equation).
- The LLM standardizes the prompt (e.g., makes multiplication explicit) and proposes solution steps.
- SymPy computes the final answer deterministically from the proposed final form.
- The system returns a readable explanation as a single text output.

Why it matters: it validates the “LLM proposes / tool verifies” pattern before adding schemas and modular agents.

### Phase 2 — Structured outputs + deterministic edge-case handling

Goal: make the system debuggable and reliable by enforcing a schema contract and returning structured artifacts.

What “working” means in Phase 2:

- The system returns a **structured result** (a dict) with the full trace: problem summary, steps, solver answer, verified answer, and explanation.
- LLM outputs are constrained to strict structured data and validated, reducing “almost JSON” failures.
- Deterministic edge-cases are handled explicitly (e.g., constant equations like `9+5=17` are treated as a truth check rather than “solve for x”).

Why it matters: once inputs/outputs are structured, you can log, test, and build UI/API layers without guessing what the model meant.

### Phase 3 — Real “agents” + HITL + stronger verification

Goal: modular responsibilities and production behavior (without over-engineering).

What “working” means in Phase 3 (current behavior):

- The pipeline is explicitly modular (Parser / Solver / Verifier / Explainer), so each part has a single responsibility.
- The system has **explicit outcomes** instead of “always answer”:
  - **OK**: verified answer is produced and explained.
  - **Mismatch**: the solver’s claim conflicts with SymPy; the system can retry with feedback once (configurable).
  - **Need clarification (HITL)**: the system pauses and asks the user to clarify when input is ambiguous or the computation cannot be trusted.
  - **Error**: computation/verification fails in a way that can’t be recovered automatically.
- Ambiguity handling is first-class: the system prefers to ask questions rather than guess on messy input (e.g., OCR artifacts or incomplete expressions).
- Verification is stricter: it recomputes with SymPy and normalizes results before comparing; it also supports multi-equation inputs.
- The LLM backend is swappable (OpenAI by default; Ollama supported) without changing the behavior or output shape.

Why it matters: most failures in tool-augmented math systems are format/ambiguity/domain issues—Phase 3 isolates those concerns and makes failure modes explicit (`need_clarification`, retry on mismatch, etc.).

---

## 🚧 Next Phases (Roadmap)

- Phase 4 → RAG for math knowledge
- Phase 5 → HITL + confidence scoring
- Phase 6 → Memory layer
