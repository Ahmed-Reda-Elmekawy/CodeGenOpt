from pathlib import Path
import sys

import gradio as gr

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.agents.technical_translator import TechnicalTranslator
from core.agents.prompt_engineer import PromptEngineer
from core.agents.code_generator import CodeGenerator
from core.agents.code_optimizer import CodeOptimizer

translator_agent = TechnicalTranslator()
prompt_engineer_agent = PromptEngineer()
code_generator_agent = CodeGenerator()
code_optimizer_agent = CodeOptimizer()


# ===== Functions =====
def run_translator(text: str):
    res = translator_agent.run(text)
    if isinstance(res, dict) and "error" in res:
        return f"Translation error:\n{res['error']}"
    return res


def run_prompt_engineer(text: str):
    return prompt_engineer_agent.run(text)


def run_code_generator(function_spec_json: str):
    """
    Accepts a JSON string describing a function spec and returns
    generated Python code as a string.
    """
    import json

    try:
        spec = json.loads(function_spec_json)
    except json.JSONDecodeError as e:
        return f"# Invalid JSON: {e}"

    res = code_generator_agent.run(spec)
    if isinstance(res, dict) and "error" in res:
        return f"# Code Generation Error:\n{res['error']}"
    return res


def run_code_optimizer(code: str):
    """
    Professional code optimization using industry-standard tools.
    """
    if not code.strip():
        return (
            "",
            "# Please provide Python code to optimize",
            "",
            "",
            "**Status:** Ready",
            "",
            "",
        )

    try:
        optimized_code, result_info = code_optimizer_agent.run(code)
    except Exception as e:
        return (
            code,
            f"# Error in optimization:\n{e}",
            "No improvements applied",
            "No tools used",
            "**Status:** Optimization failed",
            f"**Statistics:**\n• Process failed: {e}",
            "**Type Check:** Not run",
        )

    success = result_info.get("success", False)
    tools_used = result_info.get("steps", [])

    # Format status
    status = (
        "**Status:** Optimization completed"
        if success
        else "**Status:** Optimization failed"
    )

    # Format improvements based on steps run and code changes
    improvements = []
    if "autoflake" in tools_used:
        improvements.append("Removed unused imports & variables (autoflake)")
    if "isort" in tools_used:
        improvements.append("Organized and sorted imports (isort)")
    if "autopep8" in tools_used:
        improvements.append("Fixed spacing and PEP8 styling issues (autopep8)")
    if "pyupgrade" in tools_used:
        improvements.append("Modernized Python code syntax to 3.10+ rules (pyupgrade)")
    if "black" in tools_used:
        improvements.append("Applied canonical code formatting rules (black)")

    mypy_output = result_info.get("mypy_output", "")
    if mypy_output:
        improvements.append("Verified static type hints with Mypy check")

    improvements_text = (
        "\n".join([f"• {imp}" for imp in improvements])
        if improvements
        else "No improvements applied"
    )

    # Format tools used
    tools_text = (
        f"**Tools Used:** {', '.join(tools_used)}" if tools_used else "No tools used"
    )

    # Format statistics
    original_lines = len(code.splitlines())
    final_lines = len(optimized_code.splitlines())
    size_reduction = len(code) - len(optimized_code)

    stats_text = f"""**Statistics:**
• Original lines: {original_lines}
• Final lines: {final_lines}
• Size reduction: {size_reduction} chars
• Steps: {len(tools_used)}/5"""

    # Format MyPy results
    # Mypy reports success if stdout is empty or contains success messages, and has no "error:"
    mypy_passed = (
        mypy_output == ""
        or "Success:" in mypy_output
        or "no issues found" in mypy_output.lower()
    )
    if mypy_passed and "error:" not in mypy_output:
        mypy_status = "**Type Check:** Passed"
    else:
        mypy_status = "**Type Check:** Completed with issues"

    return (
        code,
        optimized_code,
        improvements_text,
        tools_text,
        status,
        stats_text,
        mypy_status,
    )


