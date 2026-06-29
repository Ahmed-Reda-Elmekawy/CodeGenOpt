import os
import subprocess
import tempfile
import ast
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class CodeOptimizer:
    """
    Safe Python code optimizer using a structured toolchain approach.
    It preserves functional correctness while applying style, structure, and import optimizations.
    """

    def __init__(self, debug_mode: bool = False, target_python_version: str = "3.12"):
        self.debug_mode = debug_mode
        self.target_python_version = target_python_version
        if debug_mode:
            logger.info("CodeOptimizer initialized - ready to optimize generated code")
            logger.info(f"Target Python version: {target_python_version}")

    # ------------------------------------------
    # Stage 1 - Postprocess raw code (moved here)
    # ------------------------------------------
    def _postprocess_code(self, code: str) -> str:
        """
        Lightweight cleanup:
        - Strip Markdown fences (```python / ```).
        - Trim leading/trailing whitespace.
        - If commentary appears before function/class, keep only code block.
        """
        if "```python" in code:
            code = code.split("```python", 1)[1].rsplit("```", 1)[0]
        elif "```" in code:
            code = code.split("```", 1)[1].rsplit("```", 1)[0]

        return code.strip()

    # ------------------------------------------
    # Helper: Run shell commands safely
    # ------------------------------------------
    def _run_tool(self, command: list[str], cwd: str):
        try:
            subprocess.run(
                command, cwd=cwd, check=True, capture_output=not self.debug_mode
            )
        except subprocess.CalledProcessError as e:
            if self.debug_mode:
                logger.warning(
                    f"[WARN] Tool {command[0]} failed:\n{e.stderr.decode(errors='ignore')}"
                )
            # Do not raise — we continue safely

    # ------------------------------------------
    # Helper: Syntax validation (AST parse)
    # ------------------------------------------
    def _is_syntax_valid(self, code: str) -> bool:
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    # ------------------------------------------
    # Core: Safe optimization pipeline
    # ------------------------------------------
    def run(self, raw_code: str) -> Tuple[str, Dict[str, Any]]:
        """
        Full optimization pipeline:
        - Postprocess raw LLM code
        - Apply linting & style tools (autoflake → isort → autopep8 → pyupgrade → black)
        - Type check via mypy
        """
        result_info = {"steps": [], "success": True, "errors": []}

        if not raw_code.strip():
            return raw_code, {"success": False, "error": "Empty code"}

        cleaned_code = self._postprocess_code(raw_code)

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "snippet.py")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(cleaned_code)

            def step(name, cmd):
                result_info["steps"].append(name)
                self._run_tool(cmd, tmpdir)
                # reload file
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()

            # 1 - autoflake – remove unused imports & vars safely
            step(
                "autoflake",
                [
                    "autoflake",
                    "--in-place",
                    "--remove-all-unused-imports",
                    "--ignore-init-module-imports",
                    "snippet.py",
                ],
            )

            # 2 - isort – organize imports
            step("isort", ["isort", "snippet.py", "--profile", "black"])

            # 3 - autopep8 – fix indentation, spacing, minor style issues
            step(
                "autopep8", ["autopep8", "--in-place", "--aggressive", "snippet.py"]
            )

            # 4 - pyupgrade – modernize syntax (Python 3+)
            step("pyupgrade", ["pyupgrade", "--py310-plus", "snippet.py"])

            # 5 - black – final formatting pass
            step("black", ["black", "--quiet", "snippet.py"])

            # 6 - mypy – static type check (no modification)
            mypy_result = subprocess.run(
                ["mypy", "snippet.py", "--ignore-missing-imports"],
                cwd=tmpdir,
                capture_output=True,
                text=True,
            )
            result_info["mypy_output"] = mypy_result.stdout.strip()

            # Load final version
            with open(file_path, "r", encoding="utf-8") as f:
                optimized_code = f.read()

        # ------------------------------------------
        # Verify final syntax
        # ------------------------------------------
        if not self._is_syntax_valid(optimized_code):
            result_info["success"] = False
            result_info["errors"].append("Syntax error after optimization")
            return cleaned_code, result_info

        return optimized_code, result_info
