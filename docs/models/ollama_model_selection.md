# Ollama Model Selection For CodeGenOpt Agents

This document provides a hardware-aware and task-aware rationale for selecting
Ollama-compatible models for CodeGenOpt agents. It is intended for public
research documentation and should be updated as model availability, benchmark
evidence, or deployment hardware changes.

## Selection Criteria

Model selection considered the following factors:

- Task fit for each agent role.
- Publicly reported code-generation and instruction-following benchmarks.
- Local hardware constraints for CPU and lightweight GPU inference.
- Latency and memory requirements.
- Empirical behavior observed in exploratory local tests.
- Availability through Ollama-compatible model identifiers.

## Hardware Constraints

The local evaluation environment includes 32 GB RAM and a 4 GB dedicated GPU.
This favors small to medium models, especially quantized variants. Large models
can still be used through cloud inference backends when local latency or memory
constraints become limiting.

## Candidate Models

| Model | Primary strength | Notes |
| --- | --- | --- |
| `llama3:latest` | General reasoning, instruction following, multilingual prompting | Suitable for prompt rewriting, coordination, and explanatory tasks |
| `codellama:7b-instruct` | Code generation and code transformation | Suitable for generation, testing, and optimization agents |
| `deepseek-coder:6.7b-instruct` | Code-specialized generation | Useful as an alternative code model or robustness check |
| `mistral:7b` | General compact instruction model | Useful fallback for lightweight local inference |
| `gemma:2b` | Low-resource inference | Useful for constrained environments, but generally weaker for code-heavy tasks |

## Recommended Agent Assignments

| CodeGenOpt agent | Recommended model class | Rationale |
| --- | --- | --- |
| Prompt Engineer | General instruction model such as `llama3:latest` | Strong prompt rewriting and multilingual instruction following |
| Technical Translator | General instruction model with multilingual capability | Translation requires semantic preservation more than code synthesis |
| Code Generator | Code-specialized model such as `codellama:7b-instruct` | Code pretraining improves implementation quality |
| Code Optimizer | Code-specialized model such as `codellama:7b-instruct` | Refactoring and optimization benefit from code-focused training |
| Code Tester / Evaluator | Code-specialized model or general reasoning model | Test generation needs code understanding; evaluation may need explanatory reasoning |
| Coordinator | General instruction model | Orchestration requires instruction following and structured decision-making |

## Scientific Rationale

CodeGenOpt separates the code-generation workflow into specialized agents. This
supports assigning models according to the dominant task type:

- General instruction models are well suited to prompt reformulation,
  translation, coordination, and reporting.
- Code-specialized models are better suited to implementation, transformation,
  and test-oriented reasoning.
- Cloud-hosted models may be preferable for large-scale evaluation when local
  hardware creates unacceptable latency or memory limits.

## Reproducibility Guidance

When reporting experiments, record:

1. Model name and version/tag.
2. Inference backend: local Ollama, Ollama-compatible endpoint, or cloud backend.
3. Decoding parameters such as temperature, top-p, context window, and max output.
4. Hardware profile for local inference.
5. Whether translator and optimizer agents were enabled.

## References

- Meta Llama documentation: https://ai.meta.com/llama/
- Code Llama repository: https://github.com/facebookresearch/codellama
- DeepSeek-Coder repository: https://github.com/deepseek-ai/DeepSeek-Coder
- HumanEval benchmark context: https://paperswithcode.com/sota/code-generation-on-humaneval
- Mistral model announcement: https://mistral.ai/news/announcing-mistral-7b/
- Gemma documentation: https://ai.google.dev/gemma

## Maintenance Note

This recommendation is not fixed. Newer models should be adopted when they
provide better task performance, lower latency, improved reproducibility, or
better fit with the target deployment environment.
