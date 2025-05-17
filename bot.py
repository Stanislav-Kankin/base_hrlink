import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import config
from handlers import router
from utils.logging import logger


async def main():
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            link_preview_is_disabled=True
            )
    )

    dp = Dispatcher()
    dp.include_router(router)

    logger.info("Бот-справочник HRlink запущен")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
