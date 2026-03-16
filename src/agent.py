import asyncio
import json
import sys

from dotenv import load_dotenv

from tools.destination import search_destination
from tools.itinerary import generate_itinerary
from tools.budget import estimate_budget
from tools.weather import get_weather_info
from llm_client import get_async_client, GEMINI_MODEL

load_dotenv()

SYSTEM_PROMPT = """You are an expert travel planner. Help users plan trips by researching
destinations, generating itineraries, estimating budgets, and providing weather information.

Use the available tools to gather accurate information before making recommendations.
Always provide practical, actionable travel advice tailored to the user's needs."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_destination",
            "description": "Research a travel destination. Returns country, language, currency, timezone, top attractions, best areas to stay, and local tips.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "The destination city or country to research."
                    }
                },
                "required": ["destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_itinerary",
            "description": "Generate a detailed day-by-day travel itinerary. Accounts for flight duration, visa requirements, and arrival logistics based on origin.",
            "parameters": {
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
        }
    },
    {
        "type": "function",
        "function": {
            "name": "estimate_budget",
            "description": "Estimate travel budget with a breakdown by category (accommodation, food, transport, activities).",
            "parameters": {
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
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_info",
            "description": "Get typical weather information for a destination in a given month for travel planning.",
            "parameters": {
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


async def _run_gemini(client, prompt: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    while True:
        response = await client.chat.completions.create(
            model=GEMINI_MODEL,
            messages=messages,
            tools=TOOLS,
        )
        choice = response.choices[0]
        tool_calls = choice.message.tool_calls

        if choice.finish_reason == "stop" or not tool_calls:
            return choice.message.content or ""

        messages.append({
            "role": "assistant",
            "content": choice.message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in tool_calls
            ],
        })

        for tc in tool_calls:
            print(f"  [calling {tc.function.name}...]", flush=True)
            result = await execute_tool(tc.function.name, json.loads(tc.function.arguments))
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })


async def run_agent(prompt: str) -> str:
    client = await get_async_client()
    return await _run_gemini(client, prompt)


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
