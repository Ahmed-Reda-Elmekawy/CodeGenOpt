# evaluation/metrics.py
"""
This module defines key evaluation and analysis utilities for code generation
and model performance benchmarking.

It provides metrics for:
1. Syntax validation of generated code.
2. Latency and timing statistics (e.g., mean, median, percentiles).
3. Aggregation of resource usage data (CPU and memory).
4. Pass@k computation — a common metric in code generation tasks indicating
   the probability that a correct solution appears within the top-k model outputs.

These metrics are used to evaluate both the **quality** and **efficiency**
of AI-generated code during model evaluation.
"""

import statistics
from typing import List, Dict, Any


def is_syntax_valid(code: str) -> bool:
    """
    Check whether a given Python code string is syntactically valid.

    The function attempts to compile the provided code. If the code compiles successfully,
    it is considered valid; otherwise, a syntax or compilation error is caught.

    Args:
        code (str): Python code as a string.

    Returns:
        bool: True if the code is syntactically valid, False otherwise.

    Example:
        >>> is_syntax_valid("print('Hello')")
        True
        >>> is_syntax_valid("if True print('Hi')")
        False
    """
    try:
        compile(code, "<string>", "exec")
        return True
    except Exception:
        return False


def compute_latency_stats(durations: List[float]) -> Dict[str, float]:
    """
    Compute detailed latency statistics from a list of duration values (in seconds).

    This function summarizes time-based performance metrics typically collected
    during model inference, benchmarking, or evaluation runs.

    Args:
        durations (List[float]): List of duration values (in seconds).

    Returns:
        Dict[str, float]: Statistical summary including:
            - count: Number of samples.
            - mean: Average duration.
            - median: Middle value.
            - stdev: Population standard deviation.
            - p50, p90, p95: Percentile latency values.

    Example:
        >>> compute_latency_stats([0.1, 0.15, 0.2])
        {
            'count': 3,
            'mean': 0.15,
            'median': 0.15,
            'stdev': 0.0412,
            'p50': 0.15,
            'p90': 0.2,
            'p95': 0.2
        }
    """
    if not durations:
        return {}

    sorted_d = sorted(durations)
    return {
        "count": len(durations),
        "mean": round(statistics.mean(durations), 4),
        "median": round(statistics.median(durations), 4),
        "stdev": round(statistics.pstdev(durations), 4) if len(durations) > 1 else 0.0,
        "p50": round(sorted_d[int(len(sorted_d) * 0.5)], 4),
        "p90": round(sorted_d[max(0, int(len(sorted_d) * 0.9) - 1)], 4),
        "p95": round(sorted_d[max(0, int(len(sorted_d) * 0.95) - 1)], 4),
    }


def aggregate_resource_stats(resource_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate resource usage statistics across multiple function runs.

    This function combines multiple resource usage profiles (collected via tools
    like `psutil`) and computes mean and peak summaries for CPU and memory usage.

    Args:
        resource_list (List[Dict[str, Any]]): List of dictionaries containing
            per-run resource statistics. Each dictionary is expected to have:
                - "cpu_percent_avg"
                - "cpu_percent_peak"
                - "mem_rss_avg_bytes"
                - "mem_rss_peak_bytes"

    Returns:
        Dict[str, Any]: Aggregated resource statistics including:
            - cpu_percent_avg_mean: Average of average CPU usage.
            - cpu_percent_peak_max: Highest peak CPU usage observed.
            - mem_rss_avg_mean_bytes: Mean of average memory usage.
            - mem_rss_peak_max_bytes: Maximum peak memory usage in bytes.

    Example:
        >>> stats = [
        ...     {"cpu_percent_avg": 12, "cpu_percent_peak": 50, "mem_rss_avg_bytes": 10e6, "mem_rss_peak_bytes": 20e6},
        ...     {"cpu_percent_avg": 8, "cpu_percent_peak": 40, "mem_rss_avg_bytes": 12e6, "mem_rss_peak_bytes": 25e6}
        ... ]
        >>> aggregate_resource_stats(stats)
        {
            'cpu_percent_avg_mean': 10.0,
            'cpu_percent_peak_max': 50.0,
            'mem_rss_avg_mean_bytes': 11000000,
            'mem_rss_peak_max_bytes': 25000000
        }
    """
    if not resource_list:
        return {}

    # Extract relevant metrics across runs
    cpu_avgs = [r.get("cpu_percent_avg", 0) for r in resource_list]
    cpu_peaks = [r.get("cpu_percent_peak", 0) for r in resource_list]
    mem_avgs = [r.get("mem_rss_avg_bytes", 0) for r in resource_list]
    mem_peaks = [r.get("mem_rss_peak_bytes", 0) for r in resource_list]

    return {
        "cpu_percent_avg_mean": round(sum(cpu_avgs) / len(cpu_avgs), 2),
        "cpu_percent_peak_max": round(max(cpu_peaks), 2),
        "mem_rss_avg_mean_bytes": int(sum(mem_avgs) / len(mem_avgs)),
        "mem_rss_peak_max_bytes": int(max(mem_peaks)),
    }


def compute_pass_at_k(results: List[Dict[str, Any]], k: int = 1) -> Dict[str, Any]:
    """
    Compute the Pass@k metric for a list of code generation results.

    Pass@k measures the proportion of problems for which at least one
    of the top-k generated solutions passes all test cases.
    It is a standard metric used in evaluating code generation models
    (e.g., Codex, CodeT5, CodeLlama).

    Args:
        results (List[Dict[str, Any]]): List of results where each item represents a coding task.
            Each task dictionary is expected to include an "attempts" list, where
            each attempt is a dictionary containing a `passed: bool` field.
        k (int, optional): The cutoff rank for evaluation. Defaults to 1.

    Returns:
        Dict[str, Any]: Summary of Pass@k metrics including:
            - total_tasks: Total number of evaluated problems.
            - passed_at_1: Number of tasks passed at least once (first attempt).
            - passed_at_k: Number of tasks passed within top-k attempts.
            - pass_at_1_pct: Percentage of total passed at 1.
            - pass_at_k_pct: Percentage of total passed within k.

    Example:
        >>> sample_results = [
        ...     {"attempts": [{"passed": False}, {"passed": True}]},
        ...     {"attempts": [{"passed": False}]},
        ... ]
        >>> compute_pass_at_k(sample_results, k=2)
        {
            'total_tasks': 2,
            'passed_at_1': 0,
            'passed_at_2': 1,
            'pass_at_1_pct': 0.0,
            'pass_at_2_pct': 50.0
        }
    """
    total = len(results)

    # Count how many tasks have *any* successful attempt in all attempts
    passed_at_1 = sum(
        1 for r in results if any(a.get("passed", False) for a in r.get("attempts", []))
    )

    # Count tasks that pass within top-k attempts
    passed_at_k = 0
    for r in results:
        attempts = r.get("attempts", [])[:k]
        if any(a.get("passed", False) for a in attempts):
            passed_at_k += 1

    return {
        "total_tasks": total,
        "passed_at_1": passed_at_1,
        f"passed_at_{k}": passed_at_k,
        "pass_at_1_pct": round(passed_at_1 / total * 100, 3) if total else 0.0,
        f"pass_at_{k}_pct": round(passed_at_k / total * 100, 3) if total else 0.0,
    }
