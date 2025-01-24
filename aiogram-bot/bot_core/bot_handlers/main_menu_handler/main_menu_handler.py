from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot_core.bot_db.alchemy_models import UserTelegram, Client, ClientProfile, Seller, SellerProfile
from bot_core.bot_db.db_engine import telegram_bot_session
from bot_core.utils.callback_actions import Calls, CollectDataStates
from bot_core.utils.download_replies import BOT_REPLIES

router = Router()


async def create_profiles(db:AsyncSession,callback: types.CallbackQuery, rus_or_kaz:str):
    existing_user = await db.execute(select(UserTelegram).filter(UserTelegram.telegram_id == callback.from_user.id))
    existing_user = existing_user.scalar_one_or_none()
    if not existing_user:
        raise Exception('User not found')

    if callback.data == Calls.SELLER_CHOICE:
        existing_client = await db.execute(select(Client).filter(Client.user_telegram_id == existing_user.telegram_id))
        client = existing_client.scalar_one_or_none()
        if client:
            await callback.message.answer(
                f'На Этот телеграм айди {callback.from_user.id} уже зарегистрирован Покупатель')
            raise Exception('Client already exists!')
        new_seller = Seller(user_telegram_id=existing_user.telegram_id)
        db.add(new_seller)
        await db.flush()
        new_profile_seller = SellerProfile(client_id=new_seller.id)
        new_profile_seller.language = rus_or_kaz
        db.add(new_profile_seller)
    elif callback.data == Calls.CLIENT_CHOICE:
        existing_seller = await db.execute(select(Seller).filter(Seller.user_telegram_id == existing_user.telegram_id))
        seller = existing_seller.scalar_one_or_none()
        if seller:
            await callback.message.answer(f'На Этот телеграм айди {callback.from_user.id} уже зарегистрирован Продавец')
            raise Exception('Seller already exists!')
        new_client = Client(user_telegram_id=existing_user.telegram_id)
        db.add(new_client)
        await db.flush()
        new_client_profile = ClientProfile(seller_id=new_client.id)
        new_client_profile.language = rus_or_kaz
        db.add(new_client_profile)
    else:
        raise Exception('Unknown user type (client or seller)')


def create_menu_main_kb(language:str) -> types.InlineKeyboardMarkup:
    '''
    Результаты лоттереи
    Ваш код
    Зарегистрировать аккумулятор
    '''
    lottery_result_button=BOT_REPLIES['lottery_result_button'][language]
    profile_button=BOT_REPLIES['profile_button'][language]
    register_battery_button=BOT_REPLIES['register_battery_button'][language]
    help_text=BOT_REPLIES['help_text'][language]



    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=lottery_result_button, callback_data=Calls.LOTTERY_RESULTS),
                types.InlineKeyboardButton(text=profile_button, callback_data=Calls.GO_TO_PROFILE),
                types.InlineKeyboardButton(text=register_battery_button, callback_data=Calls.REGISTRATION_BATTERY),
                types.InlineKeyboardButton(text=help_text, callback_data=Calls.HELP))
    builder.adjust(1)
    keyboard = builder.as_markup()
    return keyboard




async def main_menu(callback: types.CallbackQuery, state: FSMContext, db: AsyncSession):
    '''
    1) функция делаем полноценного юзера в бд telegram user>client>client_profile
    2) делаем полноценного баера в бд telegram telegam user>seller>seller_profile
    3) делаем меню для клиента или продавца
    '''

    state_dict = await state.get_data()
    rus_or_kaz = state_dict.get('language')

    if callback.data in (Calls.CLIENT_CHOICE, Calls.SELLER_CHOICE):
        await callback.answer('Creating Profile')
        async with db.begin():
            await create_profiles(db, callback, rus_or_kaz)
        await db.commit()
    elif callback.data == Calls.MAIN_MENU:
        if
    create_menu_main_kb(rus_or_kaz)
    await callback.answer('Ok')
    await callback.message.answer(BOT_REPLIES['main_menu_text'][rus_or_kaz], reply_markup=create_menu_main_kb(rus_or_kaz))

router.callback_query.register(main_menu, F.data.in_([Calls.CLIENT_CHOICE, Calls.SELLER_CHOICE, Calls.MAIN_MENU]), StateFilter(CollectDataStates.messages_of))