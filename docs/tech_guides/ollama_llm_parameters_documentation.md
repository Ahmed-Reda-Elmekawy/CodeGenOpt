# OllamaLLM — Parameter Reference and Effects

**Purpose:** This document explains commonly used `OllamaLLM(...)` constructor
parameters, how they affect inference behavior, and how they should be recorded
for reproducible CodeGenOpt experiments.

---

## Table of contents

1. Overview
2. General usage notes
3. Parameter reference (alphabetical)
4. Recommended presets (CPU-only, GPU)
5. Examples
6. Troubleshooting & tuning tips

---

## 1. Overview

`OllamaLLM` exposes a mix of *runtime controls* (device, threads, context size), *sampling/decoding controls* (temperature, top_k, top_p, repeat_penalty, mirostat, etc.), *client/transport options* (base_url, client_kwargs), and *integration hooks* (callbacks, tags, metadata). Changing these parameters alters latency, memory use, determinism, and output style.

This file documents each parameter, its meaning, how it affects the model, and practical recommendations for translation and code tasks.

---

## 2. General usage notes

- **Start conservative.** If out-of-memory errors occur, reduce `num_ctx` and `num_predict` first, then `num_thread`.
- **Deterministic output:** set `temperature=0.0`, and prefer `top_k`/`top_p` that constrain sampling. For precise translations or formal outputs, deterministic settings are best.
- **GPU usage:** set `num_gpu` > 0 only if the target machine and local runtime support GPU inference. Use `nvidia-smi` or operating-system tools to confirm GPU availability and VRAM.
- **Context size:** `num_ctx` affects memory; larger contexts allow the model to see/remember more tokens but consume more RAM/VRAM.
- **Validation on init:** `validate_model_on_init` can prevent mismatches between model and requested device but can slow startup.

---

## 3. Parameter reference (alphabetical)

> For each parameter: **Type** — *Default* — **Description & effect** — **Practical advice**

### `async_client_kwargs`

- **Type:** `dict | None` — *Default:* `{}`
- **Description:** Keyword arguments forwarded to the asynchronous client used to call the Ollama backend when using async APIs. Can contain connection timeout, headers, proxies, SSL options, etc.
- **Effect:** Alters networking behavior for async calls; does not change model behavior directly.
- **Advice:** Use to tune timeouts or to supply auth headers in remote setups.

### `base_url`

- **Type:** `str | None` — *Default:* `None`
- **Description:** Base URL of the Ollama API server (e.g., `http://localhost:11434` or a remote host). When omitted, a default local socket or default endpoint is used.
- **Effect:** Points requests to a custom server. A wrong URL causes connection errors.
- **Advice:** Set this when the Ollama server runs on a custom port/host or when a remote inference server is used.

### `cache`

- **Type:** `BaseCache | bool | None` — *Default:* `None`
- **Description:** Cache backend or flag to enable/disable caching. If true or a cache instance, the LLM might reuse previous outputs for identical prompts (dependent on implementation).
- **Effect:** Speeds repeated identical queries and reduces compute and latency. Can alter reproducibility if cache returns stale outputs.
- **Advice:** Use caching for high-throughput, repeated prompts. Clear cache when changing model or prompts.

### `callback_manager`

- **Type:** `BaseCallbackManager | None` — *Default:* `None`
- **Description:** Central manager for lifecycle callbacks (events, telemetry, metrics). Used by the LangChain ecosystem.
- **Effect:** Allows centralized handling of events, logging, or streaming tokens.
- **Advice:** Provide if integrating with monitoring or custom telemetry.

### `callbacks`

- **Type:** `Callbacks | None` — *Default:* `None`
- **Description:** A list of callback handlers called during inference (token streaming, start/finish events, error handlers).
- **Effect:** Enables streaming output to UI, logging tokens as generated, or custom behavior on errors.
- **Advice:** Use when building interactive UIs or to capture partial outputs; streaming callbacks can increase responsiveness but add complexity.

### `client_kwargs`

- **Type:** `dict | None` — *Default:* `{}`
- **Description:** Keywords forwarded to the synchronous client when making requests to the Ollama endpoint. Similar to `async_client_kwargs` but for sync calls.
- **Effect:** Controls low-level client behaviors (timeouts, headers, proxy, SSL).
- **Advice:** Tune network timeouts or add custom headers here.

