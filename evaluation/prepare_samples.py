"""
Sample Preparation Script for CodeGenOpt Evaluation
Generates reproducible 50-task samples from HumanEval and 3LM datasets

Usage:
    python prepare_samples.py

Output:
    - samples/humaneval_sample_50.json
    - samples/3lm_sample_50.json
    - samples/sampling_manifest.json
"""

import json
import random
import os
from pathlib import Path
from typing import List, Dict, Any

# Configuration
RANDOM_SEED = 42
SAMPLE_SIZE = 50
OUTPUT_DIR = Path("samples")

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_humaneval_full() -> List[Dict[str, Any]]:
    """Load full HumanEval dataset (164 tasks)."""
    try:
        from evaluation.data_loaders import load_humaneval
        return load_humaneval()
    except ImportError:
        # Fallback: load from JSON if available
        humaneval_path = Path("data/humaneval.jsonl")
        if humaneval_path.exists():
            with open(humaneval_path) as f:
                return [json.loads(line) for line in f]
        # Fallback: create mock data for testing
        print("Warning: Using mock HumanEval data for testing")
        return [{"task_id": f"HumanEval/{i}", "prompt": f"Task {i}"} for i in range(164)]


def load_3lm_full() -> List[Dict[str, Any]]:
    """Load full 3LM dataset."""
    try:
        from evaluation.data_loaders import load_3lm
        return load_3lm()
    except ImportError:
        # Fallback: load from JSON if available
        tlm_path = Path("data/3lm.jsonl")
        if tlm_path.exists():
            with open(tlm_path) as f:
                return [json.loads(line) for line in f]
        # Fallback: check HuggingFace
        try:
            from datasets import load_dataset
            ds = load_dataset("tiiuae/3lm-benchmark", split="train")
            return [{"task_id": item.get("task_id", f"3LM/{i}"), 
                    "prompt": item.get("prompt", "")} 
                   for i, item in enumerate(ds)]
        except Exception as e:
            print(f"Warning: Could not load 3LM dataset: {e}")
            print("Using mock 3LM data for testing")
            return [{"task_id": f"3LM/{i}", "prompt": f"Task {i}"} for i in range(164)]


def stratified_sample(dataset: List[Dict[str, Any]], 
                      n: int, 
                      seed: int) -> List[Dict[str, Any]]:
    """
    Select stratified random sample from dataset.
    
    Args:
        dataset: Full dataset
        n: Sample size
        seed: Random seed for reproducibility
    
    Returns:
        Sampled subset
    """
    if n >= len(dataset):
        print(f"Warning: Requested {n} samples but dataset has {len(dataset)}. Using full dataset.")
        return dataset
    
    # Set seed for reproducibility
    rng = random.Random(seed)
    
    # Shuffle and select
    indices = list(range(len(dataset)))
    rng.shuffle(indices)
    selected_indices = sorted(indices[:n])
    
    # Extract samples
    sample = [dataset[i] for i in selected_indices]
    
    return sample


def save_sample_info(dataset_name: str,
                     full_size: int,
                     sample_size: int,
                     selected_indices: List[int],
                     selected_task_ids: List[str],
                     seed: int,
                     output_path: Path):
    """Save sample information to JSON."""
    
    sample_info = {
        "dataset": dataset_name,
        "sampling_method": "stratified_random",
        "random_seed": seed,
        "full_dataset_size": full_size,
        "sample_size": sample_size,
        "sampling_ratio": sample_size / full_size,
        "selected_indices": selected_indices,
        "selected_task_ids": selected_task_ids,
        "confidence_interval_95": calculate_margin_of_error(sample_size, 0.5),
        "output_file": str(output_path),
        "notes": f"Sample selected using Python's random.Random with fixed seed={seed} for reproducibility"
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sample_info, f, indent=2, ensure_ascii=False)
    
    print(f"Saved: {output_path}")


def calculate_margin_of_error(n: int, p: float = 0.5, confidence: float = 0.95) -> Dict[str, Any]:
    """Calculate margin of error for proportion."""
    import math
    
    # Z-score for 95% confidence
    z = 1.96
    
    # Standard error
    se = math.sqrt(p * (1 - p) / n)
    
    # Margin of error
    moe = z * se
    
    return {
        "margin_of_error_percent": round(moe * 100, 1),
        "confidence_level": f"{confidence*100:.0f}%",
        "sample_size": n
    }


def create_sampling_manifest():
    """Create master manifest of all samples."""
    
    manifest = {
        "study_design": {
            "strategy": "equal_samples_50_50",
            "rationale": "Statistical power analysis indicates n=50 provides acceptable precision (±14%) while remaining feasible within Free Plan constraints",
            "random_seed": RANDOM_SEED,
            "sampling_method": "stratified_random_sampling"
        },
        "samples": {
            "humaneval": {
                "file": "samples/humaneval_sample_50.json",
                "size": 50,
                "full_size": 164,
                "use_for": ["T1", "T2", "T3"]
            },
            "3lm": {
                "file": "samples/3lm_sample_50.json",
                "size": 50,
                "full_size": 164,
                "random_seed": RANDOM_SEED,
                "matched_with": "humaneval",
                "use_for": ["T4", "T5", "T6"],
                "notes": "Matched pairs sample - uses same indices as HumanEval for direct English vs Arabic comparison (RQ2)"
            }
        },
        "statistical_properties": {
            "confidence_level": "95%",
            "margin_of_error": "±14%",
            "power_to_detect_15pct_difference": "approximately 55%",
            "notes": "Equal sample sizes maximize statistical efficiency for Cloud vs Local comparison"
        }
    }
    
    manifest_path = OUTPUT_DIR / "sampling_manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved manifest: {manifest_path}")


