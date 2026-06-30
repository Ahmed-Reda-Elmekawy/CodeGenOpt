# Ollama Usage Guide For CodeGenOpt

## Introduction
This guide provides reproducible instructions for installing Ollama,
downloading models, running basic tests, and recording model-serving settings
for CodeGenOpt experiments.

---

## 1. Installing Ollama

### Linux (Debian/Ubuntu)
```bash
curl -fsSL https://ollama.com/install.sh | sh
```
- See the official instructions: [Ollama Installation Guide](https://github.com/ollama/ollama/blob/main/docs/linux.md)

### Windows / macOS
- Refer to [Ollama Downloads](https://ollama.com/download) and follow the platform-specific instructions.

---

## 2. Verifying Ollama Installation
```bash
ollama --version
ollama list
```
- The first command shows the installed version.
- The second lists available models (should be empty after fresh install).

---

## 3. Downloading Models
To download a model (example: Llama 3):
```bash
ollama pull llama3:latest
```
For other models:
```bash
ollama pull codellama:7b-instruct
ollama pull deepseek-coder:6.7b-instruct
ollama pull mistral:7b
ollama pull gemma:2b
```
- The download size is several GB per model. Ensure sufficient disk space.

---

## 4. Running and Testing Models
Models can be run interactively or by piping a prompt:

### Interactive Mode
```bash
ollama run llama3:latest
```
- Type a prompt and press Enter.

### One-shot Prompt (non-interactive)
```bash
echo "Write a Python function to compute Fibonacci numbers." | ollama run codellama:7b-instruct
```

---

## 5. Useful Ollama Commands
- List all local models:
  ```bash
  ollama list
  ```
- Remove a model:
  ```bash
  ollama rm <model-name>
  ```
- Show model info:
  ```bash
  ollama show <model-name>
  ```
- Stop all running Ollama processes:
  ```bash
  ollama stop
  ```
- For more commands:
  ```bash
  ollama --help
  ```

---

## 6. Troubleshooting
## 6. Reproducibility Checklist

For scientific reporting, record:

- Ollama version.
- Model name and tag.
- Host hardware profile.
- CPU/GPU mode.
- Prompt template or direct command used.
- Decoding parameters, if configured.

## 7. Troubleshooting

- If memory errors occur, unload unused models or use quantized versions.
- For CPU-only systems, avoid models larger than 7B.
- Check [Ollama Issues](https://github.com/ollama/ollama/issues) for help.

---

## 8. References
- [Ollama Official Documentation](https://ollama.com/)
- [Ollama GitHub](https://github.com/ollama/ollama)
- [Meta Llama 3 Technical Report](https://ai.meta.com/llama/)
- [CodeLlama Benchmarks](https://github.com/facebookresearch/codellama)
- [DeepSeek-Coder Benchmarks](https://github.com/deepseek-ai/DeepSeek-Coder)

---

This guide is intended for research and technical documentation. It should be
updated when model availability, Ollama features, or evaluation hardware change.