### `custom_get_token_ids`

- **Type:** `Callable[[str], list[int]] | None` — *Default:* `None`
- **Description:** Custom tokenizer function mapping strings to token IDs. Useful when integrating a specific tokenizer or token counting strategy.
- **Effect:** Changes how inputs are tokenized and therefore how `num_ctx` is consumed; can affect decoding if tokenization differs from the model's expected tokenizer.
- **Advice:** Provide only when the exact tokenization format expected by the model is known; mismatched tokenization can cause broken prompts or inaccurate memory estimates.

### `format`

- **Type:** `Literal['', 'json']` — *Default:* `""` (empty)
- **Description:** Expected output format. When `'json'` is selected, some runtimes may validate or post-process output as JSON.
- **Effect:** Can enable structured outputs or add validation; may fail if model doesn't produce valid JSON.
- **Advice:** Use `'json'` for structured machine-readable outputs and pair it with strict prompting.

### `keep_alive`

- **Type:** `int | str | None` — *Default:* `None`
- **Description:** Keep-alive setting for persistent connections to reduce repeated startup overhead. Could be seconds or a flag depending on implementation.
- **Effect:** Keeps the client connection open across multiple calls for faster subsequent queries.
- **Advice:** Useful for batch/throughput scenarios. For short scripts, can be omitted.

### `limit` *(not present in signature)*

- **Note:** Not in the provided signature — ignore.

### `metadata`

- **Type:** `dict | None` — *Default:* `None`
- **Description:** Arbitrary metadata attached to the LLM instance (for logging, provenance, experiment tracking).
- **Effect:** No direct effect on model outputs; used for bookkeeping.
- **Advice:** Add metadata such as `{'purpose': 'translation', 'experiment': 'run-id'}` for traceability.

### `mirostat`

- **Type:** `int | None` — *Default:* `None`
- **Description:** Mirostat is an adaptive sampling method that controls target entropy. When set (commonly 1 or 2), it triggers mirostat mode where `mirostat_eta` and `mirostat_tau` further configure behavior.
- **Effect:** Attempts to keep generated token distribution at a target entropy; useful to maintain a constant level of surprise.
- **Advice:** Use only if familiar with mirostat. For deterministic translation set `temperature=0.0` (mirostat is unnecessary).

### `mirostat_eta`

- **Type:** `float | None` — *Default:* `None`
- **Description:** Learning rate for mirostat's adaptive updates.
- **Effect:** Controls how fast the algorithm updates its target; too large can oscillate, too small can adapt slowly.
- **Advice:** Keep defaults unless experimenting with adaptive sampling.

### `mirostat_tau`

- **Type:** `float | None` — *Default:* `None`
- **Description:** Target entropy value used by mirostat.
- **Effect:** Sets the desired unpredictability level of outputs.
- **Advice:** Leave unset for translations or short-form deterministic tasks.

### `model`

- **Type:** `str` — *Required*
- **Description:** Name or identifier of the model to load (for example `llama3`, `ggml-model.bin`, or other local model identifiers supported by the Ollama installation).
- **Effect:** Determines capabilities, required memory/VRAM, and tokenization. Larger models usually produce better outputs at the cost of latency and memory.
- **Advice:** Match `model` to hardware capability. For example, use smaller or quantized models on CPU and larger models only when sufficient GPU memory is available.

### `name`

- **Type:** `str | None` — *Default:* `None`
- **Description:** Optional name for the LLM instance used for identification or metrics.
- **Effect:** Primarily cosmetic / bookkeeping.
- **Advice:** Use for experiment tracking or multiple concurrent models.

### `num_ctx`

- **Type:** `int | None` — *Default:* `None`
- **Description:** Context window size (maximum number of tokens the model can attend to). Affects prompt length and memory footprint.
- **Effect:** Larger `num_ctx` means the model can process longer prompts but uses more RAM/VRAM. If set larger than the model's native context, it may be ignored or error.
- **Advice:** Typical values: `2048` (safe on moderate RAM), `4096` (requires more memory), `8192+` only if model & hardware support it.

### `num_gpu`

