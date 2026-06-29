from pathlib import Path
import sys
import gradio as gr
import json

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.agents.technical_translator import TechnicalTranslator
from core.agents.prompt_engineer import PromptEngineer
from core.agents.code_generator import CodeGenerator
from core.agents.code_optimizer import CodeOptimizer

# Initialize all agents
translator_agent = TechnicalTranslator()
prompt_engineer_agent = PromptEngineer()
code_generator_agent = CodeGenerator()
code_optimizer_agent = CodeOptimizer()


def pipeline_run_streaming(user_text: str):
    """
    Streaming pipeline with progressive results - yields intermediate results
    """
    if not user_text.strip():
        yield "", "", "", "", "Please provide a problem description."
        return

    # Initialize empty results
    english_text = ""
    json_spec_text = ""
    generated_code = ""
    optimized_code = ""

    try:
        # Step 1: Translation to English
        yield english_text, json_spec_text, generated_code, optimized_code, "Step 1: Translating input to English."

        english_text = translator_agent.run(user_text)
        if isinstance(english_text, dict) and "error" in english_text:
            error_msg = f"Translation error: {english_text['error']}"
            yield "", "", "", "", error_msg
            return

        yield english_text, json_spec_text, generated_code, optimized_code, "Step 1 complete: translation finished."

        # Step 2: Convert to structured JSON specification
        yield english_text, json_spec_text, generated_code, optimized_code, "Step 2: Generating JSON specification."

        json_spec = prompt_engineer_agent.run(english_text)

        # Handle error cases from prompt engineer
        if isinstance(json_spec, dict) and "error" in json_spec:
            error_msg = f"Prompt engineering error: {json_spec['error']}"
            yield english_text, json.dumps(
                json_spec, indent=2
            ), generated_code, optimized_code, error_msg
            return

        json_spec_text = json.dumps(json_spec, indent=2)
        yield english_text, json_spec_text, generated_code, optimized_code, "Step 2 complete: JSON specification ready."

        # Step 3: Generate code from specification
        yield english_text, json_spec_text, generated_code, optimized_code, "Step 3: Generating Python code."

        generated_code = code_generator_agent.run(json_spec)
        if isinstance(generated_code, dict) and "error" in generated_code:
            error_msg = f"Code generation error: {generated_code['error']}"
            yield english_text, json_spec_text, "", "", error_msg
            return

        yield english_text, json_spec_text, generated_code, optimized_code, "Step 3 complete: code generation finished."

        # Step 4: Optimize the generated code
        yield english_text, json_spec_text, generated_code, optimized_code, "Step 4: Optimizing code with the configured toolchain."

        try:
            optimized_code, result_info = code_optimizer_agent.run(generated_code)
        except Exception as e:
            error_msg = f"Code optimization error: {e}"
            yield english_text, json_spec_text, generated_code, "", error_msg
            return

        # Format final summary
        success = result_info.get("success", False)
        tools_used = result_info.get("steps", [])

        improvements = []
        if "autoflake" in tools_used:
            improvements.append("Removed unused imports & variables (autoflake)")
        if "isort" in tools_used:
            improvements.append("Organized and sorted imports (isort)")
        if "autopep8" in tools_used:
            improvements.append("Fixed spacing and PEP8 styling issues (autopep8)")
        if "pyupgrade" in tools_used:
            improvements.append(
                "Modernized Python code syntax to 3.10+ rules (pyupgrade)"
            )
        if "black" in tools_used:
            improvements.append("Applied canonical code formatting rules (black)")

        mypy_output = result_info.get("mypy_output", "")
        if mypy_output:
            improvements.append("Verified static type hints with Mypy check")

        size_reduction = len(generated_code) - len(optimized_code)

        final_summary = f"""
Pipeline completed.

Optimization results:
• Status: {'Success' if success else 'Failed'}
• Tools Used: {', '.join(tools_used) if tools_used else 'None'}
• Steps Completed: {len(tools_used)}/5
• Size Reduction: {size_reduction} characters

Applied improvements ({len(improvements)}):
{chr(10).join([f'• {imp}' for imp in improvements[:8]])}
{'• ... and more' if len(improvements) > 8 else ''}

Staged pipeline execution completed.
"""

        yield english_text, json_spec_text, generated_code, optimized_code, final_summary

    except Exception as e:
        error_summary = f"Pipeline error: {str(e)}"
        yield english_text, json_spec_text, generated_code, optimized_code, error_summary


def pipeline_run(user_text: str):
    """
    Legacy non-streaming function for compatibility
    """
    # Convert streaming generator to single result
    results = list(pipeline_run_streaming(user_text))
    if results:
        return results[-1]  # Return final result
    return "", "", "", "", "No results generated"


