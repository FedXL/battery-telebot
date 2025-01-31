from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from bot_core.bot_db.db_handlers import create_profiles, check_user
from bot_core.create_bot import bot_log
from bot_core.utils.callback_actions import Calls, CollectDataStates, SpecialStates, CatchBattery, CatchCode
from bot_core.utils.download_replies import BOT_REPLIES

router = Router()

def create_menu_main_kb(language: str, client_or_seller: str) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()


    builder.row(
        types.InlineKeyboardButton(text='Регистрация', callback_data=Calls.PROFILE.START_REGISTRATION),
        types.InlineKeyboardButton(text=BOT_REPLIES['rules_watch_button'][language], callback_data=Calls.RULES_WATCH)
    )

    faq_button = types.InlineKeyboardButton(text=BOT_REPLIES['faq_button'][language],
                                               callback_data=Calls.GO_TO_FAQ)

    if client_or_seller == 'client':
        builder.row(types.InlineKeyboardButton(text=BOT_REPLIES['register_battery_button'][language],
                                               callback_data=Calls.REGISTRATION_BATTERY))
    elif client_or_seller == 'seller':
        builder.row(types.InlineKeyboardButton(text=BOT_REPLIES['register_seller_button'][language],
                                               callback_data=Calls.REGISTRATION_CODE),faq_button)

    profile_button = types.InlineKeyboardButton(text=BOT_REPLIES['profile_button'][language],callback_data=Calls.GO_TO_PROFILE)
    builder.row(profile_button,
                types.InlineKeyboardButton(text=BOT_REPLIES['lottery_result_button'][language],
                                                           callback_data=Calls.LOTTERY_RESULTS))

    builder.row(types.InlineKeyboardButton(text=BOT_REPLIES['help_button'][language], callback_data=Calls.CATCH_MESSAGE))

    return builder.as_markup()



async def main_menu(callback_or_message: types.CallbackQuery | types.Message, state: FSMContext, db: AsyncSession) -> None:
    """
    меню
    1) генерация текста преветсвия.
    2) создание пользователя если Calls в ClientChoice и SellerChoice
    3) создание меню для пользователя или продавца
    4) проверка и добавление в storage langugage и cleient_or_seller
    """

    state_dict = await state.get_data()
    bot_log.info(f"MAIN MENU HANDLER {state_dict}")
    rus_or_kaz = state_dict.get('language')
    to_kill = state_dict.get('kill_message',None)
    bot = callback_or_message.bot
    if to_kill:
        for mes in to_kill:
            message_id = to_kill.pop(0)
            await bot.delete_message(chat_id=callback_or_message.from_user.id ,message_id=message_id)
        state_dict['kill_message'] = []
        await state.set_data(state_dict)

    client_or_seller = state_dict.get('client_or_seller')
    if client_or_seller is None:
        bot_log.critical('client_or_seller is None got to extract it from db')
        result, state_dict = await check_user(db=db, telegram_id=callback_or_message.from_user.id)
        if state_dict:
            client_or_seller = state_dict['client_or_seller']

    menu_text = BOT_REPLIES['main_menu_seller'][rus_or_kaz] if client_or_seller == 'seller' else \
    BOT_REPLIES['main_menu_client'][rus_or_kaz]
    if isinstance(callback_or_message, types.CallbackQuery):
        bot_log.info(f'CALLBACK - WAY')
        if callback_or_message.data in (Calls.CLIENT_CHOICE, Calls.SELLER_CHOICE):
            await callback_or_message.answer('Creating Profile')
            await create_profiles(db=db,rus_or_kaz=rus_or_kaz, telegram_id=callback_or_message.from_user.id,callback_data=callback_or_message.data)
        elif callback_or_message.data in (Calls.MAIN_MENU,):
            await callback_or_message.answer('Main menu')

        create_menu_main_kb(rus_or_kaz, client_or_seller)

        await callback_or_message.message.edit_text(menu_text, reply_markup=create_menu_main_kb(rus_or_kaz, client_or_seller))
    elif isinstance(callback_or_message, types.Message):
        if 'start' not in callback_or_message.text:
            await callback_or_message.delete()
        bot_log.info(f'FROM MESSAGE - WAY (start)')
        response=await callback_or_message.answer(text='_',reply_markup=types.ReplyKeyboardRemove())
        await response.delete()
        await callback_or_message.answer(menu_text, reply_markup=create_menu_main_kb(rus_or_kaz,client_or_seller))
        await state.set_state(SpecialStates.messages_of)

router.callback_query.register(main_menu, F.data.in_([Calls.CLIENT_CHOICE, Calls.SELLER_CHOICE, Calls.MAIN_MENU]), StateFilter(SpecialStates.messages_of))
router.message.register(main_menu, F.text.in_([BOT_REPLIES['to_main_menu_from_battery']['rus'],BOT_REPLIES['to_main_menu_from_battery']['kaz']]),
                        StateFilter(CatchBattery.catch_battery,SpecialStates.messanger,CatchCode.catch_code))