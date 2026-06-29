# utils.py
import json
import re
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

# Try optional libs (they may not be installed; fallbacks are provided)
try:
    import dirtyjson  # pip install dirtyjson
except Exception:
    dirtyjson = None

try:
    import json_repair  # pip install jsonrepair
except Exception:
    json_repair = None


def extract_json_like(text: str) -> Optional[str]:
    """
    Extract the first balanced JSON-like substring from text.
    Returns the substring (including leading '{' and trailing '}') or None.
    """
    if not text:
        return None

    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i+1]

    # Fallback: greedy regex (may be noisy but useful)
    m = re.search(r'\{.*\}', text, re.DOTALL)
    return m.group(0) if m else None


def _manual_basic_repair(s: str) -> str:
    """
    Perform light-weight repairs:
    - remove trailing commas before } or ]
    - convert stray single quotes to double quotes in simple cases
    """
    tmp = s.strip()
    # Remove trailing commas
    tmp = re.sub(r",\s*}", "}", tmp)
    tmp = re.sub(r",\s*]", "]", tmp)
    # If there are single quotes but no double quotes, swap them
    if "'" in tmp and '"' not in tmp:
        tmp = tmp.replace("'", '"')
    return tmp


def parse_with_fallbacks(json_str: str) -> Any:
    """
    Try multiple strategies to parse a JSON-like string into Python objects.
    Raises ValueError if all attempts fail.
    """
    last_err = None
    if not json_str:
        raise ValueError("Empty JSON string supplied")

    # Strategy 1: standard json
    try:
        return json.loads(json_str)
    except Exception as e:
        last_err = e

    # Strategy 2: dirtyjson (handles trailing commas, single quotes, etc.)
    if dirtyjson is not None:
        try:
            return dirtyjson.loads(json_str)
        except Exception as e:
            last_err = e

    # Strategy 3: json_repair (attempt to repair then parse)
    if json_repair is not None:
        try:
            repaired = json_repair.repair_json(json_str)
            return json.loads(repaired)
        except Exception as e:
            last_err = e

    # Strategy 4: small manual fixes and try again
    try:
        repaired = _manual_basic_repair(json_str)
        return json.loads(repaired)
    except Exception as e:
        last_err = e

    # If still failing, raise a descriptive error
    raise ValueError(f"All parsing attempts failed. Last error: {last_err}")


def validate_min_schema(obj: Any, required_keys=("function_name", "signature", "description")) -> bool:
    """
    Simple minimal validation: ensure `obj` is a dict and contains required keys.
    """
    if not isinstance(obj, dict):
        return False
    return set(required_keys).issubset(set(obj.keys()))
