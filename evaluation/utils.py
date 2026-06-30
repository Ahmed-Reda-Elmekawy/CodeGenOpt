# evaluation/utils.py
"""
This module provides utility functions for environment inspection,
directory preparation, and resource profiling during function execution.

Main functionalities:
1. ensure_dirs() – Safely create directories if they don't exist.
2. get_env_info() – Collect environment information (Git, Python packages, hardware).
3. timed_run_with_resource_profile() – Execute a function while measuring CPU, memory, and execution time.

These utilities are useful for experimental pipelines, benchmarking,
and reproducibility tracking (e.g., during model evaluation or training).
"""

import os
import time
import psutil
import subprocess
import json
from typing import Callable, Any, Tuple, Dict
import datetime
import platform
import multiprocessing


def ensure_dirs(paths):
    """
    Ensure that all directories listed in `paths` exist.
    If a directory does not exist, it is automatically created.

    Args:
        paths (list[str]): A list of directory paths to check or create.

    Example:
        >>> ensure_dirs(["logs", "results/checkpoints"])
    """
    for p in paths:
        os.makedirs(p, exist_ok=True)


def get_env_info(save: bool = False, auto_push: bool = False) -> Dict[str, Any]:
    """
    Collect and optionally persist environment, system, and Git information.

    Features:
        - Gathers Git commit and branch info.
        - Collects dependencies (prefers requirements.txt or generates via pipreqs).
        - Detects CPU info.
        - Saves results locally to a timestamped JSON file.
        - Commits and pushes results to the current Git repository automatically.

    Args:
        save (bool): Whether to save the collected info to disk.
        auto_push (bool): Whether to commit and push results to GitHub automatically.

    Returns:
        dict: Dictionary containing environment metadata.

    Example:
        >>> get_env_info()
        {
            "timestamp": "2025-10-26T21:30:00Z",
            "git_commit": "a7f3c2b...",
            "git_branch": "main",
            "cpu_model": "Intel(R) Core(TM) i7-11800H",
            "cpu_cores": 16,
            "dependencies": ["numpy==1.26.4", "torch==2.1.0"]
        }
    """

    # --- Git metadata ---
    try:
        git_commit = (
            subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        )
        git_branch = (
            subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            .decode()
            .strip()
        )
    except Exception:
        git_commit = "unknown"
        git_branch = "unknown"

    # --- Installed dependencies ---
    pip_freeze = []
    requirements_path = "requirements.txt"
    try:
        if os.path.exists(requirements_path):
            with open(requirements_path, "r", encoding="utf-8") as f:
                pip_freeze = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
        else:
            print("[INFO] requirements.txt not found — generating via pipreqs...")
            try:
                subprocess.run(
                    ["pipreqs", ".", "--force"], check=True, capture_output=True
                )
                if os.path.exists(requirements_path):
                    with open(requirements_path, "r", encoding="utf-8") as f:
                        pip_freeze = [
                            line.strip()
                            for line in f
                            if line.strip() and not line.startswith("#")
                        ]
            except Exception as e:
                print(f"[WARN] pipreqs generation failed: {e}")
                pip_freeze = (
                    subprocess.check_output(["pip", "freeze"]).decode().splitlines()
                )
    except Exception as e:
        print(f"[ERROR] Failed to collect dependencies: {e}")
        pip_freeze = []

    # --- System info ---
    try:
        cpu = platform.processor()
        cores = multiprocessing.cpu_count()
    except Exception:
        cpu = "unknown"
        cores = 0

    # --- Build metadata dictionary ---
    env_info = {
        "timestamp": datetime.datetime.utc().isoformat() + "Z",
        "git_commit": git_commit,
        "git_branch": git_branch,
        "cpu_model": cpu,
        "cpu_cores": cores,
        "dependencies": pip_freeze,
    }

    # --- Save results locally ---
    if save:
        os.makedirs("env_snapshots", exist_ok=True)
        output_path = f"env_snapshots/env_snapshot_{datetime.datetime.utc().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(env_info, f, indent=4)
        print(f"[INFO] Environment info saved to {output_path}")

    # --- Git commit and push ---
    if auto_push and git_branch != "unknown":
        try:
            # Create a new branch for snapshot
            snapshot_branch = (
                f"env-snapshot/{datetime.datetime.utc().strftime('%Y%m%d_%H%M%S')}"
            )
            subprocess.run(["git", "checkout", "-b", snapshot_branch], check=True)
            subprocess.run(["git", "add", "env_snapshots/"], check=True)
            subprocess.run(
                [
                    "git",
                    "commit",
                    "-m",
                    f"Add environment snapshot ({snapshot_branch})",
                ],
                check=True,
            )
            subprocess.run(["git", "push", "-u", "origin", snapshot_branch], check=True)
            print(f"[INFO] Snapshot committed and pushed to branch '{snapshot_branch}'")
            env_info["snapshot_branch"] = snapshot_branch
        except Exception as e:
            print(f"[WARN] Git push failed: {e}")

    return env_info


