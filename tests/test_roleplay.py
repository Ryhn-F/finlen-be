import uuid
import pytest
from httpx import AsyncClient


async def create_test_user_and_login(client: AsyncClient, suffix: str) -> tuple[dict, str]:
    username = f"roleplayer_{suffix}"
    email = f"roleplayer_{suffix}@example.com"
    password = "StrongPassword123!"

    reg = await client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert reg.status_code == 201

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return reg.json(), token


@pytest.mark.asyncio
async def test_roleplay_session_lifecycle(client: AsyncClient):
    uid1 = uuid.uuid4().hex[:8]
    uid2 = uuid.uuid4().hex[:8]
    user1, token1 = await create_test_user_and_login(client, uid1)
    user2, token2 = await create_test_user_and_login(client, uid2)

    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    # 1. Fetch available scenarios
    scenarios_res = await client.get("/api/v1/scenarios")
    assert scenarios_res.status_code == 200
    scenario_id = scenarios_res.json()[0]["id"]

    # 2. Create session unauthorized
    unauth_create = await client.post("/api/v1/roleplay/sessions", json={"scenario_id": scenario_id})
    assert unauth_create.status_code == 401

    # 3. Create session authorized
    create_res = await client.post(
        "/api/v1/roleplay/sessions",
        json={"scenario_id": scenario_id},
        headers=headers1,
    )
    assert create_res.status_code == 201, create_res.text
    session_data = create_res.json()
    session_id = session_data["session_id"]
    assert session_data["status"] == "active"
    assert session_data["turn_number"] == 1
    assert "first_npc_message" in session_data
    assert len(session_data["first_npc_message"]) > 0

    # 4. Get session details
    detail_res = await client.get(
        f"/api/v1/roleplay/sessions/{session_id}",
        headers=headers1,
    )
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["session_id"] == session_id
    assert detail["status"] == "active"
    assert "scores" in detail
    assert "current_state" in detail

    # 5. Access check: User 2 should be forbidden from accessing User 1's session
    forbidden_res = await client.get(
        f"/api/v1/roleplay/sessions/{session_id}",
        headers=headers2,
    )
    assert forbidden_res.status_code == 403

    # 6. Send user message (Turn evaluation)
    msg_res = await client.post(
        f"/api/v1/roleplay/sessions/{session_id}/messages",
        json={"message": "Saya ingin melihat salinan kontrak dan bukti surat tugas resmi Anda terlebih dahulu."},
        headers=headers1,
    )
    assert msg_res.status_code == 200, msg_res.text
    msg_data = msg_res.json()
    assert msg_data["turn_number"] >= 1
    assert "evaluation" in msg_data
    assert "scores" in msg_data["evaluation"]
    assert "consequence" in msg_data["evaluation"]
    assert "feedback" in msg_data["evaluation"]
    assert "npc_response" in msg_data
    assert "session_scores" in msg_data
    assert msg_data["xp_earned_this_turn"] > 0

    # Verify score deltas strictly within -5..5
    scores = msg_data["evaluation"]["scores"]
    for k in ["critical_thinking", "risk_awareness", "impulse_control", "decision_making"]:
        assert -5 <= scores[k] <= 5

    # 7. Retrieve messages
    history_res = await client.get(
        f"/api/v1/roleplay/sessions/{session_id}/messages",
        headers=headers1,
    )
    assert history_res.status_code == 200
    messages = history_res.json()
    assert len(messages) >= 2  # Opening NPC message + User message + NPC response

    # 8. Complete session
    complete_res = await client.post(
        f"/api/v1/roleplay/sessions/{session_id}/complete",
        headers=headers1,
    )
    assert complete_res.status_code == 200, complete_res.text
    comp_data = complete_res.json()
    assert comp_data["status"] == "completed"
    assert comp_data["xp_earned"] > 0
    assert "progression" in comp_data
    assert comp_data["progression"]["level"] >= 1

    # 9. Verify completed session cannot receive additional messages
    after_complete_msg = await client.post(
        f"/api/v1/roleplay/sessions/{session_id}/messages",
        json={"message": "Halo apakah masih aktif?"},
        headers=headers1,
    )
    assert after_complete_msg.status_code == 400
    assert "Cannot send messages to a 'completed' session" in after_complete_msg.json()["detail"]

    # 10. Verify /auth/me reflects user progression
    me_res = await client.get("/api/v1/auth/me", headers=headers1)
    assert me_res.status_code == 200
    user_me = me_res.json()
    assert user_me["xp"] >= comp_data["xp_earned"]
    assert user_me["financial_instinct"] > 0.0
