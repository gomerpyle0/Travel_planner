# Travel Planner - Claude Code Project Guide

## Project Overview

A Travel Planner MCP (Model Context Protocol) Agent that helps users plan trips by
providing destination research, itinerary generation, budget estimation, and travel
recommendations using Claude AI.

---

## Architecture

```
Travel_planner/
├── CLAUDE.md              # This file - project guide
├── README.md
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
├── src/
│   ├── __init__.py
│   ├── agent.py           # Main Claude agent entrypoint
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── destination.py # Destination research tool
│   │   ├── itinerary.py   # Itinerary generation tool
│   │   ├── budget.py      # Budget estimation tool
│   │   └── weather.py     # Weather info tool
│   └── mcp_server.py      # MCP server exposing the agent to external clients
└── tests/
    ├── __init__.py
    └── test_agent.py
```

### Design: Agent-First, MCP as External Interface

The agent (`agent.py`) is the core — it owns the tools and the agentic loop.
The MCP server (`mcp_server.py`) wraps the agent and exposes it to the outside
world (Claude Desktop, other MCP clients) as a single `plan_trip` tool.

```
External client (Claude Desktop, etc.)
        │  MCP protocol
        ▼
  mcp_server.py          ← exposes agent to the outside world
        │  calls
        ▼
    agent.py             ← agentic loop + tool orchestration
        │  calls
        ▼
  tools/*.py             ← individual travel planning tools
```

---

## Build Steps

### Step 1: Project Setup
- [ ] Initialize Python project structure (folders and `__init__.py` files)
- [ ] Create `requirements.txt` with dependencies:
  - `anthropic` (Claude API SDK)
  - `mcp` (Model Context Protocol SDK)
  - `python-dotenv` (env var management)
  - `httpx` (async HTTP requests)
  - `pytest` + `pytest-asyncio` (testing)
- [ ] Create `.env.example` with `ANTHROPIC_API_KEY=your_key_here`
- [ ] Install dependencies: `pip install -r requirements.txt`

### Step 2: Define Travel Planner Tools
Each tool is a Python function exposed via MCP:

- [ ] **`search_destination(destination: str)`**
  - Returns key info: country, language, currency, timezone, top attractions
- [ ] **`generate_itinerary(source: str, destination: str, days: int, interests: list[str])`**
  - `source`: traveler's origin city/country (e.g. `"New York"`, `"London"`)
  - Itinerary accounts for source location: flight routes, travel time from origin,
    visa requirements based on departure country, and arrival day logistics
  - Returns day-by-day itinerary plan starting from departure
- [ ] **`estimate_budget(destination: str, days: int, travel_style: str)`**
  - Returns budget breakdown (accommodation, food, transport, activities)
- [ ] **`get_weather_info(destination: str, month: str)`**
  - Returns typical weather for travel planning

### Step 3: Build the Claude Agent
- [x] Create `src/agent.py` using the `anthropic` SDK
- [x] Configure the agent with a system prompt describing its role as a travel planner
- [x] Implement an agentic loop: send messages → handle tool calls → return results
- [x] Wire the agent directly to the tools in `src/tools/`
- [x] Add a CLI interface: `python src/agent.py "Plan a 5-day trip to Tokyo"`

### Step 4: Build the MCP Server
- [x] Create `src/mcp_server.py` using the `mcp` SDK
- [x] Expose the agent as a single `plan_trip` MCP tool so external clients
      (Claude Desktop, other agents) can call it via the MCP protocol
- [x] Test the MCP server runs: `python src/mcp_server.py`

### Step 5: Write Tests
- [x] Test each tool function individually
- [x] Test the agent responds correctly to a sample trip planning request
- [x] Run tests: `pytest tests/`

### Step 6: Polish & Document
- [x] Update `README.md` with setup instructions and usage examples
- [ ] Add error handling (API failures, invalid destinations, missing env vars)
- [ ] Add input validation to all tools

---

## Running the Project

```bash
# 1. Set up environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the travel planner agent
python src/agent.py "Plan a 7-day trip to Paris for a family of 4"

# 4. Run tests
pytest tests/
```

---

## Key Design Decisions

- **Agent-first**: `agent.py` is the core — it owns tools and the agentic loop.
  MCP wraps the agent to expose it externally, not the other way around.
- **Async-first**: All tools use `async def` for non-blocking HTTP calls.
- **Claude model**: `claude-opus-4-6` with adaptive thinking for the agent
  (best capability); `claude-sonnet-4-6` for individual tool calls.

---

## Environment Variables

| Variable            | Description                        | Required |
|---------------------|------------------------------------|----------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key             | Yes      |
