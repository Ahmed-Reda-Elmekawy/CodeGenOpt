# Ollama Local Model Serving

## Overview

Ollama is a local model-serving framework for running large language models on
developer or research hardware. In CodeGenOpt, Ollama is used as one possible
backend for local inference and for comparing local execution against cloud
model execution.

## Role In CodeGenOpt

Ollama supports:

- Local LLM inference for agent testing.
- Offline or privacy-preserving development workflows.
- Comparison of local and cloud inference modes.
- Reproducible model invocation through explicit model tags.

## Installation

Linux installation:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

For macOS and Windows, use the official installer from:

```text
https://ollama.com/download
```

## Common Commands

List locally available models:

```bash
ollama list
```

Download a model:

```bash
ollama pull llama3
```

Run a model interactively:

```bash
ollama run llama3
```

Run a one-shot prompt:

```bash
echo "Write a Python function to reverse a string." | ollama run llama3
```

Start the local API server:

```bash
ollama serve
```

Show model metadata:

```bash
ollama show llama3
```

## API Example

By default, Ollama exposes an API at `http://localhost:11434`.

```bash
curl http://localhost:11434/api/generate \
  -d '{"model": "llama3", "prompt": "Write a Python function to reverse a string."}'
```

## Python Integration

```python
from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3")
result = llm.invoke("Summarize CodeGenOpt in one paragraph.")
print(result)
```

## Code Generation Example

```python
from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3")
prompt = "Write a Python function that sorts integers using bubble sort."
code = llm.invoke(prompt)
print(code)
```

## Reproducibility Notes

When using Ollama for scientific evaluation, record:

- Model name and tag.
- Ollama version.
- Host hardware profile.
- Decoding parameters.
- Whether the run used CPU or GPU acceleration.
- Any prompt templates or post-processing applied by the pipeline.

## Limitations

- Local performance depends strongly on CPU, RAM, GPU memory, and quantization.
- Outputs may differ across model versions or decoding settings.
- Generated code must be tested before being treated as correct.

## References

- Ollama documentation: https://ollama.com/docs
- Ollama API reference: https://ollama.com/docs/api
- LangChain Ollama integration: https://python.langchain.com/docs/integrations/llms/ollama
