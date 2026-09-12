import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_scenarios_listing_and_detail(client: AsyncClient):
    # 1. List scenarios
    res = await client.get("/api/v1/scenarios")
    assert res.status_code == 200, res.text
    scenarios = res.json()
    assert len(scenarios) >= 10, f"Expected at least 10 scenarios, found {len(scenarios)}"

    first_scenario = scenarios[0]
    assert "id" in first_scenario
    assert "title" in first_scenario
    assert "slug" in first_scenario
    assert "category" in first_scenario
    assert "difficulty" in first_scenario
    assert "npc_role" in first_scenario
    assert "system_prompt" not in first_scenario

    # 2. Retrieve scenario detail by ID
    scenario_id = first_scenario["id"]
    detail_res = await client.get(f"/api/v1/scenarios/{scenario_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == scenario_id
    assert "financial_context" in detail
    assert "objective" in detail
    assert "initial_state" in detail
    assert "max_turns" in detail
    # Ensure sensitive internal system prompt is NEVER exposed
    assert "system_prompt" not in detail
    # Learning materials are always present (possibly empty list)
    assert "learning_materials" in detail
    assert isinstance(detail["learning_materials"], list)

    # 3. Non-existent scenario UUID
    non_existent = str(uuid.uuid4())
    not_found = await client.get(f"/api/v1/scenarios/{non_existent}")
    assert not_found.status_code == 404

    # 4. Invalid UUID format
    invalid_uuid = await client.get("/api/v1/scenarios/not-a-valid-uuid")
    assert invalid_uuid.status_code == 422
