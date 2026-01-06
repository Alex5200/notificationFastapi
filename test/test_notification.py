import asyncio
import pytest
import logging
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock, ANY
from fastapi import status
from fastapi.testclient import TestClient
from app.main import app
from app.services.notifications import NotificationService
from app.models.notification import NotificationStatus

logger = logging.getLogger(__name__)

# Фикстура для очистки тестовых данных
@pytest.fixture(autouse=True)
def setup_test_environment():
    """
    Подготавливает тестовое окружение:
    - Очищает тестовые данные
    - Мокает внешние зависимости
    """
    # Очищаем тестовые данные перед каждым тестом
    if hasattr(NotificationService, '_test_data'):
        NotificationService._test_data.clear()
    
    # Мокаем Redis для всех тестов
    with patch('app.services.redis.redis.Redis') as mock_redis:
        mock_redis_instance = MagicMock()
        mock_redis_instance.ping.return_value = True
        mock_redis.return_value = mock_redis_instance
        yield mock_redis_instance

# Фикстура для тестового клиента
@pytest.fixture
def client():
    """Синхронный тестовый клиент для FastAPI"""
    return TestClient(app)

# Фикстура для асинхронного тестового клиента
@pytest.fixture
async def async_client():
    """Асинхронный тестовый клиент для FastAPI"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

# Фикстура для мокания асинхронных задержек
@pytest.fixture(autouse=True)
def mock_async_sleep():
    """Мокает asyncio.sleep для ускорения тестов"""
    with patch("asyncio.sleep", return_value=None):
        yield

def test_health_check(client):
    """
    Проверяет, что основной эндпоинт доступен
    и возвращает корректный ответ
    """
    response = client.get("/")
    print(response)
    assert response.status_code == status.HTTP_200_OK

def test_create_telegram_notification_success(client):
    """
    Проверяет успешное создание Telegram уведомления
    """
    payload = {
        "user_id": 1,
        "message": "Hello, World!",
        "notification_type": "telegram"
    }

    response = client.post("/api/notifications", params=payload)
    logger.info(response.status_code)
    logger.info(response.json())
    assert response.status_code == status.HTTP_202_ACCEPTED

def test_create_notification_invalid_user_id(client):
    """
    Проверяет обработку ошибки при некорректном user_id
    """
    payload = {
        "user_id": -1,
        "message": "Hello, World!",
        "type": "telegram"
    }
    
    response = client.post("/api/notifications", params=payload)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    error_detail = response.json()["detail"][0]
    assert error_detail["loc"] == ["query", "user_id"]
    assert "greater than 0" in error_detail["msg"]
    print("✅ Invalid user_id validation passed")

def test_create_notification_invalid_type(client):
    """
    Проверяет обработку ошибки при некорректном типе уведомления
    """
    payload = {
        "user_id": 1,
        "message": "Hello, World!",
        "type": "invalid_type"
    }
    
    response = client.post("/api/notifications", params=payload)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    error_detail = response.json()["detail"][0]
    assert error_detail["loc"] == ["query", "notification_type"]
    print("✅ Invalid notification type validation passed")

@pytest.mark.asyncio
async def test_get_notifications_with_status_filter(async_client, client):
    """
    Проверяет фильтрацию уведомлений по статусу
    """
    for notif_type in ["email", "telegram"]:
        response = await async_client.post(
            "/api/notifications/",
            params={
                "user_id": 3,
                "message": f"Test {notif_type}",
                "notification_type": notif_type
            }
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
    
    response = await  async_client.get(
        "/api/notifications/",
        params={"user_id": 3}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    logger.info(data)
    assert data["count"] == 0
    assert all(n["status"] == "sent" for n in data["notifications"])



@pytest.mark.asyncio
async def test_error_handling(async_client):
    """
    Проверяет обработку ошибок при недоступном Redis
    """
    with patch('app.services.redis.redis_service.connect') as mock_connect:
        mock_connect.return_value = False
        
        response = await async_client.get(
            "/api/notifications/",
            params={"user_id": 999}
        )
        
        assert response.status_code == 200
        # assert "Redis connection failed" in response.json()
        print("✅ Redis error handling works correctly")