# evaluation/run_evaluation.py
import os
import json
import argparse
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from core.agents.coordinator import Coordinator
from evaluation.data_loaders import load_dataset_by_name
from evaluation.sandbox_tester import run_in_sandbox
from evaluation.utils import ensure_dirs, get_env_info, timed_run_with_resource_profile
from evaluation.metrics import (
    compute_latency_stats,
    aggregate_resource_stats,
    compute_pass_at_k,
    is_syntax_valid,
)

RESULTS_DIR = "evaluation/results"
RAW_DIR = os.path.join(RESULTS_DIR, "raw")
SUMMARY_DIR = os.path.join(RESULTS_DIR, "summary")


def run_evaluation(
    dataset_name: str,
    dataset_local_path: Optional[str],
    model_config: Optional[Dict[str, Any]] = None,
    use_translator: bool = True,
    use_optimizer: bool = True,
    shared_llm: bool = True,
    cloud_llm: bool = False,
    debug_mode: bool = False,
    attempts_per_task: int = 1,
    dataset_limit: Optional[int] = None,
    experiment_name: Optional[str] = None,
    sample_indices: Optional[List[int]] = None,
):

    # Configure logging
    if debug_mode:
        import logging
        # Configure global logging
        logging.basicConfig(
            level=logging.DEBUG,  # Set the desired logging level here, e.g., DEBUG, INFO, WARNING, ERROR
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # setup dirs
    ensure_dirs([RAW_DIR, SUMMARY_DIR])

    dataset = load_dataset_by_name(dataset_name, dataset_local_path)
    
    # Apply sample indices if provided (for matched pairs design)
    if sample_indices is not None:
        print(f"Using provided sample indices: {sample_indices[:10]}... (total: {len(sample_indices)})")
        dataset = [dataset[i] for i in sample_indices if i < len(dataset)]
    
    if dataset_limit:
        dataset = dataset[:dataset_limit]

    coordinator = Coordinator(
        llm_config=model_config,
        use_translator=use_translator,
        use_optimizer=use_optimizer,
        shared_llm=shared_llm,
        cloud_llm=cloud_llm,
        debug_mode=debug_mode,
    )

    all_results = []
    for i, task in enumerate(dataset):
        task_id = task.get("task_id", f"task_{i}")
        prompt = task.get("prompt", "")
        test = task.get("test", "")
        canonical_solution = task.get("canonical_solution", "")  # Reference solution if available
        entry_point = task.get("entry_point", "")  # Function name to test
        
        record = {
            "task_id": task_id,
            "task_index": sample_indices[i] if sample_indices else i,  # Original dataset index
            "prompt": prompt,
            "test": test,
            "canonical_solution": canonical_solution,
            "entry_point": entry_point,
            "attempts": [],
        }

        for attempt_idx in range(attempts_per_task):
            try:
                # Track per-agent timing if coordinator supports it
                import time
                pipeline_start = time.time()
                
                def call_pipeline():
                    return coordinator.run(prompt)

                result, duration, resource_stats = timed_run_with_resource_profile(
                    call_pipeline, sample_interval=0.5, timeout=4000
                )
                
                pipeline_end = time.time()
                total_pipeline_time = pipeline_end - pipeline_start
                
                # extract final code and metadata
                final_code = (
                    result.get("final_code", "") if isinstance(result, dict) else ""
                )
                syntax_ok = is_syntax_valid(final_code)
                
                # Classify errors more specifically
                error_type = None
                error_message = None
                if not syntax_ok:
                    error_type = "syntax_error"
                    error_message = "Generated code has syntax errors"
                
                # Run human_eval-style test
                sandbox_result = run_in_sandbox(final_code, test)
                
                # Update error classification based on test results
                if not sandbox_result["passed"]:
                    if syntax_ok:  # Syntax is OK but tests failed
                        error_type = "test_failure"
                        error_message = sandbox_result.get("error", "Test cases failed")
                
                # Extract intermediate outputs if available in result
                intermediate_outputs = {}
                if isinstance(result, dict):
                    intermediate_outputs = {
                        "translated_prompt": result.get("translated_prompt", ""),
                        "problem_spec": result.get("problem_spec", ""),
                        "generated_code_raw": result.get("generated_code_raw", ""),
                        "optimization_steps": result.get("optimization_steps", []),
                    }

                attempt_record = {
                    "attempt_idx": attempt_idx + 1,
                    "duration_sec": duration,
                    "total_pipeline_time_sec": total_pipeline_time,
                    "resource_stats": resource_stats,
                    "final_code": final_code,
                    "intermediate_outputs": intermediate_outputs,
                    "syntax_ok": syntax_ok,
                    "passed": sandbox_result["passed"],
                    "test_output": sandbox_result.get("output", ""),
                    "error_type": error_type,
                    "error_message": error_message,
                    "error": None if sandbox_result["passed"] else error_message,
                }
            except Exception as e:
                error_str = str(e)
                # Classify exception type
                if "timeout" in error_str.lower():
                    exc_error_type = "timeout"
                elif "connection" in error_str.lower() or "network" in error_str.lower():
                    exc_error_type = "network_error"
                elif "memory" in error_str.lower():
                    exc_error_type = "memory_error"
                else:
                    exc_error_type = "runtime_error"
                
                attempt_record = {
                    "attempt_idx": attempt_idx,
                    "duration_sec": None,
                    "total_pipeline_time_sec": None,
                    "resource_stats": {},
                    "final_code": "",
                    "intermediate_outputs": {},
                    "syntax_ok": False,
                    "passed": False,
                    "test_output": None,
                    "error_type": exc_error_type,
                    "error_message": error_str,
                    "error": error_str,
                }

            record["attempts"].append(attempt_record)

        # # save per-task
        # safe_task_id = task_id.replace("/", "_").replace(" ", "_")
        # out_path = os.path.join(RAW_DIR, f"{safe_task_id}.json")
        # with open(out_path, "w", encoding="utf-8") as f:
        #     json.dump(record, f, ensure_ascii=False, indent=2)

        all_results.append(record)

    # aggregate
    durations = [
        a["duration_sec"]
        for t in all_results
        for a in t["attempts"]
        if a.get("duration_sec") is not None
    ]
    resource_list = [
        a["resource_stats"]
        for t in all_results
        for a in t["attempts"]
        if a.get("resource_stats")
    ]
    latency_stats = compute_latency_stats(durations)
    resource_stats = aggregate_resource_stats(resource_list)
    pass_stats = compute_pass_at_k(all_results, k=1)

    env = get_env_info()
    timestamp = datetime.now(
        timezone.utc
    ).isoformat()  # datetime.now().strftime("%Y%m%d_%H%M%S")

    # Build experiment identifier (must be before summary dict)
    exp_id = experiment_name if experiment_name else f"{dataset_name}_{timestamp}"

    summary = {
        "timestamp": timestamp,
        "experiment_name": experiment_name,
        "experiment_id": exp_id,
        "test_config": {
            "dataset": dataset_name,
            "sample_indices": sample_indices,
            "num_tasks": len(all_results),
            "attempts_per_task": attempts_per_task,
            "use_translator": use_translator,
            "use_optimizer": use_optimizer,
            "shared_llm": shared_llm,
            "cloud_llm": cloud_llm,
        },
        "model_config": model_config,
        "latency": latency_stats,
        "resource": resource_stats,
        "pass_stats": pass_stats,
        "env_info": env,
    }

    # save summary with enhanced metadata
    summary_filename = f"summary_{exp_id}.json"
    summary_path = os.path.join(SUMMARY_DIR, summary_filename)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(
            {"summary": summary, "results": all_results},
            f,
            ensure_ascii=False,
            indent=2,
        )

    print("Saved summary to:", summary_path)

    # --- Save detailed results for appendix/analysis ---
    # Save individual task results for detailed analysis
    details_path = os.path.join(RAW_DIR, f"details_{exp_id}.json")
    with open(details_path, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": summary,
            "results": all_results
        }, f, ensure_ascii=False, indent=2)
    print(f"Saved detailed results to: {details_path}")
    
    # --- Save summary as CSV for easy import to Excel/SPSS ---
    csv_summary_path = os.path.join(SUMMARY_DIR, f"summary_{exp_id}.csv")
    save_summary_csv(summary, csv_summary_path)
    print(f"Saved CSV summary to: {csv_summary_path}")
    
    # --- Auto commit and push results to GitHub ---
    try:
        import subprocess

        # Create a branch name based on experiment
        safe_exp_name = exp_id.replace("/", "_").replace(" ", "_")
        branch_name = f"eval-run/{safe_exp_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Also save a comparison-ready summary file
        comparison_path = os.path.join(SUMMARY_DIR, f"comparison_ready_{exp_id}.json")
        save_comparison_format(summary, all_results, comparison_path)

        # Create new branch
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)

        # Stage all evaluation results and summaries
        subprocess.run(["git", "add", "evaluation/results/"], check=True)

        # Commit with descriptive message including experiment name
        commit_msg = f"Add evaluation results for {exp_id} ({timestamp})"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)

        # Push to GitHub and set upstream
        subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)

        print(f"[INFO] Evaluation committed and pushed to branch '{branch_name}'")

    except Exception as e:
        print(f"[WARN] Git push failed: {e}")

    return summary_path


