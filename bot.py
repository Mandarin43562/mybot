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
CHANNEL_LINK = "https://t.me/+Lh0WShQxAaZiOTMy"
# ===================================

# Текст сообщения после подписки
WAIT_TEXT = (
    "Здравствуйте!\n"
    "Благодарим за интерес к нашему товару!\n\n"
    "Ожидайте ответа оператора.\n"
    "Пришлём вам инструкцию в порядке очереди."
)

# Через сколько секунд удалять сообщение (10 минут = 600 секунд)
DELETE_AFTER = 600

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def is_subscribed(user_id: int) -> bool:
    """Тихая проверка подписки на канал."""
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

async def delete_after(message: Message, seconds: int):
    """Удаляет сообщение через N секунд."""
    await asyncio.sleep(seconds)
    try:
        await message.delete()
    except Exception as e:
        logging.warning(f"Не удалось удалить сообщение: {e}")

async def send_wait_message(chat_id: int):
    """Отправляет сообщение ожидания и планирует его удаление."""
    msg = await bot.send_message(chat_id=chat_id, text=WAIT_TEXT)
    asyncio.create_task(delete_after(msg, DELETE_AFTER))

@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id

    if await is_subscribed(user_id):
        # Пункт 2: подписан — сразу шлём сообщение
        await send_wait_message(user_id)
    else:
        # Пункт 3: не подписан — просим подписаться
        await message.answer(
            "Для продолжения работы подпишитесь на наш канал 👇",
            reply_markup=subscribe_kb()
        )

@dp.callback_query(F.data == "check_sub")
async def check_sub(callback: CallbackQuery):
    user_id = callback.from_user.id

    # Удаляем сообщение с просьбой подписаться (в любом случае)
    try:
        await callback.message.delete()
    except Exception:
        pass

    if await is_subscribed(user_id):
        # Пункт 4: подписался — шлём сообщение из пункта 2
        await callback.answer()
        await send_wait_message(user_id)
    else:
        # Пункт 5: не подписался — снова просим подписаться
        await callback.answer("Вы ещё не подписались 😔", show_alert=True)
        await callback.message.answer(
            "Для продолжения работы подпишитесь на наш канал 👇",
            reply_markup=subscribe_kb()
        )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
