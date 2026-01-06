from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime
import json

class UserStatus(BaseModel):
    user_id: int
    status: Literal["pending", "sent"] = "pending"
    type: Literal["telegram", "email"] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_redis_hash(self) -> dict:
        return {
            "user_id": str(self.user_id),
            "status": self.status,
            "type": self.type,
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_redis_hash(cls, data: dict) -> "UserStatus":
        return cls(
            user_id=int(data[b"user_id"]),
            status=data[b"status"].decode(),
            type=data[b"type"].decode(),
            updated_at=datetime.fromisoformat(data[b"updated_at"].decode())
        )