def timed_run_with_resource_profile(
    func: Callable[..., Any],
    args: tuple = (),
    kwargs: dict = {},
    sample_interval: float = 0.2,
    timeout: float | None = None,
) -> Tuple[Any, float, Dict]:
    """
    Execute a function and measure its resource usage (CPU, memory) and execution time.

    This function runs `func` in a separate thread while sampling CPU and memory
    consumption periodically using `psutil`. It can also enforce an optional timeout.

    Args:
        func (Callable[..., Any]): Target function to execute.
        args (tuple, optional): Positional arguments for the function. Defaults to ().
        kwargs (dict, optional): Keyword arguments for the function. Defaults to {}.
        sample_interval (float, optional): Time interval (in seconds) between samples. Defaults to 0.2.
        timeout (float | None, optional): Maximum allowed execution time in seconds. Defaults to None.

    Returns:
        tuple:
            - result (Any): The return value of the executed function.
            - duration (float): Total execution time in seconds.
            - resource_stats (dict): Profiling statistics including average and peak CPU/memory usage.

    Raises:
        TimeoutError: If the function exceeds the given timeout.
        Exception: If the executed function raises an exception.

    Example:
        >>> def slow_add(a, b):
        ...     time.sleep(1)
        ...     return a + b
        >>> result, duration, stats = timed_run_with_resource_profile(slow_add, args=(2, 3))
        >>> print(result, duration, stats)
        5 1.01 {'samples': 5, 'cpu_percent_avg': 12.4, 'mem_rss_avg_bytes': 5801984, ...}
    """

    # Get the current process for resource monitoring
    proc = psutil.Process()
    cpu_percent_samples = []
    mem_rss_samples = []

    import threading

    result_container = {}
    exception_container = {}

    def target():
        """Thread target that executes the function and captures its result or exception."""
        try:
            result_container["result"] = func(*args, **kwargs)
        except Exception as e:
            exception_container["exception"] = e

    start = time.time()
    thread = threading.Thread(target=target)
    thread.start()

    try:
        while thread.is_alive():
            # Sample CPU and memory usage periodically
            try:
                cpu = proc.cpu_percent(interval=None)
                mem = proc.memory_info().rss
                cpu_percent_samples.append(cpu)
                mem_rss_samples.append(mem)
            except Exception:
                pass  # Skip sample if psutil fails temporarily

            time.sleep(sample_interval)

            # Timeout handling
            if timeout and (time.time() - start) > timeout:
                raise TimeoutError("timed_run_with_resource_profile timed out")

        thread.join()
    finally:
        end = time.time()

    # Raise any captured exception from the target function
    if "exception" in exception_container:
        raise exception_container["exception"]

    # Compute aggregated statistics
    duration = round(end - start, 4)
    cpu_avg = (
        round(sum(cpu_percent_samples) / len(cpu_percent_samples), 2)
        if cpu_percent_samples
        else 0.0
    )
    cpu_peak = round(max(cpu_percent_samples), 2) if cpu_percent_samples else 0.0
    mem_avg = int(sum(mem_rss_samples) / len(mem_rss_samples)) if mem_rss_samples else 0
    mem_peak = int(max(mem_rss_samples)) if mem_rss_samples else 0

    resource_stats = {
        "samples": len(cpu_percent_samples),
        "cpu_percent_avg": cpu_avg,
        "cpu_percent_peak": cpu_peak,
        "mem_rss_avg_bytes": mem_avg,
        "mem_rss_peak_bytes": mem_peak,
    }

    return result_container.get("result"), duration, resource_stats
