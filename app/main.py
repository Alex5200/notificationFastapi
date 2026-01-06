from fastapi import FastAPI, BackgroundTasks, HTTPException,Query
from fastapi.responses import RedirectResponse
from app.routers import notification
import asyncio
import time

app = FastAPI(title="Сервис уведомлений")

app.include_router(notification.router)

@app.get("/")
async def main():
    return RedirectResponse("/docs")