import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# ============ НАСТРОЙКИ ============
BOT_TOKEN = "8704832247:AAE9wb1AcO6Rj1dIP8odbMt89Hn1KNij9ko"
CHANNEL_ID = "@skidkology"
CHANNEL_LINK = "https://t.me/skidkology"
# ===================================

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def is_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception as e:
        logging.error(f"Ошибка проверки подписки: {e}")
        return False

def subscribe_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Перейти на канал", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_sub")]
    ])

@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id

    if await is_subscribed(user_id):
        await message.answer(
            "Ожидайте ответа оператора.\n"
            "Пришлём вам инструкцию в порядке очереди."
        )
    else:
        await message.answer(
            "Для продолжения работы подпишитесь на наш канал 👇",
            reply_markup=subscribe_kb()
        )

@dp.callback_query(F.data == "check_sub")
async def check_sub(callback: CallbackQuery):
    user_id = callback.from_user.id

    if await is_subscribed(user_id):
        try:
            await callback.message.delete()
        except Exception:
            pass

        await callback.message.answer(
            "Ожидайте ответа оператора.\n"
            "Пришлём вам инструкцию в порядке очереди."
        )
        await callback.answer()
    else:
        await callback.answer("Вы ещё не подписались 😔", show_alert=True)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())