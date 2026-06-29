import logging
import json
from typing import Dict, Any, List, Optional
from langchain_ollama import OllamaLLM
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

logger = logging.getLogger(__name__)


class CodeGenerator:
    """
    Agent for generating Python code from JSON function specs.
    Ensures all examples include all parameters before sending to the LLM.
    """

    def __init__(
        self,
        llm: Optional[OllamaLLM] = None,
        model_name: str = "llama3",
        temperature: float = 0.2,
        max_tokens: int = 512,
        context_size: int = 4096,
        debug_mode: bool = False,
    ):
        self.debug_mode = debug_mode

        # Initialize LLM
        # use shared LLM if passed, otherwise create a new one
        self.llm = llm or OllamaLLM(
            model=model_name,
            temperature=temperature,
            num_gpu=1,
            num_thread=12,
            num_ctx=context_size,
            num_predict=max_tokens,
        )

        # System prompt
        self.system_prompt = (
            "You are an expert Python developer. "
            "Implement Python functions from structured JSON specs. "
            "Generate valid, runnable Python code only."
        )

        # Human prompt
        human_template = (
            "Given the following function specification in JSON format:\n\n"
            "{function_json}\n\n"
            "Write the complete Python function definition only (no extra text):\n"
            "- Use EXACT name and signature.\n"
            "- Include docstring with description, constraints, examples, exceptions.\n"
            "- Ensure examples have all parameters as named keys; fill missing with null.\n"
            "- Use Python built-in types (bool, int, str, list, dict) in isinstance() checks.\n"
            "- Output ONLY the function code."
        )

        self.template = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(self.system_prompt),
                HumanMessagePromptTemplate.from_template(human_template),
            ]
        )

        self.chain = self.template | self.llm

    def _prepare_spec(self, spec: Dict[str, Any]) -> Dict[str, str]:
        spec_clean = dict(spec)

        # Convert to JSON string for ChatPromptTemplate
        return {"function_json": json.dumps(spec_clean, ensure_ascii=False, indent=2)}


    def run(self, function_spec: Dict[str, Any]) -> str | dict:
        if not isinstance(function_spec, dict):
            return "# Error: function_spec must be a dict."

        if self.debug_mode:
            logger.info(
                f"Generating code for function: {function_spec.get('function_name')}"
            )

        function_json = self._prepare_spec(function_spec)

        try:
            code = self.chain.invoke(function_json)
            return code
        except Exception as e:
            logger.exception(f"[CodeGenerator] Generation Code failed: {e}")
            return {"error": f"[CodeGenerator] Generation Code failed: {e}"}
