import asyncio
from datetime import datetime
from typing import List, Optional
from app.models.notification import (
    NotificationRecord, NotificationType, NotificationStatus
)
from app.services.redis import redis_service

class NotificationService:
    @staticmethod
    async def send_telegram_notification(user_id: int, message: str) -> NotificationRecord:
        record = NotificationRecord(
            user_id=user_id,
            message=message,
            type=NotificationType.TELEGRAM,
            status=NotificationStatus.PENDING
        )
        
        with redis_service.get_connection() as r:
            r.hset(f"notification:{record.user_id}:{record.created_at.timestamp()}",
                    mapping=record.to_redis_hash())
        
        await asyncio.sleep(2)

        record.status = NotificationStatus.SENT
        record.sent_at = datetime.utcnow()

        with redis_service.get_connection() as r:
            r.hset(f"notification:{record.user_id}:{record.created_at.timestamp()}", 
                    mapping=record.to_redis_hash())
        
        return record

    @staticmethod
    async def send_email_notification(user_id: int, message: str) -> NotificationRecord:
        record = NotificationRecord(
            user_id=user_id,
            message=message,
            type=NotificationType.EMAIL,
            status=NotificationStatus.PENDING
        )


        with redis_service.get_connection() as r:
            r.hset(f"notification:{record.user_id}:{record.created_at.timestamp()}", 
                    mapping=record.to_redis_hash())

        await asyncio.sleep(3)

        record.status = NotificationStatus.SENT
        record.sent_at = datetime.utcnow()

        with redis_service.get_connection() as r:
            r.hset(f"notification:{record.user_id}:{record.created_at.timestamp()}", 
                    mapping=record.to_redis_hash())

        return record

    @staticmethod
    def get_user_notifications(user_id: int, status: Optional[NotificationStatus] = None) -> List[NotificationRecord]:
        notifications = []

        with redis_service.get_connection() as r:
            keys = r.keys(f"notification:{user_id}:*")

            for key in keys:
                data = r.hgetall(key)
                if data:
                    try:
                        notification = NotificationRecord.from_redis_hash(data)
                        if status is None or notification.status == status:
                            notifications.append(notification)
                    except Exception as e:
                        print(f"Error parsing notification {key}: {e}")

        return sorted(notifications, key=lambda x: x.created_at, reverse=True)