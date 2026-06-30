# LangChain Framework Usage In CodeGenOpt

## Overview

LangChain provides abstractions for prompt templates, model invocation, output
parsing, and composable LLM workflows. CodeGenOpt uses these abstractions to
standardize interactions with local or remote model backends across agents.

## Role In CodeGenOpt

LangChain is used for:

- Defining reusable prompt templates.
- Invoking Ollama-compatible language models.
- Structuring agent inputs and outputs.
- Supporting future extensions such as structured parsing, tracing, and tool use.

## Installation

```bash
pip install langchain langchain-ollama
```

## Basic Example

```python
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

prompt = PromptTemplate(
    input_variables=["input_text"],
    template="Summarize the following technical text: {input_text}",
)

llm = OllamaLLM(model="llama3")
chain = prompt | llm

result = chain.invoke({"input_text": "CodeGenOpt evaluates generated code."})
print(result)
```

## Reproducibility Considerations

For research reporting, model calls should record:

- Model name and tag.
- Prompt template version.
- Decoding parameters.
- Backend endpoint or local runtime configuration.
- Whether caching, streaming, or callbacks were enabled.

## References

- LangChain documentation: https://python.langchain.com/docs/
- LangChain repository: https://github.com/langchain-ai/langchain
- LangChain Ollama integration: https://python.langchain.com/docs/integrations/llms/ollama
