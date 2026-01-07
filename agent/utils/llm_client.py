import os
from typing import Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


class LLMConfigError(Exception):
    pass


def get_openai_api_key() -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise LLMConfigError(
            "OPENAI_API_KEY not found in environment variables. "
            "Please set it in your .env file or environment."
        )
    return api_key


def initialize_llm(
    model: Optional[str] = None,
    temperature: float = 0.7,
    api_key: Optional[str] = None,
) -> ChatOpenAI:
    if model is None:
        model = os.getenv("LLM_MODEL", "gpt-4")
    
    if api_key is None:
        api_key = get_openai_api_key()
    
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=api_key,
    )


def get_llm_client() -> ChatOpenAI:
    return initialize_llm()

