# Experimenting JEEBench on Different LLMs

**Questions**
1) What parameters to decide which LLM performs better on JEEBench


**_Note_**: DeepSeek-R1-Distill-Qwen-7B was chosen as sample model for designing the pipeline of testing LLMs on JEEBench dataset

## Experimenting JEEBench on "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"

- Tested the model on JEEBench math problems.
- Stored the results in csv file
- Viewed the dataset in colab notebook
- Converted to json for better representation.

### Store LLM response + metadata in dataset
- Following information was stored while performing inference.
```
Index(['problem_idx', 'description', 'type', 'gold', 'question', 'temperature',
       'solved', 'run_id', 'model', 'timestamp', 'raw_output', 'thinking',
       'extracted_answer', 'correct', 'latency_sec', 'has_boxed',
       'thinking_length', 'output_length', 'self_corrected',
       'constraint_checked', 'elimination_detected', 'approach'],
      dtype='object')
```


- JSON Schema for better understanding
```
[
  {
    "problem_idx": int,
    "description": string,
    "type": string,
    "gold": string,
    "question": string,
    "runs": {
      "<temperature>": {
        "solved": string,
        "run_id": string,
        "model": string,
        "timestamp": string,
        "raw_output": string,
        "thinking": string,
        "extracted_answer": string,
        "correct": boolean,
        "latency_sec": float,
        "has_boxed": boolean,
        "thinking_length": int,
        "output_length": int,
        "self_corrected": boolean,
        "constraint_checked": boolean,
        "elimination_detected": boolean,
        "approach": string
      }
    }
  }
]
```

