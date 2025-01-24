
from bot_core.utils.download_replies import load_replies
async def main_aiogram_bot():
    """Основная точка входа для запуска телеграм-бота."""
    result = await load_replies()
    if result:
        import logging
        from bot_core.bot_handlers.ask_data_handler import collect_data
        from bot_core.bot_handlers.main_menu_handler import main_menu_handler
        from bot_core.bot_handlers import commands
        from bot_core.create_bot import dp, bot
        logging.info("Настройка бота")
        dp.include_router(commands.router)
        dp.include_router(collect_data.router)
        dp.include_router(main_menu_handler.router)
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)