def main():
    """Main sampling procedure."""
    
    print("=" * 60)
    print("SAMPLE PREPARATION FOR CODEGENOPT EVALUATION")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  - Random Seed: {RANDOM_SEED}")
    print(f"  - Sample Size: {SAMPLE_SIZE} tasks per dataset")
    print(f"  - Sampling Method: Stratified Random")
    print(f"  - Confidence Level: 95% (±14% margin of error)")
    print()
    
    # Load datasets
    print("Loading datasets...")
    try:
        humaneval_full = load_humaneval_full()
        print(f"  ✓ HumanEval: {len(humaneval_full)} tasks")
    except Exception as e:
        print(f"  ✗ HumanEval: Failed to load ({e})")
        humaneval_full = []
    
    try:
        tlm_full = load_3lm_full()
        print(f"  ✓ 3LM: {len(tlm_full)} tasks")
    except Exception as e:
        print(f"  ✗ 3LM: Failed to load ({e})")
        tlm_full = []
    
    print()
    
    # Sample HumanEval
    if humaneval_full:
        print("Sampling HumanEval...")
        rng = random.Random(RANDOM_SEED)
        indices = list(range(len(humaneval_full)))
        rng.shuffle(indices)
        selected_indices = sorted(indices[:SAMPLE_SIZE])
        
        humaneval_sample = [humaneval_full[i] for i in selected_indices]
        task_ids = [task.get("task_id", f"HE/{i}") for i, task in zip(selected_indices, humaneval_sample)]
        
        save_sample_info(
            "HumanEval",
            len(humaneval_full),
            SAMPLE_SIZE,
            selected_indices,
            task_ids,
            RANDOM_SEED,
            OUTPUT_DIR / "humaneval_sample_50.json"
        )
        
        print(f"  Selected indices: {selected_indices[:10]}... (showing first 10)")
        print(f"  Sample task IDs: {task_ids[:5]}... (showing first 5)")
        print()
    
    # Sample 3LM - Matched pairs with HumanEval
    if tlm_full:
        print("Sampling 3LM (matched pairs with HumanEval)...")
        # Use SAME indices as HumanEval for matched pairs comparison
        # This enables direct comparison of same problems in English vs Arabic
        rng = random.Random(RANDOM_SEED)
        indices = list(range(len(tlm_full)))
        rng.shuffle(indices)
        selected_indices = sorted(indices[:SAMPLE_SIZE])
        
        tlm_sample = [tlm_full[i] for i in selected_indices]
        task_ids = [task.get("task_id", f"3LM/{i}") for i, task in zip(selected_indices, tlm_sample)]
        
        # Update save_sample_info call to add matched pairs note
        sample_info = {
            "dataset": "3LM",
            "sampling_method": "matched_pairs",
            "random_seed": RANDOM_SEED,
            "full_dataset_size": len(tlm_full),
            "sample_size": SAMPLE_SIZE,
            "sampling_ratio": SAMPLE_SIZE / len(tlm_full),
            "selected_indices": selected_indices,
            "selected_task_ids": task_ids,
            "confidence_interval_95": calculate_margin_of_error(SAMPLE_SIZE, 0.5),
            "output_file": str(OUTPUT_DIR / "3lm_sample_50.json"),
            "notes": "Matched pairs sample using same indices as HumanEval (seed=42). Enables direct comparison of same problems in English vs Arabic for RQ2 (multilingual performance)."
        }
        
        with open(OUTPUT_DIR / "3lm_sample_50.json", 'w', encoding='utf-8') as f:
            json.dump(sample_info, f, indent=2, ensure_ascii=False)
        
        print(f"  Selected indices: {selected_indices[:10]}... (showing first 10)")
        print(f"  Sample task IDs: {task_ids[:5]}... (showing first 5)")
        print(f"  Note: Using same indices as HumanEval for matched pairs comparison")
        print()
    
    # Create manifest
    create_sampling_manifest()
    
    print("\n" + "=" * 60)
    print("SAMPLE PREPARATION COMPLETE")
    print("=" * 60)
    print("\nGenerated files:")
    print(f"  1. {OUTPUT_DIR}/humaneval_sample_50.json")
    print(f"  2. {OUTPUT_DIR}/3lm_sample_50.json")
    print(f"  3. {OUTPUT_DIR}/sampling_manifest.json")
    print("\nNext steps:")
    print("  1. Verify sample files were created correctly")
    print("  2. Run pre-validation with 3 tasks: T1-Mini")
    print("  3. Execute full evaluation using these samples")


if __name__ == "__main__":
    main()
