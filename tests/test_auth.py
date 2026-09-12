from httpx import ASGITransport, AsyncClient

from app.main import app

async def test_missing_api_key_returns_401():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as unauthenticated_client:
        resp = await unauthenticated_client.get("/user/1")
        assert resp.status_code == 401

async def test_wrong_api_key_returns_401():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers={"X-API-KEY": "wrong-key"}) as client_with_wrong_key:
        resp = await client_with_wrong_key.get("/user/1")
        assert resp.status_code == 401


