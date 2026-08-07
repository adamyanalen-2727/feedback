from aiogram import Bot, Dispatcher, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from dotenv import load_dotenv
from db_connection import input_from_telegram, init_pool, close_pool
import os
import logging

load_dotenv()

logger = logging.getLogger("telegram_bot")

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
    logger.info(f"New feedback #{feedback_id} from {feedback.name} {feedback.surname}, {feedback.stars}/5")

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
        logger.warning(f"Callback for unknown/handled feedback_id={feedback_id}")
        await callback.answer("This feedback was already handled or not found.", show_alert=True)
        return

    if action == "approve":
        status = "✅ Approved"
        try:
            await input_from_telegram(
                name=feedback.name,
                surname=feedback.surname,
                stars=feedback.stars,
                message=feedback.comment
            )
        except Exception as e:
            logger.exception(f"Approve failed for feedback_id={feedback_id}")
            await callback.answer("Failed to save feedback to DB.", show_alert=True)
            print(f"DB insert error: {e}")
            return
        logger.info(f"Feedback #{feedback_id} approved by admin")
    else:
        status = "❌ Rejected"
        logger.info(f"Feedback #{feedback_id} rejected by admin")

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
    logger.info("Telegram bot started")
    print("Telegram bot started")
    await init_pool()
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await close_pool()    
        logger.info("Telegram bot stopped")        
