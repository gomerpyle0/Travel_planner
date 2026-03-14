import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()


async def estimate_budget(
    destination: str,
    days: int,
    travel_style: str,
) -> dict:
    """
    Estimate the travel budget for a trip.

    Args:
        destination: The destination city or country.
        days: Number of days for the trip.
        travel_style: One of "budget", "mid-range", or "luxury".

    Returns:
        A dict with per-day and total cost breakdown by category.
    """
    prompt = f"""Estimate the travel budget for a {days}-day trip to {destination} with a {travel_style} travel style.

Return a JSON object with:
{{
  "destination": "{destination}",
  "days": {days},
  "travel_style": "{travel_style}",
  "currency": "local currency code",
  "per_day": {{
    "accommodation": number,
    "food": number,
    "local_transport": number,
    "activities": number,
    "miscellaneous": number,
    "total": number
  }},
  "total_trip": {{
    "accommodation": number,
    "food": number,
    "local_transport": number,
    "activities": number,
    "miscellaneous": number,
    "subtotal": number,
    "flights_estimate": number,
    "grand_total": number
  }},
  "notes": "Brief explanation of assumptions and money-saving tips"
}}

All amounts should be in USD. Respond in plain JSON only, no markdown."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    import json
    text = response.content[0].text.strip()
    return json.loads(text)
