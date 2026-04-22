# Math Mentor

# 🧠 Math Mentor — LLM + Tool-Based Math Reasoning System

A minimal, production-style AI system that solves math problems using:

* 🧠 LLM for reasoning
* ⚙️ SymPy for exact computation
* 🔗 Structured pipeline design

---

## 🚀 Overview

This project demonstrates a **clean LLM-to-tool pipeline**:

```
User Input
   ↓
LLM → Problem Structuring
   ↓
LLM → Step-by-step Solution
   ↓
SymPy → Exact Computation
   ↓
LLM → Final Explanation
```

Unlike typical LLM demos, this system:

* separates reasoning from computation
* ensures deterministic answers
* is designed for extensibility (agents, RAG, HITL)

---

## 🎯 Phase 1 Goal

Build a **reliable, debuggable end-to-end pipeline** — not a complex AI system.

Key outcomes:

* Structured LLM outputs
* Tool-verified answers
* Modular architecture

---

## 📁 Project Structure

```
app/
├── llm.py          # LLM reasoning layer
├── math_tool.py    # SymPy-based computation
├── pipeline.py     # Orchestration logic
```

---

## 🧠 How It Works

### Input

```
2x + 5 = 15
```

### Output

```
Steps:
1. Subtract 5 from both sides
2. Simplify
3. Divide both sides

Final Answer: x = 5
```

---

## 🧪 Usage

### Run via Python

```python
from app.pipeline import run_pipeline

print(run_pipeline("2x + 5 = 15"))
```

---

## ⚙️ Tech Stack

* Python 3.10+
* OpenAI API
* SymPy

---

## 🧩 Design Principles

* **Separation of concerns**

  * LLM → reasoning
  * Python → computation

* **Determinism**

  * No randomness in outputs

* **Modularity**

  * Each component independently testable

---

## ⚠️ Phase 1 Constraints

This project intentionally avoids:

* ❌ Agents
* ❌ RAG (Retrieval Augmented Generation)
* ❌ Memory systems
* ❌ Human-in-the-loop

Focus is on building a **strong foundation first**.

---

## 🚧 Future Roadmap

* Phase 2 → Agent-based architecture
* Phase 3 → Verifier system
* Phase 4 → RAG for math knowledge
* Phase 5 → HITL + confidence scoring
* Phase 6 → Memory layer

---

## 🎯 Why This Matters

Most AI projects:

* rely entirely on LLM output

This system:

* verifies answers using computation
* reduces hallucination risk
* mirrors real-world AI system design

---

## 👨‍💻 Author

Built as part of an AI engineering exercise focused on:

* LLM systems design
* tool-augmented reasoning
* production-style pipelines
