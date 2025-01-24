from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from bot_core.bot_db.alchemy_models import UserTelegram, Client, ClientProfile, Seller, SellerProfile
from bot_core.bot_db.db_engine import telegram_bot_session
from bot_core.utils.callback_actions import Calls, CollectDataStates

router = Router()

async def main_menu(callback: types.CallbackQuery, state: FSMContext):
    '''
    1) функция делаем полноценного юзера в бд telegram user>client>client_profile
    2) делаем полноценного баера в бд telegram telegam user>seller>seller_profile
    3) делаем меню для клиента или продавца
    '''

    # 1step create client
    state_dict = await state.get_data()
    rus_or_kaz = state_dict.get('language')
    if callback.data in  (Calls.CLIENT_CHOICE, Calls.SELLER_CHOICE):
        await callback.answer('Creating Profile')

        async with telegram_bot_session() as session:
            async with session.begin():
                existing_user = await session.execute(
                    select(UserTelegram).filter(UserTelegram.telegram_id == callback.from_user.id)
                )
                existing_user = existing_user.scalar_one_or_none()
                if not existing_user:
                    raise Exception('User not found')
                if callback.data == Calls.SELLER_CHOICE:
                    client = existing_user.client_telegram
                    if client:
                        raise Exception('Client already exists!')
                    new_client = Client(user_telegram_id=existing_user.telegram_id)
                    session.add(new_client)
                    new_profile_client = ClientProfile(client_id=new_client.id)
                    new_profile_client.language = rus_or_kaz
                    session.add(new_profile_client)
                elif callback.data == Calls.CLIENT_CHOICE:
                    seller = existing_user.seller_telegram
                    if seller:
                        raise Exception('Seller already exists!')
                    new_seller = Seller(user_telegram_id=existing_user.telegram_id)
                    session.add(new_seller)
                    new_profile_seller = SellerProfile(seller_id=new_seller.id)
                    new_profile_seller.language = rus_or_kaz
                    session.add(new_profile_seller)
                else:
                    raise Exception('Unknown user type (client or seller)')
                await session.commit()
    await callback.answer('ты в главном меню')
    await callback.message.answer('Теперь ты в главном меню')

router.callback_query.register(main_menu, F.data.in_([Calls.CLIENT_CHOICE, Calls.SELLER_CHOICE, Calls.MAIN_MENU]),StateFilter(CollectDataStates.messages_of))