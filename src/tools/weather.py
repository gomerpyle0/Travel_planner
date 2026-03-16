import json

from llm_client import get_sync_client, GEMINI_MODEL

client = get_sync_client()


async def get_weather_info(destination: str, month: str) -> dict:
    """
    Get typical weather information for a destination in a given month.

    Args:
        destination: The destination city or country.
        month: The month of travel (e.g. "January", "July").

    Returns:
        A dict with temperature, rainfall, and travel weather advice.
    """
    prompt = f"""Provide typical weather information for {destination} in {month}.

Return a JSON object with:
{{
  "destination": "{destination}",
  "month": "{month}",
  "temperature": {{
    "average_high_c": number,
    "average_low_c": number,
    "average_high_f": number,
    "average_low_f": number
  }},
  "rainfall": {{
    "average_mm": number,
    "rainy_days": number,
    "description": "dry / light / moderate / heavy"
  }},
  "humidity": "low / moderate / high",
  "sunshine_hours_per_day": number,
  "weather_summary": "1-2 sentence description of typical weather",
  "what_to_pack": ["item1", "item2", "item3"],
  "travel_advisory": "Any weather-related travel warnings or tips for this month"
}}

Respond in plain JSON only, no markdown."""

    response = client.chat.completions.create(
        model=GEMINI_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.choices[0].message.content.strip()
    return json.loads(text)
