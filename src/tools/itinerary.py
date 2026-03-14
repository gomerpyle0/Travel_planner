import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()


async def generate_itinerary(
    source: str,
    destination: str,
    days: int,
    interests: list[str],
) -> dict:
    """
    Generate a day-by-day travel itinerary.

    Args:
        source: Traveler's origin city/country (e.g. "New York", "London").
        destination: The destination city or country.
        days: Number of days for the trip.
        interests: List of traveler interests (e.g. ["food", "history", "hiking"]).

    Returns:
        A dict with trip summary and a day-by-day itinerary list.
    """
    interests_str = ", ".join(interests) if interests else "general sightseeing"

    prompt = f"""Create a detailed {days}-day travel itinerary for a traveler going from {source} to {destination}.

Traveler interests: {interests_str}

Important considerations:
- The traveler is departing from {source}, so account for flight duration and arrival time on Day 1.
- Include visa/entry requirements relevant to travelers from {source}.
- Suggest realistic flight options or transit routes from {source} to {destination}.
- Factor in jet lag recovery if the time zone difference is large.

Return a JSON object with:
{{
  "trip_summary": {{
    "source": "{source}",
    "destination": "{destination}",
    "days": {days},
    "interests": {interests},
    "estimated_flight_duration": "X hours",
    "visa_requirement": "visa-free / visa on arrival / e-visa / visa required",
    "best_entry_airport": "airport name and code"
  }},
  "itinerary": [
    {{
      "day": 1,
      "title": "Day title",
      "theme": "Arrival & Orientation",
      "morning": "Activity description",
      "afternoon": "Activity description",
      "evening": "Activity description",
      "accommodation": "Recommended area to stay",
      "tips": "Practical tip for this day"
    }}
  ]
}}

Respond in plain JSON only, no markdown."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    import json
    text = response.content[0].text.strip()
    return json.loads(text)
