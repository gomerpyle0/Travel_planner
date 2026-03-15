"""
Tests for the Travel Planner agent and tools.

Run with:
    pytest tests/
"""

import json
import sys
import os
import pytest

# Allow imports from src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


# ---------------------------------------------------------------------------
# Tool tests
# ---------------------------------------------------------------------------

class TestSearchDestination:
    @pytest.mark.asyncio
    async def test_returns_required_fields(self):
        from tools.destination import search_destination

        result = await search_destination("Paris")
        assert isinstance(result, dict)
        for field in ("country", "language", "currency", "timezone", "top_attractions"):
            assert field in result, f"Missing field: {field}"

    @pytest.mark.asyncio
    async def test_top_attractions_is_list(self):
        from tools.destination import search_destination

        result = await search_destination("Tokyo")
        assert isinstance(result["top_attractions"], list)
        assert len(result["top_attractions"]) > 0


class TestGenerateItinerary:
    @pytest.mark.asyncio
    async def test_returns_trip_summary_and_itinerary(self):
        from tools.itinerary import generate_itinerary

        result = await generate_itinerary(
            source="London",
            destination="Rome",
            days=3,
            interests=["history", "food"],
        )
        assert isinstance(result, dict)
        assert "trip_summary" in result
        assert "itinerary" in result

    @pytest.mark.asyncio
    async def test_itinerary_day_count(self):
        from tools.itinerary import generate_itinerary

        result = await generate_itinerary(
            source="New York",
            destination="Tokyo",
            days=5,
            interests=["culture"],
        )
        assert len(result["itinerary"]) == 5

    @pytest.mark.asyncio
    async def test_trip_summary_fields(self):
        from tools.itinerary import generate_itinerary

        result = await generate_itinerary(
            source="Sydney",
            destination="Bali",
            days=4,
            interests=["beach", "relaxation"],
        )
        summary = result["trip_summary"]
        assert summary["source"] == "Sydney"
        assert summary["destination"] == "Bali"
        assert summary["days"] == 4


class TestEstimateBudget:
    @pytest.mark.asyncio
    async def test_returns_budget_structure(self):
        from tools.budget import estimate_budget

        result = await estimate_budget(
            destination="Bangkok",
            days=7,
            travel_style="budget",
        )
        assert isinstance(result, dict)
        assert "per_day" in result
        assert "total_trip" in result

    @pytest.mark.asyncio
    async def test_per_day_has_total(self):
        from tools.budget import estimate_budget

        result = await estimate_budget(
            destination="Paris",
            days=5,
            travel_style="mid-range",
        )
        assert "total" in result["per_day"]
        assert result["per_day"]["total"] > 0

    @pytest.mark.asyncio
    async def test_grand_total_present(self):
        from tools.budget import estimate_budget

        result = await estimate_budget(
            destination="Maldives",
            days=5,
            travel_style="luxury",
        )
        assert "grand_total" in result["total_trip"]
        assert result["total_trip"]["grand_total"] > 0


class TestGetWeatherInfo:
    @pytest.mark.asyncio
    async def test_returns_weather_fields(self):
        from tools.weather import get_weather_info

        result = await get_weather_info("Barcelona", "June")
        assert isinstance(result, dict)
        for field in ("temperature", "rainfall", "humidity", "weather_summary"):
            assert field in result, f"Missing field: {field}"

    @pytest.mark.asyncio
    async def test_temperature_has_high_low(self):
        from tools.weather import get_weather_info

        result = await get_weather_info("Iceland", "January")
        temp = result["temperature"]
        assert "average_high_c" in temp
        assert "average_low_c" in temp

    @pytest.mark.asyncio
    async def test_what_to_pack_is_list(self):
        from tools.weather import get_weather_info

        result = await get_weather_info("Dubai", "August")
        assert isinstance(result["what_to_pack"], list)


# ---------------------------------------------------------------------------
# Agent integration test
# ---------------------------------------------------------------------------

class TestAgent:
    @pytest.mark.asyncio
    async def test_agent_responds_to_trip_query(self):
        from agent import run_agent

        result = await run_agent(
            "Give me a brief overview for a 3-day trip to Lisbon from London."
        )
        assert isinstance(result, str)
        assert len(result) > 100  # Should be a substantive response
        # Should mention Lisbon somewhere in the output
        assert "Lisbon" in result or "lisbon" in result.lower()
