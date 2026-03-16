import os
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

OLLAMA_MODEL = "qwen3:1.7b"
ANTHROPIC_AGENT_MODEL = "claude-opus-4-6"
ANTHROPIC_TOOL_MODEL = "claude-sonnet-4-6"


def get_sync_client():
    if PROVIDER == "anthropic":
        import anthropic
        return anthropic.Anthropic()
    else:
        from openai import OpenAI
        return OpenAI(base_url=f"{OLLAMA_HOST}/v1", api_key="ollama")


async def get_async_client():
    if PROVIDER == "anthropic":
        import anthropic
        return anthropic.AsyncAnthropic()
    else:
        from openai import AsyncOpenAI
        return AsyncOpenAI(base_url=f"{OLLAMA_HOST}/v1", api_key="ollama")


def get_response_text(response) -> str:
    """Extract text content from either an Anthropic or OpenAI-compatible response."""
    if PROVIDER == "anthropic":
        return response.content[0].text.strip()
    else:
        return response.choices[0].message.content.strip()