def save_summary_csv(summary: Dict[str, Any], csv_path: str):
    """Save summary statistics as CSV for easy import to Excel/SPSS."""
    import csv
    
    # Flatten nested dictionaries for CSV
    flat_summary = {
        "timestamp": summary.get("timestamp", ""),
        "experiment_name": summary.get("experiment_name", ""),
        "experiment_id": summary.get("experiment_id", ""),
        "dataset": summary.get("test_config", {}).get("dataset", ""),
        "num_tasks": summary.get("test_config", {}).get("num_tasks", 0),
        "use_translator": summary.get("test_config", {}).get("use_translator", False),
        "use_optimizer": summary.get("test_config", {}).get("use_optimizer", False),
        "shared_llm": summary.get("test_config", {}).get("shared_llm", False),
        "cloud_llm": summary.get("test_config", {}).get("cloud_llm", False),
        # Latency stats
        "latency_count": summary.get("latency", {}).get("count", 0),
        "latency_mean": summary.get("latency", {}).get("mean", 0),
        "latency_median": summary.get("latency", {}).get("median", 0),
        "latency_stdev": summary.get("latency", {}).get("stdev", 0),
        "latency_p50": summary.get("latency", {}).get("p50", 0),
        "latency_p90": summary.get("latency", {}).get("p90", 0),
        "latency_p95": summary.get("latency", {}).get("p95", 0),
        # Resource stats
        "cpu_avg": summary.get("resource", {}).get("cpu_percent_avg_mean", 0),
        "cpu_peak": summary.get("resource", {}).get("cpu_percent_peak_max", 0),
        "mem_avg_mb": summary.get("resource", {}).get("mem_rss_avg_mean_bytes", 0) / 1_000_000,
        "mem_peak_mb": summary.get("resource", {}).get("mem_rss_peak_max_bytes", 0) / 1_000_000,
        # Pass stats
        "total_tasks": summary.get("pass_stats", {}).get("total_tasks", 0),
        "passed_at_1": summary.get("pass_stats", {}).get("passed_at_1", 0),
        "pass_at_1_pct": summary.get("pass_stats", {}).get("pass_at_1_pct", 0),
        # Environment
        "git_commit": summary.get("env_info", {}).get("git_commit", "")[:8],
        "cpu_model": summary.get("env_info", {}).get("cpu_model", ""),
        "cpu_cores": summary.get("env_info", {}).get("cpu_cores", 0),
    }
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=flat_summary.keys())
        writer.writeheader()
        writer.writerow(flat_summary)
    
    print(f"Saved CSV summary: {csv_path}")


