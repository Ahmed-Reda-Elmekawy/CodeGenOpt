"""
Unit tests for the PromptEngineer agent.

This test suite covers:
- Correct generation of structured JSON for English programming tasks.
- Ensures that JSON keys and structure exist (function_name, signature, description, constraints, examples, exceptions).
- Handles invalid and edge-case inputs.
- Gracefully reports parsing errors if the LLM returns malformed JSON.

Usage:
    pytest tests/agents/test_prompt_engineer.py -v

Requirements:
- Ollama LLM must be running locally with the required model(s).
- The agent should be able to output structured JSON for technical prompts.

Author: Ahmed Reda
Date: 2025-08-31
"""

import pytest
from core.agents.prompt_engineer import PromptEngineer
from tests.agents.utility import print_result


@pytest.mark.parametrize("problem_description", [
    "Write a Python function that checks if a number is prime.",
    "Write a Python function that reverses a string.",
    "Write a Python function that sorts a list of integers using bubble sort.",
])
def test_valid_generation(problem_description):
    agent = PromptEngineer(debug_mode=True)
    result = agent.run(problem_description)

    try:
        # Must be dict
        assert isinstance(result, dict), "Result is not a dict"
        # Required keys
        for key in ["function_name", "signature", "description", "constraints", "examples", "exceptions"]:
            assert key in result, f"Missing key: {key}"
        print_result(f"PromptEngineer valid: {problem_description}", True, result)
    except AssertionError as e:
        print_result(f"PromptEngineer valid: {problem_description}", False, f"Result: {result}\n{e}")
        raise


@pytest.mark.parametrize("problem_description", [
    "",    # Empty
    None,  # None input
])
def test_invalid_input(problem_description):
    agent = PromptEngineer()
    result = agent.run(problem_description)

    try:
        assert "error" in result, "Error key not found in result"
        print_result(f"PromptEngineer invalid: {problem_description}", True, result)
    except AssertionError as e:
        print_result(f"PromptEngineer invalid: {problem_description}", False, f"Result: {result}\n{e}")
        raise


def test_malformed_output(monkeypatch):
    """
    Simulate an LLM returning malformed output (no JSON),
    and ensure the agent reports an error gracefully.
    """

    class DummyChain:
        def invoke(self, inp):
            return "This is not JSON at all"

    agent = PromptEngineer()
    agent.chain = DummyChain()  # replace real chain

    result = agent.run("Write a Python function that calculates factorial.")

    try:
        assert "error" in result, "Error key not found in result for malformed output"
        print_result("PromptEngineer malformed JSON", True, result)
    except AssertionError as e:
        print_result("PromptEngineer malformed JSON", False, f"Result: {result}\n{e}")
        raise
