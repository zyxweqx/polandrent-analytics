async def test_create_apartment_api(client):
    response = await client.post('/apartments/', json={
        "url": "https://example.com/apt1",
        "title": "test apartment",
        "city": "Poznan",
        "price": 2000
    })
    assert response.status_code == 200
    assert response.json()["price"] == 2000
    assert response.json()["title"] == "test apartment"
    assert response.json()["city"] == "Poznan"

async def test_dublicate_url_api(client):
    await client.post('/apartments/', json={
        "url": "https://example.com/apt2",
        "title": "test apartment1",
        "city": "Poznan",
        "price": 1500
    })
    dublicated_response = await client.post('/apartments/', json={
        "url": "https://example.com/apt2",
        "title": "test apartment2",
        "city": "Poznan",
        "price": 2300
    })
    assert dublicated_response.status_code == 409
    assert dublicated_response.json() == {"detail": "Apartment already exists"}

async def test_invalid_price_api(client):
    response = await client.post('/apartments/', json={
        "url": "https://example.com/apt5",
        "title": "test apartment2",
        "city": "Poznan",
        "price": -100
    })
    assert response.status_code == 422

async def test_get_apartment_not_found(client):
    response = await client.get('/apartments/99999')
    assert response.status_code == 404

async def test_update_apartment_not_found(client):
    response = await client.patch('/apartments/99999', json={"price": 1000})
    assert response.status_code == 404

async def test_delete_apartment_not_found(client):
    response = await client.delete('/apartments/99999')
    assert response.status_code == 404
