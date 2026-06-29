import logging
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

from langchain_ollama import OllamaLLM
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.output_parsers import JsonOutputParser

logger = logging.getLogger(__name__)


# ============================
# Define JSON Schema (Pydantic)
# ============================
class ProblemSpec(BaseModel):
    function_name: str = Field(description="Python function name")
    signature: str = Field(description="Python function signature")
    description: str = Field(description="Technical description in English")
    constraints: List[str] = Field(description="List of requirements and edge cases")
    examples: List[Dict[str, dict | list]] = Field(
        description='List of {"input": {"param1": value, ...}, "output": value} examples'
    )
    exceptions: List[Dict] = Field(
        description='List of {"type": exception name, "when": condition}'
    )


class PromptEngineer:
    """
    Agent to convert an English problem description into a structured JSON specification
    for code generation tasks. Always expects English input.
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

        # LLM setup
        # use shared LLM if passed, otherwise create a new one
        self.llm = llm or OllamaLLM(
            model=model_name,
            temperature=temperature,
            num_gpu=1,
            num_thread=12,
            num_ctx=context_size,
            num_predict=max_tokens,
        )

        # JSON parser
        self.parser = JsonOutputParser(pydantic_object=ProblemSpec)

        # System message: role of the agent
        system_prompt = (
            "You are a professional prompt engineer for code generation tasks. "
            "Your job is to transform the given English problem description into a valid JSON object following the schema provided. "
            "Only output valid JSON, nothing else."
        )

        # Human message: task + input
        human_prompt = (
            "Problem description:\n{problem_description}\n\n" + "{format_instructions}"
        )

        # Unified ChatPromptTemplate
        self.template = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(system_prompt),
                HumanMessagePromptTemplate.from_template(human_prompt),
            ]
        ).partial(format_instructions=self.parser.get_format_instructions())

        # Full chain (prompt → LLM → parser)
        self.chain = self.template | self.llm | self.parser

    def run(self, problem_description: str) -> ProblemSpec | dict:
        """
        Generate a JSON specification for the given problem description.
        Always assumes input is English (TechnicalTranslator should be used before this agent).
        """
        if not problem_description or problem_description.strip() == "":
            return {"error": "Empty problem description."}

        if self.debug_mode:
            logger.info(f"[PromptEngineer] Using model: {self.llm.model}")
            logger.debug(
                "[PromptEngineer] Prompt sent to model:\n%s", problem_description
            )

        for attempt_idx in range(1):
            try:
                result = self.chain.invoke({"problem_description": problem_description})
                if self.debug_mode:
                    logger.debug("[PromptEngineer] Model response:\n%s", result)
                    logger.debug(f"[PromptEngineer] Result type: {type(result)}")
                # Handle both dict and Pydantic model cases
                if hasattr(result, "dict"):
                    return result.dict()
                elif isinstance(result, dict):
                    return result
                else:
                    logger.warning(
                        f"[PromptEngineer] Unexpected result type {type(result)} — returning as-is."
                    )
                    return {"error": f"Unexpected result type: {type(result)}"}
            except Exception as e:
                if self.debug_mode:
                    logger.warning(
                        "[PromptEngineer] JSON parsing failed (attempt %d): %s",
                        attempt_idx + 1,
                        str(e),
                    )
                continue
        logger.error("[PromptEngineer] Failed to generate JSON after retries")
        return {
            "error": "Failed to generate JSON after retries"
        }
    