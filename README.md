# 🚀 CodeGenOpt

An Intelligent Multi-Agent Framework for Programming Code Generation and Optimization using Private, Local Small Language Models (SLMs).

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

**CodeGenOpt** is an automated, privacy-first multi-agent framework designed to generate, validate, and optimize Python source code starting from natural language problem descriptions.

By utilizing local Small Language Models (SLMs) via **Ollama** and orchestrating them through **LangChain**, CodeGenOpt delivers state-of-the-art code synthesis. It eliminates dependencies on external commercial APIs, ensuring data privacy and zero API execution costs. The framework incorporates an automated post-generation optimization toolchain and validation pipeline, improving syntactic compliance and static typing correctness.

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

## 🚀 Usage Guide

### Single Invocation via Coordinator

You can run individual code generation trials by importing the `Coordinator` class:

```python
from core.agents.coordinator import Coordinator

# Initialize central orchestrator
coordinator = Coordinator(
    model_name="llama3", 
    debug_mode=True
)

prompt = "اكتب دالة بلغة بايثون للتحقق من الأعداد الأولية"

# Run execution pipeline
result = coordinator.run(prompt)
print(result["final_code"])
```

### Batch Evaluation and Execution

To replicate entire experimental runs:

```bash
# Run evaluations for all configurations
./run_all_configs.sh

# Run evaluation runner with automatic report aggregation
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

This replication package and framework are licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 📞 Contact

### Lead Researcher

* **Researcher:** Ahmed Reda Abd EL-Baset Ismail El-Mekawy
* **Institution:** Mansoura University, Egypt
* **GitHub Profile:** [@Ahmed-Reda-Elmekawy](https://github.com/Ahmed-Reda-Elmekawy)
* **Repository URL:** [https://github.com/Ahmed-Reda-Elmekawy/CodeGenOpt](https://github.com/Ahmed-Reda-Elmekawy/CodeGenOpt)

