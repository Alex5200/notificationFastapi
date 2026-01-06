from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Literal

MessageType = Literal["telegram", "email"]

class SendNotificationData(BaseModel):
    user_id: int = Field(..., gt=0, description="ID пользователя")
    message: str = Field(..., min_length=1, max_length=500,  description="Сообщение от пользователя")
    type: Optional[MessageType] = None