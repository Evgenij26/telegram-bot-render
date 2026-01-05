import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, PhotoSize
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# === НАСТРОЙКИ ===
BOT_TOKEN = os.getenv("BOT_TOKEN")  # ← читаем из переменных окружения (безопасно!)
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "6447177900"))  # ← можно задать через переменную, или оставить по умолчанию

# WEBHOOK настройки
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "https://telegram-bot-render.onrender.com")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

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
        "• Текст с занятой позицией (например: «3-е место, дивизион Супер»)\n"
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
    
    await bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=message.photo[-1].file_id,
        caption=report[:1024]
    )
    await message.answer("✅ Фотоотчёт принят.")


# === Webhook функции ===

async def on_startup(bot: Bot):
    """Вызывается при запуске — устанавливает webhook"""
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook установлен на {WEBHOOK_URL}")


async def on_shutdown(bot: Bot):
    """Вызывается при остановке — удаляет webhook"""
    await bot.delete_webhook()
    logging.info("Webhook удалён")


def main():
    """Запуск aiohttp-сервера для обработки webhook'ов"""
    dp.include_router(router)

    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    port = int(os.getenv("PORT", 8000))  # Render сам задаст PORT
    web.run_app(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    main()
