from aiogram import Bot, Dispatcher, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from dotenv import load_dotenv
import os

load_dotenv()

bot = Bot(token=TOKEN)

router = Router()

dp = Dispatcher()
dp.include_router(router)


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

@router.callback_query()
async def button_click_handler(callback: CallbackQuery):

    action = callback.data

    if action == "approve":
        await callback.message.answer(
            "Feedback approved !!!"
                )
        print("approved")

    elif action == "reject":
        await callback.message.answer(
            "Feedback rejected !!!"
                )
        print("rejected")

    await callback.answer()

async def start_bot():
    print("Telegram bot started")
    await dp.start_polling(bot)