- **Type:** `int | None` — *Default:* `None`
- **Description:** Number of GPUs to use for inference (0 means CPU-only; 1 enables GPU if available). Implementation may accept `None` as "auto-detect".
- **Effect:** Using GPUs drastically reduces latency and can allow larger `num_ctx` but requires CUDA drivers and sufficient VRAM.
- **Advice:** Set `num_gpu=1` only if `nvidia-smi` shows an available GPU and the Ollama runtime supports GPU inference.

### `num_predict`

- **Type:** `int | None` — *Default:* `None`
- **Description:** Maximum number of tokens to generate in a single call (output length cap).
- **Effect:** Directly limits the length of model outputs; higher values increase runtime and possibly memory.
- **Advice:** For translations, keep conservative (e.g., 256–512). For long-form generation increase accordingly.

### `num_thread`

- **Type:** `int | None` — *Default:* `None`
- **Description:** Number of CPU threads the runtime can use for inference.
- **Effect:** More threads can speed up CPU inference but may increase CPU contention. On multi-user machines, leave some headroom.
- **Advice:** Use `nproc --all` as a starting point on Linux. Lower the value when concurrent workloads or thermal limits are relevant.

### `repeat_last_n`

- **Type:** `int | None` — *Default:* `None`
- **Description:** Number of last tokens to consider for repetition penalty calculation.
- **Effect:** Controls the recency window used to detect and discourage repeats. A larger window makes it harder to repeat long sequences.
- **Advice:** Values like `64` are common. Increase this value when long repeated phrases appear.

### `repeat_penalty`

- **Type:** `float | None` — *Default:* `None`
- **Description:** Multiplier (>1) to penalize tokens that appeared in the recent window. Typical values >= 1.0.
- **Effect:** Reduces repeated output; too high values can lead to unnatural phrasing.
- **Advice:** Use `1.05–1.2` for general tasks. For translation, a small penalty is fine; deterministic translation normally uses `temperature=0`.

### `seed`

- **Type:** `int | None` — *Default:* `None`
- **Description:** RNG seed used for sampling-based decoding. When set and sampling enabled, seeds reproduce stochastic outputs.
- **Effect:** Makes sampling deterministic across runs when other non-deterministic sources are disabled.
- **Advice:** Use with `temperature>0` to reproduce example outputs for debugging.

### `stop`

- **Type:** `list[str] | None` — *Default:* `None`
- **Description:** Sequence(s) of tokens or strings where the model should stop generation if encountered.
- **Effect:** Useful to enforce end-of-generation markers or cut extraneous content.
- **Advice:** Use tokens like `"\n\n"`, `"END"`, or other unique markers included in prompts.

### `seed` (duplicate) — ignored; already documented

### `stop` (duplicate) — ignored; already documented

### `tfs_z`

- **Type:** `float | None` — *Default:* `None`
- **Description:** Typical Filter Sampling parameter `z` used in TFS (typical sampling) algorithm. It helps filter low-probability tokens.
- **Effect:** Adjusts which tokens are allowed during sampling; affects output diversity.
- **Advice:** Leave unset unless experimenting with typical sampling; typical sampling is less commonly used than top_k/top_p.

### `tags`

- **Type:** `list[str] | None` — *Default:* `None`
- **Description:** A list of tags/labels attached to this LLM instance for logging, filtering, or experiment tracking.
- **Effect:** No direct effect on model outputs.
- **Advice:** Add descriptive tags such as `['translation', 'evaluation']` for observability.

### `temperature`

- **Type:** `float | None` — *Default:* `None`
- **Description:** Controls randomness of sampling. `0.0` often means greedy/deterministic decoding; higher values (0.7–1.2) increase diversity.
- **Effect:** High temperature produces more creative and varied outputs, lower temperature more conservative outputs.
- **Advice:** For translation or deterministic tasks use `0.0`. For creative generation, consider `0.7–1.0`.

### `tfs_z` (duplicate) — ignored; already documented

### `top_k`

- **Type:** `int | None` — *Default:* `None`
- **Description:** Limits sampling to the top `k` highest-probability tokens at each step.
- **Effect:** A smaller `k` constrains outputs to more likely tokens and reduces odd outputs; too small can make output repetitive.
- **Advice:** Common values: `40` (conservative), `5–50`. Combine with `top_p` for hybrid filtering.

### `top_p`

