import asyncio

from aiogram import Bot, Dispatcher

from apps.telegram.router import router
from infrastructure.config import get_settings
from infrastructure.observability import configure_logging


def build_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher()
    dispatcher.include_router(router)
    return dispatcher


async def run() -> None:
    settings = get_settings()
    configure_logging(settings)

    if settings.telegram_bot_token is None:
        raise RuntimeError("BAKUNITY_TELEGRAM_BOT_TOKEN is required to run Telegram client")

    bot = Bot(token=settings.telegram_bot_token.get_secret_value())
    dispatcher = build_dispatcher()

    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(run())
