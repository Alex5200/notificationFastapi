import pytest
from datetime import datetime
from app.models.redis import UserStatus


class TestUserStatusFromRedisHash:
    """Тесты для UserStatus.from_redis_hash"""

    def test_with_bytes_keys(self):
        """Тест с bytes ключами (decode_responses=False)"""
        data = {
            b"user_id": b"123",
            b"status": b"sent",
            b"type": b"telegram",
            b"updated_at": b"2024-01-07T10:00:00"
        }

        result = UserStatus.from_redis_hash(data)

        assert result.user_id == 123
        assert result.status == "sent"
        assert result.type == "telegram"
        assert result.updated_at == datetime(2024, 1, 7, 10, 0, 0)

    def test_with_string_keys(self):
        """Тест со строковыми ключами (decode_responses=True)"""
        data = {
            "user_id": "456",
            "status": "pending",
            "type": "email",
            "updated_at": "2024-01-07T12:00:00"
        }

        result = UserStatus.from_redis_hash(data)

        assert result.user_id == 456
        assert result.status == "pending"
        assert result.type == "email"

    def test_with_empty_type(self):
        """Тест с пустым type"""
        data = {
            b"user_id": b"789",
            b"status": b"pending",
            b"type": b"",
            b"updated_at": b"2024-01-07T14:00:00"
        }

        result = UserStatus.from_redis_hash(data)

        assert result.user_id == 789
        assert result.type is None

    def test_with_invalid_status_defaults_to_pending(self):
        """Тест с невалидным статусом — должен стать pending"""
        data = {
            "user_id": "100",
            "status": "invalid_status",
            "type": "telegram",
            "updated_at": "2024-01-07T10:00:00"
        }

        result = UserStatus.from_redis_hash(data)

        assert result.status == "pending"

    def test_with_invalid_type_defaults_to_none(self):
        """Тест с невалидным типом — должен стать None"""
        data = {
            "user_id": "100",
            "status": "sent",
            "type": "sms",
            "updated_at": "2024-01-07T10:00:00"
        }

        result = UserStatus.from_redis_hash(data)

        assert result.type is None

    def test_with_missing_updated_at(self):
        """Тест без updated_at — должен использовать текущее время"""
        data = {
            b"user_id": b"200",
            b"status": b"sent",
            b"type": b"email",
            b"updated_at": b""
        }

        before = datetime.utcnow()
        result = UserStatus.from_redis_hash(data)
        after = datetime.utcnow()

        assert before <= result.updated_at <= after

    def test_empty_data_raises_error(self):
        """Тест с пустым dict — должен бросить ValueError"""
        with pytest.raises(ValueError, match="Empty data"):
            UserStatus.from_redis_hash({})

    def test_missing_user_id_raises_error(self):
        """Тест без user_id — должен бросить ValueError"""
        data = {
            b"status": b"sent",
            b"type": b"telegram"
        }

        with pytest.raises(ValueError, match="user_id is required"):
            UserStatus.from_redis_hash(data)


class TestUserStatusToRedisHash:
    """Тесты для UserStatus.to_redis_hash"""

    def test_to_redis_hash_complete(self):
        """Тест конвертации полной модели"""
        status = UserStatus(
            user_id=123,
            status="sent",
            type="telegram",
            updated_at=datetime(2024, 1, 7, 10, 0, 0)
        )

        result = status.to_redis_hash()

        assert result["user_id"] == "123"
        assert result["status"] == "sent"
        assert result["type"] == "telegram"
        assert result["updated_at"] == "2024-01-07T10:00:00"

    def test_roundtrip(self):
        """Тест туда-обратно: модель -> redis -> модель"""
        original = UserStatus(
            user_id=789,
            status="sent",
            type="email",
            updated_at=datetime(2024, 1, 7, 15, 30, 0)
        )

        redis_data = original.to_redis_hash()
        restored = UserStatus.from_redis_hash(redis_data)

        assert restored.user_id == original.user_id
        assert restored.status == original.status
        assert restored.type == original.type
        assert restored.updated_at == original.updated_at