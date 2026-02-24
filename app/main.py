from fastapi import FastAPI, BackgroundTasks, HTTPException,Query
from fastapi.responses import RedirectResponse
from app.routers import notification
from app.config import settings
import asyncio
import time


app = FastAPI(title="Сервис уведомлений")

app.include_router(notification.router)

@app.get("/")
async def main():
    return RedirectResponse("/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.server_host, port=settings.server_port, reload=settings.debug)