# Initial Functional Tests For Ollama Models

This document records exploratory functional tests used to understand how
candidate Ollama models behave on representative CodeGenOpt agent prompts. The
tests are not final benchmark results; they are qualitative probes for output
style, verbosity, code quality, and suitability for agent roles.

## Test Method

Each test used a direct command-line prompt through `ollama run`. The goal was
to observe whether the model produced concise, structured, and task-appropriate
responses for common agent operations.

The examples below can be reproduced on any machine with Ollama installed and
the corresponding model downloaded.

## 1. Prompt Engineering Probe

**Model:** `llama3:latest`

**Prompt:**

```text
Rephrase the following prompt for clarity: Write a function that returns the factorial of a number.
```

**Command:**

```bash
echo 'Rephrase the following prompt for clarity: Write a function that returns the factorial of a number.' | ollama run llama3:latest
```

**Observed behavior:**

The model produced a clearer version of the prompt and added a short definition
of factorial. This indicates strong instruction following, but also shows a
tendency toward explanatory expansion.

**Implication for CodeGenOpt:**

The prompt engineering agent should constrain output length and format when only
a rewritten prompt is required.

## 2. Code Generation Probe

**Model:** `codellama:7b-instruct`

**Prompt:**

```text
Write a Python function that returns the factorial of a number.
```

**Command:**

```bash
echo 'Write a Python function that returns the factorial of a number.' | ollama run codellama:7b-instruct
```

**Observed behavior:**

The model generated a recursive Python implementation and included test cases.
This is useful for development, but it may require post-processing when the
pipeline expects code only.

**Implication for CodeGenOpt:**

The code generation agent should use explicit instructions such as "return only
the function implementation" when extra tests or explanations are not desired.

## 3. Code Optimization Probe

**Model:** `codellama:7b-instruct`

**Prompt:**

```text
Optimize this Python function for speed: def factorial(n): return 1 if n==0 else n*factorial(n-1)
```

**Command:**

```bash
echo 'Optimize this Python function for speed: def factorial(n): return 1 if n==0 else n*factorial(n-1)' | ollama run codellama:7b-instruct
```

**Observed behavior:**

The model proposed memoization and alternative implementations, accompanied by
explanatory text.

**Implication for CodeGenOpt:**

The optimizer can benefit from code-specialized models, but output formatting
constraints are needed to separate the optimized code from natural-language
rationale.

## 4. Code Evaluation Probe

**Model:** `llama3:latest`

**Prompt:**

```text
Evaluate the correctness and efficiency of this code: def factorial(n): return 1 if n==0 else n*factorial(n-1)
```

**Command:**

```bash
echo 'Evaluate the correctness and efficiency of this code: def factorial(n): return 1 if n==0 else n*factorial(n-1)' | ollama run llama3:latest
```

**Observed behavior:**

The model discussed correctness, time complexity, recursion overhead, stack
depth risk, and possible iterative or memoized alternatives.

**Implication for CodeGenOpt:**

General instruction-tuned models are useful for explanatory evaluation, but
structured rubrics are recommended for reproducible scoring.

## 5. Alternative Code Model Probe

**Model:** `deepseek-coder:6.7b-instruct`

**Prompt:**

```text
Write a Python function to compute the nth Fibonacci number.
```

**Command:**

```bash
echo 'Write a Python function to compute the nth Fibonacci number.' | ollama run deepseek-coder:6.7b-instruct
```

**Observed behavior:**

The model provided both a simple recursive implementation and a more efficient
dynamic-programming alternative.

**Implication for CodeGenOpt:**

Alternative code-specialized models can provide useful implementation diversity,
but deterministic output requirements should be enforced during benchmarking.

## Practical Conclusions

- Code-specialized models tend to provide useful implementations and sometimes
  tests or alternative solutions.
- General instruction-tuned models are strong for rewriting, explaining, and
  evaluating code.
- Concise and reproducible agent behavior requires explicit output contracts.
- These initial tests informed model-selection and prompt-formatting decisions;
  they should not be interpreted as quantitative benchmark evidence.
