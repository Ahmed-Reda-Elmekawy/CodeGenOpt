# CodeGenOpt User Interface

This directory contains the browser-based Gradio interfaces used to inspect and
demonstrate the CodeGenOpt multi-agent code generation and optimization system.

The interfaces are included as part of the public research replication package.
They are intended to help reviewers and readers observe the system at two
levels: individual agent behavior and the complete end-to-end generation
pipeline.

The UI layer imports the production agents from `core.agents` and does not
reimplement model reasoning, prompt construction, code synthesis, or
optimization logic. This separation keeps the demonstrator aligned with the
same implementation used by the command-line and evaluation workflows.

## Directory Layout

```text
ui/
├── __init__.py
└── gradio/
    ├── agents_playground.py
    └── pipeline_demo.py
```

## Interfaces

### Agent-Level Inspection Interface

File: `ui/gradio/agents_playground.py`

Purpose: inspect each major agent independently.

Available tabs:

- Technical Translator: converts multilingual technical prompts into English.
- Prompt Engineer: converts an English problem statement into a structured JSON
  function specification.
- Code Generator: generates Python code from a JSON function specification.
- Code Optimizer: runs generated or pasted Python code through the formatting,
  cleanup, modernization, and type-checking toolchain.

Use this interface when reviewing the responsibilities of individual agents,
checking intermediate transformations, or demonstrating the modular design of
the system.

### End-to-End Pipeline Interface

File: `ui/gradio/pipeline_demo.py`

Purpose: demonstrate the complete end-to-end system as a staged workflow.

Execution stages:

1. Translate the user problem into English.
2. Generate a structured JSON specification.
3. Generate Python source code from the specification.
4. Optimize and type-check the generated code.
5. Stream each intermediate result back to the UI.

Use this interface for public demonstrations, thesis review, and qualitative
inspection of the integrated agent pipeline.

## Runtime Requirements

Install the project dependencies from the repository root:

```bash
pip install -r requirements.txt
```

The UI requires:

- Python 3.12 or later.
- Gradio.
- The CodeGenOpt core package available on `PYTHONPATH`.
- Ollama or the configured model backend required by the agents.
- Formatter and validation tools used by `CodeOptimizer`: `autoflake`,
  `isort`, `autopep8`, `pyupgrade`, `black`, and `mypy`.

## Running the UI

From the repository root:

```bash
python ui/gradio/agents_playground.py
```

or:

```bash
python ui/gradio/pipeline_demo.py
```

The helper script can also be used:

```bash
./scripts/run_gradio.sh agents_playground
./scripts/run_gradio.sh pipeline_demo
```

Gradio prints a local URL in the terminal, usually `http://127.0.0.1:7860`.

## Suggested Review Workflow

For a concise review session:

1. Start `pipeline_demo.py`.
2. Load one multilingual example from the HumanEval-inspired examples section.
3. Run the complete pipeline and inspect the four intermediate outputs.
4. Open `agents_playground.py` only if a specific intermediate stage requires
   closer inspection.

## Operational Notes

- Both interfaces instantiate agent objects at module load time. Startup time
  depends on the configured model backend and local service availability.
- The UI does not own business logic. Agent behavior should be changed in
  `core/agents`, then surfaced here only when the interaction contract changes.
- `pipeline_run_streaming` yields intermediate values, so each stage can update
  the browser before the full pipeline completes.
- Error responses from agents are displayed in the UI instead of raising raw
  exceptions to the browser.
- The optimizer interface returns original code, optimized code, tool usage,
  basic statistics, and type-check status as separate UI outputs.

## Public Release Checklist

Before publishing UI changes to the public repository:

1. Run Python compilation checks:

   ```bash
   python -m py_compile ui/gradio/agents_playground.py ui/gradio/pipeline_demo.py
   ```

2. Launch each Gradio interface locally and verify that the page renders.
3. Run one simple example in each affected workflow.
4. Confirm any new UI dependency is listed in `requirements.txt`.
5. Keep examples concise, reproducible, and appropriate for academic review.
6. Use commit messages that describe reviewer-facing value, such as
   `docs: document Gradio UI review workflow`.

## Known Boundaries

- The current UI is a research demonstration interface, not an authenticated
  production web application.
- Long-running model calls depend on local hardware, Ollama availability, and
  configured model size.
- The UI does not persist user inputs, generated code, or optimization results.