def load_example(example_text: str):
    """Load example into the input field"""
    return example_text


# HumanEval-inspired examples in multiple languages
humaneval_examples = [
    # Problem 1: Two Sum (inspired by HumanEval)
    {
        "english": "Write a function that takes a list of integers and a target sum, and returns the indices of two numbers that add up to the target.",
        "arabic": "اكتب دالة تأخذ قائمة من الأرقام الصحيحة ومجموع مستهدف، وترجع فهارس الرقمين اللذين يجمعان للوصول للهدف",
        "french": "Écrivez une fonction qui prend une liste d'entiers et une somme cible, et retourne les indices de deux nombres qui s'additionnent pour atteindre la cible",
        "chinese": "编写一个函数，接受一个整数列表和一个目标和，返回两个数字的索引，这两个数字相加等于目标值",
        "spanish": "Escribe una función que tome una lista de enteros y una suma objetivo, y devuelva los índices de dos números que sumen el objetivo",
    },
    # Problem 2: Palindrome Check
    {
        "english": "Write a function that checks if a given string is a palindrome, ignoring case and spaces.",
        "arabic": "اكتب دالة تتحقق من كون النص المعطى متماثل (palindrome)، مع تجاهل الأحرف الكبيرة والمسافات",
        "french": "Écrivez une fonction qui vérifie si une chaîne donnée est un palindrome, en ignorant la casse et les espaces",
        "chinese": "编写一个函数来检查给定字符串是否为回文，忽略大小写和空格",
        "spanish": "Escribe una función que verifique si una cadena dada es un palíndromo, ignorando mayúsculas y espacios",
    },
    # Problem 3: Fibonacci
    {
        "english": "Write a function that returns the nth Fibonacci number using dynamic programming for efficiency.",
        "arabic": "اكتب دالة ترجع الرقم الفيبوناتشي رقم n باستخدام البرمجة الديناميكية للكفاءة",
        "french": "Écrivez une fonction qui retourne le nième nombre de Fibonacci en utilisant la programmation dynamique pour l'efficacité",
        "chinese": "编写一个函数，使用动态规划返回第n个斐波那契数以提高效率",
        "spanish": "Escribe una función que devuelva el enésimo número de Fibonacci usando programación dinámica para eficiencia",
    },
    # Problem 4: Prime Numbers
    {
        "english": "Write a function that returns all prime numbers up to a given number n using the Sieve of Eratosthenes algorithm.",
        "arabic": "اكتب دالة ترجع جميع الأرقام الأولية حتى الرقم n باستخدام خوارزمية غربال إراتوستينس",
        "french": "Écrivez une fonction qui retourne tous les nombres premiers jusqu'à un nombre donné n en utilisant l'algorithme du crible d'Ératosthène",
        "chinese": "编写一个函数，使用埃拉托斯特尼筛法算法返回给定数字n以内的所有质数",
        "spanish": "Escribe una función que devuelva todos los números primos hasta un número dado n usando el algoritmo de la Criba de Eratóstenes",
    },
    # Problem 5: Binary Search
    {
        "english": "Write a function that implements binary search on a sorted array and returns the index of the target element, or -1 if not found.",
        "arabic": "اكتب دالة تنفذ البحث الثنائي على مصفوفة مرتبة وترجع فهرس العنصر المستهدف، أو -1 إذا لم يوجد",
        "french": "Écrivez une fonction qui implémente la recherche binaire sur un tableau trié et retourne l'index de l'élément cible, ou -1 s'il n'est pas trouvé",
        "chinese": "编写一个函数，在排序数组上实现二分搜索，返回目标元素的索引，如果未找到则返回-1",
        "spanish": "Escribe una función que implemente búsqueda binaria en un array ordenado y devuelva el índice del elemento objetivo, o -1 si no se encuentra",
    },
]

