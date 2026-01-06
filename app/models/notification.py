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

    @classmethod
    def from_redis_hash(cls,  data: dict) -> "NotificationRecord":
        return cls(
            user_id=int(data.get(b"user_id", data.get("user_id"))),
            message=data.get(b"message", data.get("message")).decode() if isinstance(data.get(b"message"), bytes) else data.get("message"),
            type=NotificationType(data.get(b"type", data.get("type")).decode() if isinstance(data.get(b"type"), bytes) else data.get("type")),
            status=NotificationStatus(data.get(b"status", data.get("status")).decode() if isinstance(data.get(b"status"), bytes) else data.get("status")),
            created_at=datetime.fromisoformat(data.get(b"created_at", data.get("created_at")).decode() if isinstance(data.get(b"created_at"), bytes) else data.get("created_at")),
            sent_at=datetime.fromisoformat(data.get(b"sent_at", data.get("sent_at")).decode()) if data.get(b"sent_at") and data.get(b"sent_at") != b"" else None
        )