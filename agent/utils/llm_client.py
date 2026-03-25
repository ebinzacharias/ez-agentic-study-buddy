import os
from typing import Optional, Union

import httpx
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

load_dotenv()


def _get_http_client() -> httpx.Client:
    """Return an httpx.Client configured with the corporate proxy and SSL verification disabled.
    
    Corporate proxies that do SSL inspection replace server certs with their own CA.
    verify=False bypasses the SSL check so the Groq API call succeeds through the proxy.
    """
    proxy_url = os.getenv("PROXY_URL", "").strip()
    if proxy_url:
        return httpx.Client(proxy=proxy_url, verify=False)
    # No explicit proxy — still disable verify in case the system proxy does SSL inspection
    return httpx.Client(verify=False)


class LLMConfigError(Exception):
    pass


def get_api_key(env_var: str, provider_name: str) -> str:
    api_key = os.getenv(env_var)
    if not api_key:
        raise LLMConfigError(
            f"{env_var} not found in environment variables. "
            f"Please set it in your .env file or environment to use {provider_name}."
        )
    return api_key


def initialize_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    api_key: Optional[str] = None,
) -> Union[ChatGroq, ChatOpenAI]:
    if provider is None:
        provider = os.getenv("LLM_PROVIDER", "groq")
    
    if provider.lower() == "groq":
        if model is None:
            model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
        if api_key is None:
            api_key = get_api_key("GROQ_API_KEY", "Groq")
        return ChatGroq(
            model=model,
            temperature=temperature,
            api_key=api_key,  # type: ignore[arg-type]
            http_client=_get_http_client(),
        )
    
    elif provider.lower() == "openai":
        if model is None:
            model = os.getenv("LLM_MODEL", "gpt-4")
        if api_key is None:
            api_key = get_api_key("OPENAI_API_KEY", "OpenAI")
        proxy_url = os.getenv("PROXY_URL", "").strip()
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,  # type: ignore[arg-type]
            http_async_client=httpx.AsyncClient(
                proxy=proxy_url if proxy_url else None,
                verify=False,
            ),
        )
    
    else:
        raise LLMConfigError(
            f"Unsupported LLM provider: {provider}. "
            "Supported providers: 'groq', 'openai'"
        )


def get_llm_client() -> Union[ChatGroq, ChatOpenAI]:
    return initialize_llm()

