"""Точка входа — запуск бота удаления фона"""
import asyncio
import logging
import sys

# uvloop ускоряет asyncio в 2-4 раза (не работает на Windows!)
try:
    import uvloop
    uvloop.install()
except ImportError:
    pass  # на Windows — работаем без uvloop

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings

# настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Инициализация и запуск бота"""
    # подключаемся к Local Bot API если указан URL
    session = None
    api_url = settings.bot_api_url
    if api_url != "https://api.telegram.org":
        session = AiohttpSession(
            api=TelegramAPIServer.from_base(api_url, is_local=True),
            timeout=300,  # 5 минут — обработка тяжёлых фото может занять время
        )
        logger.info(f"Local Bot API: {api_url}")

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session,
    )
    dp = Dispatcher(storage=MemoryStorage())

    # подключаем хэндлеры (порядок важен!)
    from bot.handlers import start, admin, remover

    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(remover.router)

    # подключаем мидлвари
    from bot.middlewares.rate_limit import RateLimitMiddleware
    from bot.middlewares.subscription import SubscriptionMiddleware

    dp.message.middleware(RateLimitMiddleware())
    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())

    # фоновая очистка
    async def _background_cleanup() -> None:
        """Фоновая задача: очистка памяти каждые 5 минут"""
        from bot.middlewares.rate_limit import cleanup_stale_entries
        from bot.services.cache import cleanup_expired as cleanup_cutout_cache
        while True:
            await asyncio.sleep(300)  # 5 минут
            removed = cleanup_stale_entries()
            if removed:
                logger.info("Фоновая очистка: удалено %d записей rate limit", removed)
            removed_cutouts = cleanup_cutout_cache()
            if removed_cutouts:
                logger.info("Фоновая очистка: удалено %d cutout-кэшей", removed_cutouts)

    @dp.startup()
    async def on_startup() -> None:
        # создаём таблицы в БД
        from bot.database import engine
        from bot.database.models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Таблицы БД созданы")

        # прогрев дефолтной rembg-сессии в фоне (не блокируем старт polling)
        async def _warmup_rembg() -> None:
            from bot.services.remover import _get_session
            try:
                await asyncio.to_thread(_get_session, settings.default_model)
                logger.info("rembg-сессия %s прогрета", settings.default_model)
            except Exception as e:
                logger.warning("Прогрев rembg не удался: %s", e)

        asyncio.create_task(_warmup_rembg())

        # запускаем фоновую очистку
        asyncio.create_task(_background_cleanup())
        logger.info("Фоновая очистка запущена (интервал 5 мин)")

        bot_info = await bot.get_me()
        logger.info(f"Бот @{bot_info.username} запущен!")

        # ставим дефолтное меню команд (глобально, для новых юзеров)
        from bot.utils.commands import set_default_commands
        await set_default_commands(bot)
        logger.info("Дефолтное меню команд установлено")

    @dp.shutdown()
    async def on_shutdown() -> None:
        logger.info("Бот остановлен")

    # запускаем polling с retry на сетевые сбои
    try:
        while True:
            try:
                logger.info("Запуск polling...")
                await dp.start_polling(bot)
                break  # штатный выход (shutdown)
            except (asyncio.CancelledError, KeyboardInterrupt):
                raise
            except Exception as e:
                logger.exception("Polling упал: %s — рестарт через 5 сек", e)
                await asyncio.sleep(5)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
