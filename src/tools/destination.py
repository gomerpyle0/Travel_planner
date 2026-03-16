import json

from llm_client import get_sync_client, GEMINI_MODEL

client = get_sync_client()


async def search_destination(destination: str) -> dict:
    """
    Research a travel destination and return key information.

    Args:
        destination: The destination city or country to research.

    Returns:
        A dict with country, language, currency, timezone, and top attractions.
    """
    prompt = f"""Research the travel destination: {destination}

Return a structured summary with the following fields:
- country: the country name
- capital (if destination is a country) or city
- language: official language(s)
- currency: currency name and code
- timezone: main timezone(s)
- top_attractions: list of 5 must-see attractions
- best_areas_to_stay: list of 2-3 recommended neighborhoods/areas
- local_tips: 2-3 practical tips for visitors

Respond in plain JSON only, no markdown."""

    response = client.chat.completions.create(
        model=GEMINI_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.choices[0].message.content.strip()
    return json.loads(text)
