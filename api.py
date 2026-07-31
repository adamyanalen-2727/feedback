import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional
from telegram_bot import send_feedback

app = FastAPI()

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
    }

if __name__ == "__main__":
    uvicorn.run(
            "api:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
        )
