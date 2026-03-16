import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


def get_sync_client():
    from openai import OpenAI
    return OpenAI(base_url=GEMINI_BASE_URL, api_key=GEMINI_API_KEY)


async def get_async_client():
    from openai import AsyncOpenAI
    return AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=GEMINI_API_KEY)
