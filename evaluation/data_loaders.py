"""
This module provides a unified set of utilities for loading datasets used in code generation
and evaluation experiments.

It supports:
1. Local JSONL datasets stored on disk.
2. Hugging Face datasets such as:
   - "openai_humaneval" (standard HumanEval benchmark)
   - "tiiuae/evalplus-arabic" (Arabic 3LM variant of HumanEval)

The goal is to offer a consistent interface for retrieving task data
for code generation, completion, and evaluation pipelines.
"""

import json
from typing import List, Dict, Any, Optional
from datasets import load_dataset


def load_local_jsonl(path: str) -> List[Dict[str, Any]]:
    """
    Load a dataset stored locally in JSON Lines (JSONL) format.

    Each line in a JSONL file represents a single JSON object.
    This function reads the file line-by-line, decodes each JSON entry,
    and returns them as a list of Python dictionaries.

    Args:
        path (str): Path to the local `.jsonl` file.

    Returns:
        List[Dict[str, Any]]: A list of parsed JSON objects.

    Example:
        Suppose `data.jsonl` contains:
        {"id": 1, "text": "Hello"}
        {"id": 2, "text": "World"}

        >>> items = load_local_jsonl("data.jsonl")
        >>> print(items)
        [{'id': 1, 'text': 'Hello'}, {'id': 2, 'text': 'World'}]
    """
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue  # skip empty lines
            items.append(json.loads(line))
    return items


def load_humaneval(local_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Load the HumanEval dataset, either from a local JSONL file or directly from Hugging Face Hub.

    HumanEval is a benchmark created by OpenAI to evaluate code generation models.
    It consists of programming problems with a prompt, reference solution, and unit tests.

    Args:
        local_path (Optional[str]): Path to a local JSONL file containing the dataset.
                                   If provided, it is used instead of downloading from the Hub.

    Returns:
        List[Dict[str, Any]]: A list of dataset items, where each item includes:
            - 'task_id': Unique identifier for the task.
            - 'prompt': The programming task or problem description.
            - 'canonical_solution': The official reference solution.
            - 'test': The corresponding unit test code.

    Example:
        >>> tasks = load_humaneval()
        >>> print(tasks[0].keys())
        dict_keys(['task_id', 'prompt', 'canonical_solution', 'test'])
    """
    if local_path:
        return load_local_jsonl(local_path)

    # Load HumanEval from the Hugging Face Datasets Hub
    ds = load_dataset("openai_humaneval")
    out = []

    for item in ds["test"]:
        out.append(
            {
                "task_id": item.get("task_id"),
                "prompt": item.get("prompt"),
                "canonical_solution": item.get("canonical_solution", ""),
                "test": item.get("test"),
            }
        )

    return out


def load_3lm(local_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Load the 3LM (Arabic HumanEval-style) dataset.

    This dataset is a localized adaptation of HumanEval for Arabic,
    provided by the TII UAE (Technology Innovation Institute) under
    the name "evalplus-arabic".

    Args:
        local_path (Optional[str]): Path to a local JSONL file containing the dataset.
                                   If provided, it is used instead of downloading from the Hub.

    Returns:
        List[Dict[str, Any]]: A list of dataset entries, each with:
            - 'task_id': Task identifier.
            - 'prompt': Arabic programming prompt.
            - 'canonical_solution': The reference implementation.
            - 'test': Unit test for functional verification.

    Example:
        >>> tasks = load_3lm()
        >>> print(tasks[0]['prompt'])
        '# اكتب دالة لإيجاد مجموع الأعداد الزوجية في قائمة...'
    """
    if local_path:
        return load_local_jsonl(local_path)

    # Load specific configuration for the Arabic HumanEval variant
    ds = load_dataset("tiiuae/evalplus-arabic", "humanevalplus-arabic")
    out = []

    for item in ds["test"]:
        out.append(
            {
                "task_id": item.get("task_id"),
                "prompt": item.get("prompt"),  # Arabic prompt text
                "canonical_solution": item.get("canonical_solution", ""),
                "test": item.get("test"),
            }
        )

    return out


def load_dataset_by_name(name: str, local_path: Optional[str] = None):
    """
    Unified dataset loader that selects the correct loading function based on the dataset name.

    Supports:
    - "humaneval" (or variations like "human-eval", "human_eval")
    - "3lm" / "evalplus-arabic" / "evalplus" (Arabic variant)
    - Custom local JSONL files (as a fallback option)

    Args:
        name (str): Dataset name or alias.
        local_path (Optional[str]): Optional path to a local JSONL file.

    Returns:
        List[Dict[str, Any]]: The loaded dataset as a list of dictionaries.

    Raises:
        ValueError: If the dataset name is not recognized and no local path is provided.

    Example:
        >>> load_dataset_by_name("humaneval")
        >>> load_dataset_by_name("3lm")
        >>> load_dataset_by_name("custom", "my_data.jsonl")
    """
    name = name.lower()

    # Route to the appropriate loader
    if name in ("humaneval", "human-eval", "human_eval"):
        return load_humaneval(local_path)
    if name in ("3lm", "evalplus-arabic", "evalplus"):
        return load_3lm(local_path)

    # Fallback to a local JSONL dataset if path is given
    if local_path:
        return load_local_jsonl(local_path)

    # If no match found → raise clear error message
    raise ValueError(
        f"Unknown dataset: {name}. Provide --local-path to load a JSONL file."
    )
