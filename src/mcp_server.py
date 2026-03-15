"""
MCP server that exposes the Travel Planner agent as a single `plan_trip` tool.

External clients (Claude Desktop, other MCP clients) connect here and call
`plan_trip` — this server delegates to agent.py which runs the full agentic loop.

Usage:
    python src/mcp_server.py
"""

import asyncio
import sys
import os

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

# Allow imports from src/ when running as a script
sys.path.insert(0, os.path.dirname(__file__))

from agent import run_agent

server = Server("travel-planner")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="plan_trip",
            description=(
                "Plan a trip using the Travel Planner AI agent. "
                "Provide a natural language request describing the trip — "
                "destination, duration, interests, travel style, etc. "
                "The agent will research the destination, build an itinerary, "
                "estimate the budget, and check weather."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "request": {
                        "type": "string",
                        "description": (
                            "Natural language trip planning request. "
                            "Example: 'Plan a 7-day budget trip to Tokyo from New York "
                            "in July, interested in food and history.'"
                        ),
                    }
                },
                "required": ["request"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name != "plan_trip":
        raise ValueError(f"Unknown tool: {name}")

    request = arguments.get("request", "")
    if not request:
        raise ValueError("'request' argument is required")

    result = await run_agent(request)
    return [types.TextContent(type="text", text=result)]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
