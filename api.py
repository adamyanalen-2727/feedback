import uvicorn
import asyncio
import logging
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional
from telegram_bot import send_feedback, start_bot
from db_connection import create_env, get_feedback
from logging.handlers import RotatingFileHandler
from pydantic import BaseModel, Field, field_validator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(
            "/var/log/feedback-bot/bot.log",
            maxBytes=100_000_000,   # 100 MB
            backupCount=5,
        ),
    ],
)

logger = logging.getLogger("fastapi_app")


asyncio.run(create_env())

app = FastAPI()

class Feedback(BaseModel):
    name: str = Field(min_length=1)
    surname: str = Field(min_length=1)
    stars: int = Field(ge=1, le=5)
    comment: Optional[str] = None

@app.post("/feedback")
async def create_feedback(feedback: Feedback):
    await send_feedback(feedback)
    return {
        "messange": "Feedback saved",
        "feedback": feedback
    }

@app.get("/get_feedback")
async def get_feedback_json():
    data = await get_feedback()
    logger.info(f"/get_feedback returned {len(data)} rows")
    return {"feedbacks": data}

@app.on_event("startup")
async def start_telegram():
    asyncio.create_task(start_bot())

if __name__ == "__main__":
    uvicorn.run(
            "api:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
        )
