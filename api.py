from fastapi import FastApi
from pydantic import BaseModel, Field
from typing import Optional
from telegram_bot import send_feedback
app = FastApi()

class Feedback(BaseModel):
    name: str
    surname: str
    start: int = Field(ge=1, le=5)
    comment: Optional[str] = None


@app.post("/feedback")
def create_feedback(feedback: Feedback):
    result = send_feedback(feedback)
    return {
        "messange": "Feedback saved",
        "feedback": feedback

