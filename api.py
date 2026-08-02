import uvicorn
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional
from telegram_bot import send_feedback, start_bot

app = FastAPI()

class Feedback(BaseModel):
    name: str
    surname: str
    stars: int = Field(ge=1, le=5)
    comment: Optional[str] = None


@app.post("/feedback")
async def create_feedback(feedback: Feedback):
    await send_feedback(feedback)
    return {
        "messange": "Feedback saved",
        "feedback": feedback
    }

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