# ===== Gradio UI =====
with gr.Blocks(
    theme=gr.themes.Soft(),
    title="CodeGenOpt Agent Inspection",
    css="""
    @media (prefers-color-scheme: dark) {
        body, .gradio-container { background-color: #0f172a !important; color: #e2e8f0 !important; }
        .gr-button-primary { background-color: #7c3aed !important; color: white !important; }
    }
    @media (prefers-color-scheme: light) {
        body, .gradio-container { background-color: #f8fafc !important; color: #1a202c !important; }
        .gr-button-primary { background-color: #4f46e5 !important; color: white !important; }
    }
""",
) as demo:

    # ===== Header =====
    with gr.Row():
        with gr.Column():
            gr.HTML(
                """
            <div style='text-align:center; margin: 20px auto; max-width:700px;'>
                <h1 style='font-size:2.2em; margin-bottom:0.3em;'>CodeGenOpt Agent Inspection</h1>
                <p style='opacity:0.85; font-size:1.1em; margin-top:0;'>
                    Review each agent in the code generation and optimization workflow independently.
                </p>
            </div>
            """
            )

    # ===== Translator Tab =====
    with gr.Tab("Translator"):
        with gr.Group():
            gr.Markdown(
                "### Technical Translator\nEnter a technical or programming prompt in any language and review the normalized English version."
            )

            inp = gr.Textbox(
                label="Input Text",
                placeholder="Type or paste any technical prompt in any language...",
                lines=3,
            )
            out = gr.Textbox(label="English Translation", lines=3)

            btn = gr.Button("Run Translator", variant="primary")
            btn.click(run_translator, inputs=inp, outputs=out)

            # ===== Examples with languages =====
            gr.Markdown("#### Examples: Add Two Numbers in Different Languages")
            examples = [
                ("🇪🇬 Arabic", "اكتب دالة بايثون تجمع رقمين"),
                ("🇫🇷 French", "Écris une fonction Python qui additionne deux nombres"),
                ("🇨🇳 Chinese", "用Python写一个函数，计算两个数的和"),
                ("🇪🇸 Spanish", "Escribe una función de Python que sume dos números"),
                ("🇩🇪 German", "Schreibe eine Python-Funktion, die zwei Zahlen addiert"),
                ("🇬🇧 English", "Write a Python function that adds two numbers"),
            ]

            with gr.Row():
                for lang, ex in examples:
                    gr.Examples(
                        examples=[[ex]],
                        inputs=inp,
                        label=f"{lang}",
                    )

    # ===== Prompt Engineer Tab =====
    with gr.Tab("Prompt Engineer"):
        with gr.Group():
            gr.Markdown(
                "### Prompt Engineer\nTakes an English problem description and outputs a structured JSON specification for code generation."
            )
            inp2 = gr.Textbox(
                label="Problem Description (English)",
                placeholder="E.g., Write a function to compute factorial...",
                lines=3,
            )
            out2 = gr.JSON(label="JSON Specification")
            btn2 = gr.Button("Generate JSON Specification", variant="primary")
            btn2.click(run_prompt_engineer, inputs=inp2, outputs=out2)

    # ===== Code Generator Tab =====
    with gr.Tab("Code Generator"):
        with gr.Group():
            gr.Markdown(
                "### Code Generator\nPaste a function specification JSON and get generated Python code."
            )
            inp3 = gr.Textbox(
                label="Function Specification (JSON)",
                placeholder='{"function_name": "add", "signature": "def add(a:int,b:int)->int", ...}',
                lines=8,
            )
            out3 = gr.Textbox(label="Generated Python Code", lines=10)
            btn3 = gr.Button("Generate Code", variant="primary")
            btn3.click(run_code_generator, inputs=inp3, outputs=out3)

    # ===== Code Optimizer Tab =====
    with gr.Tab("Code Optimizer"):
        with gr.Group():
            gr.Markdown(
                """
                ### Code Optimizer

                **Toolchain:**
                Black, isort, autoflake, autopep8, pyupgrade, mypy

                **Outputs:** formatting, import cleanup, syntax modernization, and static type-check status.
                """
            )

            # Input Section
            inp4 = gr.Textbox(
                label="Input Python Code",
                placeholder="Paste Python code for optimization...",
                lines=8,
            )

            # Quick Examples
            with gr.Row():
                example1_btn = gr.Button("Syntax Issues", size="sm")
                example2_btn = gr.Button("Import Cleanup", size="sm")
                example3_btn = gr.Button("Simple Optimizations", size="sm")
                example4_btn = gr.Button("Type Hints", size="sm")

            # Main action button
            btn4 = gr.Button("Optimize Code", variant="primary", size="lg")

            # Results Display
            with gr.Row():
                with gr.Column():
                    original_display = gr.Textbox(
                        label="Original Code", lines=12, interactive=False
                    )
                with gr.Column():
                    out4 = gr.Textbox(
                        label="Optimized Code", lines=12, interactive=False
                    )

            # Status and Results
            with gr.Row():
                with gr.Column():
                    status_display = gr.Markdown("**Status:** Ready")
                    tools_display = gr.Markdown("**Tools Used:** None")
                with gr.Column():
                    stats_display = gr.Markdown("**Statistics:** No data")
                    mypy_display = gr.Markdown("**Type Check:** Not run")

            # Improvements
            improvements_display = gr.Textbox(
                label="Applied Improvements", lines=6, interactive=False
            )

            # Connect button to function
            btn4.click(
                run_code_optimizer,
                inputs=inp4,
                outputs=[
                    original_display,
                    out4,
                    improvements_display,
                    tools_display,
                    status_display,
                    stats_display,
                    mypy_display,
                ],
            )

            # Example Button Actions
            example1_btn.click(
                lambda: """# Syntax Issues Example
def process_data(data, config):
    result = {}
    for item in data:
        if isinstance(item.get("active"), true):
            result["active"] = item
        elif isinstance(item.get("status"), null):
            result["inactive"] = item
    try:
        return json.dumps(result)
    except:
        pass
    return result""",
                outputs=inp4,
            )

            example2_btn.click(
                lambda: """# Import Cleanup Example
import os
import sys
import json
import re
from collections import defaultdict, namedtuple, deque
from typing import List, Dict, Optional, Any, Union
import functools
import itertools

def simple_function(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    result = defaultdict(list)
    unused_var = "not used"

    for item in data:
        if item.get("type") == "active":
            result["active"].append(item)

    return dict(result)""",
                outputs=inp4,
            )

            example3_btn.click(
                lambda: """# Performance Example
def calculate_stuff():
    x = 5 + 0
    y = 10 * 1
    z = 8 - 0
    w = 12 / 1

    result = []
    for i in range(len([1, 2, 3, 4, 5])):
        result.append(i * 2)

    return x, y, z, w, result""",
                outputs=inp4,
            )

            example4_btn.click(
                lambda: """# Type Hints Example
def legacy_function(x, y):
    if x == None:
        return y
    elif x == True:
        return x and y
    else:
        return x + y

data = {
    "name": "example",
    "value": 42,
    "active": True
}

result = legacy_function(data["value"], data["active"])""",
                outputs=inp4,
            )

    # ===== Footer =====
    gr.HTML(
        """
    <div style='text-align:center; margin-top:40px; font-size:0.9em; opacity:0.7;'>
        Built with <a href="https://www.gradio.app" target="_blank" style="color:#4a90e2;">Gradio</a> |
        CodeGenOpt research replication package
    </div>
    """
    )

if __name__ == "__main__":
    demo.launch()
