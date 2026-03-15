# Travel Planner

An AI-powered travel planning agent built with Claude. Ask it anything about a trip — it researches destinations, builds day-by-day itineraries, estimates budgets, and checks weather.

## Architecture

```
External client (Claude Desktop, etc.)
        │  MCP protocol
        ▼
  mcp_server.py     ← exposes agent to the outside world as a single tool
        │  calls
        ▼
    agent.py         ← agentic loop + tool orchestration (claude-opus-4-6)
        │  calls
        ▼
  tools/*.py         ← destination / itinerary / budget / weather tools
```

## Setup

**1. Clone and configure environment**
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

## Usage

### CLI (direct)
```bash
python src/agent.py "Plan a 7-day trip to Japan from New York in April, interested in food and temples"
python src/agent.py "5-day budget trip to Bangkok"
python src/agent.py "Luxury 3-day weekend in Paris"
```

### MCP Server (Claude Desktop / other MCP clients)
```bash
python src/mcp_server.py
```

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "travel-planner": {
      "command": "python",
      "args": ["/path/to/Travel_planner/src/mcp_server.py"],
      "env": {
        "ANTHROPIC_API_KEY": "your-key-here"
      }
    }
  }
}
```

Then ask Claude Desktop: *"Use the travel planner to plan a 5-day trip to Tokyo."*

## Running Tests
```bash
pytest tests/
```

Tests cover all four tools individually and one end-to-end agent integration test. Requires `ANTHROPIC_API_KEY` to be set.

## Tools

| Tool | Description |
|------|-------------|
| `search_destination` | Country, language, currency, timezone, top attractions |
| `generate_itinerary` | Day-by-day plan accounting for origin, visa, flight time |
| `estimate_budget` | Per-day and total cost breakdown by category |
| `get_weather_info` | Typical weather for a destination in a given month |

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Yes |
