
async def test_create_user(client):
    response = await client.post("/user/", json={"telegram_id": 1, "username": "test1"})
    assert response.status_code == 200
    assert response.json()['telegram_id'] == 1

async def test_get_user_by_id(client):
    create_response = await client.post("/user/", json={"telegram_id": 2, "username": "test2"})
    created_user_id = create_response.json()['id']
    response = await client.get(f"/user/{created_user_id}")
    assert response.status_code == 200
    assert response.json()['id'] == created_user_id
    assert response.json()['telegram_id'] == 2

async def test_undefined_user(client):
    response = await client.get("/user/99999")
    assert response.status_code == 404
    assert response.json() == {'detail': 'User not found'}
