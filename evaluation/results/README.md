# Evaluation Results

This directory contains previously generated CodeGenOpt evaluation artifacts.
The files were produced by earlier runs of `evaluation/run_evaluation.py` and
are included so the full `evaluation/` directory can be shared as a complete
scientific review package.

## Directory Contents

| Path | Contents |
| --- | --- |
| `raw/` | Detailed per-task experiment traces. |
| `summary/` | Per-experiment summaries in JSON/CSV and comparison-ready JSON files. |
| `tables/` | Aggregate tables generated from the summary files. |
| `figures/` | Generated figures, if report generation has been run. |

## File Types

| Pattern | Meaning |
| --- | --- |
| `raw/details_*.json` | Full experiment details for a named configuration. |
| `raw/HumanEval_*.json` | Individual or mode-specific HumanEval task traces from earlier runs. |
| `summary/summary_*.json` | Summary metadata plus task-level result records. |
| `summary/summary_*.csv` | Flat summary rows for spreadsheet/statistical analysis. |
| `summary/comparison_ready_*.json` | Compact format for comparing configurations. |
| `tables/*.csv` | Aggregated tables prepared from multiple experiments. |

## How To Read The Results

Start with `tables/` for high-level comparisons, then inspect the matching
`summary/summary_*.json` file for experiment metadata. Use the corresponding
`raw/details_*.json` file when per-task generated code, failures, or timing
details are needed.

## Reproducing Existing Results

To reproduce an existing result, rerun `evaluation/run_evaluation.py` with the
same:

- `--experiment_name`
- `--dataset`
- `--dataset_limit` or `--sample_indices_file`
- `--attempts`
- translator and optimizer flags
- local/cloud LLM backend
- model configuration and runtime environment

The regenerated files will be written back into this directory tree using the
same naming scheme.
