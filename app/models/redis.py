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
        return UserStatus._decode_value(value)

    @classmethod
    def from_redis_hash(cls, data: dict) -> "UserStatus":
        if not data:
            raise ValueError("Empty data received from Redis")

        user_id_str = cls._get_field(data, "user_id")
        status = cls._get_field(data, "status")
        type_str = cls._get_field(data, "type")
        updated_at_str = cls._get_field(data, "updated_at")

        if not user_id_str:
            raise ValueError("user_id is required")

        updated_at = datetime.utcnow()
        if updated_at_str and updated_at_str.strip():
            try:
                updated_at = datetime.fromisoformat(updated_at_str)
            except ValueError:
                pass  

        return cls(
            user_id=int(user_id_str),
            status=status if status in ("pending", "sent", "failed") else "pending",
            type=type_str if type_str in ("telegram", "email"),
            updated_at=updated_at
        )