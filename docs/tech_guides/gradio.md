# Gradio Integration For Interactive Agent Testing

## Purpose

Gradio is used in CodeGenOpt to provide lightweight browser-based interfaces for
manual inspection of agents and pipeline behavior. These interfaces support
qualitative validation during development and demonstrations for reviewers.

## Role In CodeGenOpt

The Gradio interfaces are not required for batch evaluation. They are optional
tools for:

- Inspecting individual agent behavior.
- Demonstrating translation, generation, and optimization flows.
- Collecting qualitative feedback before running larger evaluations.
- Comparing local and cloud-backed pipeline behavior interactively.

## Minimal Example

The following example illustrates how a CodeGenOpt agent can be wrapped in a
simple Gradio interface:

```python
import gradio as gr
from core.agents.technical_translator import TechnicalTranslator


def translate(text: str) -> str:
    agent = TechnicalTranslator()
    return agent.run(text)


interface = gr.Interface(
    fn=translate,
    inputs=gr.Textbox(lines=3, label="Input prompt"),
    outputs=gr.Textbox(label="English technical prompt"),
    title="CodeGenOpt Technical Translator",
    description=(
        "Translates technical or programming prompts into English while "
        "preserving semantic and domain-specific meaning."
    ),
)

interface.launch()
```

## Running The Included Interfaces

Install Gradio if it is not already available:

```bash
pip install gradio
```

Run the agent playground:

```bash
python ui/gradio/agents_playground.py
```

Run the pipeline demo:

```bash
python ui/gradio/pipeline_demo.py
```

The helper script can also be used:

```bash
./scripts/run_gradio.sh agents_playground
./scripts/run_gradio.sh pipeline_demo
```

After launch, Gradio prints a local URL, typically under
`http://127.0.0.1:<port>`.

## Reproducibility Notes

- Gradio demos are intended for interactive inspection, not for quantitative
  benchmark reporting.
- Batch evaluation should be performed with `evaluation/run_evaluation.py`.
- Publicly exposed Gradio interfaces should use authentication, rate limits, and
  resource controls.

## References

- Gradio documentation: https://www.gradio.app/docs
- Gradio repository: https://github.com/gradio-app/gradio
