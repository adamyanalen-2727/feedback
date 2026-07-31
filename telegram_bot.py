from aiogram import Bot, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = "8812617489:AAEIdUqG5Vq4jEqYNnKN3XD18uXSF-lDWYs"
ADMIN_ID = "1354274325"

bot = Bot(token=TOKEN)

def create_feedback_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
               [
                   InlineKeyboardButton(
                       text="✅ Approve",
                       callback_data = "approve"
                   ),
                   InlineKeyboardButton(
                       text="❌ Reject",
                       callback_data = "reject"
                   )
               ]
        ]
    )
    
    return keyboard

async def send_feedback(feedback):

    message = (
        "⭐ New Feedback\n\n"
        f"Name: {feedback.name}\n"
        f"Surname: {feedback.surname}\n"
        f"Rating: {feedback.start}/5\n"
        f"Comment: {feedback.comment or 'No comment'}"        
    )

    await bot.send_message(
            chat_id=ADMIN_ID,
            text=message,
            reply_markup=create_feedback_keyboard()
            )
