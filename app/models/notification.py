from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Literal, Optional

class NotificationType(str, Enum):
    TELEGRAM = "telegram"
    EMAIL = "email"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"

class NotificationRecord(BaseModel):
    user_id: int = Field(..., gt=0)
    message: str = Field(..., min_length=1, max_length=1000)
    type: NotificationType
    status: NotificationStatus
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None

    def to_redis_hash(self) -> dict:
        return {
            "user_id": str(self.user_id),
            "message": self.message,
            "type": self.type.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "sent_at": self.sent_at.isoformat() if self.sent_at else ""
        }

   class NotificationRecord(BaseModel):
    user_id: int = Field(..., gt=0)
    message: str = Field(..., min_length=1, max_length=1000)
    type: NotificationType
    status: NotificationStatus
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None

    def to_redis_hash(self) -> dict:
        return {
            "user_id": str(self.user_id),
            "message": self.message,
            "type": self.type.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "sent_at": self.sent_at.isoformat() if self.sent_at else ""
        }

    @staticmethod
    def _decode_value(value) -> str:
        if value is None:
            return ""
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return str(value)

    @staticmethod
    def _get_field(data: dict, field: str) -> str:
        value = data.get(field.encode("utf-8"))
        if value is None:
            value = data.get(field)
        return NotificationRecord._decode_value(value)

    @classmethod
    def from_redis_hash(cls, data: dict) -> "NotificationRecord":
        if not data:
            raise ValueError("Empty data received from Redis")

        user_id_str = cls._get_field(data, "user_id")
        message = cls._get_field(data, "message")
        notif_type = cls._get_field(data, "type")
        status = cls._get_field(data, "status")
        created_at_str = cls._get_field(data, "created_at")
        sent_at_str = cls._get_field(data, "sent_at")

        if not user_id_str:
            raise ValueError("user_id is required")
        if not message:
            raise ValueError("message is required")
        if not notif_type:
            raise ValueError("type is required")
        if not status:
            raise ValueError("status is required")
        if not created_at_str:
            raise ValueError("created_at is required")

        sent_at = None
        if sent_at_str and sent_at_str.strip():
            sent_at = datetime.fromisoformat(sent_at_str)

        return cls(
            user_id=int(user_id_str),
            message=message,
            type=NotificationType(notif_type),
            status=NotificationStatus(status),
            created_at=datetime.fromisoformat(created_at_str),
            sent_at=sent_at
        )