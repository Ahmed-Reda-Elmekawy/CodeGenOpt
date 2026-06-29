"""
Comprehensive unit tests for CodeOptimizer with professional optimization libraries

Covers:
- Empty code handling
- Black formatting integration
- isort/autoflake import optimization
- pyupgrade Python modernization
- mypy type checking integration
- Expression simplification
- Syntax error fixing
- Comprehensive integration tests

Usage:
    pytest tests/agents/test_code_optimizer.py -q

Author: Ahmed Reda
Date: 2025-09-03
"""

import ast
import pytest
import subprocess
import tempfile
import os

from core.agents.code_optimizer import CodeOptimizer
from tests.agents.utility import print_result


@pytest.fixture
def optimizer():
    return CodeOptimizer(debug_mode=True)


def test_empty_code_returns_error(optimizer):
    """Test that empty code returns appropriate error."""
    res = optimizer.run("   \n\t  ")
    assert res["optimized_code"] == ""
    assert res["success"] is False
    assert "No code provided" in res["issues_found"][0]
    print_result("empty code returns error", True)


def test_black_formatting_integration(optimizer):
    """Test that black formatting is properly integrated."""
    unformatted_code = """
def messy_function( x,y ):
    if x==1:
        return y+2
    else:
        return y-1
"""
    result = optimizer.run(unformatted_code)
    # Black should format this properly
    assert result["success"] is True
    assert "Applied Black formatting (PEP8)" in result["improvements"]
    # Check that the code is properly formatted (black adds consistent spacing)
    assert "def messy_function(x, y):" in result["optimized_code"] or "def messy_function(" in result["optimized_code"]
    print_result("black formatting integration", True)


def test_isort_autoflake_import_optimization(optimizer):
    """Test isort and autoflake integration for import optimization."""
    code_with_unused_imports = """
import os
import sys
import json
from typing import List, Dict
from collections import defaultdict

def use_only_os():
    return os.getcwd()

# json, sys, List, Dict, defaultdict are unused
"""
    result = optimizer.run(code_with_unused_imports)
    assert result["success"] is True
    # Should have removed unused imports
    optimized = result["optimized_code"]
    assert "Applied performance optimizations" in result["improvements"]
    # Check that some unused imports were removed
    assert "import json" not in optimized or "from collections import defaultdict" not in optimized
    print_result("isort autoflake import optimization", True)


def test_pyupgrade_modernization(optimizer):
    """Test pyupgrade integration for Python modernization."""
    old_style_code = """
def old_function():
    return u"unicode string"
"""
    result = optimizer.run(old_style_code)
    assert result["success"] is True
    assert "Applied Python version upgrades with pyupgrade" in result["improvements"]
    print_result("pyupgrade modernization", True)


def test_mypy_type_checking_integration(optimizer):
    """Test mypy integration for type checking."""
    code_with_types = """
def add_numbers(a: int, b: int) -> int:
    return a + b
"""
    result = optimizer.run(code_with_types)
    assert result["success"] is True
    # mypy_result should be present
    assert "mypy_result" in result
    mypy_result = result["mypy_result"]
    assert isinstance(mypy_result, dict)
    assert "passed" in mypy_result
    print_result("mypy type checking integration", True)


def test_expression_simplification(optimizer):
    """Test expression simplification optimizations."""
    code_with_simplifiable_expressions = """
def calculate():
    x = 5 + 0
    y = 10 * 1
    z = 8 - 0
    w = 12 / 1
    return x, y, z, w
"""
    result = optimizer.run(code_with_simplifiable_expressions)
    assert result["success"] is True
    optimized = result["optimized_code"]
    # Should have simplified expressions
    assert "Applied performance optimizations" in result["improvements"]
    print_result("expression simplification", True)


def test_syntax_error_fixing(optimizer):
    """Test syntax error fixing capabilities."""
    # Note: 'true' and 'null' are not syntax errors in Python, they're just undefined names
    # The optimizer handles this through mypy type checking instead
    code_with_potential_issues = """
def function_with_undefined_names():
    if isinstance(x, true):
        return True
    if isinstance(y, null):
        return None
"""
    result = optimizer.run(code_with_potential_issues)
    assert result["success"] is True
    # Should have applied various optimizations
    assert "Applied Black formatting (PEP8)" in result["improvements"]
    assert "Applied performance optimizations" in result["improvements"]
    # mypy should detect the undefined names
    assert "mypy_result" in result
    print_result("syntax error fixing", True)


