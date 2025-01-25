from datetime import datetime
from typing import Union, Dict

from aiogram import types
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot_core.bot_db.alchemy_models import UserTelegram, Client, Seller, ClientProfile, SellerProfile
from bot_core.utils.callback_actions import Calls


async def check_user(telegram_id, db: AsyncSession) -> Union[bool, bool] or Union[bool, Dict[str, str]]:

    async with db.begin():
        telegram_user = await db.execute(select(UserTelegram).filter(UserTelegram.telegram_id == telegram_id))
        telegram_user = telegram_user.scalar_one_or_none()
        if not telegram_user:
            return False, False

        client = await db.execute(select(Client).filter(Client.user_telegram_id == telegram_user.telegram_id))
        client = client.scalar_one_or_none()

        seller = await db.execute(select(Seller).filter(Seller.user_telegram_id == telegram_user.telegram_id))
        seller = seller.scalar_one_or_none()

        if client and seller:
            raise Exception('User has both client and seller profiles')

        if not client and not seller:
            return True, False

        if client:

            client_or_seller='client'
            profile = await db.execute(select(ClientProfile).filter(ClientProfile.client_id == client.id))
        elif seller:
            client_or_seller='seller'
            profile = await db.execute(select(SellerProfile).filter(SellerProfile.seller_id == seller.id))

        profile = profile.scalar_one_or_none()
        if not profile:
            raise Exception('User has client or seller but no profile')
        profile_data_base = {'language':profile.language,'client_or_seller':client_or_seller}
        return True, profile_data_base


async def create_user(telegram_id, username, db: AsyncSession):
    async with db.begin():
        new_user = UserTelegram(
            telegram_id=telegram_id,
            username=username,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(new_user)
        await db.flush()
    return new_user







async def create_profiles(db: AsyncSession,
                          rus_or_kaz: str,
                          callback_data:str,
                          telegram_id):
    async with db.begin():
        existing_user = await db.execute(select(UserTelegram).filter(UserTelegram.telegram_id == telegram_id))
        existing_user = existing_user.scalar_one_or_none()
        if not existing_user:
            raise Exception('User not found')

        if callback_data == Calls.SELLER_CHOICE:
            existing_client = await db.execute(
                select(Client).filter(Client.user_telegram_id == existing_user.telegram_id))
            client = existing_client.scalar_one_or_none()
            if client:
                return False , f"На этот телеграм айди {telegram_id} уже зарегистрирован покупатель"
            new_seller = Seller(user_telegram_id=existing_user.telegram_id)
            db.add(new_seller)
            await db.flush()
            new_profile_seller = SellerProfile(seller_id=new_seller.id)
            new_profile_seller.language = rus_or_kaz
            db.add(new_profile_seller)
        elif callback_data == Calls.CLIENT_CHOICE:
            existing_seller = await db.execute(
                select(Seller).filter(Seller.user_telegram_id == existing_user.telegram_id))
            seller = existing_seller.scalar_one_or_none()
            if seller:
                return False, f"На этот телеграм айди {telegram_id} уже зарегистрирован продавец"
            new_client = Client(user_telegram_id=existing_user.telegram_id)
            db.add(new_client)
            await db.flush()
            new_client_profile = ClientProfile(client_id=new_client.id)
            new_client_profile.language = rus_or_kaz
            db.add(new_client_profile)
        else:
            return False, f'Непонятный callback_data {callback_data}'
    return True, 'Профиль создан'
