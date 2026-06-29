"""
Utilities for loading, validating, and processing datasets such as HumanEval and MBPP.
"""
import os
import json
from typing import List, Dict, Any

def load_json_dataset(path: str) -> List[Dict[str, Any]]:
    """Load a JSON dataset file and return a list of problems."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset file not found: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict) and 'problems' in data:
        return data['problems']
    elif isinstance(data, list):
        return data
    else:
        raise ValueError("Invalid dataset format.")

def validate_problem_structure(problem: Dict[str, Any], required_keys: List[str]) -> bool:
    """Validate that a problem dict contains all required keys."""
    return all(key in problem for key in required_keys)

def validate_dataset(dataset: List[Dict[str, Any]], required_keys: List[str]) -> List[int]:
    """Return indices of invalid problems in the dataset."""
    invalid = []
    for idx, problem in enumerate(dataset):
        if not validate_problem_structure(problem, required_keys):
            invalid.append(idx)
    return invalid

def summary(dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Return a summary of the dataset."""
    return {
        "total_problems": len(dataset),
        "sample_problem": dataset[0] if dataset else None
    }
