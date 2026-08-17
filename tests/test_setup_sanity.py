

async def test_create_user_via_api(client):
    response = await client.post("/user/", json={"telegram_id": 111, "username": "sanity"})

    assert response.status_code == 200
    assert response.json()["telegram_id"] == 111
