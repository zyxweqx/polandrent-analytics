async def test_create_subscriptions(client):
    user_response = await client.post('/user/', json={"telegram_id": 3, "username": "test3"})
    user_id = user_response.json()['id']
    sub_response = await client.post('/subscriptions/', json={"user_id": user_id, "city": "Poznan"})
    assert sub_response.status_code == 200
    assert sub_response.json()['city'] == "Poznan"
    assert sub_response.json()['user_id'] == user_id

async def test_create_sub_user_undefined(client):
    response = await client.post('subscriptions/', json={"user_id": 99999, "city": "Poznan"})
    assert response.status_code == 404
    assert response.json() == {'detail': 'User not found'}

async def test_price_subscriptions(client):
    user_response = await client.post('/user/', json={"telegram_id": 4, "username": "test4"})
    user_id = user_response.json()['id']
    sub_response = await client.post('/subscriptions/', json={"user_id": user_id, "city": "Poznan", "price_min": 5000, "price_max": 2000})
    assert sub_response.status_code == 422

async def test_subscriptions_list(client):
    user_response = await client.post('/user/', json={"telegram_id": 5, "username": "test5"})
    user_id = user_response.json()['id']
    await client.post('/subscriptions/', json={"user_id": user_id, "city": "Poznan"})
    await client.post('/subscriptions/', json={"user_id": user_id, "city": "Warszawa"})
    get_response = await client.get(f'/subscriptions/user/{user_id}')
    assert get_response.status_code == 200
    assert len(get_response.json()) == 2

async def test_partly_update(client):
    user_response = await client.post('/user/', json={"telegram_id": 6, "username": "test6"})
    user_id = user_response.json()['id']
    create_sub = await client.post('/subscriptions/', json={"user_id": user_id, "city": "Poznan", "rooms_min": 2, "price_max": 1500})
    sub_id = create_sub.json()['id']
    update_response = await client.patch(f'subscriptions/{sub_id}', json={"rooms_min": 3})
    assert update_response.status_code == 200
    assert update_response.json()['rooms_min'] == 3
    assert update_response.json()['price_max'] == 1500

async def test_deleting_subscriptions(client):
    user_response = await client.post('/user/', json={"telegram_id": 7, "username": "test7"})
    user_id = user_response.json()['id']
    create_sub = await client.post('/subscriptions/', json={"user_id": user_id, "city": "Poznan", "rooms_min": 2, "price_max": 1500})
    sub_id = create_sub.json()['id']
    delete_response = await client.delete(f'subscriptions/{sub_id}')
    assert delete_response.status_code == 200

async def test_deleting_undefined_subscriptions(client):
    delete_sub = await client.delete('/subscriptions/9999')
    assert delete_sub.status_code == 404
    assert delete_sub.json() == {'detail': 'Subscription not found'}