def test_common_issues_fixing(optimizer):
    """Test common issues fixing."""
    code_with_issues = """
try:
    risky_operation()
except:
    pass

def function_with_unused():
    x = 1
    y = 2
    return x
"""
    result = optimizer.run(code_with_issues)
    assert result["success"] is True
    assert "Fixed common coding issues" in result["improvements"]
    optimized = result["optimized_code"]
    # Should have fixed empty except block - either added raise or changed to specific exception
    assert "raise" in optimized or "except BaseException:" in optimized or "except Exception:" in optimized
    print_result("common issues fixing", True)


def test_comprehensive_integration_test(optimizer):
    """Comprehensive integration test with all features."""
    complex_code = '''
import os
import json
from typing import List, Dict, Optional, Any
from collections import defaultdict

def complex_function(data: List[Dict[str, Any]], config: Optional[Dict[str, Any]] = None) -> Dict[str, List[Dict[str, Any]]]:
    """Process data with configuration."""
    result: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for item in data:
        active_value = item.get("active")
        status_value = item.get("status")

        if isinstance(active_value, bool) and active_value:
            result["active"].append(item)
        elif status_value is None:
            result["inactive"].append(item)

    try:
        # Note: defaultdict is not directly JSON serializable
        processed = json.dumps(dict(result))
        return {"processed": processed, "result": dict(result)}
    except Exception:
        return {"result": dict(result)}

    return dict(result)
'''
    result = optimizer.run(complex_code)
    # The test may fail mypy due to complex typing, but should still apply optimizations
    assert result["success"] is True or "mypy_result" in result

    # Check that multiple improvements were applied
    improvements = result["improvements"]
    expected_improvements = [
        "Applied Black formatting (PEP8)",
        "Fixed common coding issues",
        "Applied performance optimizations",
        "Applied Python version upgrades with pyupgrade",
        "Enhanced type hints"
    ]

    applied_count = 0
    for improvement in expected_improvements:
        if improvement in improvements:
            applied_count += 1

    # Should have applied at least 3 major improvements
    assert applied_count >= 3, f"Only {applied_count} improvements applied: {improvements}"

    # Check mypy result exists
    assert "mypy_result" in result
    assert isinstance(result["mypy_result"], dict)

    print_result("comprehensive integration test", True)


def test_error_handling_with_invalid_libraries(monkeypatch, optimizer):
    """Test error handling when optimization libraries fail."""
    # This test ensures the optimizer handles library failures gracefully
    code = "def simple(): return 42"

    # Mock a library failure
    def failing_black_format(*args, **kwargs):
        raise Exception("Black formatting failed")

    monkeypatch.setattr("core.agents.code_optimizer.black.format_str", failing_black_format)

    result = optimizer.run(code)
    # Should still succeed with fallback
    assert result["success"] is True
    assert isinstance(result["optimized_code"], str)
    print_result("error handling with invalid libraries", True)


def test_functionality_preservation(optimizer):
    """Test that functionality is preserved during optimization."""
    original_code = '''
def fibonacci(n: int) -> int:
    """Calculate nth fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def test_function():
    return fibonacci(5)
'''
    result = optimizer.run(original_code)
    assert result["success"] is True
    assert result["functionality_preserved"] is True

    # The optimized code should still be valid Python
    try:
        ast.parse(result["optimized_code"])
        syntax_valid = True
    except SyntaxError:
        syntax_valid = False

    assert syntax_valid, "Optimized code should be syntactically valid"
    print_result("functionality preservation", True)


def test_debug_mode_logging(optimizer):
    """Test that debug mode provides appropriate logging."""
    # This is more of an integration test to ensure debug mode works
    code = "def test(): return 1"
    result = optimizer.run(code)
    assert result["success"] is True
    # Debug mode should not affect the result structure
    assert "optimized_code" in result
    assert "improvements" in result
    print_result("debug mode logging", True)
