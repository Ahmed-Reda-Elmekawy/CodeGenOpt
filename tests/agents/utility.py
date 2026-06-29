from difflib import SequenceMatcher

def assert_text_similar(a, b, threshold=0.2):
    """Assert that two strings are similar above a threshold (0-1),
    or that the expected phrase is a substring of the result (case-insensitive).
    This makes tests robust to LLM output variation."""
    a_lower = a.lower()
    b_lower = b.lower()
    ratio = SequenceMatcher(None, a_lower, b_lower).ratio()
    if ratio >= threshold or a_lower in b_lower:
        return
    assert False, f"Texts not similar enough: {ratio: threshold}\nExpected: {a}\nResult: {b}"
"""
Utility functions and constants for agent tests.
Extracted from common patterns in test files.
"""

SUCCESS_ICON = "✅"
FAIL_ICON = "❌"


def print_result(test_name, passed, details=None):
    icon = SUCCESS_ICON if passed else FAIL_ICON
    msg = f"{icon} {test_name}"
    if details:
        msg += f" — {details}"
    print(msg)
