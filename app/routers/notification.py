import asyncio
from fastapi import APIRouter, BackgroundTasks, Query, HTTPException
from typing import Optional, Literal
from datetime import datetime
from app.models.notification import (
    NotificationRecord, NotificationType, NotificationStatus
)
from app.services.notifications import NotificationService
from app.services.redis import redis_service

router = APIRouter(
    prefix="/api/notifications",
    tags=["notifications"]
)

@router.post("/",
    summary="Отправка уведомлений",
    description="Отправка уведомления пользователю через указанный канал",
    response_description="Успешно созданное уведомление",
    status_code=202
)
async def send_notification(
    background_tasks: BackgroundTasks,
    user_id: int = Query(..., gt=0, description="ID пользователя"),
    message: str = Query(..., min_length=1, max_length=1000, description="Текст уведомления"),
    notification_type: NotificationType = Query(..., description="Тип уведомления")
):
    if notification_type not in [NotificationType.TELEGRAM, NotificationType.EMAIL]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid notification type. Must be one of: {[t.value for t in NotificationType]}"
        )

    if notification_type == NotificationType.TELEGRAM:
        background_tasks.add_task(
            NotificationService.send_telegram_notification,
            user_id,
            message
        )
    elif notification_type == NotificationType.EMAIL:
        background_tasks.add_task(
            NotificationService.send_email_notification,
            user_id,
            message
        )
    else:
        raise HTTPException(
            status_code=400,
            detail=f"err type {notification_type}"
        )

    return {
        "message": "Notification processing started",
        "user_id": user_id,
        "type": notification_type.value,
        "status": "accepted"
    }

@router.get("/",
    summary="Получение уведомлений пользователя",
    description="Получение списка уведомлений для конкретного пользователя с возможной фильтрацией по статусу",
    response_description="Список уведомлений пользователя"
)
async def get_notifications(
    user_id: int = Query(..., gt=0, description="ID пользователя"),
    status: Optional[Literal["sent", "pending", "failed"]] = Query(None, description="Фильтр по статусу")
):
    try:
        status_enum = NotificationStatus(status) if status else None
        notifications = NotificationService.get_user_notifications(user_id, status_enum)

        return {
            "user_id": user_id,
            "notifications": [notification.dict() for notification in notifications],
            "count": len(notifications)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))