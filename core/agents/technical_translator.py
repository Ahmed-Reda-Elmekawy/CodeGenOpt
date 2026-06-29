from typing import Optional
from langchain_ollama import OllamaLLM
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
import logging

logger = logging.getLogger(__name__)


class TechnicalTranslator:
    """
    Agent to translate natural language input into English,
    preserving technical meaning and context, using only local Ollama LLM.
    Suitable for technical and programming-related translation tasks.
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

        # use shared LLM if passed, otherwise create a new one
        self.llm = llm or OllamaLLM(
            model=model_name,
            temperature=temperature,
            num_gpu=1,
            num_thread=12,
            num_ctx=context_size,
            num_predict=max_tokens,
        )

        # System message: role of the agent
        system_prompt = (
            "You are a technical translator specializing in computer programming and engineering concepts. "
            "Your only task is to accurately translate technical and programming problems from any language to English. "
            "Maintain the original meaning, technical terms, and all specifics while translating. "
            "Only respond with the translation, no other text."
        )

        # Human message: task + input
        human_prompt = (
            "TASK: TRANSLATE THE FOLLOWING TEXT TO ENGLISH\n\n"
            "Rules:\n"
            "1. If the input is already in English, return it unchanged.\n"
            "2. If the input is in another language, translate it accurately to English.\n"
            "3. Pay special attention to technical and programming terms.\n"
            "4. Do not add any explanations or notes.\n"
            "5. Output only the translated text.\n\n"
            "Input: {input_text}\n\n"
            "Translation:"
        )

        # Unified ChatPromptTemplate
        self.template = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(system_prompt),
                HumanMessagePromptTemplate.from_template(human_prompt),
            ]
        )

        self.translation_chain = self.template | self.llm

    def run(self, input_text: str) -> str | dict:
        if not input_text or input_text.strip() == "":
            return ""

        if self.debug_mode:
            logger.info(
                f"[TechnicalTranslator] TechnicalTranslator initialized with model: {self.llm.model}"
            )
            logger.info(f"[TechnicalTranslator] Translating input:\n {input_text}")

        try:
            result = self.translation_chain.invoke({"input_text": input_text})
            translation = result.strip()
            if self.debug_mode:
                logger.debug(f"[TechnicalTranslator] Output:\n {translation}")
            return translation
        except Exception as e:
            logger.exception(f"[TechnicalTranslator] Translation failed: {e}")
            return {"error": f"[TechnicalTranslator] Translation failed: {e}"}
