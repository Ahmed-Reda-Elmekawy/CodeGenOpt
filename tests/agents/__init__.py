"""
tests.agents — Unit test suite for individual CodeGenOpt agents.

Covers:
    - TechnicalTranslator  (test_technical_translator.py)
    - PromptEngineer       (test_prompt_engineer.py)
    - CodeGenerator        (test_code_generator.py)
    - CodeOptimizer        (test_code_optimizer.py)
    - Coordinator          (test_coordinator.py)

Shared helpers are in utility.py (print_result, assert_text_similar).

Usage:
    PYTHONPATH=. pytest tests/agents/ -v
"""
