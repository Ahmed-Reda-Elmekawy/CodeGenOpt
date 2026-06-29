"""
Integration tests for a realistic example: check_dict_case

These tests generate code with the CodeGenerator agent using a realistic JSON spec,
execute the generated function, and validate behavior against the spec examples
and edge cases.

Note: Requires local Ollama model(s) and may take time.
"""

import json
import pytest
from core.agents.code_generator import CodeGenerator
from tests.agents.utility import print_result


@pytest.fixture(scope="module")
def generator():
    # debug_mode=True will print prompts/responses; set False for quieter runs
    return CodeGenerator(debug_mode=False)


def _exec_generated(code: str):
    """
    Execute generated code in an isolated namespace and return the namespace dict.
    Raises any SyntaxError/Exception occurred during exec.
    """
    ns = {}
    exec(compile(code, "<generated>", "exec"), ns)
    return ns


def test_check_dict_case_integration(generator):
    # JSON that output from PromptEngineer (include true/false/null)
    function_spec_json = """
    {
        "function_name": "check_dict_case",
        "signature": "def check_dict_case(dict: dict) -> bool",
        "description": "Returns True if all keys are strings in lower case or all keys are strings in upper case, else returns False. Returns False if the given dictionary is empty.",
        "constraints": ["The input dictionary should not be empty."],
        "examples": [
            {"input": {"a": "apple", "b": "banana"}, "output": true},
            {"input": {"a": "apple", "A": "banana", "B": "banana"}, "output": false},
            {"input": {"8": "banana", "a": "apple"}, "output": false},
            {"input": {"Name": "John", "Age": "36", "City": "Houston"}, "output": false},
            {"input": {"STATE": "NC", "ZIP": "12345"}, "output": true}
        ],
        "exceptions": [
            {"type": "TypeError", "when": "If the input is not a dictionary."}
        ]
    }
    """

    # JSON → dict Python 
    function_spec = json.loads(function_spec_json)

    # Generate code
    generated = generator.run(function_spec)
    try:
        assert isinstance(generated, str) and generated.strip(), "No code generated"
        assert (
            "def check_dict_case" in generated or "def check_dict_case(" in generated
        ), "Generated code missing function definition"
        print_result("Generate check_dict_case", True)
    except AssertionError as e:
        print_result("Generate check_dict_case", False, generated)
        raise

    # Execute generated code and fetch the function
    try:
        ns = _exec_generated(generated)
    except Exception as e:
        print_result("Exec generated code", False, str(e))
        raise

    assert "check_dict_case" in ns, "Function check_dict_case not found after exec"
    func = ns["check_dict_case"]

    # Run all provided examples
    for ex in function_spec["examples"]:
        inp = ex["input"]
        expected = ex["output"]
        try:
            result = func(inp)
        except Exception as e:
            # If implementation raises, fail unless it's allowed for that input in spec
            print_result(
                f"Example run for input={inp}", False, f"Raised exception: {e}"
            )
            raise
        try:
            assert isinstance(
                result, bool
            ), f"Result should be bool for input {inp}, got {type(result)}"
            assert (
                result is expected
            ), f"Expected {expected} but got {result} for input {inp}"
            print_result(f"Example run for input={inp}", True)
        except AssertionError:
            print_result(f"Example run for input={inp}", False, f"Got: {result}")
            raise

    # Empty dict should return False (per description)
    try:
        res_empty = func({})
    except Exception as e:
        print_result("Empty dict handling (raised)", False, str(e))
        raise
    assert res_empty is False, f"Empty dict should return False, got {res_empty}"
    print_result("Empty-dict handling", True)

    # Non-dict input: prefer TypeError, but accept False as alternative behavior
    non_dict_input = 123
    raised_type_error = False
    try:
        out = func(non_dict_input)
    except TypeError:
        raised_type_error = True
        print_result("Non-dict handling (TypeError)", True)
    except Exception as e:
        # Other exceptions are unexpected
        print_result("Non-dict handling (other exception)", False, str(e))
        raise

    if not raised_type_error:
        # If no TypeError, allow returning False (some implementations choose this)
        try:
            assert (
                out is False
            ), f"For non-dict input expected False or TypeError, got {out!r}"
            print_result("Non-dict handling (returned False)", True)
        except AssertionError:
            print_result("Non-dict handling", False, f"Returned: {out!r}")
            raise
