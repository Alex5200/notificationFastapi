from pydantic import BaseModel, Field
from typing import Literal, Optional, ClassVar, Tuple
from datetime import datetime


class UserStatus(BaseModel):
    user_id: int
    status: Literal["pending", "sent", "failed"] = "pending"
    type: Optional[Literal["telegram", "email"]] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    VALID_STATUSES: ClassVar[Tuple[str, ...]] = ("pending", "sent", "failed")
    VALID_TYPES: ClassVar[Tuple[str, ...]] = ("telegram", "email")

    def to_redis_hash(self) -> dict:
        return {
            "user_id": str(self.user_id),
            "status": self.status,
            "type": self.type or "",
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
        status_str = cls._get_field(data, "status")
        type_str = cls._get_field(data, "type")
        updated_at_str = cls._get_field(data, "updated_at")

        if not user_id_str:
            raise ValueError("user_id is required")

        status = status_str if status_str in cls.VALID_STATUSES else "pending"

        notif_type = type_str if type_str in cls.VALID_TYPES else None

        updated_at = datetime.utcnow()
        if updated_at_str and updated_at_str.strip():
            try:
                updated_at = datetime.fromisoformat(updated_at_str)
            except ValueError:
                pass

        return cls(
            user_id=int(user_id_str),
            status=status,
            type=notif_type,
            updated_at=updated_at
        )