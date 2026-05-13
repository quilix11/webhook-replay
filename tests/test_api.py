import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock

from src.main import app
from src.db.database_session import get_async_session
from src.models.webhook_entity import WebHook

# Dummy webhook object
dummy_webhook = WebHook(
    id=1,
    headers={"Content-Type": "application/json"},
    payload={"foo": "bar"},
    event_name=None
)

# Mock session dependency
async def override_get_async_session():
    mock_session = AsyncMock()
    
    # Mock for router.get("/webhooks/{id}")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = dummy_webhook
    mock_session.execute.return_value = mock_result
    
    yield mock_session

app.dependency_overrides[get_async_session] = override_get_async_session

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_receive_webhook(async_client):
    with patch("src.api.webhook_routes.save_webhook", new_callable=AsyncMock) as mock_save:
        mock_save.return_value = dummy_webhook
        
        response = await async_client.post("/webhooks/receive", json={"foo": "bar"}, headers={"Content-Type": "application/json"})
        
        assert response.status_code == 200
        assert response.json() == {"status": "success", "id": 1}
        mock_save.assert_called_once()

@pytest.mark.asyncio
async def test_list_webhooks(async_client):
    with patch("src.api.webhook_routes.get_all_webhooks", new_callable=AsyncMock) as mock_get_all:
        mock_get_all.return_value = [dummy_webhook]
        
        response = await async_client.get("/webhooks/list")
        
        assert response.status_code == 200
        # FastAPI's jsonable_encoder handles the SQLAlchemy model serialization
        data = response.json()["data"][0]
        assert data["id"] == 1
        assert data["payload"] == {"foo": "bar"}
        assert response.json()["count"] == 1
        mock_get_all.assert_called_once()

@pytest.mark.asyncio
async def test_get_hook(async_client):
    response = await async_client.get("/webhooks/1")
    
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["payload"] == {"foo": "bar"}

@pytest.mark.asyncio
async def test_get_hook_not_found(async_client):
    async def override_not_found_session():
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        yield mock_session
        
    app.dependency_overrides[get_async_session] = override_not_found_session
    
    response = await async_client.get("/webhooks/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "WebHook not found"}
    
    # Restore original override
    app.dependency_overrides[get_async_session] = override_get_async_session

@pytest.mark.asyncio
async def test_replay_hook(async_client):
    with patch("src.api.webhook_routes.replay_webhooks", new_callable=AsyncMock) as mock_replay:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_replay.return_value = mock_response
        
        response = await async_client.post("/webhooks/1/replay?target=http://example.com")
        
        assert response.status_code == 200
        assert response.json() == {"status_code": 200}
        mock_replay.assert_called_once()