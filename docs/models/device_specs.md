# Evaluation Hardware Profile

This document summarizes the hardware and software environment used for local
development, lightweight model inference, and selected CodeGenOpt evaluation
runs. It is written as a reproducibility note for public research review and
does not include personal identifiers, network addresses, product IDs, or
account-specific information.

## System Class

| Component | Specification |
| --- | --- |
| Workstation class | Mobile workstation |
| Device model | HP ZBook 15 G6 |
| System architecture | x86_64 |
| Operating systems | Linux and Windows dual-boot |
| Primary development environment | Linux |

## Processor

| Component | Specification |
| --- | --- |
| CPU | Intel Core i7-9880H |
| Microarchitecture | Coffee Lake |
| Cores / threads | 8 cores / 16 threads |
| Base frequency | Approximately 2.6 GHz |
| L3 cache | 16 MB |

## Memory

| Component | Specification |
| --- | --- |
| Installed RAM | 32 GB DDR4 |
| Practical local-inference profile | Suitable for small and medium quantized models |
| Recommended workload class | CPU inference, lightweight GPU inference, evaluation orchestration, dataset processing |

## Graphics

| Component | Specification |
| --- | --- |
| Dedicated GPU | NVIDIA Quadro T1000 |
| Dedicated GPU memory | 4 GB GDDR5 |
| Integrated GPU | Intel UHD Graphics 630 |
| CUDA availability | Available, but constrained by the 4 GB VRAM limit |

## Storage

| Component | Specification |
| --- | --- |
| Primary storage | 512 GB NVMe SSD |
| Secondary storage | 1 TB HDD |
| Recommended use | SSD for active code and environments; HDD for large logs, archived datasets, and generated artifacts |

## Relevance To CodeGenOpt

The local hardware profile is appropriate for:

- Running the CodeGenOpt orchestration pipeline.
- Executing benchmark tests and generated-code validation.
- Running small or quantized local models through Ollama.
- Producing reproducibility artifacts such as logs, summaries, and plots.

The hardware profile is not ideal for:

- Full-precision inference with large models.
- Heavy fine-tuning of multi-billion-parameter models.
- Long-running concurrent GPU workloads.

## Recommended Local Model Class

| Model class | Suitability |
| --- | --- |
| 2B to 7B quantized models | Recommended |
| 7B instruction-tuned code models | Feasible, especially with quantization |
| 13B+ models | Not recommended on this hardware unless heavily quantized and latency is acceptable |
| Cloud-hosted models | Recommended for large-scale or time-sensitive evaluation |

## Reproducibility Note

The reported hardware profile should be interpreted as a local development and
evaluation environment, not as a requirement for the CodeGenOpt system. Exact
latency and resource measurements may differ on other machines, especially when
using different CPU generations, GPU memory sizes, model quantization levels, or
cloud-hosted inference backends.
