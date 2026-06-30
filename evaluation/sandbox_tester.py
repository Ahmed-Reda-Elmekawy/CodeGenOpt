import io
import contextlib
from typing import Dict, Any


def run_in_sandbox(candidate_code: str, test_code: str) -> Dict[str, Any]:
    """
    Executes candidate solution and corresponding test code in a restricted environment.

    Mimics HumanEval-style validation:
    - The `candidate_code` defines the solution (e.g., a function).
    - The `test_code` contains assertions or a test function.
    - The function returns whether all tests passed successfully.
    """
    local_env = {}
    stdout_capture = io.StringIO()
    success = False
    error_msg = None

    try:
        # Step 1: Compile and execute candidate solution
        compiled_candidate = compile(candidate_code, "<candidate>", "exec")
        exec(compiled_candidate, {}, local_env)

        # Step 2: Execute tests (assert-based)
        with contextlib.redirect_stdout(stdout_capture):
            compiled_test = compile(test_code, "<test>", "exec")
            exec(compiled_test, {}, local_env)

        success = True  # If no exceptions, all tests passed
    except Exception as e:
        error_msg = str(e)

    return {
        "passed": success,
        "error": error_msg,
    }
