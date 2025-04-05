
from bot_core.utils.download_replies import load_replies
async def main_aiogram_bot():
    """Основная точка входа для запуска телеграм-бота."""
    result = await load_replies()
    if result:
        from bot_core.bot_handlers.ask_data_handler import collect_data
        from bot_core.bot_handlers.main_menu_handler import main_menu_handler
        from bot_core.bot_handlers.main_menu_handler import show_list_for_client
        from bot_core.bot_handlers.main_menu_handler import show_list_for_seller
        from bot_core.bot_handlers.main_menu_handler import battery_catch_handler
        from bot_core.bot_handlers.main_menu_handler import code_catch_handler
        from bot_core.bot_handlers.main_menu_handler import lottery_result
        from bot_core.bot_handlers.profile_handler import profile_handler
        from bot_core.bot_handlers.profile_handler.survey import survey_handler
        from bot_core.bot_handlers.profile_handler.survey import change_language_handler
        from bot_core.bot_handlers.ask_data_handler import agreement_handler
        from bot_core.bot_handlers.messanger import messanger_handler
        from bot_core.bot_handlers import start_handler
        from bot_core.create_bot import dp, bot

        dp.include_router(start_handler.router)
        dp.include_router(collect_data.router)
        dp.include_router(main_menu_handler.router)
        dp.include_router(profile_handler.router)
        dp.include_router(survey_handler.router)
        dp.include_router(change_language_handler.router)
        dp.include_router(battery_catch_handler.router)
        dp.include_router(agreement_handler.router)
        dp.include_router(show_list_for_client.router)
        dp.include_router(code_catch_handler.router)
        dp.include_router(show_list_for_seller.router)
        dp.include_router(lottery_result.router)
        # dp.include_router(messanger_handler.router)
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
