"""
CodeGenOpt: Command-Line Interface (CLI) & REPL Entry Point
===========================================================
This module serves as the primary evaluation and execution entry point for the
CodeGenOpt system. It provides a robust interface to orchestrate the
multi-agent pipeline, enabling researchers to execute single-prompt trials or
initiate an interactive shell (REPL) using various local and cloud LLMs.

Algorithmic Pipeline Sequence:
-----------------------------
1. [User Input] ──> 2. [TechnicalTranslator] ──> 3. [PromptEngineer]
                                                           │ (Pydantic Spec)
                                                           ▼
4. [Final Code] <── 5. [CodeOptimizer] <────────── 6. [CodeGenerator]
                           (AST Formatter)

Key Features:
- Warm REPL mode: Maintains a persistent LLM runner context for interactive testing.
- Custom Model Routing: Dynamically targets local Ollama models or cloud backends.
- Execution Topology Toggles: Disables translation or optimization phases for ablations.
- CPU Fallback Engine: Safely bypasses local GPU runtimes in CUDA-constrained hosts.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Ensure project root directory is within system path for absolute module imports
sys.path.insert(0, str(Path(__file__).parent))

from core.agents.coordinator import Coordinator

# ─── Logging & Diagnostics Initialization ─────────────────────────────────────
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("codegenopt.cli")


# ─── Pipeline Helper Routines ──────────────────────────────────────────────────

def _build_coordinator(args: argparse.Namespace) -> Coordinator:
    """
    Constructs and configures the multi-agent Coordinator pipeline instance.

    Args:
        args (argparse.Namespace): Parsed command-line flags.

    Returns:
        Coordinator: Configured orchestrator client ready to run prompt evaluations.
    """
    llm_config = None
    # Programmatically inject runtime constraint parameters for Ollama LLM client
    if args.model or args.cpu:
        llm_config = {
            "model": args.model or "llama3",
            "temperature": 0.2,
            "num_gpu": 1,
            "num_thread": 12,
            "num_ctx": 4096,
            "num_predict": 512,
        }
        if args.cpu:
            logger.info("Enforcing CPU-only execution topology (num_gpu=0).")
            llm_config["num_gpu"] = 0  # Restricts execution strictly to host CPU cores
            
    return Coordinator(
        llm_config=llm_config,
        use_translator=not args.no_translator,
        use_optimizer=not args.no_optimizer,
        cloud_llm=args.cloud,
        debug_mode=args.debug,
    )


def _print_result(result: Dict[str, Any], verbose: bool = False) -> None:
    """
    Formats and prints the pipeline processing results to the standard output.

    Args:
        result (Dict[str, Any]): Structured dictionary holding outcomes of each agent.
        verbose (bool): If True, dumps intermediate specifications and translations.
    """
    divider = "=" * 60

    if result.get("error"):
        print(f"\n{divider}")
        print("❌  Pipeline execution failed")
        print(f"{divider}")
        print(f"Details: {result['error']}")
        return

    print(f"\n{divider}")
    print("✅  Pipeline completed successfully")
    print(divider)

    if verbose:
        if result.get("translated"):
            print(f"\n📝  [Agent 1] Translated Prompt:\n{result['translated']}")
        if result.get("spec"):
            print(f"\n📋  [Agent 2] Pydantic Prompt Spec:\n{json.dumps(result['spec'], indent=2, ensure_ascii=False)}")
        if result.get("generated_code"):
            print(f"\n🏗   [Agent 3] Raw Synthesized Code:\n```python\n{result['generated_code']}\n```")

    final = result.get("final_code")
    if final:
        print(f"\n💡  [Agent 4] Final Normalized Code:\n```python\n{final}\n```")
    else:
        print("\n⚠️   Warning: No final output script returned.")


# ─── Execution Orchestrator Modes ─────────────────────────────────────────────

def run_single(args: argparse.Namespace) -> int:
    """
    Runs a single problem prompt through the active multi-agent pipeline of Coordinator.

    Args:
        args (argparse.Namespace): CLI inputs contains the raw problem string.

    Returns:
        int: Exit status code (0 for success, 1 on compilation/generation failure).
    """
    coordinator = _build_coordinator(args)
    print(f"🚀  Orchestrating pipeline evaluation for: \"{args.problem}\"")
    result = coordinator.run(args.problem)
    _print_result(result, verbose=args.verbose)
    return 0 if result.get("final_code") else 1


def run_interactive(args: argparse.Namespace) -> int:
    """
    Starts an interactive REPL shell, keeping LLM instance context warm.

    Args:
        args (argparse.Namespace): Configurations parsed for the session.

    Returns:
        int: Exit status code of execution (always 0 upon standard shutdown).
    """
    print("\n" + "=" * 60)
    print("               CodeGenOpt — Interactive REPL Mode")
    print("   Provide engineering statements below. Type 'exit' to terminate.")
    print("=" * 60 + "\n")

    coordinator = _build_coordinator(args)

    while True:
        try:
            problem = input("CodeGenOpt › ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting interactive environment. Goodbye!")
            return 0

        if problem.lower() in {"quit", "exit", "q", ""}:
            if problem == "":
                continue
            print("Exiting interactive environment. Goodbye!")
            return 0

        result = coordinator.run(problem)
        _print_result(result, verbose=args.verbose)


# ─── CLI ──────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codegenopt",
        description="CodeGenOpt — Orchestrated Multi-Agent System (MAS) for Code Generation & Optimization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate code from an English prompt
  python main.py --problem "Write a binary search function in Python"

  # Generate code from an Arabic prompt (translator enabled by default)
  python main.py --problem "اكتب دالة للبحث الثنائي في Python"

  # Run without the translator or optimizer agents
  python main.py --problem "..." --no-translator --no-optimizer

  # Use a cloud-hosted model
  python main.py --problem "..." --cloud

  # Interactive REPL mode
  python main.py --interactive

  # Enable verbose output (show all intermediate pipeline stages)
  python main.py --problem "..." --verbose
        """,
    )

    # ── Operation mode (mutually exclusive) ───────────────────────────────────
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--problem", "-p",
        type=str,
        metavar="TEXT",
        help="Natural-language problem description to process.",
    )
    mode.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Start an interactive REPL session.",
    )

    # ── Pipeline toggles ──────────────────────────────────────────────────────
    parser.add_argument(
        "--no-translator",
        action="store_true",
        default=False,
        help="Disable the TechnicalTranslator agent (use raw input).",
    )
    parser.add_argument(
        "--no-optimizer",
        action="store_true",
        default=False,
        help="Disable the CodeOptimizer toolchain post-processing step.",
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=None,
        metavar="NAME",
        help="Ollama model name to use (e.g. llama3.2:3b, qwen3:0.6b). Overrides default.",
    )
    parser.add_argument(
        "--cloud",
        action="store_true",
        default=False,
        help="Use cloud-hosted model instead of local Ollama model.",
    )
    parser.add_argument(
        "--cpu",
        action="store_true",
        default=False,
        help="Force CPU execution by disabling GPU usage for Ollama.",
    )

    # ── Output options ────────────────────────────────────────────────────────
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=False,
        help="Print all intermediate pipeline stages (translation, spec, raw code).",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug-level logging across all agent modules.",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.interactive:
        return run_interactive(args)

    return run_single(args)


if __name__ == "__main__":
    sys.exit(main())