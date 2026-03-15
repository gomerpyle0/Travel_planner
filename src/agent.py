import asyncio
import json
import sys

import anthropic
from dotenv import load_dotenv

from tools.destination import search_destination
from tools.itinerary import generate_itinerary
from tools.budget import estimate_budget
from tools.weather import get_weather_info

load_dotenv()

SYSTEM_PROMPT = """You are an expert travel planner. Help users plan trips by researching
destinations, generating itineraries, estimating budgets, and providing weather information.

Use the available tools to gather accurate information before making recommendations.
Always provide practical, actionable travel advice tailored to the user's needs."""

TOOLS = [
    {
        "name": "search_destination",
        "description": "Research a travel destination. Returns country, language, currency, timezone, top attractions, best areas to stay, and local tips.",
        "input_schema": {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "The destination city or country to research."
                }
            },
            "required": ["destination"]
        }
    },
    {
        "name": "generate_itinerary",
        "description": "Generate a detailed day-by-day travel itinerary. Accounts for flight duration, visa requirements, and arrival logistics based on origin.",
        "input_schema": {
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "description": "Traveler's origin city or country (e.g. 'New York', 'London')."
                },
                "destination": {
                    "type": "string",
                    "description": "The destination city or country."
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days for the trip."
                },
                "interests": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of traveler interests (e.g. ['food', 'history', 'hiking'])."
                }
            },
            "required": ["source", "destination", "days", "interests"]
        }
    },
    {
        "name": "estimate_budget",
        "description": "Estimate travel budget with a breakdown by category (accommodation, food, transport, activities).",
        "input_schema": {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "The destination city or country."
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days for the trip."
                },
                "travel_style": {
                    "type": "string",
                    "enum": ["budget", "mid-range", "luxury"],
                    "description": "Travel style: budget, mid-range, or luxury."
                }
            },
            "required": ["destination", "days", "travel_style"]
        }
    },
    {
        "name": "get_weather_info",
        "description": "Get typical weather information for a destination in a given month for travel planning.",
        "input_schema": {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "The destination city or country."
                },
                "month": {
                    "type": "string",
                    "description": "The month of travel (e.g. 'January', 'July')."
                }
            },
            "required": ["destination", "month"]
        }
    }
]


async def execute_tool(name: str, tool_input: dict) -> str:
    if name == "search_destination":
        result = await search_destination(**tool_input)
    elif name == "generate_itinerary":
        result = await generate_itinerary(**tool_input)
    elif name == "estimate_budget":
        result = await estimate_budget(**tool_input)
    elif name == "get_weather_info":
        result = await get_weather_info(**tool_input)
    else:
        return f"Unknown tool: {name}"
    return json.dumps(result)


async def run_agent(prompt: str) -> str:
    client = anthropic.AsyncAnthropic()
    messages = [{"role": "user", "content": prompt}]

    while True:
        async with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=8192,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        ) as stream:
            response = await stream.get_final_message()

        if response.stop_reason == "end_turn":
            text = next(
                (b.text for b in response.content if b.type == "text"), ""
            )
            return text

        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
        if not tool_use_blocks:
            text = next(
                (b.text for b in response.content if b.type == "text"), ""
            )
            return text

        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in tool_use_blocks:
            print(f"  [calling {block.name}...]", flush=True)
            result = await execute_tool(block.name, block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })

        messages.append({"role": "user", "content": tool_results})


def main():
    if len(sys.argv) < 2:
        print("Usage: python src/agent.py \"<your travel query>\"")
        print("Example: python src/agent.py \"Plan a 5-day trip to Tokyo\"")
        sys.exit(1)

    prompt = " ".join(sys.argv[1:])
    print(f"Planning your trip...\n")
    result = asyncio.run(run_agent(prompt))
    print(result)


if __name__ == "__main__":
    main()