def save_comparison_format(summary: Dict[str, Any], all_results: List[Dict], comparison_path: str):
    """Save results in a format optimized for cross-experiment comparison."""
    comparison_data = {
        "metadata": {
            "experiment_name": summary.get("experiment_name"),
            "experiment_id": summary.get("experiment_id"),
            "timestamp": summary.get("timestamp"),
            "dataset": summary.get("test_config", {}).get("dataset"),
            "config": summary.get("test_config"),
        },
        "aggregated": {
            "pass_at_1_pct": summary.get("pass_stats", {}).get("pass_at_1_pct"),
            "pass_at_k_pct": summary.get("pass_stats", {}).get("pass_at_k_pct"),
            "latency_mean": summary.get("latency", {}).get("mean"),
            "latency_median": summary.get("latency", {}).get("median"),
            "latency_p95": summary.get("latency", {}).get("p95"),
            "cpu_avg": summary.get("resource", {}).get("cpu_percent_avg_mean"),
            "cpu_peak": summary.get("resource", {}).get("cpu_percent_peak_max"),
            "mem_peak_mb": summary.get("resource", {}).get("mem_rss_peak_max_bytes", 0) / 1_000_000,
        },
        "per_task": [
            {
                "task_id": r.get("task_id"),
                "task_index": r.get("task_index"),
                "passed": r.get("attempts", [{}])[0].get("passed", False),
                "syntax_ok": r.get("attempts", [{}])[0].get("syntax_ok", False),
                "error_type": r.get("attempts", [{}])[0].get("error_type"),
                "duration_sec": r.get("attempts", [{}])[0].get("duration_sec"),
            }
            for r in all_results
        ]
    }
    
    with open(comparison_path, 'w', encoding='utf-8') as f:
        json.dump(comparison_data, f, ensure_ascii=False, indent=2)
    
    print(f"Saved comparison-ready data: {comparison_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Run evaluation over datasets (humaneval, 3lm, mbpp or local JSONL)."
    )
    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="Dataset name: humaneval | 3lm | mbpp | local",
    )
    parser.add_argument(
        "--dataset_local_path",
        type=str,
        default=None,
        help="Local JSONL path (if dataset is local or to override HF).",
    )
    parser.add_argument(
        "--attempts", type=int, default=1, help="Attempts per task (for pass@k)."
    )
    parser.add_argument(
        "--disable_translator",
        action="store_true",
        help="Disable translator (enabled by default).",
    )
    parser.add_argument(
        "--disable_optimizer",
        action="store_true",
        help="Disable optimizer (enabled by default).",
    )
    parser.add_argument(
        "--shared_llm", action="store_true", help="Use shared LLM for all Agents."
    )
    parser.add_argument(
        "--cloud_llm", action="store_true", help="Use cloud LLM for all Agents."
    )
    parser.add_argument("--debug_mode", action="store_true", help="Enable debug mode.")
    parser.add_argument(
        "--dataset_limit",
        type=int,
        default=None,
        help="Limit number of tasks (for quick tests).",
    )
    parser.add_argument(
        "--model_config",
        type=str,
        default=None,
        help="Path to JSON file or inline JSON string specifying model configuration.",
    )
    parser.add_argument(
        "--experiment_name",
        type=str,
        default=None,
        help="Experiment identifier (e.g., T1_CLOUD_HE_50_OPT). Used for naming output files.",
    )
    parser.add_argument(
        "--sample_indices_file",
        type=str,
        default=None,
        help="Path to JSON file containing sample indices (for reproducible sampling).",
    )
    args = parser.parse_args()

    # Parse model config (either inline JSON or file path)
    model_cfg = None
    if args.model_config:
        try:
            if os.path.exists(args.model_config):
                with open(args.model_config, "r", encoding="utf-8") as f:
                    model_cfg = json.load(f)
            else:
                model_cfg = json.loads(args.model_config)
        except Exception as e:
            print(f"Failed to parse model_config: {e}")
            model_cfg = None
    
    # Load sample indices if provided
    sample_indices = None
    if args.sample_indices_file:
        try:
            with open(args.sample_indices_file, 'r') as f:
                indices_data = json.load(f)
                sample_indices = indices_data.get('selected_indices', None)
                print(f"Loaded sample indices from {args.sample_indices_file}: {len(sample_indices)} tasks")
        except Exception as e:
            print(f"Warning: Could not load sample indices file: {e}")
    
    print("parse_args: ", args)
    run_evaluation(
        dataset_name=args.dataset,
        dataset_local_path=args.dataset_local_path,
        model_config=model_cfg,
        attempts_per_task=args.attempts,
        use_translator=not args.disable_translator,
        use_optimizer=not args.disable_optimizer,
        shared_llm=args.shared_llm,
        cloud_llm=args.cloud_llm,
        debug_mode=args.debug_mode,
        dataset_limit=args.dataset_limit,
        experiment_name=args.experiment_name,
        sample_indices=sample_indices,
    )


if __name__ == "__main__":
    main()
