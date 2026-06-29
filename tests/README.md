# tests

This folder contains all unit tests and integration tests for the CodeGenOpt system.

**Contents:**

- Unit tests for each agent and utility
- Integration tests for the complete pipeline
- Test data and expected outputs

# CodeGenOpt Test Suite

This directory contains all unit and integration tests for the CodeGenOpt agents and pipeline.

## 1. Activate the Python Virtual Environment

Before running any tests, activate your virtual environment (venv):

**On Linux/macOS:**

```bash
source venv/bin/activate
```

**On Windows (cmd):**

```cmd
venv\Scripts\activate
```

**On Windows (PowerShell):**

```powershell
venv\Scripts\Activate.ps1
```

If you do not have a virtual environment, create one with:

```bash
python3 -m venv venv
```

## 2. Install Dependencies

Make sure all required packages are installed:

```bash
pip install -r ./requirements.txt
```

## 3. Running Tests

You can run all tests using pytest from the root or tests directory:

```bash
pytest -v
```

To run only agent tests:

```bash
pytest tests/agents -v
```

To run a specific test file:

```bash
pytest tests/agents/test_technical_translator.py -v
```

## 4. Test Structure

- `tests/agents/` : Unit and integration tests for each agent.
- `tests/agents/utility.py` : Shared test utilities and helpers.

## 5. Notes

- Some tests require Ollama LLM models to be running locally.
- Make sure your environment variables and config files are set up as needed.
- For best results, use the same Python version as specified in the project requirements.


