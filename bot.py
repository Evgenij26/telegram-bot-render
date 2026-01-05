import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, PhotoSize
from aiogram.filters import Command

# === НАСТРОЙКИ ===
BOT_TOKEN = "8322867794:AAG8txqr-sBY0IT9CNAVOHfJ6f63oo4SGO4"  # ← сюда вставь токен от BotFather
ADMIN_CHAT_ID = 6447177900   # ← замени на свой ID (узнать можно через @userinfobot)

# =================

bot = Bot(token=BOT_TOKEN)
router = Router()
dp = Dispatcher()

@router.message(Command("start"))
@router.message(Command("help"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет, капитан! 📋\n\n"
        "Отправляй сюда:\n"
        "• Текст с занятой позицией (например: «3-е место, дивизион Супер)\n"
        "• ИЛИ фото с результатом.\n\n"
        "Все отчёты будут переданы лидеру клана."
    )

@router.message(F.text)
async def handle_text_report(message: Message):
    report = f"📝 Отчёт от @{message.from_user.username or message.from_user.id}:\n\n{message.text}"
    await bot.send_message(ADMIN_CHAT_ID, report)
    await message.answer("✅ Текстовый отчёт принят.")

@router.message(F.photo)
async def handle_photo_report(message: Message):
    caption = message.caption or "Без подписи"
    report = f"📸 Фотоотчёт от @{message.from_user.username or message.from_user.id}:\n\n{caption}"
    
    # Пересылаем фото с подписью
    await bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=message.photo[-1].file_id,  # самое большое разрешение
        caption=report[:1024]  # Telegram ограничивает длину подписи
    )
    await message.answer("✅ Фотоотчёт принят.")

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
