from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from bot_core.bot_db.db_handlers import create_profiles
from bot_core.create_bot import bot_log
from bot_core.utils.callback_actions import Calls, CollectDataStates
from bot_core.utils.download_replies import BOT_REPLIES


router = Router()


def create_menu_main_kb(language:str) -> types.InlineKeyboardMarkup:
    '''
    Результаты лоттереи
    Ваш код
    Зарегистрировать аккумулятор
    '''
    lottery_result_button=BOT_REPLIES['lottery_result_button'][language]
    profile_button=BOT_REPLIES['profile_button'][language]
    register_battery_button=BOT_REPLIES['register_battery_button'][language]
    help_button_text=BOT_REPLIES['help_button'][language]



    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=lottery_result_button, callback_data=Calls.LOTTERY_RESULTS),
                types.InlineKeyboardButton(text=profile_button, callback_data=Calls.GO_TO_PROFILE),
                types.InlineKeyboardButton(text=register_battery_button, callback_data=Calls.REGISTRATION_BATTERY),
                types.InlineKeyboardButton(text=help_button_text, callback_data=Calls.HELP))
    builder.adjust(1)
    keyboard = builder.as_markup()
    return keyboard



async def main_menu(callback_or_message: types.CallbackQuery | types.Message, state: FSMContext, db: AsyncSession):
    """
    меню
    1) генерация текста преветсвия.
    2) создание пользователя если Calls в ClientChoice и SellerChoice
    3) создание меню для пользователя или продавца
    4) проверка и добавление в storage langugage и cleient_or_seller
    """

    state_dict = await state.get_data()
    rus_or_kaz = state_dict.get('language')
    seller_or_client = state_dict.get('client_or_seller')

    if isinstance(callback_or_message, types.CallbackQuery):
        bot_log.info(f'CALLBACK - WAY')
        if callback_or_message.data in (Calls.CLIENT_CHOICE, Calls.SELLER_CHOICE):
            await callback_or_message.answer('Creating Profile')
            await create_profiles(db=db,rus_or_kaz=rus_or_kaz, telegram_id=callback_or_message.from_user.id,callback_data=callback_or_message.data)
        elif callback_or_message.data in (Calls.MAIN_MENU,):
            await callback_or_message.answer('Main menu')

        create_menu_main_kb(rus_or_kaz)
        await callback_or_message.message.edit_text(BOT_REPLIES['main_menu_text'][rus_or_kaz], reply_markup=create_menu_main_kb(rus_or_kaz))
    elif isinstance(callback_or_message, types.Message):
        bot_log.info(f'FROM MESSAGE - WAY (start)')
        create_menu_main_kb(rus_or_kaz)
        await callback_or_message.answer(BOT_REPLIES['main_menu_text'][rus_or_kaz], reply_markup=create_menu_main_kb(rus_or_kaz))

router.callback_query.register(main_menu, F.data.in_([Calls.CLIENT_CHOICE, Calls.SELLER_CHOICE, Calls.MAIN_MENU]))