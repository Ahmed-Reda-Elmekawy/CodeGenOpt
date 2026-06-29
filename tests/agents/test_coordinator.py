"""
Unit tests for the Coordinator agent.

This test suite covers:
- Full pipeline execution (Translator → Prompt Engineer → Code Generator → Optimizer).
- Optional usage of Translator and Optimizer.
- Optional shared LLM across all agents.
- Error handling at each stage (translator, prompt engineer, generator, optimizer).
- Ensures the pipeline always returns a structured result.

Usage:
    pytest tests/agents/test_coordinator.py -v

Requirements:
- Ollama LLM must be running locally with the required model(s).
- All dependent agents (TechnicalTranslator, PromptEngineer, CodeGenerator, CodeOptimizer)
  must be implemented and functional.

Author: Ahmed Reda
Date: 2025-09-06
"""
import pytest
from core.agents.coordinator import Coordinator
from tests.agents.utility import print_result


@pytest.mark.parametrize("use_translator,use_optimizer,shared_llm", [
    (True, True, True),
    (True, False, True),
    (False, True, True),
    (False, False, True),
    (True, True, False),
    (True, False, False),
    (False, True, False),
    (False, False, False),
])
def test_pipeline_basic(use_translator, use_optimizer, shared_llm):
    coordinator = Coordinator(
        use_translator=use_translator,
        use_optimizer=use_optimizer,
        shared_llm=shared_llm,
        debug_mode=True
    )

    task = "Write a Python function that returns the factorial of a number."
    result = coordinator.run(task)

    # Ensure structured output
    assert isinstance(result, dict)
    assert "final_code" in result
    assert "error" in result

    # Validate that final_code is generated (unless error occurred)
    success = result["final_code"] is not None and result["error"] is None

    print_result(
        f"Pipeline (translator={use_translator}, optimizer={use_optimizer}, shared_llm={shared_llm})",
        success,
        result
    )


def test_pipeline_error_handling():
    """Force pipeline to fail by passing invalid input."""
    coordinator = Coordinator(
        use_translator=True,
        use_optimizer=True,
        shared_llm=True,
        debug_mode=True
    )

    # Invalid input (non-string) to trigger translator/prompt failure
    result = coordinator.run(12345)

    assert isinstance(result, dict)
    assert result["final_code"] is None
    assert result["error"] is not None

    print_result("Pipeline error handling", True, result)


def test_pipeline_passthrough_no_translator():
    """Ensure that when translator is disabled, input is passed directly to PromptEngineer."""
    coordinator = Coordinator(
        use_translator=False,
        use_optimizer=False,
        shared_llm=True
    )

    task = "Write a Python function that checks if a string is a palindrome."
    result = coordinator.run(task)

    assert result["translated"] is None  # no translator used
    assert result["spec"] is not None
    assert result["final_code"] is not None
    assert result["error"] is None

    print_result("Pipeline passthrough without translator", True, result)
