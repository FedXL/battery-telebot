from datetime import datetime
from typing import Union, Dict

from aiogram import types
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot_core.bot_db.alchemy_models import UserTelegram, Client, Seller, ClientProfile, SellerProfile
from bot_core.create_bot import bot_log
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
        is_full_profile = profile_completeness(profile=profile)
        profile_dict = profile_to_dict(profile=profile)
        if not profile:
            raise Exception('User has client or seller but no profile')

        profile_data_base = {'language': profile.language,
                             'profile_data': profile_dict,
                             'client_or_seller': client_or_seller,
                             'profile_completeness': is_full_profile}
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


def profile_completeness(profile: Union[ClientProfile, SellerProfile]) -> bool:
    '''Надо для определения какой в меню профиля меню заказывать полное или урезанное'''
    if isinstance(profile, ClientProfile):
        bot_log.warning('CLIENT profile_completeness')
        bot_log.info(f"Profile is full {profile.first_name} | {profile.second_name} | {profile.patronymic} | {profile.contact_phone} | {profile.contact_email}")
        if profile.first_name and profile.second_name and profile.patronymic and profile.contact_phone and profile.contact_email:
            bot_log.warning('CLIENT profile_completeness is full')
            return True
        else:
            bot_log.warning('CLIENT profile_completeness is NOT full')
            return False
    elif isinstance(profile, SellerProfile):
        bot_log.warning('SELLER profile_completeness')
        bot_log.info(f"Profile is full {profile.first_name} | {profile.second_name} | {profile.patronymic} | {profile.company_address} | {profile.company_name} | {profile.contact_phone} | {profile.contact_email}")
        if profile.first_name and profile.second_name and profile.patronymic and profile.company_address and profile.company_name and profile.contact_phone and profile.contact_email:
            bot_log.warning('SELLER profile_completeness is full')
            return True
        else:
            bot_log.warning('SELLER profile_completeness is NOT full')
            return False

def profile_to_dict(profile: Union[ClientProfile,SellerProfile]) -> dict:
    profile_dict = {
        'client_or_seller': 'client',
        'phone_from_telegram': profile.phone_from_telegram,
        'first_name': profile.first_name,
        'second_name': profile.second_name,
        'patronymic': profile.patronymic,
        'contact_phone': profile.contact_phone,
        'contact_email': profile.contact_email,
        'language': profile.language
    }
    if isinstance(profile, SellerProfile):
        profile_dict['client_or_seller'] = 'seller'
        profile_dict['company_address'] = profile.company_address
        profile_dict['company_name'] = profile.company_name
    return profile_dict



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


async def save_profile_data_collected(db: AsyncSession, state_data: dict, telegram_id: int):
    async with db.begin():
        existing_user = await db.execute(select(UserTelegram).filter(UserTelegram.telegram_id == telegram_id))
        existing_user = existing_user.scalar_one_or_none()
        if not existing_user:
            raise Exception('User not found')
        if state_data['client_or_seller'] == 'client':
            existing_client = await db.execute(
                select(Client).filter(Client.user_telegram_id == existing_user.telegram_id))
            client = existing_client.scalar_one_or_none()
            if not client:
                raise Exception('Client not found')
            existing_profile = await db.execute(select(ClientProfile).filter(ClientProfile.client_id == client.id))
            profile = existing_profile.scalar_one_or_none()
            if not profile:
                raise Exception('Profile not found')

            profile.first_name = state_data['profile']['SurveyLowStates:first_name_collect']
            profile.second_name = state_data['profile']['SurveyLowStates:second_name_collect']
            profile.patronymic = state_data['profile']['SurveyLowStates:patronymic_name_collect']
            profile.contact_phone = state_data['profile']['SurveyLowStates:phone_collect']
            profile.contact_email = state_data['profile']['SurveyLowStates:email_collect']
            profile.language = state_data['language']

        elif state_data['client_or_seller'] == 'seller':
            existing_seller = await db.execute(
                select(Seller).filter(Seller.user_telegram_id == existing_user.telegram_id))
            seller = existing_seller.scalar_one_or_none()
            if not seller:
                raise Exception('Seller not found')
            existing_profile = await db.execute(select(SellerProfile).filter(SellerProfile.seller_id == seller.id))
            profile = existing_profile.scalar_one_or_none()
            if not profile:
                raise Exception('Profile not found')
            profile.first_name = state_data['profile']['SurveyStates:first_name_collect']
            profile.second_name = state_data['profile']['SurveyStates:second_name_collect']
            profile.patronymic = state_data['profile']['SurveyStates:patronymic_name_collect']
            profile.contact_phone = state_data['profile']['SurveyStates:phone_collect']
            profile.contact_email = state_data['profile']['SurveyStates:email_collect']
            profile.language = state_data['language']
            profile.company_name = state_data['profile']['SurveyStates:trading_point_name_collect']
            profile.company_address = state_data['profile']['SurveyStates:trading_point_address_collect']

        else:
            raise Exception('Unknown client_or_seller')
    return True, 'Данные профиля сохранены'