with gr.Blocks(
    title="CodeGenOpt Pipeline Demonstration",
    theme=gr.themes.Soft(),
    css="""
    .gradio-container {background: #f8fafc;}
    .pipeline-step {
        background: white;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .step-header {
        font-weight: bold;
        color: #2d3748;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    """,
) as demo:

    # Header
    gr.HTML(
        """
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius:16px; padding:32px 24px; margin:32px auto; max-width:800px; text-align:center;'>
        <h1 style='color:white; font-size:2.5em; margin-bottom:0.3em; text-shadow: 0 2px 4px rgba(0,0,0,0.3);'>
            CodeGenOpt Pipeline Demonstration
        </h1>
        <p style='color:rgba(255,255,255,0.9); font-size:1.2em; margin:0;'>
            Staged inspection of translation, specification, code generation, and optimization outputs.
        </p>
        <div style='background:rgba(255,255,255,0.2); border-radius:8px; padding:12px; margin-top:16px;'>
            <p style='color:white; margin:0; font-size:1em;'>
                Translation -> Prompt Engineering -> Code Generation -> Optimization
            </p>
        </div>
    </div>
    """
    )

    # Input Section
    with gr.Row():
        with gr.Column():
            user_inp = gr.Textbox(
                label="Problem Description (Any Language)",
                placeholder="Describe a programming problem in any language...",
                lines=4,
                max_lines=8,
            )

            # Run Pipeline Button
            btn = gr.Button("Run Complete Pipeline", variant="primary", size="lg")

    # Pipeline Steps Output
    gr.Markdown("## Pipeline Steps")

    with gr.Row():
        with gr.Column():
            step1 = gr.Textbox(
                label="Step 1: English Translation", lines=3, interactive=False
            )

            step2 = gr.Code(
                label="Step 2: JSON Specification",
                language="json",
                lines=8,
                interactive=False,
            )

        with gr.Column():
            step3 = gr.Code(
                label="Step 3: Generated Code",
                language="python",
                lines=12,
                interactive=False,
            )

            step4 = gr.Code(
                label="Step 4: Optimized Code",
                language="python",
                lines=12,
                interactive=False,
            )

    # Pipeline Summary
    pipeline_summary = gr.Textbox(label="Pipeline Summary", lines=8, interactive=False)

    # Connect the streaming pipeline function
    btn.click(
        pipeline_run_streaming,
        inputs=user_inp,
        outputs=[step1, step2, step3, step4, pipeline_summary],
    )

    # Examples Section
    gr.Markdown("## HumanEval-Inspired Examples")
    gr.Markdown("*Click any example to load it into the input field*")

    # Create example buttons for each problem in different languages
    for i, example_set in enumerate(humaneval_examples, 1):
        with gr.Accordion(f"Problem {i}: {example_set['english'][:50]}...", open=False):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("**English:**")
                    en_btn = gr.Button(f"Load English Example {i}", size="sm")
                    en_btn.click(lambda ex=example_set["english"]: ex, outputs=user_inp)
                    gr.Markdown(f"*{example_set['english']}*")

                    gr.Markdown("**Arabic:**")
                    ar_btn = gr.Button(f"Load Arabic Example {i}", size="sm")
                    ar_btn.click(lambda ex=example_set["arabic"]: ex, outputs=user_inp)
                    gr.Markdown(f"*{example_set['arabic']}*")

                with gr.Column():
                    gr.Markdown("**French:**")
                    fr_btn = gr.Button(f"Load French Example {i}", size="sm")
                    fr_btn.click(lambda ex=example_set["french"]: ex, outputs=user_inp)
                    gr.Markdown(f"*{example_set['french']}*")

                    gr.Markdown("**Chinese:**")
                    cn_btn = gr.Button(f"Load Chinese Example {i}", size="sm")
                    cn_btn.click(lambda ex=example_set["chinese"]: ex, outputs=user_inp)
                    gr.Markdown(f"*{example_set['chinese']}*")

                    gr.Markdown("**Spanish:**")
                    es_btn = gr.Button(f"Load Spanish Example {i}", size="sm")
                    es_btn.click(lambda ex=example_set["spanish"]: ex, outputs=user_inp)
                    gr.Markdown(f"*{example_set['spanish']}*")

    # Quick Examples Row
    gr.Markdown("## Quick Examples")
    with gr.Row():
        quick_examples = [
            ("Two Sum", humaneval_examples[0]["english"]),
            ("Palindrome", humaneval_examples[1]["english"]),
            ("Fibonacci", humaneval_examples[2]["english"]),
            ("Binary Search", humaneval_examples[4]["english"]),
        ]

        for label, example in quick_examples:
            btn = gr.Button(label, size="sm")
            btn.click(lambda ex=example: ex, outputs=user_inp)

    # Footer
    gr.HTML(
        """
    <div style='text-align:center; margin-top:40px; padding:20px; background:#f7fafc; border-radius:12px;'>
        <p style='color:#4a5568; margin:0;'>
            <strong>Complete AI Pipeline:</strong>
            Technical Translation -> Prompt Engineering -> Code Generation -> Optimization
        </p>
        <p style='color:#718096; font-size:0.9em; margin:8px 0 0 0;'>
            Powered by Ollama LLMs + Industry-Standard Tools (Black, isort, autoflake, pyupgrade, mypy)
        </p>
    </div>
    """
    )

if __name__ == "__main__":
    demo.launch()
