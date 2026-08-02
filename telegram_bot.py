from aiogram import Bot, Dispatcher, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=TOKEN)

pending_feedback = {}

router = Router()

dp = Dispatcher()
dp.include_router(router)

def create_feedback_keyboard(feedback_id):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Approve",
                    callback_data=f"approve:{feedback_id}"
                ),

                InlineKeyboardButton(
                    text="❌ Reject",
                    callback_data=f"reject:{feedback_id}"
                )
            ]
        ]
    )

    return keyboard

async def send_feedback(feedback):
    feedback_id = len(pending_feedback) + 1
    pending_feedback[feedback_id] = feedback

    message = (
        "⭐ New Feedback\n\n"
        f"Name: {feedback.name}\n"
        f"Surname: {feedback.surname}\n"
        f"Rating: {feedback.stars}/5\n"
        f"Comment: {feedback.comment or 'No comment'}"
    )

    await bot.send_message(
        chat_id=ADMIN_ID,
        text=message,
        reply_markup=create_feedback_keyboard(feedback_id)
    )


@router.callback_query()
async def button_click_handler(callback: CallbackQuery):
    action, feedback_id = callback.data.split(":")
    feedback_id = int(feedback_id)
    feedback = pending_feedback.get(feedback_id)

    if feedback is None:
        await callback.answer("This feedback was already handled or not found.", show_alert=True)
        return

    if action == "approve":
        status = "✅ Approved"
    else:
        status = "❌ Rejected"

    await callback.message.edit_text(
        "⭐ Feedback\n\n"
        f"Name: {feedback.name}\n"
        f"Surname: {feedback.surname}\n"
        f"Rating: {feedback.stars}/5\n"
        f"Comment: {feedback.comment or 'No comment'}\n\n"
        f"Status: {status}"
    )

    del pending_feedback[feedback_id]  # prevent double-approve/reject
    await callback.answer()
    
async def start_bot():
    print("Telegram bot started")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
