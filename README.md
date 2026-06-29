# 🚀 CodeGenOpt

An Intelligent Multi-Agent System for Programming Code Generation and Optimization using Private, Local Small Language Models (SLMs).

<div align="center">

**Developing an Intelligent System for Programming Code Generation and Optimization**

*Official Manuscript Replication Package & Academic Repository*

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![University](https://img.shields.io/badge/University-Mansoura%20University-blue.svg)](https://www.mans.edu.eg/)
[![Ollama](https://img.shields.io/badge/Powered%20by-Ollama-orange.svg)](https://ollama.com)
[![LangChain](https://img.shields.io/badge/Built%20with-LangChain-purple.svg)](https://langchain.com)

**Researcher:** Ahmed Reda Abd EL-Baset Ismail El-Mekawy
**Institution:** Mansoura University, Egypt
**Program:** Master's in AI Techniques in Education

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
- [Experimental Replication](#experimental-replication)
- [Academic Publication](#academic-publication)
- [License](#license)
- [Contact](#contact)

---

## 🎯 Overview

**CodeGenOpt** is an automated, privacy-first multi-agent system designed to generate, validate, and optimize Python source code starting from natural language problem descriptions.

By utilizing local Small Language Models (SLMs) via **Ollama** and orchestrating them through **LangChain**, CodeGenOpt delivers state-of-the-art code synthesis. It eliminates dependencies on external commercial APIs, ensuring data privacy and zero API execution costs. The system incorporates an automated post-generation optimization toolchain and validation pipeline, improving syntactic compliance and static typing correctness.

---

## ✨ Key Features

* **🔒 Privacy-First Design:** Operates entirely locally using Ollama. Zero leakage of research or proprietary code to external APIs.
* **🤖 Sequential Multi-Agent Orchestration:** Five specialized agent modules interact sequentially to translate, structure, generate, and optimize code.
* **🌍 Multilingual Domain Normalization:** Handles Arabic and English inputs, translating and normalizing them into precise English technical descriptions.
* **⚡ Automated Toolchain Optimization:** Integrates standard code quality tools (`autoflake`, `isort`, `autopep8`, `pyupgrade`, `black`, `mypy`) to ensure strict PEP8 compliance and type safety.
* **📊 Empirical Benchmark Suite:** Includes built-in interfaces for evaluating performance against standard datasets like `HumanEval` and replication data splits.

---

## 🏗️ System Architecture

CodeGenOpt operates as a pipeline of sequential agent modifications:

```
Input (Arabic/English NL)
      │
      ▼
┌────────────────────────────────────────────────────────┐
│ 1. TechnicalTranslator (Multilingual Normalization)    │
└─────────────────────┬──────────────────────────────────┘
                      │ English Technical Description
                      ▼
┌────────────────────────────────────────────────────────┐
│ 2. PromptEngineer (Pydantic JSON Spec Generator)      │
└─────────────────────┬──────────────────────────────────┘
                      │ Structured Schema Spec
                      ▼
┌────────────────────────────────────────────────────────┐
│ 3. CodeGenerator (Context/Docstring Aware Processor)   │
└─────────────────────┬──────────────────────────────────┘
                      │ Raw Python Code Block
                      ▼
┌────────────────────────────────────────────────────────┐
│ 4. CodeOptimizer (AST & Toolchain Formatter)           │
└─────────────────────┬──────────────────────────────────┘
                      │ Clean, PEP8 & Type-Checked Code
                      ▼
            Validated Output Code
```

### Agent Module Definitions

1. **`technical_translator.py` (Multilingual Normalization):**
   Translates input text from any language (e.g., Arabic) into clean technical English. Operates at a low temperature (T=0.2) to maintain translation fidelity.
2. **`prompt_engineer.py` (Specification Generator):**
   Transforms unstructured problem descriptions into structured specifications conforming to a strict Pydantic schema (`ProblemSpec`). Yields parameters, constraints, docstrings, examples, and expected exceptions.
3. **`code_generator.py` (Synthesis Agent):**
   Synthesizes compliant Python functions from the structured JSON specification. Strips Markdown formatting artifacts post-generation.
4. **`code_optimizer.py` (Quality & Compiler Assurance):**
   Runs the synthesized code through a sequential local optimization pipeline:
   * `autoflake`: Removes unused imports and variables safely.
   * `isort`: Organizes imports according to the Black style profile.
   * `autopep8`: Rectifies indentation and basic PEP8 spacing.
   * `pyupgrade`: Modernizes syntax to Python 3.10+.
   * `black`: Restructures code formatting rules strictly.
   * `mypy`: Performs static type checking and exports results.
5. **`coordinator.py` (Pipeline Central Controller):**
   Manages state variables, handles agent invocations, injects execution parameters (local and cloud model URLs), and catches exceptions gracefully.

---

## 🛠️ Installation

### Prerequisites

* **Python 3.12** or higher.
* **Ollama** installed on your system.
* GPU acceleration (recommended for local execution).

### Step-by-Step Setup

1. **Clone the Repository:**
   
   ```bash
   git clone https://github.com/Ahmed-Reda-Elmekawy/CodeGenOpt.git
   cd CodeGenOpt
   ```
2. **Initialize Virtual Environment:**
   
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Package Dependencies:**
   
   ```bash
   pip install -r requirements.txt
   ```
4. **Install System Formatting Tools:**
   Ensure formatting tools are installed globally or in your environment:
   
   ```bash
   pip install black autopep8 isort autoflake pyupgrade mypy
   ```
5. **Install HumanEval Benchmark Suite** (Required for running evaluation benchmarks):
   
   ```bash
   pip install git+https://github.com/openai/human-eval.git
   ```
6. **Pull Local LLM/SLM Models:**
   Download your target models using Ollama:
   
   ```bash
   ollama pull llama3
   ollama pull qwen2.5-coder
   ```

---

## 🚀 Usage & Execution Guide

The primary entry point of the CodeGenOpt system is the root-level `main.py` CLI script. It provides a robust, command-line interface to orchestrate the multi-agent generation pipeline, supporting single invocations, interactive shells, CPU overrides, and verbose logging of intermediate agent processes.

### 1. Command-Line Interface (CLI)

Run `main.py` directly from the bash terminal. The system accepts a problem description and runs the complete orchestration pipeline:

```bash
python main.py --problem "اكتب دالة بلغة بايثون للتحقق من الأعداد الأولية" --verbose
```

#### CLI Arguments Reference

| Argument | Shorthand | Type | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `--problem` | `-p` | `string` | *None* | Natural-language query or problem description to compile. (Mutually exclusive with `--interactive`) |
| `--interactive` | `-i` | `flag` | `False` | Starts an interactive warm REPL session. |
| `--model` | `-m` | `string` | `None` | Specifies the Ollama model to use locally (e.g., `llama3.2:3b`, `qwen3:0.6b`). |
| `--cpu` | *None* | `flag` | `False` | Forces CPU inference via Ollama, bypassing CUDA runtimes. |
| `--cloud` | *None* | `flag` | `False` | Routes requests to the cloud-hosted backend model (`qwen3-coder:480b-cloud`). |
| `--no-translator`| *None* | `flag` | `False` | Bypasses the `TechnicalTranslator` agent, passing the raw input prompt to downstream modules. |
| `--no-optimizer` | *None* | `flag` | `False` | Disables the `CodeOptimizer` pipeline, bypassing linting, type-checking, and formatting. |
| `--verbose` | `-v` | `flag` | `False` | Outputs logs and results of all intermediate pipeline agent stages. |
| `--debug` | *None* | `flag` | `False` | Enables low-level diagnostics and HTTP transport logging. |

#### Generation Examples

* **Standard Multilingual Code Generation (GPU Local llama3):**
  ```bash
  python main.py --problem "اكتب دالة بلغة بايثون للتحقق من الأعداد الأولية" --verbose
  ```

* **Targeting a lightweight model on CPU (No GPU/CUDA):**
  ```bash
  python main.py --problem "Write a Python function to sort a list of floats" --model llama3.2:3b --cpu --verbose
  ```

* **Baseline Study (Ablating Translator & Optimizer Agents):**
  ```bash
  python main.py --problem "Implement Dijkstra's algorithm" --no-translator --no-optimizer
  ```

---

### 2. Interactive Shell (REPL Mode)

To test multiple prompts back-to-back without incurring the overhead of reloading LLM model weights each time, start the interactive REPL shell:

```bash
python main.py --interactive --model llama3.2:3b --cpu -v
```

**Interactive Console:**
```text
============================================================
               CodeGenOpt — Interactive REPL Mode
   Provide engineering statements below. Type 'exit' to terminate.
============================================================

CodeGenOpt › Write a function to check if a word is palindrome.
```

---

### 3. Programmatic API Integration

You can also import and orchestrate the multi-agent pipeline inside custom Python scripts:

```python
from core.agents.coordinator import Coordinator

# Initialize orchestrator with targeted config
coordinator = Coordinator(
    use_translator=True,
    use_optimizer=True,
    cloud_llm=False
)

# Run complete multi-agent pipeline
result = coordinator.run("اكتب دالة للبحث الثنائي")

if not result["error"]:
    print("Optimization complete!")
    print(result["final_code"])
else:
    print(f"Error: {result['error']}")
```

---

### 4. Experimental Run Replication

To recreate batch evaluations across dataset matrices:

```bash
# Run evaluations for all configurations (T1 - T6) on sample problems
./run_all_configs.sh

# Run end-to-end evaluation runner with automated report generation
./run_evaluation_with_reports.sh
```

---

## 📊 Experimental Replication

The repository contains the official dataset splits and log sheets representing the 28 experimental configurations reviewed in the paper. Raw result records are located under the `results/` directory, broken down by:

* Local vs. Cloud-hosted models.
* Ablation studies (No-Optimizer, No-Translator).
* Comparative evaluation against standard baselines.


---

## 📄 License

This replication package and system are licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 📞 Contact

### Lead Researcher

* **Researcher:** Ahmed Reda Abd EL-Baset Ismail El-Mekawy
* **Institution:** Mansoura University, Egypt
* **GitHub Profile:** [@Ahmed-Reda-Elmekawy](https://github.com/Ahmed-Reda-Elmekawy)
* **Repository URL:** [https://github.com/Ahmed-Reda-Elmekawy/CodeGenOpt](https://github.com/Ahmed-Reda-Elmekawy/CodeGenOpt)

