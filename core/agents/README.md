# Multi-Agent Code Generation System

This directory implements the core intelligent agents of the CodeGenOpt system—a modular, pipeline-based architecture for automated Python code generation and optimization using **free Small Language Models (SLMs) via Ollama**.

## 🔒 Privacy-First Design

All agents operate using **Ollama models** with complete data privacy protection:
- **Your data stays yours** — never trained on
- **Zero API costs** — all models freely available
- **Local & Cloud modes** — both maintain privacy per Ollama policy
- **Offline capable** — run entirely offline for mission-critical work

## Architecture Overview

The system follows a **sequential multi-agent pipeline** pattern where each agent specializes in a specific transformation stage:

```
Input (Natural Language) → TechnicalTranslator → PromptEngineer → CodeGenerator → CodeOptimizer → Output (Optimized Python Code)
```

All stages use **free Ollama SLMs** — no commercial LLM APIs required.

## Agent Modules

### 1. `coordinator.py` — Central Orchestrator
The `Coordinator` class serves as the primary workflow controller, managing:
- LLM initialization (shared or independent instances)
- Sequential pipeline execution with error handling
- Configuration management for local (Ollama) and cloud-hosted models
- Result aggregation and state tracking

**Key Features:**
- Configurable agent enablement (translator, optimizer)
- Robust error propagation with structured output
- Support for both unified and per-agent LLM configurations

### 2. `technical_translator.py` — Multilingual Normalization Agent
The `TechnicalTranslator` performs domain-aware translation of natural language inputs into standardized English technical descriptions.

**Responsibilities:**
- Cross-lingual normalization (Arabic/English input → English output)
- Technical terminology preservation
- Low-temperature generation (T=0.2) for deterministic output

### 3. `prompt_engineer.py` — Structured Specification Generator
The `PromptEngineer` transforms unstructured problem descriptions into validated JSON schemas using Pydantic models.

**Responsibilities:**
- Schema-compliant JSON generation via `ProblemSpec` model
- Automatic retry mechanism for parsing robustness
- Constraint extraction (function name, arguments, examples)

### 4. `code_generator.py` — Synthesis Agent
The `CodeGenerator` produces executable Python code from structured JSON specifications.

**Responsibilities:**
- Function signature synthesis
- Docstring generation with constraints and examples
- Markdown fence removal via post-processing
- Type-hint aware code generation

### 5. `code_optimizer.py` — Quality Assurance Agent
The `CodeOptimizer` applies industry-standard toolchain automation to improve code quality while preserving functional correctness.

**Optimization Pipeline:**
1. **autoflake** — Remove unused imports and variables
2. **isort** — Standardize import ordering (Black profile)
3. **autopep8** — Automated PEP8 compliance
4. **pyupgrade** — Python 3.10+ syntax modernization
5. **black** — Consistent code formatting
6. **mypy** — Static type checking

**Safety Guarantees:**
- Post-optimization AST validation
- Graceful degradation on tool failures
- Fallback to original code on syntax errors

## Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Modularity** | Each agent is self-contained with clear I/O contracts |
| **Composability** | Agents can be selectively enabled/disabled via `Coordinator` |
| **Observability** | Debug mode provides structured logging at each pipeline stage |
| **Resilience** | Error handling at agent boundaries prevents cascade failures |
| **Determinism** | Low temperature settings (T ≤ 0.2) for reproducible outputs |

## Dependencies

All agents utilize:
- **LangChain** for prompt templating and LLM orchestration
- **OllamaLLM** for local SLM inference
- **Pydantic** for schema validation
- **Standard Python toolchain** (autoflake, isort, autopep8, black, mypy, pyupgrade)

## Current System Status

| Agent | Status | Description |
|-------|--------|-------------|
| Coordinator | ✅ Active | Central pipeline orchestrator |
| TechnicalTranslator | ✅ Active | Multilingual input normalization |
| PromptEngineer | ✅ Active | JSON specification generation |
| CodeGenerator | ✅ Active | Python code synthesis |
| CodeOptimizer | ✅ Active | Toolchain-based quality enhancement |
