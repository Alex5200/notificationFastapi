import pytest
import redis
from unittest.mock import MagicMock, patch
from app.services.redis import RedisService
from app.main import app

@pytest.fixture(autouse=True)
def mock_redis_connection():
    """Мокает подключение к Redis для всех тестов"""
    mock_redis = MagicMock()
    mock_redis.ping.return_value = True
    
    with patch('redis.Redis') as mock_redis_class:
        mock_redis_class.return_value = mock_redis
        yield mock_redis

@pytest.fixture
def test_client():
    """Фикстура для тестового клиента FastAPI"""
    from fastapi.testclient import TestClient
    return TestClient(app)

@pytest.fixture
def async_test_client():
    """Фикстура для асинхронного тестового клиента"""
    from httpx import AsyncClient
    from httpx._transports.asgi import ASGITransport
    
    async def async_client():
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            yield client
    
    return async_client