- **Type:** `float | None` — *Default:* `None`
- **Description:** Nucleus sampling parameter — sample from smallest set of tokens whose cumulative probability ≥ `top_p`.
- **Effect:** `top_p=0.9–0.95` often gives a balance of coherence and diversity.
- **Advice:** For deterministic tasks set `top_p` low or `temperature=0`. Use `0.9–0.95` for general generation.

### `validate_model_on_init`

- **Type:** `bool` — *Default:* `False`
- **Description:** When True, the runtime validates that the selected model is compatible with requested devices and options during initialization.
- **Effect:** Catches mismatches early, but increases startup time.
- **Advice:** Set True during development or when switching models; False in tight-latency production starts.

### `verbose`

- **Type:** `bool` — *Default:* `_get_verbosity` (module-level)
- **Description:** Toggles verbose logging in the client. Useful for debugging.
- **Effect:** More logs on initialization and runtime behavior.
- **Advice:** Use for debugging; keep False in production.

### `format` (duplicate earlier) — already documented

### `sync_client_kwargs`

- **Type:** `dict | None` — *Default:* `{}`
- **Description:** Like `client_kwargs` but specifically for synchronous clients.
- **Effect:** Controls sync request timeouts/transport.
- **Advice:** Use this for fine-grained tuning of sync calls.

---

## 4. Recommended presets

Below are two practical presets for constructing `OllamaLLM` instances.

### CPU-only preset (for laptops with 32GB RAM)

```py
OllamaLLM(
    model="llama3",
    num_gpu=0,
    num_thread=12,
    num_ctx=2048,
    num_predict=256,
    temperature=0.0,
    repeat_last_n=64,
    repeat_penalty=1.1,
    top_k=40,
    top_p=0.95,
    validate_model_on_init=False,
    keep_alive=10,
)
```

### GPU preset for CUDA-capable hardware with adequate VRAM

```py
OllamaLLM(
    model="llama3",
    num_gpu=1,
    num_thread=8,
    num_ctx=4096,
    num_predict=512,
    temperature=0.0,
    repeat_last_n=64,
    repeat_penalty=1.05,
    top_k=40,
    top_p=0.95,
    validate_model_on_init=True,
    keep_alive=30,
)
```

---

## 5. Examples

**Example — Deterministic translation (reuse the `TechnicalTranslator` pattern):**

```py
translator = TechnicalTranslator(
    translation_model_name="llama3",
    temperature=0.0,
    timeout=30,
    debug_mode=False,
)

# Where TechnicalTranslator builds OllamaLLM with num_gpu=0, num_thread=12, ...
```

**Example — Reproducible sampling with seed:**

```py
llm = OllamaLLM(
    model="small-creative",
    temperature=0.8,
    seed=42,
    num_predict=200,
)
```

---

## 6. Troubleshooting & tuning tips

- **OOM on startup or during generation:** reduce `num_ctx`, `num_predict`, `num_thread`, or switch between CPU/GPU modes depending on where the memory pressure occurs. Reduce batch sizes when batching inputs.
- **Slow startup but fast subsequent queries:** enable `keep_alive` or run a warm-up query.
- **Unexpected output format:** check `format`, `temperature`, and the prompt. If using `'json'` format, enforce strict output instructions in the prompt.
- **No GPU utilization despite `num_gpu=1`:** ensure drivers are installed, Ollama runtime supports GPU, and the chosen model has GPU-compatible weights. Use `nvidia-smi` to inspect GPU activity.
- **Repetitive generation:** increase `repeat_penalty` slightly or increase `repeat_last_n` window.

---

## Appendix: quick mapping of parameter categories

- **Device / performance:** `num_gpu`, `num_thread`, `num_ctx`, `num_predict`
- **Sampling / decoding:** `temperature`, `top_k`, `top_p`, `repeat_penalty`, `repeat_last_n`, `mirostat*`, `tfs_z`, `seed`
- **Networking / client:** `base_url`, `client_kwargs`, `async_client_kwargs`, `sync_client_kwargs`, `keep_alive`, `timeout` (if exposed)
- **Integration / metadata:** `name`, `tags`, `metadata`, `callbacks`, `callback_manager`, `cache`
- **Safety / validation:** `validate_model_on_init`, `format`


<!-- End of OllamaLLM parameter documentation -->
